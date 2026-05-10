"""
Retriever
Retrieves relevant documents using vector similarity search.
"""

from typing import List, Dict, Any, Optional
from app.rag.vector_store import VectorStoreManager
from app.rag.embedding_pipeline import EmbeddingPipeline


class Retriever:
    """
    Retrieves relevant documents for career queries using RAG.
    
    Flow: Input query → Embed query → Search vector store → Return relevant documents
    """
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """
        Initialize the retriever with a vector store manager.
        
        Args:
            vector_store_manager: Initialized VectorStoreManager instance
        """
        self.vector_store_manager = vector_store_manager
        self.embedding_pipeline = vector_store_manager.embedding_pipeline
    
    def retrieve_careers(self, query: str, k: int = 5, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant careers based on query.
        
        Args:
            query: Search query text
            k: Number of results to return
            filters: Optional filters (e.g., industry, salary range)
        
        Returns:
            List of relevant career documents with similarity scores
        """
        # Search vector store
        results = self.vector_store_manager.search_careers(query, k)
        
        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)
        
        return results
    
    def retrieve_skills(self, query: str, k: int = 5, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant skills based on query.
        
        Args:
            query: Search query text
            k: Number of results to return
            filters: Optional filters (e.g., category, proficiency level)
        
        Returns:
            List of relevant skill documents with similarity scores
        """
        # Search vector store
        results = self.vector_store_manager.search_skills(query, k)
        
        # Apply filters if provided
        if filters:
            results = self._apply_filters(results, filters)
        
        return results
    
    def retrieve_hybrid(self, query: str, k_careers: int = 3, k_skills: int = 3) -> Dict[str, Any]:
        """
        Retrieve both careers and skills for a comprehensive result.
        
        Args:
            query: Search query text
            k_careers: Number of career results
            k_skills: Number of skill results
        
        Returns:
            Dict with both career and skill results
        """
        careers = self.retrieve_careers(query, k_careers)
        skills = self.retrieve_skills(query, k_skills)
        
        return {
            "query": query,
            "careers": careers,
            "skills": skills,
            "total_results": len(careers) + len(skills)
        }
    
    def retrieve_by_traits(self, traits: Dict[str, float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve careers based on personality traits.
        
        Converts trait scores into a natural language query for retrieval.
        
        Args:
            traits: Dictionary of trait scores (e.g., Big Five or RIASEC)
            k: Number of results to return
        
        Returns:
            List of relevant career documents
        """
        # Convert traits to query text
        query = self._traits_to_query(traits)
        
        # Retrieve careers
        return self.retrieve_careers(query, k)
    
    def retrieve_by_patterns(self, patterns: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve careers based on detected patterns.
        
        Args:
            patterns: List of detected patterns from Pattern Analysis Agent
            k: Number of results to return
        
        Returns:
            List of relevant career documents
        """
        # Convert patterns to query text
        query = self._patterns_to_query(patterns)
        
        # Retrieve careers
        return self.retrieve_careers(query, k)
    
    def _apply_filters(self, results: List[Dict[str, Any]], filters: Dict) -> List[Dict[str, Any]]:
        """
        Apply filters to search results.
        
        Args:
            results: Search results from vector store
            filters: Filter criteria
        
        Returns:
            List of filtered results
        """
        filtered = results
        
        # Filter by industry
        if "industry" in filters:
            filtered = [
                r for r in filtered
                if filters["industry"] in r.get("metadata", {}).get("industries", [])
            ]
        
        # Filter by category
        if "category" in filters:
            filtered = [
                r for r in filtered
                if filters["category"] == r.get("metadata", {}).get("category", "")
            ]
        
        # Filter by minimum similarity score
        if "min_score" in filters:
            filtered = [
                r for r in filtered
                if r.get("similarity_score", 0) >= filters["min_score"]
            ]
        
        return filtered
    
    def _traits_to_query(self, traits: Dict[str, float]) -> str:
        """
        Convert trait scores to natural language query.
        
        Args:
            traits: Dictionary of trait scores
        
        Returns:
            str: Natural language query
        """
        query_parts = []
        
        # Get top traits (above threshold)
        threshold = 70.0
        top_traits = [t for t, s in traits.items() if s >= threshold]
        
        if top_traits:
            query_parts.append(f"careers for people with high {', '.join(top_traits)}")
        else:
            # Use all traits if none above threshold
            query_parts.append(f"careers for balanced personality with {', '.join(traits.keys())}")
        
        return " ".join(query_parts)
    
    def _patterns_to_query(self, patterns: List[Dict[str, Any]]) -> str:
        """
        Convert patterns to natural language query.
        
        Args:
            patterns: List of detected patterns
        
        Returns:
            str: Natural language query
        """
        if not patterns:
            return "careers"
        
        # Use top pattern
        top_pattern = patterns[0]
        pattern_type = top_pattern.get("type", "")
        description = top_pattern.get("description", "")
        
        return f"careers for {description}"
    
    def format_results(self, results: List[Dict[str, Any]], result_type: str = "career") -> List[Dict[str, Any]]:
        """
        Format search results for API response.
        
        Args:
            results: Raw search results
            result_type: Type of results ("career" or "skill")
        
        Returns:
            List of formatted results
        """
        formatted = []
        
        for result in results:
            if result_type == "career":
                formatted.append({
                    "id": result.get("id"),
                    "title": result.get("title"),
                    "similarity_score": result.get("similarity_score", 0),
                    "metadata": result.get("metadata", {}),
                    "snippet": self._create_snippet(result.get("text", ""), 150)
                })
            else:  # skill
                formatted.append({
                    "id": result.get("id"),
                    "name": result.get("name"),
                    "similarity_score": result.get("similarity_score", 0),
                    "metadata": result.get("metadata", {}),
                    "snippet": self._create_snippet(result.get("text", ""), 150)
                })
        
        return formatted
    
    def _create_snippet(self, text: str, max_length: int) -> str:
        """
        Create a short snippet from text.
        
        Args:
            text: Full text
            max_length: Maximum length of snippet
        
        Returns:
            str: Text snippet
        """
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the retriever and vector stores.
        
        Returns:
            Dict with retrieval statistics
        """
        return {
            "career_documents": self.vector_store_manager.career_store.get_document_count() if self.vector_store_manager.career_store else 0,
            "skill_documents": self.vector_store_manager.skill_store.get_document_count() if self.vector_store_manager.skill_store else 0,
            "embedding_model": self.embedding_pipeline.model_name,
            "embedding_dimension": self.embedding_pipeline.get_embedding_dimension()
        }


class RAGPipeline:
    """
    Complete RAG pipeline for career recommendations.
    
    Combines retrieval with generation for comprehensive career guidance.
    """
    
    def __init__(self, retriever: Retriever):
        """
        Initialize the RAG pipeline.
        
        Args:
            retriever: Initialized Retriever instance
        """
        self.retriever = retriever
    
    def query(self, user_query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            user_query: User's natural language query
            context: Optional context (traits, patterns, preferences)
        
        Returns:
            Dict with retrieved documents and generated response
        """
        # Determine retrieval strategy based on context
        if context and "traits" in context:
            # Trait-based retrieval
            results = self.retriever.retrieve_by_traits(context["traits"])
            retrieval_method = "trait_based"
        elif context and "patterns" in context:
            # Pattern-based retrieval
            results = self.retriever.retrieve_by_patterns(context["patterns"])
            retrieval_method = "pattern_based"
        else:
            # Direct query retrieval
            results = self.retriever.retrieve_hybrid(user_query)
            retrieval_method = "direct_query"
        
        # Format results
        formatted_careers = self.retriever.format_results(results.get("careers", []), "career")
        formatted_skills = self.retriever.format_results(results.get("skills", []), "skill")
        
        # Generate response
        response = self._generate_response(user_query, formatted_careers, formatted_skills, context)
        
        return {
            "query": user_query,
            "retrieval_method": retrieval_method,
            "results": {
                "careers": formatted_careers,
                "skills": formatted_skills
            },
            "response": response,
            "stats": self.retriever.get_retrieval_stats()
        }
    
    def _generate_response(self, query: str, careers: List[Dict], skills: List[Dict], context: Optional[Dict]) -> str:
        """
        Generate a natural language response from retrieved documents.
        
        Args:
            query: Original user query
            careers: Retrieved career documents
            skills: Retrieved skill documents
            context: Optional context
        
        Returns:
            str: Generated response
        """
        if not careers:
            return "I couldn't find any careers matching your query. Try rephrasing or providing more specific details."
        
        # Build response
        response_parts = [f"Based on your query '{query}', here are some relevant career options:"]
        
        # Add top careers
        for i, career in enumerate(careers[:3], 1):
            response_parts.append(
                f"\n{i}. {career['title']} (Match: {career['similarity_score']:.2f})\n"
                f"   {career['snippet']}"
            )
        
        # Add skills if available
        if skills:
            response_parts.append("\n\nRelevant skills for these careers:")
            for skill in skills[:3]:
                response_parts.append(f"- {skill['name']}")
        
        return "\n".join(response_parts)
