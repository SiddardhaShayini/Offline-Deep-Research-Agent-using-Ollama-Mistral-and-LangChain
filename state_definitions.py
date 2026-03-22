"""State definitions for research workflow."""

from typing import List, TypedDict, Optional
from pydantic import BaseModel, Field


class Summary(BaseModel):
    """Summary of webpage content."""
    summary: str = Field(description="A concise summary of the webpage content")
    key_excerpts: str = Field(description="Key excerpts and quotes from the webpage")


class ResearcherState(TypedDict, total=False):
    """State for individual researcher agents."""
    researcher_messages: List  # LangChain message objects
    research_topic: str
    compressed_research: str
    raw_notes: List[str]


class ResearcherOutputState(TypedDict):
    """Output state for researcher agent."""
    compressed_research: str
    raw_notes: List[str]


class SupervisorState(TypedDict, total=False):
    """State for supervisor agent coordinating multiple researchers."""
    supervisor_messages: List  # LangChain message objects
    research_brief: str
    notes: List[str]
    raw_notes: List[str]
    research_iterations: int