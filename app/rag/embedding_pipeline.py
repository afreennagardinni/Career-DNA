"""
Embedding Pipeline
Handles text embedding using sentence-transformers for RAG system.
"""

import json
import os
from typing import List, Dict, Any
import numpy as np


class EmbeddingPipeline:
    """
    Pipeline for generating embeddings from text documents.
    
    Uses sentence-transformers to create high-quality embeddings
    for semantic search and retrieval.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding pipeline.
        
        Args:
            model_name: Name of the sentence-transformers model to use
                      Default: all-MiniLM-L6-v2 (fast, good quality)
        """
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            print(f"Error loading SentenceTransformer: {e}")
            self.model = None
            self.embedding_dim = 384 # Fallback dimension for MiniLM
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Input text string
        
        Returns:
            np.ndarray: Embedding vector
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple text strings.
        
        Args:
            texts: List of input text strings
        
        Returns:
            np.ndarray: Matrix of embedding vectors
        """
        return self.model.encode(texts, convert_to_numpy=True)
    
    def embed_career(self, career: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embedding for a career document.
        
        Combines multiple fields into a single text representation
        before embedding.
        
        Args:
            career: Career dictionary from careers.json
        
        Returns:
            Dict with career data and embedding
        """
        # Combine relevant fields into searchable text
        searchable_text = self._create_career_text(career)
        
        # Generate embedding
        embedding = self.embed_text(searchable_text)
        
        return {
            "id": career["id"],
            "title": career["title"],
            "text": searchable_text,
            "embedding": embedding,
            "metadata": {
                "category": career.get("holland_codes", []),
                "industries": career.get("industries", []),
                "salary_range": career.get("salary_range", "")
            }
        }
    
    def embed_skill(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embedding for a skill document.
        
        Args:
            skill: Skill dictionary from skills.json
        
        Returns:
            Dict with skill data and embedding
        """
        # Combine relevant fields into searchable text
        searchable_text = self._create_skill_text(skill)
        
        # Generate embedding
        embedding = self.embed_text(searchable_text)
        
        return {
            "id": skill["id"],
            "name": skill["name"],
            "text": searchable_text,
            "embedding": embedding,
            "metadata": {
                "category": skill.get("category", ""),
                "related_careers": skill.get("related_careers", [])
            }
        }
    
    def _create_career_text(self, career: Dict[str, Any]) -> str:
        """
        Create searchable text representation of a career.
        
        Args:
            career: Career dictionary
        
        Returns:
            str: Combined text for embedding
        """
        parts = []
        
        # Title and description
        parts.append(f"Career: {career['title']}")
        parts.append(f"Description: {career['description']}")
        
        # Responsibilities
        if "responsibilities" in career:
            parts.append("Responsibilities: " + ", ".join(career["responsibilities"]))
        
        # Required skills
        if "required_skills" in career:
            parts.append("Required skills: " + ", ".join(career["required_skills"]))
        
        # Preferred skills
        if "preferred_skills" in career:
            parts.append("Preferred skills: " + ", ".join(career["preferred_skills"]))
        
        # Industries
        if "industries" in career:
            parts.append("Industries: " + ", ".join(career["industries"]))
        
        # Work environment
        if "work_environment" in career:
            parts.append(f"Work environment: {career['work_environment']}")
        
        return " ".join(parts)
    
    def _create_skill_text(self, skill: Dict[str, Any]) -> str:
        """
        Create searchable text representation of a skill.
        
        Args:
            skill: Skill dictionary
        
        Returns:
            str: Combined text for embedding
        """
        parts = []
        
        # Name and description
        parts.append(f"Skill: {skill['name']}")
        parts.append(f"Category: {skill['category']}")
        parts.append(f"Description: {skill['description']}")
        
        # Related careers
        if "related_careers" in skill:
            parts.append("Related careers: " + ", ".join(skill["related_careers"]))
        
        # Proficiency levels
        if "proficiency_levels" in skill:
            levels = [f"{l['level']}: {l['description']}" for l in skill["proficiency_levels"]]
            parts.append("Proficiency levels: " + "; ".join(levels))
        
        return " ".join(parts)
    
    def load_and_embed_careers(self, careers_path: str) -> List[Dict[str, Any]]:
        """
        Load careers from JSON and generate embeddings.
        
        Args:
            careers_path: Path to careers.json file
        
        Returns:
            List of career documents with embeddings
        """
        with open(careers_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        careers = data.get("careers", [])
        
        embedded_careers = []
        for career in careers:
            embedded_career = self.embed_career(career)
            embedded_careers.append(embedded_career)
        
        return embedded_careers
    
    def load_and_embed_skills(self, skills_path: str) -> List[Dict[str, Any]]:
        """
        Load skills from JSON and generate embeddings.
        
        Args:
            skills_path: Path to skills.json file
        
        Returns:
            List of skill documents with embeddings
        """
        with open(skills_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        skills = data.get("skills", [])
        
        embedded_skills = []
        for skill in skills:
            embedded_skill = self.embed_skill(skill)
            embedded_skills.append(embedded_skill)
        
        return embedded_skills
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: Embedding dimension
        """
        return self.embedding_dim
