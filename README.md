# Offline Deep Research Agent using Ollama Mistral and LangChain

![Python](https://img.shields.io/badge/Python-blue)
![LangChain](https://img.shields.io/badge/LangChain-orange)
![Ollama](https://img.shields.io/badge/Ollama-yellow)
![Mistral](https://img.shields.io/badge/Mistral-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A complete rewrite of the original deep research system to use **Ollama with mistral** instead of external APIs (Claude, OpenAI, Tavily).

## 📋 Architecture

```
┌─────────────────────────────────────────────────────┐
│          Research Request                           │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────────┐
        │  Single Agent or Supervisor  │
        │     (LangGraph Graph)        │
        └────────────────┬─────────────┘
                         │
        ┌────────────────▼───────────────┐
        │    LLM (ChatOllama - mistral)     │
        │   (Local, no internet needed)   │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼──────────────────┐
        │  Tools & Search                   │
        ├────────────────────────────────────┤
        │ • local_search (Knowledge Base)   │
        │ • think_tool (Reflection)         │
        └────────────────────────────────────┘
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Ollama installed and running
- mistral model pulled in Ollama

### 1. Install Ollama

**On Mac/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**On Windows:**
Download from https://ollama.ai/

### 2. Pull the mistral Model

```bash
ollama pull mistral
```

This downloads the 3.8B parameter mistral model (~2.3GB).

### 3. Start Ollama Server

```bash
ollama serve
```

Keep this running in a terminal. It starts the Ollama API server on `http://localhost:11434`

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Research System

```bash
python main.py
```

## 📁 File Structure

```
ollama_research/
├── requirements.txt              # Python dependencies
├── state_definitions.py          # TypedDict definitions for state
├── utils.py                      # Tools & knowledge base
├── prompts.py                    # System prompts
├── research_agent.py             # Single researcher agent
├── multi_agent_supervisor.py     # Multi-agent coordinator
└── main.py                       # Entry point & examples
```

## 🔧 Configuration

### Ollama Settings

Edit the model initialization in `research_agent.py` and `multi_agent_supervisor.py`:

```python
model = ChatOllama(
    model="mistral",                              # Model name
    base_url="http://localhost:11434",        # Ollama server URL
    temperature=0.3,                           # Lower = more focused
    # num_ctx=4096,                           # Context window size
    # num_predict=512,                        # Max tokens to generate
)
```

### Temperature Settings

- **0.1-0.3**: For focused, deterministic research and synthesis
- **0.5-0.7**: For creative exploration
- **0.9+**: For highly creative outputs

Recommended: 0.2-0.3 for research tasks.

### Local Knowledge Base

The `LocalKnowledgeBase` in `utils.py` contains example documents. To add more:

1. **Add to `_initialize_default_kb()`** for static content
2. **Load from files** for larger knowledge bases
3. **Integrate with vector databases** (Chroma, Pinecone) for semantic search

Example of expanding the knowledge base:

```python
def _initialize_default_kb(self):
    self.documents = {
        "your_topic": [
            {
                "title": "Document Title",
                "url": "local://kb/doc-id.md",
                "content": "Full document content here..."
            }
        ]
    }
```

## 💡 Usage Examples

### Basic Single-Agent Research

```python
from langchain_core.messages import HumanMessage
from research_agent import researcher_agent

initial_state = {
    "researcher_messages": [
        HumanMessage(content="What are neural networks?")
    ]
}

result = researcher_agent.invoke(initial_state)
print(result["compressed_research"])
```

### Multi-Agent Supervisor Research

```python
import asyncio
from multi_agent_supervisor import supervisor_agent

async def main():
    initial_state = {
        "supervisor_messages": [],
        "research_brief": "Research AI and machine learning",
        "research_iterations": 0
    }
    
    result = await supervisor_agent.ainvoke(initial_state)
    print(result["notes"])

asyncio.run(main())
```

## 🔄 Research Workflow

### Single Agent Flow

```
1. LLM reads research question
2. Decides: Need more info? → tool_node : compress_research
3. tool_node: Execute search/think tools
4. Return to step 2 (loop until confident)
5. compress_research: Synthesize findings
6. Return compressed summary
```

### Supervisor Flow

```
1. Supervisor reads research brief
2. Decomposes into sub-topics
3. Launches researcher agents in parallel
4. Collects results from each agent
5. Decides: Need more research? Continue : End
6. Return aggregated notes
```

## 🛠️ Extending the System

### Add Custom Tools

```python
from langchain_core.tools import tool

@tool(parse_docstring=True)
def custom_tool(parameter: str) -> str:
    """Tool description for LLM.
    
    Args:
        parameter: Parameter description
        
    Returns:
        Result description
    """
    return "Tool result"

# Add to tools list in research_agent.py
tools = [local_search, think_tool, custom_tool]
```

### Improve Knowledge Base

Replace `LocalKnowledgeBase` with:

- **File System**: Load markdown documents
- **Vector DB**: Semantic similarity search with embeddings
- **SQL DB**: Structured data with relationships
- **API Integration**: Query live data sources (with internet)

### Use Different Models

Available Ollama models:

```bash
ollama pull llama2        # 7B-70B
ollama pull mistral       # 7B
ollama pull neural-chat   # 7B
ollama pull orca2         # 7B-13B
ollama pull dolphin-mixtral  # 8x7B MoE
```

Change in code:

```python
model = ChatOllama(
    model="mistral",  # or llama2, orca2, etc.
    base_url="http://localhost:11434",
)
```

## 📊 Performance Considerations

### Model Size vs Speed

| Model | Size | Speed | Quality | VRAM |
|-------|------|-------|---------|------|
| Phi3  | 3.8B | Fast  | Good    | 4GB  |
| Mistral | 7B | Medium | Better  | 8GB  |
| Llama2 | 7B-70B | Varies | Varies | 8-40GB |

### Optimization Tips

1. **Lower temperature** for faster, more focused responses
2. **Reduce num_ctx** (context window) for speed
3. **Use smaller models** for latency-sensitive applications
4. **Batch requests** when possible
5. **Add semantic search** to knowledge base (vector embeddings)

## 🚨 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull mistral
```

### Out of Memory

- Reduce `num_ctx` in ChatOllama config
- Use a smaller model (phi3 < mistral < llama2-7b)
- Close other applications
- Check system RAM: `free -h` (Linux) or Task Manager (Windows)

### Slow Responses

- Reduce context window size
- Use quantized models (already handled by Ollama)
- Reduce temperature for faster token generation
- Run on a GPU (if available)

## 📚 Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [mistral Model Card](https://huggingface.co/microsoft/phi-3)

## 🔒 Privacy & Security

✅ **All processing is local** - No data sent to external APIs
✅ **No API keys required** - No credential management needed
✅ **Offline capability** - Works without internet
✅ **Complete control** - Run on your own hardware

## 📝 License

This code is provided as-is for research and development purposes.

## 🤝 Contributing

Feel free to extend this system with:
- Better knowledge base implementations
- Integration with local vector databases
- Support for additional Ollama models
- Web UI for research interface
- Export to various formats (PDF, Markdown, etc.)

---

**Happy researching! 🚀**
---
## 👨‍💻 Developer
**Siddardha Shayini** 
