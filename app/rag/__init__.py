"""
RAG Package
Contains Retrieval-Augmented Generation implementations for Career DNA.
"""

# Lazy imports to avoid circular dependencies during initialization
# Import directly when needed:
# from app.rag.embedding_pipeline import EmbeddingPipeline
# from app.rag.vector_store import VectorStore, CareerVectorStore, SkillVectorStore, VectorStoreManager
# from app.rag.retriever import Retriever, RAGPipeline

__all__ = ['EmbeddingPipeline', 'VectorStore', 'CareerVectorStore', 'SkillVectorStore', 'VectorStoreManager', 'Retriever', 'RAGPipeline']
