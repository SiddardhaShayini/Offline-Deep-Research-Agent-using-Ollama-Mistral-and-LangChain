"""Document Loaders for Knowledge Base.

Load documents from various sources:
- Markdown files
- Text files
- JSON files
- Web pages (requires internet)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SUPPORT = True
except ImportError:
    WEB_SUPPORT = False

from knowledge_base import Document, kb


class DocumentLoader(ABC):
    """Abstract base class for document loaders."""
    
    @abstractmethod
    def load(self, source: str) -> List[Document]:
        """Load documents from source."""
        pass


class MarkdownLoader(DocumentLoader):
    """Load documents from Markdown files."""
    
    def load(self, directory: str) -> List[Document]:
        """Load all markdown files from directory.
        
        Args:
            directory: Path to directory containing markdown files
            
        Returns:
            List of Document objects
        """
        documents = []
        path = Path(directory)
        
        if not path.exists():
            raise ValueError(f"Directory not found: {directory}")
        
        for md_file in path.glob("*.md"):
            doc = self._load_file(md_file)
            if doc:
                documents.append(doc)
        
        return documents
    
    def _load_file(self, filepath: Path) -> Optional[Document]:
        """Load a single markdown file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract title from first h1 or filename
            title = None
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            if not title:
                title = filepath.stem.replace('_', ' ').title()
            
            return Document(
                id=filepath.stem,
                title=title,
                url=f"local://files/{filepath.stem}",
                content=content,
                metadata={"file_path": str(filepath), "format": "markdown"}
            )
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None


class TextLoader(DocumentLoader):
    """Load documents from plain text files."""
    
    def load(self, directory: str) -> List[Document]:
        """Load all text files from directory."""
        documents = []
        path = Path(directory)
        
        if not path.exists():
            raise ValueError(f"Directory not found: {directory}")
        
        for txt_file in path.glob("*.txt"):
            doc = self._load_file(txt_file)
            if doc:
                documents.append(doc)
        
        return documents
    
    def _load_file(self, filepath: Path) -> Optional[Document]:
        """Load a single text file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Use first line as title or filename
            lines = content.split('\n')
            title = lines[0] if lines[0] else filepath.stem
            
            return Document(
                id=filepath.stem,
                title=title,
                url=f"local://files/{filepath.stem}",
                content=content,
                metadata={"file_path": str(filepath), "format": "text"}
            )
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None


class JSONLoader(DocumentLoader):
    """Load documents from JSON files."""
    
    def load(self, filepath: str) -> List[Document]:
        """Load documents from JSON file.
        
        Expected format:
        [
            {
                "id": "doc1",
                "title": "Title",
                "url": "url",
                "content": "content"
            }
        ]
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            for item in data:
                doc = Document(**item)
                documents.append(doc)
            
            return documents
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return []


class WebLoader(DocumentLoader):
    """Load documents from web pages."""
    
    def __init__(self, timeout: int = 10):
        if not WEB_SUPPORT:
            raise ImportError("Web loading requires requests and beautifulsoup4")
        self.timeout = timeout
    
    def load(self, url: str, title: Optional[str] = None) -> Optional[Document]:
        """Load a single web page.
        
        Args:
            url: URL to load
            title: Optional custom title
            
        Returns:
            Document object or None if failed
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            if not title:
                title_tag = soup.find('title')
                title = title_tag.get_text() if title_tag else url
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up excessive whitespace
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            
            doc_id = url.split('/')[-1] or 'webpage'
            
            return Document(
                id=doc_id,
                title=title,
                url=url,
                content=text,
                metadata={"source": "web", "status_code": response.status_code}
            )
        except Exception as e:
            print(f"Error loading {url}: {e}")
            return None


class PDFLoader(DocumentLoader):
    """Load documents from PDF files."""
    
    def __init__(self):
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
        except ImportError:
            raise ImportError("PDF loading requires PyPDF2")
    
    def load(self, filepath: str) -> Optional[Document]:
        """Load a single PDF file."""
        try:
            with open(filepath, 'rb') as f:
                reader = self.PyPDF2.PdfReader(f)
                
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                title = Path(filepath).stem.replace('_', ' ').title()
                
                return Document(
                    id=Path(filepath).stem,
                    title=title,
                    url=f"local://files/{Path(filepath).stem}",
                    content=text,
                    metadata={"file_path": str(filepath), "format": "pdf", "pages": len(reader.pages)}
                )
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None


# ===== CONVENIENCE FUNCTIONS =====

def load_markdown_directory(directory: str) -> int:
    """Load all markdown files from directory into knowledge base.
    
    Returns:
        Number of documents loaded
    """
    loader = MarkdownLoader()
    documents = loader.load(directory)
    
    for doc in documents:
        kb.add_document(doc)
    
    print(f"Loaded {len(documents)} markdown documents")
    return len(documents)


def load_text_directory(directory: str) -> int:
    """Load all text files from directory into knowledge base."""
    loader = TextLoader()
    documents = loader.load(directory)
    
    for doc in documents:
        kb.add_document(doc)
    
    print(f"Loaded {len(documents)} text documents")
    return len(documents)


def load_json_file(filepath: str) -> int:
    """Load documents from JSON file into knowledge base."""
    loader = JSONLoader()
    documents = loader.load(filepath)
    
    for doc in documents:
        kb.add_document(doc)
    
    print(f"Loaded {len(documents)} documents from JSON")
    return len(documents)


def load_web_page(url: str, title: Optional[str] = None) -> bool:
    """Load a web page into knowledge base."""
    if not WEB_SUPPORT:
        print("Web loading not available. Install: pip install requests beautifulsoup4")
        return False
    
    loader = WebLoader()
    doc = loader.load(url, title)
    
    if doc:
        kb.add_document(doc)
        print(f"Loaded: {doc.title}")
        return True
    
    return False


def load_pdf_file(filepath: str) -> bool:
    """Load a PDF file into knowledge base."""
    loader = PDFLoader()
    doc = loader.load(filepath)
    
    if doc:
        kb.add_document(doc)
        print(f"Loaded: {doc.title}")
        return True
    
    return False


# ===== BATCH LOADING =====

class DocumentImporter:
    """Batch import documents from multiple sources."""
    
    @staticmethod
    def import_from_directory(directory: str, pattern: str = "*") -> Dict[str, int]:
        """Import documents from directory recursively.
        
        Args:
            directory: Root directory
            pattern: File pattern to match
            
        Returns:
            Dict with counts by format
        """
        counts = {"markdown": 0, "text": 0, "pdf": 0, "failed": 0}
        path = Path(directory)
        
        # Load markdown files
        md_loader = MarkdownLoader()
        try:
            for md_file in path.rglob("*.md"):
                doc = md_loader._load_file(md_file)
                if doc:
                    kb.add_document(doc)
                    counts["markdown"] += 1
        except Exception as e:
            print(f"Error loading markdown: {e}")
            counts["failed"] += 1
        
        # Load text files
        txt_loader = TextLoader()
        try:
            for txt_file in path.rglob("*.txt"):
                doc = txt_loader._load_file(txt_file)
                if doc:
                    kb.add_document(doc)
                    counts["text"] += 1
        except Exception as e:
            print(f"Error loading text: {e}")
            counts["failed"] += 1
        
        # Load PDF files
        try:
            pdf_loader = PDFLoader()
            for pdf_file in path.rglob("*.pdf"):
                doc = pdf_loader.load(str(pdf_file))
                if doc:
                    kb.add_document(doc)
                    counts["pdf"] += 1
        except ImportError:
            pass  # PDF support not available
        except Exception as e:
            print(f"Error loading PDF: {e}")
            counts["failed"] += 1
        
        return counts
    
    @staticmethod
    def import_from_json_list(filepath: str) -> int:
        """Import from JSON file containing list of documents."""
        loader = JSONLoader()
        documents = loader.load(filepath)
        
        for doc in documents:
            kb.add_document(doc)
        
        return len(documents)


if __name__ == "__main__":
    # Example usage
    print("Document Loader Examples:\n")
    
    # Load markdown files
    print("1. Loading markdown files:")
    print("   loader = MarkdownLoader()")
    print("   docs = loader.load('path/to/markdown/files')")
    print()
    
    # Load text files
    print("2. Loading text files:")
    print("   loader = TextLoader()")
    print("   docs = loader.load('path/to/text/files')")
    print()
    
    # Load from JSON
    print("3. Loading from JSON:")
    print("   load_json_file('documents.json')")
    print()
    
    # Load web page
    print("4. Loading web page:")
    print("   load_web_page('https://example.com', title='Example')")
    print()
    
    # Batch import
    print("5. Batch import from directory:")
    print("   importer = DocumentImporter()")
    print("   counts = importer.import_from_directory('path/to/documents')")
    print()
    
    # Check loaded documents
    print("Available documents in knowledge base:")
    for doc_info in kb.list_documents():
        print(f"  - {doc_info['title']} ({doc_info['size']} chars)")