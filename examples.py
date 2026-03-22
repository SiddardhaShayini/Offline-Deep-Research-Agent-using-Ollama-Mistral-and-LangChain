"""Extended Examples and Use Cases.

Demonstrates advanced usage of the research system.
"""

import asyncio
import json
from pathlib import Path
from langchain_core.messages import HumanMessage

from knowledge_base import kb
from advanced_research_agent import StreamingResearcher
from document_loaders import DocumentImporter, load_json_file
from config import get_fast_config, get_quality_config


# ===== EXAMPLE 1: BASIC RESEARCH =====

def example_basic_research():
    """Simple research on a topic."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Research")
    print("="*60 + "\n")
    
    researcher = StreamingResearcher()
    
    query = "What are the key principles of machine learning?"
    report = researcher.research(query)
    
    # Display report
    md_report = researcher.export_report(report, "markdown")
    print(md_report)
    
    # Save to file
    with open("research_report.md", "w") as f:
        f.write(md_report)
    print("\n✓ Report saved to research_report.md")


# ===== EXAMPLE 2: BATCH RESEARCH =====

def example_batch_research():
    """Research multiple topics in sequence."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Research")
    print("="*60 + "\n")
    
    researcher = StreamingResearcher()
    
    topics = [
        "What is deep learning?",
        "Explain neural networks.",
        "What are applications of AI?"
    ]
    
    reports = []
    for i, topic in enumerate(topics, 1):
        print(f"\nResearch {i}/{len(topics)}: {topic}")
        report = researcher.research(topic)
        reports.append(report)
    
    # Combine reports
    combined = {
        "total_queries": len(topics),
        "reports": [
            {
                "query": r.query,
                "summary": r.summary,
                "timestamp": r.timestamp
            }
            for r in reports
        ]
    }
    
    with open("batch_research.json", "w") as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n✓ {len(reports)} research reports saved to batch_research.json")


# ===== EXAMPLE 3: KNOWLEDGE BASE MANAGEMENT =====

def example_kb_management():
    """Manage and extend knowledge base."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Knowledge Base Management")
    print("="*60 + "\n")
    
    # List current documents
    print("Current documents in knowledge base:")
    docs = kb.list_documents()
    for doc in docs:
        print(f"  - {doc['title']} ({doc['size']} bytes)")
    
    # Save knowledge base to file
    kb.save_to_json("knowledge_base_backup.json")
    print("\n✓ Knowledge base saved to knowledge_base_backup.json")
    
    # Search examples
    print("\nSearching knowledge base:")
    
    search_queries = [
        ("machine learning", "hybrid"),
        ("deep learning", "vector"),
        ("python", "keyword"),
    ]
    
    for query, search_type in search_queries:
        results = kb.search(query, max_results=2, search_type=search_type)
        print(f"\n  Query: '{query}' ({search_type})")
        for result in results:
            print(f"    - {result['title']} (score: {result['score']:.2f})")


# ===== EXAMPLE 4: CUSTOM CONFIGURATION =====

def example_custom_config():
    """Use different configuration presets."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Configuration")
    print("="*60 + "\n")
    
    researcher = StreamingResearcher()
    
    # Test with fast config
    print("1. Fast Configuration (speed optimized):")
    fast_config = get_fast_config()
    print(f"   Temperature: {fast_config.ollama.temperature}")
    print(f"   Max Searches: {fast_config.research.max_searches}")
    print(f"   Search Type: {fast_config.knowledge_base.search_type}")
    
    # Test with quality config
    print("\n2. Quality Configuration (quality optimized):")
    quality_config = get_quality_config()
    print(f"   Temperature: {quality_config.ollama.temperature}")
    print(f"   Max Searches: {quality_config.research.max_searches}")
    print(f"   Search Type: {quality_config.knowledge_base.search_type}")
    
    print("\n✓ Configuration examples displayed")


# ===== EXAMPLE 5: DOCUMENT LOADING =====

def example_document_loading():
    """Load and organize documents."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Document Loading")
    print("="*60 + "\n")
    
    # Create example markdown files
    example_dir = Path("example_docs")
    example_dir.mkdir(exist_ok=True)
    
    # Create sample markdown file
    sample_md = example_dir / "sample.md"
    sample_md.write_text("""# Sample Document

## Introduction
This is a sample document for demonstration.

## Key Points
- Point 1
- Point 2
- Point 3

## Conclusion
Sample documents can be loaded into the knowledge base.
""")
    
    print(f"Created example documents in {example_dir}")
    
    # Load from directory
    importer = DocumentImporter()
    counts = importer.import_from_directory(str(example_dir))
    
    print(f"\n✓ Imported {counts['markdown']} markdown files")
    
    # List all documents
    all_docs = kb.list_documents()
    print(f"\nTotal documents in KB: {len(all_docs)}")


# ===== EXAMPLE 6: ASYNC RESEARCH =====

async def example_async_research():
    """Concurrent research execution."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Async Research")
    print("="*60 + "\n")
    
    researcher = StreamingResearcher()
    
    queries = [
        "What is supervised learning?",
        "What is unsupervised learning?",
    ]
    
    print(f"Running {len(queries)} research tasks concurrently...")
    
    # Run research concurrently
    tasks = [researcher.research_async(q) for q in queries]
    results = await asyncio.gather(*tasks)
    
    print(f"\n✓ Completed {len(results)} research tasks")
    
    for report in results:
        print(f"\nQuery: {report.query}")
        print(f"Summary: {report.summary[:100]}...")


# ===== EXAMPLE 7: EXPORT AND SHARING =====

def example_export_sharing():
    """Export research in multiple formats."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Export and Sharing")
    print("="*60 + "\n")
    
    researcher = StreamingResearcher()
    
    query = "Compare supervised and unsupervised learning"
    report = researcher.research(query)
    
    # Export as markdown
    md_content = researcher.export_report(report, "markdown")
    Path("report.md").write_text(md_content)
    print("✓ Exported as Markdown: report.md")
    
    # Export as JSON
    json_content = researcher.export_report(report, "json")
    Path("report.json").write_text(json_content)
    print("✓ Exported as JSON: report.json")
    
    # Create HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report.query}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 10px; }}
    </style>
</head>
<body>
    <h1>{report.query}</h1>
    <div class="summary">{report.summary}</div>
</body>
</html>"""
    
    Path("report.html").write_text(html_content)
    print("✓ Exported as HTML: report.html")


# ===== EXAMPLE 8: RESEARCH CHAINING =====

def example_research_chaining():
    """Chain multiple research queries for deeper investigation."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Research Chaining")
    print("="*60 + "\n")
    
    researcher = StreamingResearcher()
    
    # Initial research
    print("Step 1: Initial Research")
    initial_query = "What is artificial intelligence?"
    report1 = researcher.research(initial_query)
    print(f"✓ Completed: {initial_query}")
    
    # Follow-up research
    print("\nStep 2: Follow-up Research")
    followup_query = "What are the applications of artificial intelligence?"
    report2 = researcher.research(followup_query)
    print(f"✓ Completed: {followup_query}")
    
    # Synthesis
    print("\nStep 3: Synthesis")
    synthesis_query = "How do AI applications in healthcare work?"
    report3 = researcher.research(synthesis_query)
    print(f"✓ Completed: {synthesis_query}")
    
    # Combine findings
    combined_findings = f"""
# AI Research Chain

## 1. What is AI?
{report1.summary}

## 2. AI Applications
{report2.summary}

## 3. Healthcare Applications
{report3.summary}
"""
    
    Path("chained_research.md").write_text(combined_findings)
    print("\n✓ Combined research saved to chained_research.md")


# ===== EXAMPLE 9: KNOWLEDGE BASE BACKUP/RESTORE =====

def example_kb_backup_restore():
    """Backup and restore knowledge base."""
    print("\n" + "="*60)
    print("EXAMPLE 9: KB Backup and Restore")
    print("="*60 + "\n")
    
    # Backup current KB
    print("Backing up knowledge base...")
    kb.save_to_json("kb_backup_full.json")
    print(f"✓ Backed up {len(kb.documents)} documents")
    
    # Show backup info
    backup_file = Path("kb_backup_full.json")
    backup_size = backup_file.stat().st_size / 1024  # KB
    print(f"✓ Backup size: {backup_size:.1f} KB")
    
    # You can restore later with:
    # kb.load_from_json("kb_backup_full.json")
    print("✓ To restore: kb.load_from_json('kb_backup_full.json')")


# ===== EXAMPLE 10: METRICS AND ANALYTICS =====

def example_metrics_analytics():
    """Analyze research metrics and knowledge base stats."""
    print("\n" + "="*60)
    print("EXAMPLE 10: Metrics and Analytics")
    print("="*60 + "\n")
    
    # KB Statistics
    print("Knowledge Base Statistics:")
    docs = kb.list_documents()
    
    total_size = sum(d['size'] for d in docs)
    avg_size = total_size / len(docs) if docs else 0
    
    print(f"  Total Documents: {len(docs)}")
    print(f"  Total Size: {total_size / 1024:.1f} KB")
    print(f"  Average Size: {avg_size / 1024:.1f} KB")
    
    # Search Statistics
    print("\nSearch Performance:")
    test_queries = ["AI", "machine", "learning", "neural"]
    
    for query in test_queries:
        keyword_results = kb.keyword_search(query, max_results=5)
        vector_results = kb.vector_search(query, max_results=5) if kb.use_vectors else []
        hybrid_results = kb.hybrid_search(query, max_results=5)
        
        print(f"\n  Query: '{query}'")
        print(f"    Keyword: {len(keyword_results)} results")
        print(f"    Vector: {len(vector_results)} results")
        print(f"    Hybrid: {len(hybrid_results)} results")


# ===== RUN ALL EXAMPLES =====

def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("RESEARCH SYSTEM EXTENDED EXAMPLES")
    print("="*60)
    
    examples = [
        ("Basic Research", example_basic_research),
        ("Batch Research", example_batch_research),
        ("KB Management", example_kb_management),
        ("Custom Config", example_custom_config),
        ("Document Loading", example_document_loading),
        ("Export Sharing", example_export_sharing),
        ("Research Chaining", example_research_chaining),
        ("KB Backup/Restore", example_kb_backup_restore),
        ("Metrics Analytics", example_metrics_analytics),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    # Run example 1 by default
    print("\nRunning examples...\n")
    
    try:
        example_basic_research()
        example_kb_management()
        example_custom_config()
        example_document_loading()
        example_export_sharing()
        example_kb_backup_restore()
        example_metrics_analytics()
        
        print("\n" + "="*60)
        print("✓ All examples completed!")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Run async example
    print("\nRunning async example...")
    try:
        asyncio.run(example_async_research())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()