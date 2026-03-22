"""Enhanced Knowledge Base with Vector Search Support.

This module provides advanced knowledge base functionality including:
- Multiple document loading strategies
- Vector embeddings for semantic search
- Hybrid search (keyword + semantic)
- Document chunking and indexing
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    from langchain_ollama import OllamaEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    VECTOR_SUPPORT = True
except ImportError:
    VECTOR_SUPPORT = False
    RecursiveCharacterTextSplitter = None



@dataclass
class Document:
    """Document representation."""
    id: str
    title: str
    url: str
    content: str
    metadata: Dict = None
    embedding: Optional[List[float]] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class AdvancedKnowledgeBase:
    """Advanced knowledge base with multiple search strategies.
    
    Supports:
    - Keyword search (fast, for exact matches)
    - Vector search (semantic, for conceptual matches)
    - Hybrid search (combination of both)
    - Document metadata filtering
    """
    
    def __init__(self, use_vectors: bool = True):
        self.documents: Dict[str, Document] = {}
        self.use_vectors = use_vectors and VECTOR_SUPPORT
        
        if self.use_vectors:
            try:
                self.embeddings = OllamaEmbeddings(
                    model="nomic-embed-text",
                    base_url="http://localhost:11434",
                )
            except Exception as e:
                print(f"Warning: Vector embeddings not available: {e}")
                self.use_vectors = False
        
        # Only initialize text_splitter if imports succeeded
        if RecursiveCharacterTextSplitter:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
        else:
            self.text_splitter = None
        
        self._initialize_default_kb()
    
    def _initialize_default_kb(self):
        """Initialize with comprehensive knowledge base."""
        default_docs = {
            "ai-fundamentals": Document(
                id="ai-fundamentals",
                title="Artificial Intelligence Fundamentals",
                url="local://kb/ai-fundamentals",
                content="""
# Artificial Intelligence Fundamentals

## What is AI?
Artificial Intelligence refers to computer systems designed to perform tasks that typically require human intelligence. These include visual perception, speech recognition, decision-making, and language translation.

## Core Concepts

### Machine Learning
Machine Learning is a subset of AI where systems learn from data without explicit programming. Key concepts include:
- Supervised Learning: Learning from labeled examples
- Unsupervised Learning: Finding patterns in unlabeled data
- Reinforcement Learning: Learning through interaction and rewards
- Transfer Learning: Applying knowledge from one domain to another

### Deep Learning
Deep Learning uses neural networks with multiple layers (hence "deep") to learn hierarchical representations of data. Applications include:
- Computer Vision: Image recognition, object detection
- Natural Language Processing: Text analysis, translation
- Speech Recognition: Converting audio to text
- Recommendation Systems: Personalizing user experience

### Neural Networks
Neural networks are inspired by biological neurons and consist of:
- Input Layer: Receives data
- Hidden Layers: Process information
- Output Layer: Produces results
- Weights and Biases: Learnable parameters

## Common Applications

### Healthcare
- Disease diagnosis from medical imaging
- Drug discovery and development
- Patient risk prediction
- Personalized treatment recommendations

### Finance
- Fraud detection
- Algorithmic trading
- Credit risk assessment
- Portfolio optimization

### Transportation
- Autonomous vehicles
- Traffic optimization
- Route planning
- Predictive maintenance

### Natural Language Processing
- Chatbots and conversational AI
- Machine translation
- Sentiment analysis
- Text summarization

## Challenges and Limitations

### Data Requirements
- Need large amounts of training data
- Quality of data affects model performance
- Data labeling can be expensive and time-consuming

### Computational Cost
- Training large models requires significant computing power
- GPU/TPU infrastructure is expensive
- Environmental impact of large-scale training

### Interpretability
- Deep learning models are often "black boxes"
- Difficult to understand why decisions are made
- Important for high-stakes applications (healthcare, law)

### Safety and Ethics
- Bias in training data leads to biased models
- Adversarial examples can fool models
- Privacy concerns with personal data
- Job displacement from automation

## Recent Advances

### Foundation Models
Large language models trained on vast amounts of text:
- GPT series (OpenAI)
- Claude (Anthropic)
- Llama (Meta)
- Phi (Microsoft)

These models can be adapted for various tasks with minimal fine-tuning.

### Multimodal AI
Systems that can process multiple types of data:
- Vision and language: Image captioning, visual question answering
- Audio and text: Speech recognition, music generation
- Cross-modal learning: Learning relationships between different modalities

### Few-Shot Learning
Learning from very few examples, similar to human learning.

## Future Directions

### Artificial General Intelligence (AGI)
- Current AI is narrow (specialized in specific tasks)
- AGI would be as flexible as human intelligence
- Estimated decades away, if possible at all

### Efficient AI
- Smaller models with better performance
- Edge computing (AI on mobile/IoT devices)
- Reduced computational requirements

### Interpretable AI
- Better understanding of model decisions
- Explainable AI (XAI) techniques
- Building trust in AI systems

## Conclusion

AI is rapidly advancing and becoming integrated into many aspects of society. Understanding both its capabilities and limitations is crucial for responsible development and deployment.
"""
            ),
            "ml-algorithms": Document(
                id="ml-algorithms",
                title="Machine Learning Algorithms Guide",
                url="local://kb/ml-algorithms",
                content="""
# Machine Learning Algorithms

## Supervised Learning Algorithms

### Regression Algorithms
Used for predicting continuous values.

**Linear Regression**
- Simple and interpretable
- Assumes linear relationship between features and target
- Fast to train and compute
- Use case: Price prediction, forecasting

**Polynomial Regression**
- Captures non-linear relationships
- Higher degree = more complex patterns
- Risk of overfitting with high degrees
- Use case: Growth modeling, complex trends

**Ridge and Lasso Regression**
- Regularization techniques to prevent overfitting
- Ridge: L2 penalty, reduces large coefficients
- Lasso: L1 penalty, can eliminate features
- Use case: High-dimensional data with multicollinearity

**Support Vector Regression (SVR)**
- Non-parametric regression
- Good for non-linear problems
- More robust to outliers than linear regression
- Use case: Non-linear prediction tasks

### Classification Algorithms

**Logistic Regression**
- Binary classification despite the name
- Outputs probability between 0 and 1
- Fast and interpretable
- Use case: Email spam detection, disease diagnosis

**Decision Trees**
- Tree-like decision structure
- Easy to understand and interpret
- Prone to overfitting
- Use case: Feature importance analysis, rule extraction

**Random Forests**
- Ensemble of decision trees
- Better generalization than single tree
- Handles both regression and classification
- Use case: Classification with many features, feature importance

**Support Vector Machines (SVM)**
- Finds optimal hyperplane separating classes
- Good for high-dimensional data
- Works well with non-linear kernels
- Use case: Image classification, text categorization

**Neural Networks**
- Universal approximators
- Can learn complex non-linear relationships
- Requires significant training data
- Use case: Deep learning, complex pattern recognition

## Unsupervised Learning Algorithms

### Clustering

**K-Means**
- Partitions data into K clusters
- Efficient and scalable
- Assumes spherical clusters
- Use case: Customer segmentation, document clustering

**Hierarchical Clustering**
- Creates dendrograms showing nested clusters
- Doesn't require specifying K in advance
- More computationally expensive
- Use case: Taxonomy creation, gene sequence analysis

**DBSCAN**
- Density-based clustering
- Handles arbitrary cluster shapes
- Identifies outliers as noise
- Use case: Spatial data, anomaly detection

**Gaussian Mixture Models (GMM)**
- Probabilistic clustering
- Soft assignments (probability of belonging to cluster)
- Assumes Gaussian distribution
- Use case: Density estimation, soft clustering

### Dimensionality Reduction

**Principal Component Analysis (PCA)**
- Linear transformation to principal components
- Reduces features while preserving variance
- Improves computational efficiency
- Use case: Visualization, feature reduction

**t-SNE**
- Non-linear dimensionality reduction
- Excellent for visualization
- Computationally expensive
- Use case: 2D/3D visualization of high-dimensional data

**Autoencoders**
- Neural network for unsupervised learning
- Learns compact representation (latent space)
- Can be non-linear
- Use case: Anomaly detection, data denoising

## Ensemble Methods

**Bagging**
- Bootstrap aggregating
- Reduces variance of high-variance models
- Example: Random Forests
- Use case: Improving model stability

**Boosting**
- Sequentially builds models, focusing on mistakes
- Reduces both bias and variance
- Examples: Gradient Boosting, AdaBoost
- Use case: Winning Kaggle competitions

**Stacking**
- Multiple base models with a meta-learner
- Combines strengths of different algorithms
- More complex to tune
- Use case: Maximum predictive power

## Deep Learning Architectures

### Convolutional Neural Networks (CNN)
- Specialized for image processing
- Convolutional layers extract features
- Pooling layers reduce dimensionality
- Use case: Image classification, object detection

### Recurrent Neural Networks (RNN)
- Process sequential data
- LSTM and GRU variants handle long sequences
- Maintains hidden state
- Use case: Time series, language modeling

### Transformer Architecture
- Self-attention mechanism
- Parallelizable training
- State-of-the-art NLP
- Use case: Language models, machine translation

## Algorithm Selection Guide

Choose based on:
1. **Problem Type**: Regression vs Classification vs Clustering
2. **Data Size**: Small/medium/large
3. **Feature Count**: Few/moderate/many
4. **Interpretability**: Important or not
5. **Computational Resources**: CPU/GPU available
6. **Training Time**: Quick iteration vs thorough tuning

## Performance Metrics

### Regression
- Mean Squared Error (MSE)
- Mean Absolute Error (MAE)
- R² Score
- Root Mean Squared Error (RMSE)

### Classification
- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC

### Clustering
- Silhouette Score
- Davies-Bouldin Index
- Calinski-Harabasz Index
"""
            ),
        }
        
        for doc in default_docs.values():
            self.add_document(doc)
    
    def add_document(self, document: Document) -> None:
        """Add a document to the knowledge base."""
        self.documents[document.id] = document
        
        # Generate embedding if vectors are enabled
        if self.use_vectors and document.embedding is None:
            try:
                document.embedding = self.embeddings.embed_query(document.content[:500])
            except Exception as e:
                print(f"Warning: Could not embed document {document.id}: {e}")
    
    def keyword_search(self, query: str, max_results: int = 3) -> List[Tuple[Document, float]]:
        """Simple keyword-based search.
        
        Returns list of (document, score) tuples sorted by relevance.
        """
        results = []
        query_terms = query.lower().split()
        
        for doc in self.documents.values():
            content_lower = (doc.title + " " + doc.content).lower()
            score = 0
            
            for term in query_terms:
                score += content_lower.count(term)
            
            if score > 0:
                results.append((doc, score))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]
    
    def vector_search(self, query: str, max_results: int = 3) -> List[Tuple[Document, float]]:
        """Semantic search using embeddings.
        
        Returns list of (document, similarity_score) tuples.
        """
        if not self.use_vectors:
            return []
        
        try:
            query_embedding = self.embeddings.embed_query(query)
            results = []
            
            for doc in self.documents.values():
                if doc.embedding is None:
                    continue
                
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                results.append((doc, similarity))
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:max_results]
        
        except Exception as e:
            print(f"Warning: Vector search failed: {e}")
            return []
    
    def hybrid_search(self, query: str, max_results: int = 3) -> List[Tuple[Document, float]]:
        """Hybrid search combining keyword and vector search.
        
        Uses weighted combination of both approaches.
        """
        keyword_results = self.keyword_search(query, max_results=10)
        vector_results = self.vector_search(query, max_results=10) if self.use_vectors else []
        
        # Normalize scores
        keyword_scores = {doc.id: score for doc, score in keyword_results}
        vector_scores = {doc.id: score for doc, score in vector_results}
        
        # Combine scores (60% keyword, 40% vector)
        combined = {}
        for doc_id in set(list(keyword_scores.keys()) + list(vector_scores.keys())):
            keyword_score = keyword_scores.get(doc_id, 0)
            vector_score = vector_scores.get(doc_id, 0)
            
            # Normalize to 0-1 range
            max_keyword = max(keyword_scores.values()) if keyword_scores else 1
            max_vector = max(vector_scores.values()) if vector_scores else 1
            
            norm_keyword = (keyword_score / max_keyword) if max_keyword > 0 else 0
            norm_vector = (vector_score / max_vector) if max_vector > 0 else 0
            
            combined[doc_id] = 0.6 * norm_keyword + 0.4 * norm_vector
        
        # Return top results
        results = [
            (self.documents[doc_id], score)
            for doc_id, score in sorted(combined.items(), key=lambda x: x[1], reverse=True)
        ]
        return results[:max_results]
    
    def search(
        self, 
        query: str, 
        max_results: int = 3,
        search_type: str = "hybrid"
    ) -> List[Dict]:
        """Search the knowledge base.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            search_type: "keyword", "vector", or "hybrid"
            
        Returns:
            List of document dictionaries with relevance scores
        """
        if search_type == "keyword":
            results = self.keyword_search(query, max_results)
        elif search_type == "vector":
            results = self.vector_search(query, max_results)
        else:  # hybrid
            results = self.hybrid_search(query, max_results)
        
        # Format results
        formatted = []
        for doc, score in results:
            formatted.append({
                "id": doc.id,
                "title": doc.title,
                "url": doc.url,
                "content": doc.content[:1000],
                "raw_content": doc.content,
                "score": float(score),
                "metadata": doc.metadata,
            })
        
        return formatted
    
    def load_from_json(self, filepath: str) -> None:
        """Load documents from JSON file.
        
        Expected format:
        [
            {
                "id": "doc1",
                "title": "Title",
                "url": "url",
                "content": "content",
                "metadata": {...}
            }
        ]
        """
        with open(filepath, 'r') as f:
            docs = json.load(f)
        
        for doc_dict in docs:
            doc = Document(**doc_dict)
            self.add_document(doc)
    
    def save_to_json(self, filepath: str) -> None:
        """Save documents to JSON file."""
        docs_list = []
        for doc in self.documents.values():
            docs_list.append({
                "id": doc.id,
                "title": doc.title,
                "url": doc.url,
                "content": doc.content,
                "metadata": doc.metadata,
                "created_at": doc.created_at,
                # Don't save embeddings (can regenerate)
            })
        
        with open(filepath, 'w') as f:
            json.dump(docs_list, f, indent=2)
    
    def get_document_by_id(self, doc_id: str) -> Optional[Document]:
        """Retrieve a specific document by ID."""
        return self.documents.get(doc_id)
    
    def list_documents(self) -> List[Dict]:
        """List all documents with basic info."""
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "url": doc.url,
                "created_at": doc.created_at,
                "size": len(doc.content),
            }
            for doc in self.documents.values()
        ]
    
    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x ** 2 for x in a) ** 0.5
        norm_b = sum(x ** 2 for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


# Global instance
kb = AdvancedKnowledgeBase(use_vectors=True)