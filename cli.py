#!/usr/bin/env python3
"""Command Line Interface for Research System.

Usage:
    python cli.py research "Your research question"
    python cli.py search "Your search query"
    python cli.py load markdown /path/to/files
    python cli.py export report.md
    python cli.py config show
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from knowledge_base import kb
from document_loaders import (
    DocumentImporter, load_markdown_directory, 
    load_text_directory, load_json_file
)
from advanced_research_agent import StreamingResearcher
from config import (
    config, get_fast_config, get_quality_config, 
    get_balanced_config, get_minimal_config
)


class ResearchCLI:
    """Command-line interface for research system."""
    
    def __init__(self):
        self.researcher = StreamingResearcher()
        self.config = config
    
    def cmd_research(self, args):
        """Run research on a topic."""
        if not args.query:
            print("Error: Query required")
            return 1
        
        print(f"\n{'='*60}")
        print(f"Research: {args.query}")
        print(f"{'='*60}\n")
        
        try:
            report = self.researcher.research(args.query)
            
            # Export in requested format
            if args.output:
                content = self.researcher.export_report(report, args.format)
                with open(args.output, 'w') as f:
                    f.write(content)
                print(f"✓ Report saved to {args.output}")
            else:
                content = self.researcher.export_report(report, args.format)
                print(content)
            
            return 0
        
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def cmd_search(self, args):
        """Search the knowledge base."""
        if not args.query:
            print("Error: Query required")
            return 1
        
        print(f"\nSearching: {args.query}\n")
        
        results = kb.search(
            args.query,
            max_results=args.limit,
            search_type=args.type
        )
        
        if not results:
            print("No results found.")
            return 0
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Score: {result['score']:.2f}")
            print(f"   Content: {result['content'][:200]}...")
        
        return 0
    
    def cmd_load(self, args):
        """Load documents from various sources."""
        if not args.source or not args.path:
            print("Error: Source and path required")
            return 1
        
        print(f"\nLoading {args.source} documents from {args.path}...\n")
        
        try:
            if args.source == "markdown":
                count = load_markdown_directory(args.path)
            elif args.source == "text":
                count = load_text_directory(args.path)
            elif args.source == "json":
                count = load_json_file(args.path)
            else:
                print(f"Error: Unknown source type: {args.source}")
                return 1
            
            print(f"✓ Loaded {count} documents")
            return 0
        
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def cmd_list(self, args):
        """List loaded documents."""
        documents = kb.list_documents()
        
        if not documents:
            print("No documents loaded.")
            return 0
        
        print(f"\n{len(documents)} documents in knowledge base:\n")
        
        for doc in documents:
            print(f"• {doc['title']}")
            print(f"  ID: {doc['id']}")
            print(f"  Size: {doc['size']} bytes")
            print()
        
        return 0
    
    def cmd_config(self, args):
        """Manage configuration."""
        if args.action == "show":
            print("\nCurrent Configuration:")
            print(self.config)
            return 0
        
        elif args.action == "set":
            if not args.key or args.value is None:
                print("Error: Key and value required")
                return 1
            
            # Parse the value
            try:
                if args.value.lower() in ('true', 'false'):
                    value = args.value.lower() == 'true'
                elif args.value.isdigit():
                    value = int(args.value)
                else:
                    try:
                        value = float(args.value)
                    except:
                        value = args.value
            except:
                value = args.value
            
            # Set value in config
            parts = args.key.split('.')
            obj = self.config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
            
            print(f"✓ Set {args.key} = {value}")
            return 0
        
        elif args.action == "save":
            if not args.file:
                print("Error: File path required")
                return 1
            
            self.config.save_to_file(args.file)
            print(f"✓ Configuration saved to {args.file}")
            return 0
        
        elif args.action == "load":
            if not args.file:
                print("Error: File path required")
                return 1
            
            from config import Config
            self.config = Config.from_file(args.file)
            print(f"✓ Configuration loaded from {args.file}")
            return 0
        
        elif args.action == "preset":
            if not args.preset:
                print("Error: Preset name required (fast, quality, balanced, minimal)")
                return 1
            
            if args.preset == "fast":
                self.config = get_fast_config()
            elif args.preset == "quality":
                self.config = get_quality_config()
            elif args.preset == "balanced":
                self.config = get_balanced_config()
            elif args.preset == "minimal":
                self.config = get_minimal_config()
            else:
                print(f"Error: Unknown preset: {args.preset}")
                return 1
            
            print(f"✓ Applied {args.preset} preset")
            return 0
        
        else:
            print(f"Error: Unknown action: {args.action}")
            return 1
    
    def cmd_export(self, args):
        """Export knowledge base."""
        if not args.file:
            print("Error: Output file required")
            return 1
        
        print(f"\nExporting to {args.file}...\n")
        
        try:
            kb.save_to_json(args.file)
            print(f"✓ Exported {len(kb.documents)} documents to {args.file}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def cmd_import(self, args):
        """Import knowledge base."""
        if not args.file:
            print("Error: Input file required")
            return 1
        
        print(f"\nImporting from {args.file}...\n")
        
        try:
            kb.load_from_json(args.file)
            print(f"✓ Imported {len(kb.documents)} documents from {args.file}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    def cmd_batch(self, args):
        """Batch import from directory."""
        if not args.directory:
            print("Error: Directory required")
            return 1
        
        print(f"\nBatch importing from {args.directory}...\n")
        
        try:
            importer = DocumentImporter()
            counts = importer.import_from_directory(args.directory)
            
            print(f"✓ Import complete:")
            print(f"  Markdown: {counts['markdown']}")
            print(f"  Text: {counts['text']}")
            print(f"  PDF: {counts['pdf']}")
            print(f"  Failed: {counts['failed']}")
            
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Research System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run research
  python cli.py research "What is machine learning?"
  
  # Search knowledge base
  python cli.py search "neural networks" --type hybrid
  
  # Load documents
  python cli.py load markdown /path/to/files
  python cli.py load json documents.json
  
  # Manage configuration
  python cli.py config show
  python cli.py config preset fast
  python cli.py config set ollama.temperature 0.5
  
  # Export/Import knowledge base
  python cli.py export kb.json
  python cli.py import kb.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Research command
    research_parser = subparsers.add_parser('research', help='Run research on a topic')
    research_parser.add_argument('query', help='Research query')
    research_parser.add_argument('-o', '--output', help='Output file path')
    research_parser.add_argument('-f', '--format', default='markdown', 
                               choices=['markdown', 'json'], help='Output format')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search knowledge base')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-t', '--type', default='hybrid',
                             choices=['keyword', 'vector', 'hybrid'], help='Search type')
    search_parser.add_argument('-l', '--limit', type=int, default=3, help='Max results')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load documents')
    load_parser.add_argument('source', choices=['markdown', 'text', 'json'], help='Document source')
    load_parser.add_argument('path', help='Path to files or JSON file')
    
    # List command
    subparsers.add_parser('list', help='List loaded documents')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('action', 
                             choices=['show', 'set', 'save', 'load', 'preset'],
                             help='Configuration action')
    config_parser.add_argument('-k', '--key', help='Config key (for set)')
    config_parser.add_argument('-v', '--value', help='Config value (for set)')
    config_parser.add_argument('-f', '--file', help='Config file path')
    config_parser.add_argument('-p', '--preset', help='Preset name (for preset)')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export knowledge base')
    export_parser.add_argument('file', help='Output file path')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import knowledge base')
    import_parser.add_argument('file', help='Input file path')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch import from directory')
    batch_parser.add_argument('directory', help='Directory to import from')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    cli = ResearchCLI()
    
    # Dispatch to appropriate command
    if args.command == 'research':
        return cli.cmd_research(args)
    elif args.command == 'search':
        return cli.cmd_search(args)
    elif args.command == 'load':
        return cli.cmd_load(args)
    elif args.command == 'list':
        return cli.cmd_list(args)
    elif args.command == 'config':
        return cli.cmd_config(args)
    elif args.command == 'export':
        return cli.cmd_export(args)
    elif args.command == 'import':
        return cli.cmd_import(args)
    elif args.command == 'batch':
        return cli.cmd_batch(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())