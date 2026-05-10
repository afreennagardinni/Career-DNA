"""
Career DNA Pipeline
Unified pipeline connecting all agents for comprehensive career analysis.
"""

from typing import Dict, List, Any
from app.agents.psychometric_agent import PsychometricAgent
from app.agents.pattern_analysis_agent import PatternAnalysisAgent
from app.agents.career_query_agent import CareerQueryAgent
from app.agents.rag_retrieval_agent import RAGRetrievalAgent
from app.agents.decision_agent import DecisionAgent


def run_career_dna_pipeline(assessment_data: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run the complete Career DNA pipeline through all agents.
    
    Flow:
    1. Psychometric Agent → Extract traits
    2. Pattern Analysis Agent → Detect patterns
    3. Career Query Agent → Generate career matches
    4. RAG Retrieval Agent → Retrieve relevant documents
    5. Decision Agent → Combine and recommend
    
    Args:
        assessment_data: {
            "assessment_type": "big_five_ocean" or "riasec",
            "answers": [{"question_id": "O1", "value": 4}, ...],
            "user_id": int
        }
        user_context: Optional user preferences and context
    
    Returns:
        {
            "personality": {
                "traits": {...},
                "dominant_traits": [...],
                "confidence": float
            },
            "top_careers": [
                {
                    "rank": int,
                    "career": str,
                    "match_score": float,
                    "description": str,
                    "skills": [...]
                }
            ],
            "confidence_scores": {
                "psychometric": float,
                "pattern": float,
                "career_query": float,
                "rag": float,
                "overall": float
            },
            "explanation": str,
            "action_plan": {...},
            "metadata": {...}
        }
    """
    if user_context is None:
        user_context = {}
    
    # Initialize all agents
    psychometric_agent = PsychometricAgent()
    pattern_agent = PatternAnalysisAgent()
    career_query_agent = CareerQueryAgent(use_rag=True)
    rag_agent = RAGRetrievalAgent(use_rag=True)
    decision_agent = DecisionAgent()
    
    # Step 1: Psychometric Agent - Extract traits
    psychometric_output = psychometric_agent.process(assessment_data)
    
    # Step 2: Pattern Analysis Agent - Detect patterns
    pattern_input = {
        "traits": psychometric_output.get("traits", {}),
        "user_id": assessment_data.get("user_id")
    }
    pattern_output = pattern_agent.process(pattern_input)
    
    # Step 3: Career Query Agent - Generate career matches
    career_query_input = {
        "traits": psychometric_output.get("traits", {}),
        "patterns": pattern_output.get("patterns", []),
        "holland_code": psychometric_output.get("holland_code", ""),
        "user_preferences": user_context
    }
    career_query_output = career_query_agent.process(career_query_input)
    
    # Step 4: RAG Retrieval Agent - Retrieve relevant documents
    rag_input = {
        "traits": psychometric_output.get("traits", {}),
        "patterns": pattern_output.get("patterns", []),
        "query": "careers matching personality profile",
        "k": 5
    }
    rag_output = rag_agent.process(rag_input)
    
    # Step 5: Decision Agent - Combine and recommend
    decision_input = {
        "psychometric_output": psychometric_output,
        "pattern_output": pattern_output,
        "career_query_output": career_query_output,
        "rag_output": rag_output,
        "user_context": user_context
    }
    decision_output = decision_agent.process(decision_input)
    
    # Build structured response
    personality = {
        "traits": psychometric_output.get("traits", {}),
        "dominant_traits": psychometric_output.get("dominant_traits", []),
        "trait_profile": psychometric_output.get("trait_profile", ""),
        "confidence": psychometric_output.get("confidence", 0.0)
    }
    
    top_careers = decision_output.get("recommendations", [])
    
    confidence_scores = {
        "psychometric": psychometric_output.get("confidence", 0.0),
        "pattern": 0.8 if pattern_output.get("patterns") else 0.5,
        "career_query": 0.8 if career_query_output.get("career_matches") else 0.5,
        "rag": 0.8 if rag_output.get("rag_enabled") else 0.0,
        "overall": decision_output.get("confidence", 0.0)
    }
    
    explanation = " ".join(decision_output.get("reasoning", []))
    
    return {
        "personality": personality,
        "top_careers": top_careers,
        "confidence_scores": confidence_scores,
        "explanation": explanation,
        "action_plan": decision_output.get("action_plan", {}),
        "metadata": {
            "assessment_type": assessment_data.get("assessment_type"),
            "user_id": assessment_data.get("user_id"),
            "pipeline_complete": True,
            "rag_enabled": rag_output.get("rag_enabled", False),
            "agent_outputs": {
                "psychometric": psychometric_output.get("agent"),
                "pattern": pattern_output.get("agent"),
                "career_query": career_query_output.get("agent"),
                "rag": rag_output.get("agent"),
                "decision": decision_output.get("agent")
            }
        }
    }


def run_career_dna_pipeline_from_profile(profile_data: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Run the Career DNA pipeline from an existing user profile.
    
    Args:
        profile_data: {
            "career_dna": {
                "personality": {"big_five": {...}},
                "interests": {"riasec": {...}, "holland_code": "RIS"}
            },
            "user_id": int
        }
        user_context: Optional user preferences and context
    
    Returns:
        Structured pipeline output
    """
    if user_context is None:
        user_context = {}
    
    # Initialize all agents
    psychometric_agent = PsychometricAgent()
    pattern_agent = PatternAnalysisAgent()
    career_query_agent = CareerQueryAgent(use_rag=True)
    rag_agent = RAGRetrievalAgent(use_rag=True)
    decision_agent = DecisionAgent()
    
    # Extract traits from profile
    career_dna = profile_data.get("career_dna", {})
    traits = {
        "big_five": career_dna.get("personality", {}).get("big_five", {}),
        "riasec": career_dna.get("interests", {}).get("riasec", {})
    }
    holland_code = career_dna.get("interests", {}).get("holland_code", "")
    
    # Step 1: Psychometric Agent - Get traits summary
    psychometric_output = psychometric_agent.get_traits_summary(profile_data)
    
    # Step 2: Pattern Analysis Agent - Detect patterns
    pattern_input = {
        "traits": traits,
        "user_id": profile_data.get("user_id")
    }
    pattern_output = pattern_agent.process(pattern_input)
    
    # Step 3: Career Query Agent - Generate career matches
    career_query_input = {
        "traits": traits,
        "patterns": pattern_output.get("patterns", []),
        "holland_code": holland_code,
        "user_preferences": user_context
    }
    career_query_output = career_query_agent.process(career_query_input)
    
    # Step 4: RAG Retrieval Agent - Retrieve relevant documents
    rag_input = {
        "traits": traits,
        "patterns": pattern_output.get("patterns", []),
        "query": "careers matching personality profile",
        "k": 5
    }
    rag_output = rag_agent.process(rag_input)
    
    # Step 5: Decision Agent - Combine and recommend
    decision_input = {
        "psychometric_output": psychometric_output,
        "pattern_output": pattern_output,
        "career_query_output": career_query_output,
        "rag_output": rag_output,
        "user_context": user_context
    }
    decision_output = decision_agent.process(decision_input)
    
    # Build structured response
    personality = {
        "traits": traits,
        "dominant_traits": psychometric_output.get("dominant_traits", []),
        "trait_profile": psychometric_output.get("trait_profile", ""),
        "confidence": psychometric_output.get("confidence", 0.0)
    }
    
    top_careers = decision_output.get("recommendations", [])
    
    confidence_scores = {
        "psychometric": psychometric_output.get("confidence", 0.0),
        "pattern": 0.8 if pattern_output.get("patterns") else 0.5,
        "career_query": 0.8 if career_query_output.get("career_matches") else 0.5,
        "rag": 0.8 if rag_output.get("rag_enabled") else 0.0,
        "overall": decision_output.get("confidence", 0.0)
    }
    
    explanation = " ".join(decision_output.get("reasoning", []))
    
    return {
        "personality": personality,
        "top_careers": top_careers,
        "confidence_scores": confidence_scores,
        "explanation": explanation,
        "action_plan": decision_output.get("action_plan", {}),
        "metadata": {
            "user_id": profile_data.get("user_id"),
            "profile_complete": True,
            "pipeline_complete": True,
            "rag_enabled": rag_output.get("rag_enabled", False),
            "agent_outputs": {
                "psychometric": psychometric_output.get("agent"),
                "pattern": pattern_output.get("agent"),
                "career_query": career_query_output.get("agent"),
                "rag": rag_output.get("agent"),
                "decision": decision_output.get("agent")
            }
        }
    }
