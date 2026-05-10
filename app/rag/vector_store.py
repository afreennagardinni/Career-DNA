"""
Vector Store
FAISS-based vector storage for semantic search and retrieval.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from app.rag.embedding_pipeline import EmbeddingPipeline


class VectorStore:
    """
    FAISS-based vector store for efficient similarity search.
    
    Stores embeddings and enables fast retrieval of similar documents.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the vector store.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.documents = []  # Store document metadata
        self.doc_ids = []  # Map index to document ID
    
    def create_index(self, embeddings: np.ndarray, documents: List[Dict[str, Any]]):
        """
        Create FAISS index from embeddings.
        
        Args:
            embeddings: Matrix of embedding vectors
            documents: List of document dictionaries with metadata
        """
        # Create FAISS index (Inner Product for cosine similarity)
        # Normalize embeddings for cosine similarity
        normalized_embeddings = self._normalize_embeddings(embeddings)
        
        # Create index
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(normalized_embeddings.astype('float32'))
        
        # Store documents
        self.documents = documents
        self.doc_ids = [doc['id'] for doc in documents]
    
    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Normalize embeddings for cosine similarity.
        
        Args:
            embeddings: Matrix of embedding vectors
        
        Returns:
            np.ndarray: Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norms
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of similar documents with scores
        """
        if self.index is None:
            return []
        
        # Normalize query embedding
        query_embedding = query_embedding.reshape(1, -1)
        normalized_query = self._normalize_embeddings(query_embedding)
        
        # Search
        scores, indices = self.index.search(normalized_query.astype('float32'), k)
        
        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                result = self.documents[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results
    
    def save(self, index_path: str, documents_path: str):
        """
        Save index and documents to disk.
        
        Args:
            index_path: Path to save FAISS index
            documents_path: Path to save documents metadata
        """
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save documents
        with open(documents_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'doc_ids': self.doc_ids
            }, f)
    
    def load(self, index_path: str, documents_path: str):
        """
        Load index and documents from disk.
        
        Args:
            index_path: Path to load FAISS index
            documents_path: Path to load documents metadata
        """
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load documents
        with open(documents_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.doc_ids = data['doc_ids']
    
    def get_document_count(self) -> int:
        """
        Get the number of documents in the store.
        
        Returns:
            int: Number of documents
        """
        return len(self.documents)


class CareerVectorStore(VectorStore):
    """
    Specialized vector store for career documents.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the career vector store.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        super().__init__(embedding_dim)
        self.store_type = "careers"
    
    def build_from_careers(self, embedded_careers: List[Dict[str, Any]]):
        """
        Build index from embedded career documents.
        
        Args:
            embedded_careers: List of career documents with embeddings
        """
        # Extract embeddings and documents
        embeddings = np.array([doc['embedding'] for doc in embedded_careers])
        documents = [
            {
                'id': doc['id'],
                'title': doc['title'],
                'text': doc['text'],
                'metadata': doc['metadata']
            }
            for doc in embedded_careers
        ]
        
        self.create_index(embeddings, documents)
    
    def search_careers(self, query: str, embedding_pipeline: EmbeddingPipeline, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for careers based on query text.
        
        Args:
            query: Search query text
            embedding_pipeline: Embedding pipeline instance
            k: Number of results to return
        
        Returns:
            List of similar career documents
        """
        # Generate query embedding
        query_embedding = embedding_pipeline.embed_text(query)
        
        # Search
        results = self.search(query_embedding, k)
        
        return results


class SkillVectorStore(VectorStore):
    """
    Specialized vector store for skill documents.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize the skill vector store.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        super().__init__(embedding_dim)
        self.store_type = "skills"
    
    def build_from_skills(self, embedded_skills: List[Dict[str, Any]]):
        """
        Build index from embedded skill documents.
        
        Args:
            embedded_skills: List of skill documents with embeddings
        """
        # Extract embeddings and documents
        embeddings = np.array([doc['embedding'] for doc in embedded_skills])
        documents = [
            {
                'id': doc['id'],
                'name': doc['name'],
                'text': doc['text'],
                'metadata': doc['metadata']
            }
            for doc in embedded_skills
        ]
        
        self.create_index(embeddings, documents)
    
    def search_skills(self, query: str, embedding_pipeline: EmbeddingPipeline, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for skills based on query text.
        
        Args:
            query: Search query text
            embedding_pipeline: Embedding pipeline instance
            k: Number of results to return
        
        Returns:
            List of similar skill documents
        """
        # Generate query embedding
        query_embedding = embedding_pipeline.embed_text(query)
        
        # Search
        results = self.search(query_embedding, k)
        
        return results


class VectorStoreManager:
    """
    Manager for multiple vector stores.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Initialize the vector store manager.
        
        Args:
            base_dir: Base directory for storing vector stores
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'vector_stores')
        
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
        self.career_store = None
        self.skill_store = None
        self.embedding_pipeline = None
    
    def initialize(self, careers_path: str, skills_path: str, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize all vector stores.
        
        Args:
            careers_path: Path to careers.json
            skills_path: Path to skills.json
            model_name: Name of sentence-transformers model
        """
        # Initialize embedding pipeline
        self.embedding_pipeline = EmbeddingPipeline(model_name)
        
        # Load and embed careers
        embedded_careers = self.embedding_pipeline.load_and_embed_careers(careers_path)
        
        # Load and embed skills
        embedded_skills = self.embedding_pipeline.load_and_embed_skills(skills_path)
        
        # Create career store
        self.career_store = CareerVectorStore(self.embedding_pipeline.get_embedding_dimension())
        self.career_store.build_from_careers(embedded_careers)
        
        # Create skill store
        self.skill_store = SkillVectorStore(self.embedding_pipeline.get_embedding_dimension())
        self.skill_store.build_from_skills(embedded_skills)
        
        # Save to disk
        self.save_stores()
    
    def save_stores(self):
        """Save all vector stores to disk."""
        career_index_path = os.path.join(self.base_dir, 'career_index.faiss')
        career_docs_path = os.path.join(self.base_dir, 'career_documents.pkl')
        self.career_store.save(career_index_path, career_docs_path)
        
        skill_index_path = os.path.join(self.base_dir, 'skill_index.faiss')
        skill_docs_path = os.path.join(self.base_dir, 'skill_documents.pkl')
        self.skill_store.save(skill_index_path, skill_docs_path)
    
    def load_stores(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Load all vector stores from disk.
        
        Args:
            model_name: Name of sentence-transformers model
        """
        # Initialize embedding pipeline
        self.embedding_pipeline = EmbeddingPipeline(model_name)
        
        # Load career store
        self.career_store = CareerVectorStore(self.embedding_pipeline.get_embedding_dimension())
        career_index_path = os.path.join(self.base_dir, 'career_index.faiss')
        career_docs_path = os.path.join(self.base_dir, 'career_documents.pkl')
        
        if os.path.exists(career_index_path) and os.path.exists(career_docs_path):
            self.career_store.load(career_index_path, career_docs_path)
        
        # Load skill store
        self.skill_store = SkillVectorStore(self.embedding_pipeline.get_embedding_dimension())
        skill_index_path = os.path.join(self.base_dir, 'skill_index.faiss')
        skill_docs_path = os.path.join(self.base_dir, 'skill_documents.pkl')
        
        if os.path.exists(skill_index_path) and os.path.exists(skill_docs_path):
            self.skill_store.load(skill_index_path, skill_docs_path)
    
    def search_careers(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for careers.
        
        Args:
            query: Search query
            k: Number of results
        
        Returns:
            List of career results
        """
        if self.career_store is None:
            return []
        return self.career_store.search_careers(query, self.embedding_pipeline, k)
    
    def search_skills(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for skills.
        
        Args:
            query: Search query
            k: Number of results
        
        Returns:
            List of skill results
        """
        if self.skill_store is None:
            return []
        return self.skill_store.search_skills(query, self.embedding_pipeline, k)
