"""
RAG Retrieval Agent
Retrieves relevant career and skill documents using RAG.
"""

from typing import Dict, List, Any
import os

# Try to import RAG components
try:
    from app.rag.embedding_pipeline import EmbeddingPipeline
    from app.rag.vector_store import VectorStoreManager
    from app.rag.retriever import Retriever
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class RAGRetrievalAgent:
    """
    Agent responsible for retrieving relevant documents using RAG.
    
    Flow: Input (query/context) → Process (RAG retrieval) → Output (relevant documents)
    """
    
    def __init__(self, use_rag: bool = True):
        """
        Initialize the RAG retrieval agent.
        
        Args:
            use_rag: Whether to use RAG for retrieval (default: True)
        """
        self.agent_name = "RAGRetrievalAgent"
        
        # Check if RAG is available
        if use_rag and not RAG_AVAILABLE:
            print("RAG components not available, using fallback")
            use_rag = False
        
        self.use_rag = use_rag
        
        # Initialize RAG components
        if use_rag:
            try:
                self._init_rag()
            except Exception as e:
                print(f"RAG initialization failed: {e}, using fallback")
                self.use_rag = False
        else:
            self.retriever = None
    
    def _init_rag(self):
        """Initialize RAG components."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        careers_path = os.path.join(base_dir, 'data', 'careers.json')
        skills_path = os.path.join(base_dir, 'data', 'skills.json')
        vector_stores_dir = os.path.join(base_dir, 'data', 'vector_stores')
        
        self.vector_store_manager = VectorStoreManager(vector_stores_dir)
        
        if os.path.exists(os.path.join(vector_stores_dir, 'career_index.faiss')):
            self.vector_store_manager.load_stores()
        else:
            self.vector_store_manager.initialize(careers_path, skills_path)
        
        self.retriever = Retriever(self.vector_store_manager)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input to retrieve relevant documents.
        
        Input:
            {
                "query": str (optional),
                "traits": {...} (optional),
                "patterns": [...] (optional),
                "k": int (default 5)
            }
        
        Process:
            1. Determine retrieval strategy
            2. Retrieve relevant careers and skills
            3. Format results
        
        Output:
            {
                "agent": "RAGRetrievalAgent",
                "careers": [...],
                "skills": [...],
                "retrieval_method": "...",
                "metadata": {...}
            }
        """
        if not self.use_rag or self.retriever is None:
            return self._fallback_response()
        
        query = input_data.get("query", "")
        traits = input_data.get("traits", {})
        patterns = input_data.get("patterns", [])
        k = input_data.get("k", 5)
        
        # Determine retrieval strategy
        if patterns:
            careers = self.retriever.retrieve_by_patterns(patterns, k)
            retrieval_method = "pattern_based"
        elif traits:
            combined_traits = {**traits.get("big_five", {}), **traits.get("riasec", {})}
            careers = self.retriever.retrieve_by_traits(combined_traits, k)
            retrieval_method = "trait_based"
        elif query:
            results = self.retriever.retrieve_hybrid(query, k_careers=k, k_skills=k)
            careers = results.get("careers", [])
            skills = results.get("skills", [])
            retrieval_method = "direct_query"
        else:
            careers = self.retriever.retrieve_careers("careers", k)
            skills = self.retriever.retrieve_skills("skills", k)
            retrieval_method = "default"
        
        if "skills" not in locals():
            skills = self.retriever.retrieve_skills(query or "skills", k)
        
        formatted_careers = self.retriever.format_results(careers, "career")
        formatted_skills = self.retriever.format_results(skills, "skill")
        
        return {
            "agent": self.agent_name,
            "careers": formatted_careers,
            "skills": formatted_skills,
            "retrieval_method": retrieval_method,
            "metadata": {
                "career_count": len(formatted_careers),
                "skill_count": len(formatted_skills),
                "rag_enabled": self.use_rag
            }
        }
    
    def _fallback_response(self) -> Dict[str, Any]:
        """Return fallback response when RAG is unavailable."""
        return {
            "agent": self.agent_name,
            "careers": [],
            "skills": [],
            "retrieval_method": "fallback",
            "metadata": {
                "career_count": 0,
                "skill_count": 0,
                "rag_enabled": False,
                "message": "RAG not available"
            }
        }
