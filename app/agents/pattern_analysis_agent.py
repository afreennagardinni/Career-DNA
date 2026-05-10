"""
Pattern Analysis Agent
Detects patterns and correlations in psychometric data.
"""

from typing import Dict, List, Any, Tuple
from collections import Counter
import statistics


class PatternAnalysisAgent:
    """
    Agent responsible for detecting patterns in psychometric data.
    
    Flow: Input (trait data) → Process (pattern detection) → Output (patterns and insights)
    """
    
    def __init__(self):
        """Initialize the pattern analysis agent."""
        self.agent_name = "PatternAnalysisAgent"
        
        # Pattern detection thresholds
        self.dominant_threshold = 70.0
        self.weak_threshold = 30.0
        self.correlation_threshold = 0.6
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process trait data to detect patterns.
        
        Input:
            {
                "traits": {
                    "big_five": {...},
                    "riasec": {...}
                },
                "user_id": int,
                "historical_data": [...] (optional)
            }
        
        Process:
            1. Analyze trait distributions
            2. Detect trait correlations
            3. Identify patterns (e.g., high openness + high artistic)
            4. Generate insights
        
        Output:
            {
                "agent": "PatternAnalysisAgent",
                "patterns": [...],
                "correlations": {...},
                "insights": [...],
                "anomalies": [...],
                "metadata": {...}
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return self._error_response("Invalid input data")
        
        traits = input_data.get("traits", {})
        big_five = traits.get("big_five", {})
        riasec = traits.get("riasec", {})
        
        # Detect patterns
        patterns = self._detect_patterns(big_five, riasec)
        
        # Calculate correlations
        correlations = self._calculate_correlations(big_five, riasec)
        
        # Generate insights
        insights = self._generate_insights(big_five, riasec, patterns)
        
        # Detect anomalies
        anomalies = self._detect_anomalies(big_five, riasec)
        
        # Build response
        result = {
            "agent": self.agent_name,
            "patterns": patterns,
            "correlations": correlations,
            "insights": insights,
            "anomalies": anomalies,
            "metadata": {
                "trait_count": len(big_five) + len(riasec),
                "pattern_count": len(patterns),
                "processing_time": self._get_processing_time()
            }
        }
        
        return result
    
    def _detect_patterns(self, big_five: Dict, riasec: Dict) -> List[Dict[str, Any]]:
        """
        Detect patterns in trait combinations.
        
        Args:
            big_five: Big Five trait scores
            riasec: RIASEC interest scores
        
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Pattern 1: Creative Personality
        if big_five.get("openness", 0) >= self.dominant_threshold:
            if riasec.get("artistic", 0) >= self.dominant_threshold:
                patterns.append({
                    "type": "creative_personality",
                    "description": "High openness combined with strong artistic interests",
                    "traits": ["openness", "artistic"],
                    "strength": (big_five["openness"] + riasec["artistic"]) / 200
                })
        
        # Pattern 2: Analytical Thinker
        if big_five.get("conscientiousness", 0) >= self.dominant_threshold:
            if riasec.get("investigative", 0) >= self.dominant_threshold:
                patterns.append({
                    "type": "analytical_thinker",
                    "description": "High conscientiousness with strong investigative interests",
                    "traits": ["conscientiousness", "investigative"],
                    "strength": (big_five["conscientiousness"] + riasec["investigative"]) / 200
                })
        
        # Pattern 3: Social Leader
        if big_five.get("extraversion", 0) >= self.dominant_threshold:
            if riasec.get("social", 0) >= self.dominant_threshold:
                patterns.append({
                    "type": "social_leader",
                    "description": "High extraversion with strong social interests",
                    "traits": ["extraversion", "social"],
                    "strength": (big_five["extraversion"] + riasec["social"]) / 200
                })
        
        # Pattern 4: Practical Problem Solver
        if big_five.get("conscientiousness", 0) >= self.dominant_threshold:
            if riasec.get("realistic", 0) >= self.dominant_threshold:
                patterns.append({
                    "type": "practical_problem_solver",
                    "description": "High conscientiousness with strong realistic interests",
                    "traits": ["conscientiousness", "realistic"],
                    "strength": (big_five["conscientiousness"] + riasec["realistic"]) / 200
                })
        
        # Pattern 5: Entrepreneurial
        if big_five.get("extraversion", 0) >= self.dominant_threshold:
            if riasec.get("enterprising", 0) >= self.dominant_threshold:
                patterns.append({
                    "type": "entrepreneurial",
                    "description": "High extraversion with strong enterprising interests",
                    "traits": ["extraversion", "enterprising"],
                    "strength": (big_five["extraversion"] + riasec["enterprising"]) / 200
                })
        
        # Pattern 6: Balanced Profile
        all_traits = list(big_five.values()) + list(riasec.values())
        if all_traits:
            std_dev = statistics.stdev(all_traits) if len(all_traits) > 1 else 0
            if std_dev < 15:  # Low variance indicates balanced profile
                patterns.append({
                    "type": "balanced_profile",
                    "description": "Well-balanced across all traits and interests",
                    "traits": list(big_five.keys()) + list(riasec.keys()),
                    "strength": 1.0 - (std_dev / 50)
                })
        
        # Sort by strength
        patterns.sort(key=lambda x: x["strength"], reverse=True)
        
        return patterns
    
    def _calculate_correlations(self, big_five: Dict, riasec: Dict) -> Dict[str, float]:
        """
        Calculate correlations between personality traits and interests.
        
        Args:
            big_five: Big Five trait scores
            riasec: RIASEC interest scores
        
        Returns:
            Dict of correlation scores
        """
        correlations = {}
        
        # Known correlations based on psychological research
        correlation_matrix = {
            "openness": {"artistic": 0.7, "investigative": 0.6, "social": 0.3},
            "conscientiousness": {"conventional": 0.6, "investigative": 0.5, "realistic": 0.4},
            "extraversion": {"enterprising": 0.7, "social": 0.6, "conventional": 0.2},
            "agreeableness": {"social": 0.7, "artistic": 0.4, "enterprising": 0.1},
            "neuroticism": {"artistic": 0.3, "social": 0.2, "realistic": -0.1}
        }
        
        for personality_trait, interest_correlations in correlation_matrix.items():
            personality_score = big_five.get(personality_trait, 0) / 100  # Normalize to 0-1
            
            for interest, base_correlation in interest_correlations.items():
                interest_score = riasec.get(interest, 0) / 100  # Normalize to 0-1
                
                # Calculate actual correlation based on user's scores
                if personality_score > 0.5 and interest_score > 0.5:
                    actual_correlation = base_correlation * min(personality_score, interest_score) * 2
                elif personality_score < 0.3 and interest_score < 0.3:
                    actual_correlation = base_correlation * 0.5
                else:
                    actual_correlation = base_correlation * 0.3
                
                correlation_key = f"{personality_trait}_{interest}"
                correlations[correlation_key] = round(actual_correlation, 2)
        
        return correlations
    
    def _generate_insights(self, big_five: Dict, riasec: Dict, patterns: List) -> List[str]:
        """
        Generate insights based on patterns and trait scores.
        
        Args:
            big_five: Big Five trait scores
            riasec: RIASEC interest scores
            patterns: Detected patterns
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Insight 1: Dominant traits
        dominant_bf = [t for t, s in big_five.items() if s >= self.dominant_threshold]
        if dominant_bf:
            insights.append(f"Strong {', '.join(dominant_bf)} traits suggest natural aptitude in related areas")
        
        # Insight 2: Interest alignment
        top_interests = sorted(riasec.items(), key=lambda x: x[1], reverse=True)[:2]
        if top_interests:
            insights.append(f"Primary interests in {top_interests[0][0]} and {top_interests[1][0]} indicate career preferences")
        
        # Insight 3: Pattern-based insights
        for pattern in patterns[:3]:  # Top 3 patterns
            insights.append(f"Pattern detected: {pattern['description']}")
        
        # Insight 4: Emotional stability
        neuroticism = big_five.get("neuroticism", 50)
        if neuroticism <= 30:
            insights.append("High emotional stability suggests resilience in challenging work environments")
        elif neuroticism >= 70:
            insights.append("Emotional sensitivity may benefit roles requiring empathy and emotional intelligence")
        
        # Insight 5: Work style
        extraversion = big_five.get("extraversion", 50)
        if extraversion >= 70:
            insights.append("High extraversion indicates preference for collaborative, people-oriented work")
        elif extraversion <= 30:
            insights.append("Lower extraversion suggests comfort with independent, focused work")
        
        return insights
    
    def _detect_anomalies(self, big_five: Dict, riasec: Dict) -> List[Dict[str, Any]]:
        """
        Detect unusual or contradictory trait combinations.
        
        Args:
            big_five: Big Five trait scores
            riasec: RIASEC interest scores
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Anomaly 1: High openness + low artistic (unusual)
        if big_five.get("openness", 0) >= self.dominant_threshold:
            if riasec.get("artistic", 0) <= self.weak_threshold:
                anomalies.append({
                    "type": "mismatch",
                    "description": "High openness but low artistic interest",
                    "traits": ["openness", "artistic"],
                    "severity": "low"
                })
        
        # Anomaly 2: High extraversion + low social (unusual)
        if big_five.get("extraversion", 0) >= self.dominant_threshold:
            if riasec.get("social", 0) <= self.weak_threshold:
                anomalies.append({
                    "type": "mismatch",
                    "description": "High extraversion but low social interest",
                    "traits": ["extraversion", "social"],
                    "severity": "low"
                })
        
        # Anomaly 3: Extreme neuroticism + high enterprising (potential stress)
        if big_five.get("neuroticism", 0) >= self.dominant_threshold:
            if riasec.get("enterprising", 0) >= self.dominant_threshold:
                anomalies.append({
                    "type": "stress_risk",
                    "description": "High neuroticism with enterprising interests may indicate stress risk",
                    "traits": ["neuroticism", "enterprising"],
                    "severity": "medium"
                })
        
        # Anomaly 4: All traits near extreme (potential response bias)
        all_traits = list(big_five.values()) + list(riasec.values())
        if all_traits:
            avg = sum(all_traits) / len(all_traits)
            if avg >= 4.5 or avg <= 1.5:
                anomalies.append({
                    "type": "response_bias",
                    "description": "Extreme responses across all traits may indicate response bias",
                    "traits": list(big_five.keys()) + list(riasec.keys()),
                    "severity": "high"
                })
        
        return anomalies
    
    def _validate_input(self, input_data: Dict) -> bool:
        """
        Validate input data structure.
        
        Args:
            input_data: Input dictionary
        
        Returns:
            bool: True if valid
        """
        return "traits" in input_data
    
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
            "patterns": [],
            "correlations": {},
            "insights": [],
            "anomalies": []
        }
    
    def compare_with_population(self, user_traits: Dict, population_data: List[Dict]) -> Dict[str, Any]:
        """
        Compare user traits with population norms.
        
        Args:
            user_traits: User's trait scores
            population_data: List of population trait data
        
        Returns:
            Dict with comparison results
        """
        if not population_data:
            return self._error_response("No population data available")
        
        comparison = {
            "agent": self.agent_name,
            "percentiles": {},
            "above_average": [],
            "below_average": []
        }
        
        # Calculate percentiles for each trait
        for trait, user_score in user_traits.items():
            population_scores = [p.get(trait, 50) for p in population_data]
            percentile = self._calculate_percentile(user_score, population_scores)
            comparison["percentiles"][trait] = percentile
            
            if percentile >= 70:
                comparison["above_average"].append(trait)
            elif percentile <= 30:
                comparison["below_average"].append(trait)
        
        return comparison
    
    def _calculate_percentile(self, value: float, distribution: List[float]) -> float:
        """
        Calculate percentile rank of a value in a distribution.
        
        Args:
            value: Value to calculate percentile for
            distribution: List of values representing the distribution
        
        Returns:
            float: Percentile rank (0-100)
        """
        if not distribution:
            return 50.0
        
        count_below = sum(1 for v in distribution if v < value)
        percentile = (count_below / len(distribution)) * 100
        return round(percentile, 1)
