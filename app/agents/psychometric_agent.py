"""
Psychometric Agent
Extracts and processes psychometric traits from user assessment data.
"""

from typing import Dict, List, Any
from app.services.scoring_service import ScoringService


class PsychometricAgent:
    """
    Agent responsible for processing psychometric assessment data.
    
    Flow: Input (raw assessment data) → Process (trait extraction) → Output (structured traits)
    """
    
    def __init__(self):
        """Initialize the psychometric agent with scoring service."""
        self.scoring_service = ScoringService()
        self.agent_name = "PsychometricAgent"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process psychometric assessment data to extract traits.
        
        Input:
            {
                "assessment_type": "big_five_ocean" or "riasec",
                "answers": [{"question_id": "O1", "value": 4}, ...],
                "user_id": int
            }
        
        Process:
            1. Validate input data
            2. Score assessment using scoring service
            3. Extract dominant traits
            4. Normalize and structure output
        
        Output:
            {
                "agent": "PsychometricAgent",
                "traits": {
                    "big_five": {...},
                    "riasec": {...}
                },
                "dominant_traits": [...],
                "confidence": float,
                "metadata": {...}
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return self._error_response("Invalid input data")
        
        assessment_type = input_data.get("assessment_type")
        answers = input_data.get("answers", [])
        
        # Process based on assessment type
        if assessment_type == "big_five_ocean":
            result = self._process_big_five(answers)
        elif assessment_type == "riasec":
            result = self._process_riasec(answers)
        else:
            return self._error_response(f"Unknown assessment type: {assessment_type}")
        
        # Add agent metadata
        result["agent"] = self.agent_name
        result["confidence"] = self._calculate_confidence(answers, result)
        result["metadata"] = {
            "assessment_type": assessment_type,
            "answer_count": len(answers),
            "processing_time": self._get_processing_time()
        }
        
        return result
    
    def _process_big_five(self, answers: List[Dict]) -> Dict[str, Any]:
        """
        Process Big Five assessment.
        
        Args:
            answers: List of answer dictionaries
        
        Returns:
            Dict with Big Five traits
        """
        scores = self.scoring_service.score_big_five(answers)
        dominant_traits = self.scoring_service._get_dominant_traits(scores)
        
        return {
            "traits": {
                "big_five": scores
            },
            "dominant_traits": dominant_traits,
            "trait_profile": self._generate_trait_profile(scores)
        }
    
    def _process_riasec(self, answers: List[Dict]) -> Dict[str, Any]:
        """
        Process RIASEC assessment.
        
        Args:
            answers: List of answer dictionaries
        
        Returns:
            Dict with RIASEC interests
        """
        result = self.scoring_service.score_riasec(answers)
        
        return {
            "traits": {
                "riasec": result["scores"]
            },
            "holland_code": result["holland_code"],
            "top_interests": result["top_interests"],
            "interest_profile": self._generate_interest_profile(result["scores"])
        }
    
    def _generate_trait_profile(self, scores: Dict[str, float]) -> str:
        """
        Generate a human-readable trait profile description.
        
        Args:
            scores: Big Five trait scores
        
        Returns:
            str: Profile description
        """
        traits = []
        
        if scores.get("openness", 0) >= 70:
            traits.append("creative and curious")
        elif scores.get("openness", 0) <= 30:
            traits.append("practical and traditional")
        
        if scores.get("conscientiousness", 0) >= 70:
            traits.append("organized and disciplined")
        elif scores.get("conscientiousness", 0) <= 30:
            traits.append("spontaneous and flexible")
        
        if scores.get("extraversion", 0) >= 70:
            traits.append("outgoing and energetic")
        elif scores.get("extraversion", 0) <= 30:
            traits.append("reserved and introspective")
        
        if scores.get("agreeableness", 0) >= 70:
            traits.append("cooperative and empathetic")
        elif scores.get("agreeableness", 0) <= 30:
            traits.append("competitive and assertive")
        
        if scores.get("neuroticism", 0) >= 70:
            traits.append("emotionally sensitive")
        elif scores.get("neuroticism", 0) <= 30:
            traits.append("emotionally stable")
        
        return "A ".join(traits) if traits else "A balanced individual"
    
    def _generate_interest_profile(self, scores: Dict[str, float]) -> str:
        """
        Generate a human-readable interest profile description.
        
        Args:
            scores: RIASEC interest scores
        
        Returns:
            str: Profile description
        """
        top_interests = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        interest_names = {
            "realistic": "hands-on work",
            "investigative": "problem-solving",
            "artistic": "creative expression",
            "social": "helping others",
            "enterprising": "leadership",
            "conventional": "structured tasks"
        }
        
        descriptions = [interest_names.get(interest, interest) for interest, score in top_interests]
        return f"Interested in {descriptions[0]} and {descriptions[1]}"
    
    def _validate_input(self, input_data: Dict) -> bool:
        """
        Validate input data structure.
        
        Args:
            input_data: Input dictionary
        
        Returns:
            bool: True if valid
        """
        required_fields = ["assessment_type", "answers"]
        return all(field in input_data for field in required_fields)
    
    def _calculate_confidence(self, answers: List[Dict], result: Dict) -> float:
        """
        Calculate confidence score based on answer completeness.
        
        Args:
            answers: List of answers
            result: Processing result
        
        Returns:
            float: Confidence score (0-1)
        """
        # Base confidence on answer count vs expected
        expected_count = 20  # Standard assessment size
        completeness = min(len(answers) / expected_count, 1.0)
        
        # Adjust based on score distribution
        if "traits" in result:
            traits = result["traits"].get("big_five", result["traits"].get("riasec", {}))
            if traits:
                avg_score = sum(traits.values()) / len(traits)
                # Penalize extreme responses (all 1s or all 5s)
                if avg_score < 1.5 or avg_score > 4.5:
                    completeness *= 0.8
        
        return round(completeness, 2)
    
    def _get_processing_time(self) -> str:
        """
        Get simulated processing time.
        
        Returns:
            str: Processing time string
        """
        import time
        return f"{time.time():.3f}s"
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """
        Generate error response.
        
        Args:
            message: Error message
        
        Returns:
            Dict: Error response
        """
        return {
            "agent": self.agent_name,
            "error": True,
            "message": message,
            "traits": {},
            "dominant_traits": [],
            "confidence": 0.0
        }
    
    def get_traits_summary(self, profile_data: Dict) -> Dict[str, Any]:
        """
        Get a summary of traits from profile data.
        
        Args:
            profile_data: User's profile data with career_dna
        
        Returns:
            Dict: Traits summary
        """
        if not profile_data or "career_dna" not in profile_data:
            return self._error_response("No profile data available")
        
        career_dna = profile_data["career_dna"]
        summary = {
            "agent": self.agent_name,
            "personality": career_dna.get("personality", {}),
            "interests": career_dna.get("interests", {}),
            "has_complete_profile": "personality" in career_dna and "interests" in career_dna
        }
        
        return summary
