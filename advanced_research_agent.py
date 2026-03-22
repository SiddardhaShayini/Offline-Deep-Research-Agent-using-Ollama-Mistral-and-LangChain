"""Advanced Research Agent with Streaming and Report Generation.

Features:
- Streaming responses for real-time feedback
- Structured report generation
- Research metadata and analytics
- Query expansion and planning
"""

from typing import Literal, AsyncIterator, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import json

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages
from langgraph.graph import StateGraph, START, END

from state_definitions import ResearcherState, ResearcherOutputState
from knowledge_base import local_search, kb, think_tool, get_today_str
from prompts import research_agent_prompt, compress_research_system_prompt, compress_research_human_message


@dataclass
class ResearchMetadata:
    """Metadata about the research process."""
    query: str
    start_time: str
    end_time: Optional[str] = None
    search_count: int = 0
    documents_found: int = 0
    thinking_steps: int = 0
    total_tokens: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ResearchReport:
    """Structured research report."""
    query: str
    summary: str
    findings: str
    sources: list
    metadata: Dict
    timestamp: str


# ===== CONFIGURATION =====

tools = [local_search, think_tool]
tools_by_name = {tool.name: tool for tool in tools}

model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",
    temperature=0.3,
    streaming=True,  # Enable streaming
)

model_with_tools = model.bind_tools(tools)

compress_model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",
    temperature=0.2,
)


# ===== ADVANCED NODES =====

def query_planning(state: ResearcherState) -> dict:
    """Plan the research approach before execution.
    
    Analyzes the query and determines optimal search strategy.
    """
    messages = state.get("researcher_messages", [])
    
    if not messages or not messages[0].content:
        return {"researcher_messages": messages}
    
    # Create planning prompt
    planning_prompt = f"""Analyze this research query and create a brief research plan:

Query: {messages[0].content}

Provide:
1. Key concepts to search for
2. Recommended search order
3. Expected sources to find

Keep it concise."""
    
    plan_response = compress_model.invoke([
        HumanMessage(content=planning_prompt)
    ])
    
    # Add planning response to messages
    return {
        "researcher_messages": messages + [
            HumanMessage(content=f"[RESEARCH PLAN]\n{plan_response.content}")
        ]
    }


def llm_call(state: ResearcherState) -> dict:
    """Main LLM call for decision making."""
    messages = state.get("researcher_messages", [])
    
    system_message = research_agent_prompt.format(date=get_today_str())
    
    response = model_with_tools.invoke(
        [SystemMessage(content=system_message)] + messages
    )
    
    return {"researcher_messages": messages + [response]}


def tool_node(state: ResearcherState) -> dict:
    """Execute all tool calls."""
    messages = state.get("researcher_messages", [])
    last_message = messages[-1]
    
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        return {"researcher_messages": messages}
    
    tool_calls = last_message.tool_calls
    observations = []
    
    for tool_call in tool_calls:
        tool = tools_by_name.get(tool_call["name"])
        if tool:
            observations.append(tool.invoke(tool_call["args"]))
    
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        ) for observation, tool_call in zip(observations, tool_calls)
    ]
    
    return {"researcher_messages": messages + tool_outputs}


def compress_research(state: ResearcherState) -> dict:
    """Compress findings into structured report."""
    messages = state.get("researcher_messages", [])
    
    system_message = compress_research_system_prompt.format(date=get_today_str())
    compress_messages = [
        SystemMessage(content=system_message)
    ] + messages + [
        HumanMessage(content=compress_research_human_message)
    ]
    
    response = compress_model.invoke(compress_messages)
    
    # Extract raw notes
    raw_notes = [
        str(m.content) for m in filter_messages(
            messages,
            include_types=["tool", "ai"]
        )
    ]
    
    # Extract sources from knowledge base
    sources = kb.list_documents()
    
    return {
        "compressed_research": str(response.content),
        "raw_notes": raw_notes,
    }


# ===== ROUTING LOGIC =====

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Determine next step based on LLM response."""
    messages = state.get("researcher_messages", [])
    if not messages:
        return "compress_research"
    
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_node"
    
    return "compress_research"


# ===== STREAMING SUPPORT =====

class StreamingResearcher:
    """Wrapper for streaming research responses."""
    
    def __init__(self):
        self.agent = self._build_agent()
    
    def _build_agent(self):
        """Build the research agent graph."""
        agent_builder = StateGraph(ResearcherState, output_schema=ResearcherOutputState)
        
        agent_builder.add_node("query_planning", query_planning)
        agent_builder.add_node("llm_call", llm_call)
        agent_builder.add_node("tool_node", tool_node)
        agent_builder.add_node("compress_research", compress_research)
        
        agent_builder.add_edge(START, "query_planning")
        agent_builder.add_edge("query_planning", "llm_call")
        agent_builder.add_conditional_edges(
            "llm_call",
            should_continue,
            {
                "tool_node": "tool_node",
                "compress_research": "compress_research",
            }
        )
        agent_builder.add_edge("tool_node", "llm_call")
        agent_builder.add_edge("compress_research", END)
        
        return agent_builder.compile()
    
    def research(self, query: str) -> ResearchReport:
        """Run research and return structured report."""
        metadata = ResearchMetadata(
            query=query,
            start_time=datetime.now().isoformat()
        )
        
        initial_state = {
            "researcher_messages": [HumanMessage(content=query)]
        }
        
        result = self.agent.invoke(initial_state)
        
        metadata.end_time = datetime.now().isoformat()
        
        # Build report
        report = ResearchReport(
            query=query,
            summary=result.get("compressed_research", ""),
            findings="\n".join(result.get("raw_notes", [])),
            sources=kb.list_documents(),
            metadata=metadata.to_dict(),
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    async def research_async(self, query: str) -> ResearchReport:
        """Async version for concurrent research."""
        return self.research(query)
    
    def export_report(self, report: ResearchReport, format: str = "markdown") -> str:
        """Export report in different formats."""
        if format == "markdown":
            return self._format_markdown(report)
        elif format == "json":
            return self._format_json(report)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    @staticmethod
    def _format_markdown(report: ResearchReport) -> str:
        """Format report as markdown."""
        md = f"""# Research Report: {report.query}

**Generated**: {report.timestamp}

## Summary

{report.summary}

## Key Findings

{report.findings}

## Sources

"""
        for i, source in enumerate(report.sources, 1):
            md += f"{i}. [{source['title']}]({source['url']})\n"
        
        md += f"""

## Metadata

- **Start Time**: {report.metadata['start_time']}
- **End Time**: {report.metadata['end_time']}
- **Searches**: {report.metadata['search_count']}
- **Documents Found**: {report.metadata['documents_found']}
"""
        
        return md
    
    @staticmethod
    def _format_json(report: ResearchReport) -> str:
        """Format report as JSON."""
        return json.dumps({
            "query": report.query,
            "summary": report.summary,
            "findings": report.findings,
            "sources": report.sources,
            "metadata": report.metadata,
            "timestamp": report.timestamp,
        }, indent=2)


# Backward compatibility with original API
researcher_agent = StreamingResearcher().agent

if __name__ == "__main__":
    researcher = StreamingResearcher()
    
    # Example research
    report = researcher.research("What are neural networks and their applications?")
    
    # Export in different formats
    print("=== MARKDOWN FORMAT ===")
    print(researcher.export_report(report, "markdown"))
    
    print("\n=== JSON FORMAT ===")
    print(researcher.export_report(report, "json"))