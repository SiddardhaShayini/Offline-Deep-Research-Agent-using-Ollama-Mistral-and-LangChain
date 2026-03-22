"""Multi-agent supervisor for coordinating research using Ollama.

This module implements a supervisor pattern where:
1. A supervisor agent coordinates research activities and delegates tasks
2. Multiple researcher agents work on specific sub-topics independently
3. Results are aggregated and compressed for final reporting
"""

import asyncio
from typing import Literal

from langchain_ollama import ChatOllama
from langchain_core.messages import (
    HumanMessage, 
    BaseMessage, 
    SystemMessage, 
    ToolMessage,
    filter_messages,
    AIMessage,
)
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from prompts import lead_researcher_prompt
from research_agent import researcher_agent
from state_definitions import SupervisorState
from utils import get_today_str, think_tool


def get_notes_from_tool_calls(messages: list[BaseMessage]) -> list[str]:
    """Extract research notes from ToolMessage objects in supervisor message history."""
    return [tool_msg.content for tool_msg in filter_messages(messages, include_types="tool")]


# ===== CONFIGURATION =====

supervisor_model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",
    temperature=0.3,
)

# Define tools as proper functions with @tool decorator
@tool
def conduct_research(research_topic: str) -> str:
    """Conduct research on a specific topic using a researcher agent.
    
    Args:
        research_topic: The specific topic to research
        
    Returns:
        The compressed research findings
    """
    # This is a placeholder - actual execution happens in supervisor_tools
    return f"Research conducted on: {research_topic}"


@tool
def research_complete() -> str:
    """Mark research as complete.
    
    Returns:
        Confirmation that research is complete
    """
    return "Research complete"


supervisor_tools = [conduct_research, research_complete, think_tool]
supervisor_model_with_tools = supervisor_model.bind_tools(supervisor_tools)

# System constants
max_researcher_iterations = 6  # Calls to think_tool + ConductResearch
max_concurrent_researchers = 3  # Maximum parallel research tasks


# ===== SUPERVISOR NODES =====

async def supervisor(state: SupervisorState) -> Command[Literal["supervisor_tools"]]:
    """Coordinate research activities.

    Analyzes the research brief and current progress to decide:
    - What research topics need investigation
    - Whether to conduct parallel research
    - When research is complete
    """
    supervisor_messages = state.get("supervisor_messages", [])
    research_brief = state.get("research_brief", "")
    
    # Prepare system message with current date and constraints
    system_message = lead_researcher_prompt.format(
        date=get_today_str(), 
        max_concurrent_research_units=max_concurrent_researchers,
        max_researcher_iterations=max_researcher_iterations
    )
    
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=f"Research Brief:\n{research_brief}")
    ] + supervisor_messages
    
    # Make decision about next research steps
    response = await supervisor_model_with_tools.ainvoke(messages)
    
    return Command(
        goto="supervisor_tools",
        update={
            "supervisor_messages": supervisor_messages + [response],
            "research_iterations": state.get("research_iterations", 0) + 1
        }
    )


async def supervisor_tools(state: SupervisorState) -> Command[Literal["supervisor", "__end__"]]:
    """Execute supervisor decisions - either conduct research or end the process.

    Handles:
    - Executing think_tool calls for strategic reflection
    - Launching parallel research agents for different topics
    - Aggregating research results
    - Determining when research is complete
    """
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    
    if not supervisor_messages:
        return Command(
            goto=END,
            update={
                "notes": [],
                "research_brief": state.get("research_brief", "")
            }
        )
    
    most_recent_message = supervisor_messages[-1]
    
    # Initialize variables for single return pattern
    tool_messages = []
    all_raw_notes = []
    next_step = "supervisor"  # Default next step
    should_end = False
    
    # Check exit criteria first
    exceeded_iterations = research_iterations >= max_researcher_iterations
    no_tool_calls = not (hasattr(most_recent_message, 'tool_calls') and most_recent_message.tool_calls)
    
    # Check for ResearchComplete
    research_complete_called = False
    if hasattr(most_recent_message, 'tool_calls') and most_recent_message.tool_calls:
        research_complete_called = any(
            tool_call.get("name") == "research_complete" 
            for tool_call in most_recent_message.tool_calls
        )
    
    if exceeded_iterations or no_tool_calls or research_complete_called:
        should_end = True
        next_step = END
    else:
        # Execute ALL tool calls before deciding next step
        try:
            if hasattr(most_recent_message, 'tool_calls'):
                # Separate think_tool calls from conduct_research calls
                think_tool_calls = [
                    tool_call for tool_call in most_recent_message.tool_calls 
                    if tool_call.get("name") == "think_tool"
                ]
                
                conduct_research_calls = [
                    tool_call for tool_call in most_recent_message.tool_calls 
                    if tool_call.get("name") == "conduct_research"
                ]
                
                # Handle think_tool calls (synchronous)
                for tool_call in think_tool_calls:
                    observation = think_tool.invoke(tool_call.get("args", {}))
                    tool_messages.append(
                        ToolMessage(
                            content=observation,
                            name=tool_call.get("name", "think_tool"),
                            tool_call_id=tool_call.get("id", "")
                        )
                    )
                
                # Handle conduct_research calls (asynchronous)
                if conduct_research_calls:
                    # Launch parallel research agents
                    coros = []
                    for tool_call in conduct_research_calls:
                        research_topic = tool_call.get("args", {}).get("research_topic", "")
                        coros.append(
                            researcher_agent.ainvoke({
                                "researcher_messages": [
                                    HumanMessage(content=research_topic)
                                ],
                                "research_topic": research_topic
                            })
                        )
                    
                    # Wait for all research to complete
                    tool_results = await asyncio.gather(*coros, return_exceptions=True)
                    
                    # Format research results as tool messages
                    for result, tool_call in zip(tool_results, conduct_research_calls):
                        if isinstance(result, Exception):
                            content = f"Error conducting research: {str(result)}"
                        else:
                            content = result.get("compressed_research", "Error synthesizing research report")
                        
                        tool_messages.append(
                            ToolMessage(
                                content=content,
                                name=tool_call.get("name", "conduct_research"),
                                tool_call_id=tool_call.get("id", "")
                            )
                        )
                    
                    # Aggregate raw notes from all research
                    all_raw_notes = [
                        "\n".join(result.get("raw_notes", []) if not isinstance(result, Exception) else []) 
                        for result in tool_results
                    ]
        
        except Exception as e:
            print(f"Error in supervisor tools: {e}")
            should_end = True
            next_step = END
    
    # Single return point with appropriate state updates
    if should_end:
        return Command(
            goto=next_step,
            update={
                "notes": get_notes_from_tool_calls(supervisor_messages),
                "research_brief": state.get("research_brief", "")
            }
        )
    else:
        return Command(
            goto=next_step,
            update={
                "supervisor_messages": supervisor_messages + tool_messages,
                "raw_notes": all_raw_notes
            }
        )


# ===== GRAPH CONSTRUCTION =====

# Build supervisor graph
supervisor_builder = StateGraph(SupervisorState)
supervisor_builder.add_node("supervisor", supervisor)
supervisor_builder.add_node("supervisor_tools", supervisor_tools)
supervisor_builder.add_edge(START, "supervisor")
supervisor_agent = supervisor_builder.compile()


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        initial_state = {
            "supervisor_messages": [],
            "research_brief": "Conduct research on the latest developments in machine learning",
            "research_iterations": 0
        }
        
        result = await supervisor_agent.ainvoke(initial_state)
        print("\n=== Supervisor Research Complete ===")
        print(f"Notes: {result.get('notes', [])}")
    
    asyncio.run(main())