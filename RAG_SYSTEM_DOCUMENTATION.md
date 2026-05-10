# Career DNA RAG System Documentation

## Overview

RAG system using sentence-transformers and FAISS for dynamic career/skill retrieval.

## Architecture

```
Knowledge Base (JSON) → Embedding Pipeline → Vector Store (FAISS) → Retriever → Career Query Agent
```

## Components

### 1. Knowledge Base
- `data/careers.json` - 15 career profiles
- `data/skills.json` - 20 skill profiles

### 2. Embedding Pipeline (`app/rag/embedding_pipeline.py`)
- Model: all-MiniLM-L6-v2 (384 dimensions)
- Methods: `embed_text()`, `embed_career()`, `embed_skill()`

### 3. Vector Store (`app/rag/vector_store.py`)
- FAISS IndexFlatIP with cosine similarity
- Classes: `VectorStore`, `CareerVectorStore`, `SkillVectorStore`, `VectorStoreManager`
- Storage: `data/vector_stores/`

### 4. Retriever (`app/rag/retriever.py`)
- Methods: `retrieve_careers()`, `retrieve_skills()`, `retrieve_hybrid()`
- Supports: direct query, trait-based, pattern-based retrieval

### 5. Integration (`app/agents/career_query_agent.py`)
- Career Query Agent now uses RAG by default
- Fallback to static database if RAG disabled

## Usage

```python
from app.rag import VectorStoreManager, Retriever

# Initialize (first time)
manager = VectorStoreManager()
manager.initialize('data/careers.json', 'data/skills.json')

# Load existing
manager.load_stores()
retriever = Retriever(manager)

# Search
careers = retriever.retrieve_careers("software engineer", k=5)
skills = retriever.retrieve_skills("programming", k=5)
```

## Dynamic vs Static

| Feature | Static | RAG |
|---------|--------|-----|
| Careers | 10 | 15+ |
| Search | Rule-based | Semantic |
| Extensibility | Code changes | Add to JSON |

## Dependencies

- sentence-transformers==2.2.2
- faiss-cpu==1.7.4
- numpy==1.24.3
