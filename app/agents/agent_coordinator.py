"""
Agent Coordinator
Orchestrates the multi-agent system for Career DNA analysis.
"""

from typing import Dict, List, Any, Optional
from app.agents.psychometric_agent import PsychometricAgent
from app.agents.pattern_analysis_agent import PatternAnalysisAgent
from app.agents.career_query_agent import CareerQueryAgent
from app.agents.decision_agent import DecisionAgent


class AgentCoordinator:
    """
    Coordinates the multi-agent system for comprehensive career DNA analysis.
    
    Flow:
    1. Psychometric Agent → Extract traits
    2. Pattern Analysis Agent → Detect patterns
    3. Career Query Agent → Generate queries
    4. Decision Agent → Combine and recommend
    """
    
    def __init__(self):
        """Initialize the agent coordinator with all agents."""
        self.psychometric_agent = PsychometricAgent()
        self.pattern_agent = PatternAnalysisAgent()
        self.career_query_agent = CareerQueryAgent()
        self.decision_agent = DecisionAgent()
        
        self.agent_name = "AgentCoordinator"
    
    def process_assessment(self, assessment_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a complete assessment through the multi-agent pipeline.
        
        Args:
            assessment_data: {
                "assessment_type": "big_five_ocean" or "riasec",
                "answers": [{"question_id": "O1", "value": 4}, ...],
                "user_id": int
            }
            user_context: Optional user preferences and context
        
        Returns:
            Dict with complete analysis from all agents
        """
        if user_context is None:
            user_context = {}
        
        # Step 1: Psychometric Agent - Extract traits
        psychometric_output = self.psychometric_agent.process(assessment_data)
        
        # Step 2: Pattern Analysis Agent - Detect patterns
        pattern_input = {
            "traits": psychometric_output.get("traits", {}),
            "user_id": assessment_data.get("user_id")
        }
        pattern_output = self.pattern_agent.process(pattern_input)
        
        # Step 3: Career Query Agent - Generate queries
        career_query_input = {
            "traits": psychometric_output.get("traits", {}),
            "patterns": pattern_output.get("patterns", []),
            "holland_code": psychometric_output.get("holland_code", ""),
            "user_preferences": user_context
        }
        career_query_output = self.career_query_agent.process(career_query_input)
        
        # Step 4: Decision Agent - Combine and recommend
        decision_input = {
            "psychometric_output": psychometric_output,
            "pattern_output": pattern_output,
            "career_query_output": career_query_output,
            "user_context": user_context
        }
        decision_output = self.decision_agent.process(decision_input)
        
        # Build complete response
        result = {
            "coordinator": self.agent_name,
            "pipeline": {
                "psychometric_agent": psychometric_output,
                "pattern_analysis_agent": pattern_output,
                "career_query_agent": career_query_output,
                "decision_agent": decision_output
            },
            "final_recommendations": decision_output.get("recommendations", []),
            "action_plan": decision_output.get("action_plan", {}),
            "overall_confidence": decision_output.get("confidence", 0.0),
            "metadata": {
                "assessment_type": assessment_data.get("assessment_type"),
                "user_id": assessment_data.get("user_id"),
                "pipeline_complete": True,
                "processing_time": self._get_processing_time()
            }
        }
        
        return result
    
    def process_complete_profile(self, profile_data: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a complete user profile with both Big Five and RIASEC data.
        
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
            Dict with complete analysis from all agents
        """
        if user_context is None:
            user_context = {}
        
        # Extract traits from profile
        career_dna = profile_data.get("career_dna", {})
        traits = {
            "big_five": career_dna.get("personality", {}).get("big_five", {}),
            "riasec": career_dna.get("interests", {}).get("riasec", {})
        }
        holland_code = career_dna.get("interests", {}).get("holland_code", "")
        
        # Step 1: Psychometric Agent - Get traits summary
        psychometric_output = self.psychometric_agent.get_traits_summary(profile_data)
        
        # Step 2: Pattern Analysis Agent - Detect patterns
        pattern_input = {
            "traits": traits,
            "user_id": profile_data.get("user_id")
        }
        pattern_output = self.pattern_agent.process(pattern_input)
        
        # Step 3: Career Query Agent - Generate queries
        career_query_input = {
            "traits": traits,
            "patterns": pattern_output.get("patterns", []),
            "holland_code": holland_code,
            "user_preferences": user_context
        }
        career_query_output = self.career_query_agent.process(career_query_input)
        
        # Step 4: Decision Agent - Combine and recommend
        decision_input = {
            "psychometric_output": psychometric_output,
            "pattern_output": pattern_output,
            "career_query_output": career_query_output,
            "user_context": user_context
        }
        decision_output = self.decision_agent.process(decision_input)
        
        # Build complete response
        result = {
            "coordinator": self.agent_name,
            "pipeline": {
                "psychometric_agent": psychometric_output,
                "pattern_analysis_agent": pattern_output,
                "career_query_agent": career_query_output,
                "decision_agent": decision_output
            },
            "final_recommendations": decision_output.get("recommendations", []),
            "action_plan": decision_output.get("action_plan", {}),
            "overall_confidence": decision_output.get("confidence", 0.0),
            "metadata": {
                "user_id": profile_data.get("user_id"),
                "profile_complete": True,
                "pipeline_complete": True,
                "processing_time": self._get_processing_time()
            }
        }
        
        return result
    
    def run_agent_pipeline(self, input_data: Dict[str, Any], pipeline_type: str = "assessment") -> Dict[str, Any]:
        """
        Run the agent pipeline with specified type.
        
        Args:
            input_data: Input data for the pipeline
            pipeline_type: "assessment" or "profile"
        
        Returns:
            Dict with pipeline results
        """
        if pipeline_type == "assessment":
            return self.process_assessment(input_data)
        elif pipeline_type == "profile":
            return self.process_complete_profile(input_data)
        else:
            return {
                "coordinator": self.agent_name,
                "error": True,
                "message": f"Unknown pipeline type: {pipeline_type}"
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.
        
        Returns:
            Dict with agent status information
        """
        return {
            "coordinator": self.agent_name,
            "agents": {
                "psychometric_agent": {
                    "name": self.psychometric_agent.agent_name,
                    "status": "active",
                    "description": "Extracts and processes psychometric traits"
                },
                "pattern_analysis_agent": {
                    "name": self.pattern_agent.agent_name,
                    "status": "active",
                    "description": "Detects patterns and correlations in trait data"
                },
                "career_query_agent": {
                    "name": self.career_query_agent.agent_name,
                    "status": "active",
                    "description": "Generates career queries and matches"
                },
                "decision_agent": {
                    "name": self.decision_agent.agent_name,
                    "status": "active",
                    "description": "Combines outputs and makes final recommendations"
                }
            },
            "pipeline_flow": [
                "1. Psychometric Agent: Extract traits from assessment data",
                "2. Pattern Analysis Agent: Detect patterns in trait combinations",
                "3. Career Query Agent: Generate career matches and queries",
                "4. Decision Agent: Synthesize outputs and create recommendations"
            ]
        }
    
    def _get_processing_time(self) -> str:
        """
        Get total processing time.
        
        Returns:
            str: Processing time string
        """
        import time
        return f"{time.time():.3f}s"
