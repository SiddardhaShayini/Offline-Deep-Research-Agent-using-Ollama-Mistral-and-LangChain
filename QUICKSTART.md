# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Ollama
- **Mac/Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`
- **Windows**: Download from https://ollama.ai/

### Step 2: Pull mistral Model
```bash
ollama pull mistral
```

### Step 3: Start Ollama Server
```bash
ollama serve
```
Keep this terminal open. Server runs on `http://localhost:11434`

### Step 4: Install Dependencies
```bash
cd ollama_research
pip install -r requirements.txt
```

### Step 5: Run Research
```bash
python main.py
```

---

## Common Tasks

### Run Research on a Topic
```python
from langchain_core.messages import HumanMessage
from research_agent import researcher_agent

result = researcher_agent.invoke({
    "researcher_messages": [
        HumanMessage(content="Your question here")
    ]
})

print(result["compressed_research"])
```

### Use Supervisor for Complex Research
```python
import asyncio
from multi_agent_supervisor import supervisor_agent

async def main():
    result = await supervisor_agent.ainvoke({
        "supervisor_messages": [],
        "research_brief": "Research topic description",
        "research_iterations": 0
    })
    print(result["notes"])

asyncio.run(main())
```

### Add Documents to Knowledge Base
```python
from utils import kb

# Search existing docs
results = kb.search("machine learning", max_results=3)

# Add new documents (edit utils.py _initialize_default_kb)
```

### Change LLM Temperature
```python
from langchain_ollama import ChatOllama

model = ChatOllama(
    model="mistral",
    base_url="http://localhost:11434",
    temperature=0.5,  # 0.2 (focused) to 0.9 (creative)
)
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Ctrl+C | Stop research |
| Cmd+. | Stop Ollama server |

---

## Error Messages & Fixes

| Error | Fix |
|-------|-----|
| `Connection refused 11434` | Run `ollama serve` first |
| `Model mistral not found` | Run `ollama pull mistral` |
| `CUDA out of memory` | Reduce context window in code |
| `Slow responses` | Reduce temperature (0.2-0.3) |

---

## File Guide

| File | Purpose |
|------|---------|
| `main.py` | Entry point, examples |
| `research_agent.py` | Single agent logic |
| `multi_agent_supervisor.py` | Multi-agent coordinator |
| `utils.py` | Tools and knowledge base |
| `prompts.py` | System prompts |
| `state_definitions.py` | State types |

---

## Next Steps

1. **Expand Knowledge Base** - Add your own documents to `utils.py`
2. **Add Custom Tools** - Create new tools in `utils.py`
3. **Try Different Models** - Replace mistral with phi3, llama2, etc.
4. **Integrate Vector DB** - Use Chroma/Pinecone for semantic search
5. **Build Web UI** - Create Streamlit/Gradio interface

---

## Resources

- Full README: `README.md`
- Ollama Docs: https://github.com/ollama/ollama
- LangChain: https://python.langchain.com/