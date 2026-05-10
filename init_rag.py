"""
Initialize RAG Vector Stores
Run this script to build FAISS indexes from careers.json and skills.json
"""

import os
import sys

# Add app directory to path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Direct imports to avoid app initialization
from rag.embedding_pipeline import EmbeddingPipeline
from rag.vector_store import VectorStoreManager

def main():
    print("Initializing RAG Vector Stores...")
    
    # Get paths
    base_dir = os.path.dirname(__file__)
    careers_path = os.path.join(base_dir, 'data', 'careers.json')
    skills_path = os.path.join(base_dir, 'data', 'skills.json')
    
    # Check if files exist
    if not os.path.exists(careers_path):
        print(f"Error: {careers_path} not found")
        return
    
    if not os.path.exists(skills_path):
        print(f"Error: {skills_path} not found")
        return
    
    # Initialize vector store manager
    vector_stores_dir = os.path.join(base_dir, 'data', 'vector_stores')
    os.makedirs(vector_stores_dir, exist_ok=True)
    
    print(f"Careers path: {careers_path}")
    print(f"Skills path: {skills_path}")
    print(f"Vector stores dir: {vector_stores_dir}")
    
    # Initialize
    manager = VectorStoreManager(vector_stores_dir)
    manager.initialize(careers_path, skills_path, model_name="all-MiniLM-L6-v2")
    
    print("\nVector stores initialized successfully!")
    print(f"Career documents: {manager.career_store.get_document_count()}")
    print(f"Skill documents: {manager.skill_store.get_document_count()}")
    print(f"Stores saved to: {vector_stores_dir}")
    
    # Test search
    print("\nTesting search...")
    test_results = manager.search_careers("software engineer", k=3)
    print(f"Found {len(test_results)} careers for 'software engineer'")
    for result in test_results:
        print(f"  - {result['title']}: {result['similarity_score']:.3f}")

if __name__ == "__main__":
    main()
