"""Research Utilities for offline-first search using Ollama."""

from pathlib import Path
from datetime import datetime
from typing import List, Literal
import json

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %d, %Y")


def get_current_dir() -> Path:
    """Get the current directory of the module."""
    try:
        return Path(__file__).resolve().parent
    except NameError:  # __file__ is not defined
        return Path.cwd()


# ===== LOCAL KNOWLEDGE BASE =====

class LocalKnowledgeBase:
    """Simple in-memory knowledge base for research topics.
    
    In production, this would be replaced with:
    - File system based knowledge base
    - Vector database (Chroma, Pinecone, etc.)
    - Local document store
    """
    
    def __init__(self):
        self.documents = {}
        self._initialize_default_kb()
    
    def _initialize_default_kb(self):
        """Initialize with some default research topics."""
        # This is a simple example. In production, load from files or DB
        self.documents = {
            "ai": [
                {
                    "title": "Artificial Intelligence Fundamentals",
                    "url": "local://kb/ai-fundamentals.md",
                    "content": """
# Artificial Intelligence Fundamentals

## Definition
Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence. These tasks include visual perception, speech recognition, decision-making, and language translation.

## Key Areas
1. **Machine Learning**: Systems that learn from data without explicit programming
2. **Deep Learning**: Neural networks with multiple layers for complex pattern recognition
3. **Natural Language Processing**: Understanding and generating human language
4. **Computer Vision**: Interpreting visual information from images and videos

## Current Applications
- Healthcare diagnostics
- Financial forecasting
- Autonomous vehicles
- Language models and chatbots
- Recommendation systems

## Limitations
- Requires large amounts of training data
- Computationally expensive
- Lacks true understanding and reasoning
- Safety and bias concerns
"""
                },
                {
                    "title": "Machine Learning Models Overview",
                    "url": "local://kb/ml-models.md",
                    "content": """
# Machine Learning Models

## Supervised Learning
- Linear Regression: Predicting continuous values
- Classification: Predicting categories
- Decision Trees: Tree-based decision making
- Random Forests: Ensemble of decision trees

## Unsupervised Learning
- Clustering: Grouping similar data points
- Dimensionality Reduction: Reducing feature count
- Anomaly Detection: Finding outliers

## Deep Learning
- Neural Networks: Connected layers of neurons
- Convolutional Neural Networks (CNN): For image processing
- Recurrent Neural Networks (RNN): For sequence data
- Transformers: State-of-the-art for NLP
"""
                }
            ],
            "python": [
                {
                    "title": "Python Programming Guide",
                    "url": "local://kb/python-guide.md",
                    "content": """
# Python Programming

## Core Concepts
- Variables and Data Types: str, int, float, bool, list, dict, set
- Control Flow: if/else, loops, functions
- Object-Oriented Programming: Classes, inheritance, polymorphism
- Error Handling: Try/except blocks, custom exceptions

## Popular Libraries
- NumPy: Numerical computing
- Pandas: Data manipulation
- Matplotlib/Seaborn: Data visualization
- Scikit-learn: Machine learning
- TensorFlow/PyTorch: Deep learning

## Best Practices
- Use virtual environments
- Follow PEP 8 style guide
- Write tests for critical functions
- Document code with docstrings
"""
                }
            ]
        }
    
    def search(self, query: str, max_results: int = 3) -> List[dict]:
        """Search the knowledge base for relevant documents.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of matching documents
        """
        results = []
        
        # Simple keyword matching (in production, use vector similarity)
        query_terms = query.lower().split()
        
        for category, docs in self.documents.items():
            for doc in docs:
                # Score based on keyword matches
                score = 0
                content_lower = (doc["title"] + " " + doc["content"]).lower()
                
                for term in query_terms:
                    if term in content_lower:
                        score += content_lower.count(term)
                
                if score > 0:
                    results.append({
                        "title": doc["title"],
                        "url": doc["url"],
                        "content": doc["content"][:1000],  # Truncate for display
                        "raw_content": doc["content"],
                        "score": score
                    })
        
        # Sort by score and return top results
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        return results[:max_results]


# Global knowledge base instance
kb = LocalKnowledgeBase()


# ===== SEARCH TOOLS =====

@tool(parse_docstring=True)
def local_search(
    query: str,
    max_results: int = 3,
) -> str:
    """Search local knowledge base for information.
    
    Use this tool to search for information on various topics from the local
    knowledge base. This is an offline-first search that doesn't require internet.

    Args:
        query: A search query to execute
        max_results: Maximum number of results to return

    Returns:
        Formatted string of search results with summaries
    """
    # Execute search in local knowledge base
    search_results = kb.search(query, max_results=max_results)
    
    if not search_results:
        return "No results found in knowledge base. Please try different search terms."
    
    # Format output for consumption
    formatted_output = "Search results:\n\n"
    
    for i, result in enumerate(search_results, 1):
        formatted_output += f"\n--- SOURCE {i}: {result['title']} ---\n"
        formatted_output += f"URL: {result['url']}\n\n"
        formatted_output += f"CONTENT:\n{result['content']}\n\n"
        formatted_output += "-" * 80 + "\n"
    
    return formatted_output


@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    return f"Reflection recorded: {reflection}"