"""Main entry point for Ollama-based research system.

This script demonstrates how to use the research agents with Ollama and mistral.
"""

import asyncio
from langchain_core.messages import HumanMessage
from research_agent import researcher_agent
from multi_agent_supervisor import supervisor_agent


def run_single_agent_research(query: str):
    """Run a single research agent on a query.
    
    Args:
        query: The research question to investigate
    """
    print(f"\n{'='*80}")
    print(f"Starting Single Agent Research: {query}")
    print(f"{'='*80}\n")
    
    initial_state = {
        "researcher_messages": [HumanMessage(content=query)]
    }
    
    try:
        result = researcher_agent.invoke(initial_state)
        
        print("\n" + "="*80)
        print("RESEARCH COMPLETE")
        print("="*80)
        print(f"\nCompressed Research Summary:\n{result.get('compressed_research', 'No research completed')}")
        print(f"\nRaw Notes:\n{result.get('raw_notes', [])}")
        
    except Exception as e:
        print(f"Error during research: {e}")
        import traceback
        traceback.print_exc()


async def run_supervisor_research(research_brief: str):
    """Run supervisor agent for coordinated multi-agent research.
    
    Args:
        research_brief: The research brief to guide the supervisor
    """
    print(f"\n{'='*80}")
    print(f"Starting Supervisor Coordinated Research")
    print(f"{'='*80}\n")
    print(f"Research Brief: {research_brief}\n")
    
    initial_state = {
        "supervisor_messages": [],
        "research_brief": research_brief,
        "research_iterations": 0
    }
    
    try:
        result = await supervisor_agent.ainvoke(initial_state)
        
        print("\n" + "="*80)
        print("SUPERVISOR RESEARCH COMPLETE")
        print("="*80)
        print(f"\nNotes: {result.get('notes', [])}")
        print(f"\nRaw Notes: {result.get('raw_notes', [])}")
        
    except Exception as e:
        print(f"Error during supervisor research: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("Ollama + mistral + LangChain Research System")
    print("="*80)
    print("\nMake sure Ollama is running: ollama serve")
    print("And pull mistral: ollama pull mistral\n")
    
    # Example 1: Single agent research
    print("\n>>> Example 1: Single Agent Research")
    run_single_agent_research("What is machine learning and what are its main applications?")
    
    # Example 2: Supervisor coordinated research (async)
    print("\n\n>>> Example 2: Supervisor Coordinated Research")
    asyncio.run(run_supervisor_research(
        "Research the fundamentals of machine learning and Python programming"
    ))
    
    print("\n" + "="*80)
    print("All research completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()