"""Research Agent Implementation using Ollama and local knowledge base.

This module implements a research agent that can perform iterative searches
and synthesis to answer complex research questions using local-only resources.
"""

from typing import Literal

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages
from langgraph.graph import StateGraph, START, END

from state_definitions import ResearcherState, ResearcherOutputState
from utils import local_search, think_tool, get_today_str
from prompts import research_agent_prompt, compress_research_system_prompt, compress_research_human_message


# ===== CONFIGURATION =====

# Set up tools and model binding
tools = [local_search, think_tool]
tools_by_name = {tool.name: tool for tool in tools}

# Initialize Ollama model with mistral
# Make sure Ollama is running: `ollama serve`
# And pull the model: `ollama pull mistral`
model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",  # Default Ollama server URL
    temperature=0.3,  # Lower temperature for more focused research
)

model_with_tools = model.bind_tools(tools)

# Compress model (same mistral instance, could be a larger model if available)
compress_model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",
    temperature=0.2,  # Even lower for synthesis
)


# ===== AGENT NODES =====

def llm_call(state: ResearcherState):
    """Analyze current state and decide on next actions.

    The model analyzes the current conversation state and decides whether to:
    1. Call search tools to gather more information
    2. Provide a final answer based on gathered information

    Returns updated state with the model's response.
    """
    messages = state.get("researcher_messages", [])
    
    # Prepare system message with current date
    system_message = research_agent_prompt.format(date=get_today_str())
    
    response = model_with_tools.invoke(
        [SystemMessage(content=system_message)] + messages
    )
    
    return {
        "researcher_messages": messages + [response]
    }


def tool_node(state: ResearcherState):
    """Execute all tool calls from the previous LLM response.

    Executes all tool calls from the previous LLM responses.
    Returns updated state with tool execution results.
    """
    messages = state.get("researcher_messages", [])
    last_message = messages[-1]
    
    tool_calls = last_message.tool_calls
    
    # Execute all tool calls
    observations = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observations.append(tool.invoke(tool_call["args"]))
    
    # Create tool message outputs
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        ) for observation, tool_call in zip(observations, tool_calls)
    ]
    
    return {"researcher_messages": messages + tool_outputs}


def compress_research(state: ResearcherState) -> dict:
    """Compress research findings into a concise summary.

    Takes all the research messages and tool outputs and creates
    a compressed summary suitable for downstream processing.
    """
    messages = state.get("researcher_messages", [])
    
    system_message = compress_research_system_prompt.format(date=get_today_str())
    compress_messages = [
        SystemMessage(content=system_message)
    ] + messages + [
        HumanMessage(content=compress_research_human_message)
    ]
    
    response = compress_model.invoke(compress_messages)
    
    # Extract raw notes from tool and AI messages
    raw_notes = [
        str(m.content) for m in filter_messages(
            messages, 
            include_types=["tool", "ai"]
        )
    ]
    
    return {
        "compressed_research": str(response.content),
        "raw_notes": raw_notes
    }


# ===== ROUTING LOGIC =====

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Determine whether to continue research or provide final answer.

    Determines whether the agent should continue the research loop or provide
    a final answer based on whether the LLM made tool calls.

    Returns:
        "tool_node": Continue to tool execution
        "compress_research": Stop and compress research
    """
    messages = state.get("researcher_messages", [])
    if not messages:
        return "compress_research"
    
    last_message = messages[-1]
    
    # If the LLM makes a tool call, continue to tool execution
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_node"
    # Otherwise, we have a final answer
    return "compress_research"


# ===== GRAPH CONSTRUCTION =====

# Build the agent workflow
agent_builder = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

# Add nodes to the graph
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_node("compress_research", compress_research)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_node": "tool_node",  # Continue research loop
        "compress_research": "compress_research",  # Provide final answer
    },
)
agent_builder.add_edge("tool_node", "llm_call")  # Loop back for more research
agent_builder.add_edge("compress_research", END)

# Compile the agent
researcher_agent = agent_builder.compile()


if __name__ == "__main__":
    # Example usage
    from langchain_core.messages import HumanMessage
    
    # Test the researcher agent
    initial_state = {
        "researcher_messages": [
            HumanMessage(content="What are the key concepts in machine learning?")
        ]
    }
    
    result = researcher_agent.invoke(initial_state)
    print("\n=== Research Complete ===")
    print(f"Compressed Research:\n{result.get('compressed_research', 'No research completed')}")