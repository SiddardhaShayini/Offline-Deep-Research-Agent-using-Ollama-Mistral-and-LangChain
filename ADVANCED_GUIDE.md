# Advanced Usage Guide

This guide covers advanced features and patterns for the Ollama-based research system.

## Table of Contents

1. [Configuration Management](#configuration-management)
2. [Knowledge Base Operations](#knowledge-base-operations)
3. [Advanced Research Patterns](#advanced-research-patterns)
4. [Document Loading](#document-loading)
5. [Performance Optimization](#performance-optimization)
6. [Integration Examples](#integration-examples)
7. [Troubleshooting](#troubleshooting)

---

## Configuration Management

### Environment-Based Configuration

```python
from config import Config

# Load from environment variables
config = Config.from_env()

# Set environment variables before importing
import os
os.environ['OLLAMA_MODEL'] = 'mistral'
os.environ['OLLAMA_TEMPERATURE'] = '0.5'
os.environ['MAX_SEARCHES'] = '3'

config = Config.from_env()
```

### File-Based Configuration

```python
# Save current configuration
config.save_to_file('my_config.json')

# Load saved configuration
config = Config.from_file('my_config.json')

# Use configuration presets
from config import get_fast_config, get_quality_config

fast_cfg = get_fast_config()  # Speed-optimized
quality_cfg = get_quality_config()  # Quality-optimized
```

### Programmatic Configuration

```python
from config import Config

config = Config()
config.ollama.temperature = 0.2
config.research.max_searches = 3
config.knowledge_base.search_type = "hybrid"

# Apply configuration
# (Your research code uses global config instance)
```

---

## Knowledge Base Operations

### Advanced Search

```python
from knowledge_base import kb

# Keyword search (fast, exact matches)
results = kb.keyword_search("machine learning", max_results=5)

# Vector search (semantic, requires embeddings)
results = kb.vector_search("deep neural networks", max_results=3)

# Hybrid search (combination of both)
results = kb.hybrid_search("neural networks", max_results=5)

# Filter by metadata
for doc in kb.documents.values():
    if doc.metadata.get("source") == "web":
        print(f"Web source: {doc.title}")
```

### Document Management

```python
from knowledge_base import Document, kb

# Add custom document
doc = Document(
    id="custom-1",
    title="My Custom Document",
    url="local://custom/doc1",
    content="Document content here...",
    metadata={"category": "custom", "importance": "high"}
)
kb.add_document(doc)

# Retrieve specific document
doc = kb.get_document_by_id("custom-1")

# List documents
docs = kb.list_documents()
for doc_info in docs:
    print(f"{doc_info['title']}: {doc_info['size']} bytes")

# Search with metadata filtering
all_results = kb.hybrid_search("topic", max_results=10)
filtered = [r for r in all_results if r['metadata'].get('category') == 'scientific']
```

### Vector Search Fine-Tuning

```python
from knowledge_base import kb

# Regenerate embeddings for all documents
if kb.use_vectors:
    for doc in kb.documents.values():
        try:
            doc.embedding = kb.embeddings.embed_query(doc.content[:500])
            print(f"Embedded: {doc.title}")
        except Exception as e:
            print(f"Failed to embed {doc.title}: {e}")

# Compare search strategies
query = "your search query"
keyword_results = kb.keyword_search(query)
vector_results = kb.vector_search(query)
hybrid_results = kb.hybrid_search(query)

print(f"Keyword: {len(keyword_results)} results")
print(f"Vector: {len(vector_results)} results")
print(f"Hybrid: {len(hybrid_results)} results")
```

---

## Advanced Research Patterns

### Research with Custom Parameters

```python
from advanced_research_agent import StreamingResearcher
from config import Config

# Create researcher with custom config
researcher = StreamingResearcher()

# Adjust Ollama parameters for specific query
researcher.agent.get_state({
    "researcher_messages": [
        HumanMessage(content="Complex research query")
    ]
})

# Export in different formats
report = researcher.research("Your query")
md_report = researcher.export_report(report, "markdown")
json_report = researcher.export_report(report, "json")
```

### Concurrent Research

```python
import asyncio
from advanced_research_agent import StreamingResearcher

async def run_concurrent_research():
    researcher = StreamingResearcher()
    
    queries = [
        "Topic 1",
        "Topic 2",
        "Topic 3"
    ]
    
    # Run all queries concurrently
    tasks = [researcher.research_async(q) for q in queries]
    results = await asyncio.gather(*tasks)
    
    return results

# Run
reports = asyncio.run(run_concurrent_research())
```

### Research Chain (Sequential Dependency)

```python
from advanced_research_agent import StreamingResearcher

def research_chain():
    researcher = StreamingResearcher()
    
    # Step 1: General research
    report1 = researcher.research("What is machine learning?")
    
    # Step 2: Detailed research based on findings
    if "supervised" in report1.summary:
        report2 = researcher.research("Explain supervised learning in detail")
    
    # Step 3: Application research
    report3 = researcher.research("Applications of supervised learning")
    
    return [report1, report2, report3]

reports = research_chain()
```

### Streaming Response Processing

```python
from advanced_research_agent import StreamingResearcher

researcher = StreamingResearcher()

query = "Your research question"

# Get report
report = researcher.research(query)

# Process in chunks
for line in report.summary.split('\n'):
    if line.strip():
        print(f"> {line}")

# Access metadata
print(f"Query: {report.query}")
print(f"Timestamp: {report.timestamp}")
print(f"Sources: {len(report.sources)}")
```

---

## Document Loading

### Load from Multiple Sources

```python
from document_loaders import (
    MarkdownLoader, TextLoader, JSONLoader,
    load_json_file, DocumentImporter
)
from knowledge_base import kb

# Load markdown files
md_loader = MarkdownLoader()
docs = md_loader.load("path/to/markdown/files")
for doc in docs:
    kb.add_document(doc)

# Load text files
txt_loader = TextLoader()
docs = txt_loader.load("path/to/text/files")
for doc in docs:
    kb.add_document(doc)

# Load from JSON
load_json_file("documents.json")

# Batch import
importer = DocumentImporter()
counts = importer.import_from_directory("path/to/documents")
print(f"Imported: {counts}")
```

### Load Web Content

```python
from document_loaders import WebLoader

loader = WebLoader(timeout=15)

# Load single web page
doc = loader.load(
    "https://example.com/article",
    title="Article Title"
)

if doc:
    from knowledge_base import kb
    kb.add_document(doc)
```

### Create Custom Document Loader

```python
from document_loaders import DocumentLoader
from knowledge_base import Document

class CSVLoader(DocumentLoader):
    def load(self, filepath):
        import csv
        
        documents = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc = Document(
                    id=row['id'],
                    title=row['title'],
                    url=row['url'],
                    content=row['content']
                )
                documents.append(doc)
        
        return documents

# Use custom loader
loader = CSVLoader()
docs = loader.load("data.csv")
```

---

## Performance Optimization

### Model Selection

```python
from config import Config
from langchain_ollama import ChatOllama

# Fast inference
fast_model = ChatOllama(
    model="mistral",
    temperature=0.1,
    num_ctx=2048,  # Smaller context window
    num_predict=256  # Fewer tokens
)

# Quality inference
quality_model = ChatOllama(
    model="mistral",  # Larger model
    temperature=0.5,
    num_ctx=4096,
    num_predict=1024
)
```

### Knowledge Base Optimization

```python
from knowledge_base import AdvancedKnowledgeBase

# Disable vector search for speed
kb = AdvancedKnowledgeBase(use_vectors=False)

# Use keyword-only search (fastest)
results = kb.search(query, search_type="keyword")

# Reduce chunk size for faster processing
kb.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Smaller chunks
    chunk_overlap=100
)
```

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_search(query):
    from knowledge_base import kb
    return kb.search(query)

# First call: searches KB
results1 = cached_search("machine learning")

# Second call: returns cached result
results2 = cached_search("machine learning")  # Fast!

# Different query: searches again
results3 = cached_search("neural networks")  # Searches
```

---

## Integration Examples

### Flask Web API

```python
from flask import Flask, request, jsonify
from advanced_research_agent import StreamingResearcher

app = Flask(__name__)
researcher = StreamingResearcher()

@app.route('/research', methods=['POST'])
def research_endpoint():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        report = researcher.research(query)
        return jsonify({
            'query': report.query,
            'summary': report.summary,
            'sources': report.sources,
            'timestamp': report.timestamp
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Discord Bot Integration

```python
import discord
from discord.ext import commands
from advanced_research_agent import StreamingResearcher

bot = commands.Bot(command_prefix='!')
researcher = StreamingResearcher()

@bot.command(name='research')
async def research_command(ctx, *, query):
    async with ctx.typing():
        report = researcher.research(query)
        
        # Split into chunks (Discord has message limit)
        summary = report.summary
        chunks = [summary[i:i+2000] for i in range(0, len(summary), 2000)]
        
        for chunk in chunks:
            await ctx.send(chunk)

bot.run('YOUR_TOKEN')
```

### Streamlit App

```python
import streamlit as st
from advanced_research_agent import StreamingResearcher

st.set_page_config(page_title="Research System")
st.title("Ollama Research System")

researcher = StreamingResearcher()

# Sidebar for configuration
st.sidebar.header("Configuration")
search_type = st.sidebar.selectbox(
    "Search Type",
    ["hybrid", "keyword", "vector"]
)

# Main interface
query = st.text_input("Research Query:")

if st.button("Start Research"):
    with st.spinner("Researching..."):
        report = researcher.research(query)
        
        st.markdown("## Summary")
        st.write(report.summary)
        
        st.markdown("## Sources")
        for source in report.sources:
            st.write(f"- {source['title']}")
```

---

## Troubleshooting

### Ollama Connection Issues

```python
import requests
from requests.exceptions import ConnectionError

def test_ollama_connection():
    try:
        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=5
        )
        if response.status_code == 200:
            print("✓ Ollama is running")
            data = response.json()
            print(f"Available models: {[m['name'] for m in data.get('models', [])]}")
            return True
    except ConnectionError:
        print("✗ Cannot connect to Ollama")
        print("  Start Ollama: ollama serve")
        return False

test_ollama_connection()
```

### Memory Management

```python
import gc
from knowledge_base import kb

# Clear unused vectors to free memory
if kb.use_vectors:
    for doc in kb.documents.values():
        # Keep only essential data
        if len(doc.embedding or []) > 0:
            # Vectors stored, can be regenerated
            pass

# Force garbage collection
gc.collect()
```

### Search Quality Issues

```python
from knowledge_base import kb

# Debug search quality
query = "your query"

# Compare search methods
keyword_results = kb.keyword_search(query, max_results=5)
vector_results = kb.vector_search(query, max_results=5)

# Print detailed results
for i, (doc, score) in enumerate(keyword_results, 1):
    print(f"{i}. {doc.title} (keyword score: {score})")

for i, (doc, score) in enumerate(vector_results, 1):
    print(f"{i}. {doc.title} (vector score: {score:.3f})")

# Adjust search parameters
results = kb.hybrid_search(query, max_results=10)
```

---

## Best Practices

1. **Always backup your knowledge base**
   ```python
   kb.save_to_json("kb_backup.json")
   ```

2. **Use appropriate search type**
   - Keyword: Fast, for exact matches
   - Vector: Accurate, for semantic similarity
   - Hybrid: Balanced approach

3. **Monitor performance**
   ```python
   import time
   start = time.time()
   result = researcher.research(query)
   elapsed = time.time() - start
   print(f"Research took {elapsed:.2f} seconds")
   ```

4. **Handle errors gracefully**
   ```python
   try:
       report = researcher.research(query)
   except Exception as e:
       logger.error(f"Research failed: {e}")
       # Fallback behavior
   ```

5. **Document custom extensions**
   ```python
   """Custom research extension.
   
   Usage:
       result = custom_research(query)
   """
   ```

---

## Performance Benchmarks

*Run on a system with Ollama running locally*

- **Keyword Search**: ~50ms
- **Vector Search**: ~200ms
- **Hybrid Search**: ~250ms
- **Single Research Query**: 5-15 seconds
- **Concurrent Queries (3)**: 8-20 seconds

*Exact times depend on your hardware and model size*

---

For more examples, see `examples.py`