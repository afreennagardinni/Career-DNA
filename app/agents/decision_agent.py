"""
Decision Agent
Combines outputs from all agents to make final career recommendations.
"""

from typing import Dict, List, Any
import statistics


class DecisionAgent:
    """
    Agent responsible for combining agent outputs and making final decisions.
    
    Flow: Input (agent outputs) → Process (decision synthesis) → Output (final recommendations)
    """
    
    def __init__(self):
        """Initialize the decision agent."""
        self.agent_name = "DecisionAgent"
        
        # Decision weights
        self.weights = {
            "psychometric": 0.3,
            "pattern": 0.25,
            "career_query": 0.45
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process outputs from all agents to make final recommendations.
        
        Input:
            {
                "psychometric_output": {...},
                "pattern_output": {...},
                "career_query_output": {...},
                "user_context": {...} (optional)
            }
        
        Process:
            1. Validate and normalize agent outputs
            2. Combine scores using weighted algorithm
            3. Apply decision rules
            4. Generate final recommendations
            5. Create action plan
        
        Output:
            {
                "agent": "DecisionAgent",
                "recommendations": [...],
                "action_plan": {...},
                "confidence": float,
                "reasoning": [...],
                "metadata": {...}
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return self._error_response("Invalid input data")
        
        psychometric_output = input_data.get("psychometric_output", {})
        pattern_output = input_data.get("pattern_output", {})
        career_query_output = input_data.get("career_query_output", {})
        user_context = input_data.get("user_context", {})
        
        # Normalize and validate outputs
        normalized_outputs = self._normalize_outputs(
            psychometric_output,
            pattern_output,
            career_query_output
        )
        
        # Combine career matches
        combined_careers = self._combine_career_matches(
            normalized_outputs["psychometric"],
            normalized_outputs["pattern"],
            normalized_outputs["career_query"]
        )
        
        # Apply decision rules
        filtered_careers = self._apply_decision_rules(
            combined_careers,
            normalized_outputs["pattern"],
            user_context
        )
        
        # Generate final recommendations
        recommendations = self._generate_recommendations(
            filtered_careers,
            normalized_outputs,
            user_context
        )
        
        # Create action plan
        action_plan = self._create_action_plan(
            recommendations,
            normalized_outputs,
            user_context
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            normalized_outputs,
            recommendations,
            action_plan
        )
        
        # Calculate overall confidence
        confidence = self._calculate_overall_confidence(
            normalized_outputs,
            recommendations
        )
        
        # Build response
        result = {
            "agent": self.agent_name,
            "recommendations": recommendations,
            "action_plan": action_plan,
            "confidence": confidence,
            "reasoning": reasoning,
            "metadata": {
                "career_count": len(recommendations),
                "agent_outputs": list(normalized_outputs.keys()),
                "processing_time": self._get_processing_time()
            }
        }
        
        return result
    
    def _normalize_outputs(self, psychometric: Dict, pattern: Dict, career_query: Dict) -> Dict[str, Dict]:
        """
        Normalize and validate agent outputs.
        
        Args:
            psychometric: Psychometric agent output
            pattern: Pattern analysis agent output
            career_query: Career query agent output
        
        Returns:
            Dict of normalized outputs
        """
        normalized = {}
        
        # Normalize psychometric output
        normalized["psychometric"] = {
            "traits": psychometric.get("traits", {}),
            "dominant_traits": psychometric.get("dominant_traits", []),
            "confidence": psychometric.get("confidence", 0.5),
            "valid": not psychometric.get("error", False)
        }
        
        # Normalize pattern output
        normalized["pattern"] = {
            "patterns": pattern.get("patterns", []),
            "insights": pattern.get("insights", []),
            "anomalies": pattern.get("anomalies", []),
            "correlations": pattern.get("correlations", {}),
            "valid": not pattern.get("error", False)
        }
        
        # Normalize career query output
        normalized["career_query"] = {
            "career_matches": career_query.get("career_matches", []),
            "search_terms": career_query.get("search_terms", []),
            "queries": career_query.get("queries", []),
            "valid": not career_query.get("error", False)
        }
        
        return normalized
    
    def _combine_career_matches(self, psychometric: Dict, pattern: Dict, career_query: Dict) -> List[Dict[str, Any]]:
        """
        Combine career matches from all agents.
        
        Args:
            psychometric: Normalized psychometric output
            pattern: Normalized pattern output
            career_query: Normalized career query output
        
        Returns:
            List of combined career matches
        """
        career_map = {}
        
        # Start with career query matches
        for career in career_query.get("career_matches", []):
            career_map[career["title"]] = {
                "title": career["title"],
                "category": career.get("category", ""),
                "description": career.get("description", ""),
                "skills": career.get("skills", []),
                "base_score": career["match_score"],
                "pattern_bonus": 0,
                "psychometric_bonus": 0,
                "insights": []
            }
        
        # Add pattern bonuses
        for pattern_data in pattern.get("patterns", []):
            pattern_type = pattern_data["type"]
            pattern_strength = pattern_data["strength"]
            
            for career_title, career_data in career_map.items():
                # Check if pattern matches career
                if self._pattern_matches_career(pattern_type, career_title):
                    career_data["pattern_bonus"] += pattern_strength * 20
                    career_data["insights"].append(f"Pattern match: {pattern_type}")
        
        # Add psychometric bonuses
        dominant_traits = psychometric.get("dominant_traits", [])
        for career_title, career_data in career_map.items():
            if self._traits_match_career(dominant_traits, career_title):
                career_data["psychometric_bonus"] += 15
                career_data["insights"].append(f"Trait alignment: {', '.join(dominant_traits)}")
        
        # Calculate combined scores
        combined_matches = []
        for career_title, career_data in career_map.items():
            combined_score = (
                career_data["base_score"] * 0.6 +
                career_data["pattern_bonus"] * 0.2 +
                career_data["psychometric_bonus"] * 0.2
            )
            career_data["combined_score"] = round(combined_score, 2)
            combined_matches.append(career_data)
        
        # Sort by combined score
        combined_matches.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return combined_matches
    
    def _pattern_matches_career(self, pattern_type: str, career_title: str) -> bool:
        """
        Check if a pattern matches a career.
        
        Args:
            pattern_type: Pattern type
            career_title: Career title
        
        Returns:
            bool: True if matches
        """
        pattern_career_map = {
            "creative_personality": ["Designer", "Artist", "Writer", "UX", "Creative"],
            "analytical_thinker": ["Data Scientist", "Analyst", "Researcher", "Scientist", "Engineer"],
            "social_leader": ["Manager", "HR", "Team Lead", "Director", "Consultant"],
            "practical_problem_solver": ["Developer", "Engineer", "Technician", "Specialist"],
            "entrepreneurial": ["Founder", "Entrepreneur", "Business", "Sales", "Marketing"]
        }
        
        if pattern_type in pattern_career_map:
            related_careers = pattern_career_map[pattern_type]
            return any(career in career_title for career in related_careers)
        
        return False
    
    def _traits_match_career(self, traits: List[str], career_title: str) -> bool:
        """
        Check if traits match a career.
        
        Args:
            traits: List of dominant traits
            career_title: Career title
        
        Returns:
            bool: True if matches
        """
        trait_career_map = {
            "openness": ["Designer", "Artist", "Creative", "UX", "Product"],
            "conscientiousness": ["Engineer", "Analyst", "Manager", "Developer", "Scientist"],
            "extraversion": ["Manager", "Sales", "Marketing", "Leader", "Director"],
            "agreeableness": ["HR", "Teacher", "Counselor", "Social", "Psychologist"],
            "neuroticism": []  # Neuroticism doesn't directly map to careers
        }
        
        for trait in traits:
            if trait in trait_career_map:
                related_careers = trait_career_map[trait]
                if any(career in career_title for career in related_careers):
                    return True
        
        return False
    
    def _apply_decision_rules(self, careers: List[Dict], pattern_output: Dict, user_context: Dict) -> List[Dict]:
        """
        Apply decision rules to filter and rank careers.
        
        Args:
            careers: Combined career matches
            pattern_output: Pattern analysis output
            user_context: User context and preferences
        
        Returns:
            List of filtered careers
        """
        filtered = []
        
        # Rule 1: Minimum score threshold
        min_score = user_context.get("min_score", 50)
        
        # Rule 2: Check for anomalies that might disqualify certain careers
        anomalies = pattern_output.get("anomalies", [])
        has_stress_risk = any(a["type"] == "stress_risk" for a in anomalies)
        
        for career in careers:
            # Apply minimum score rule
            if career["combined_score"] < min_score:
                continue
            
            # Apply stress risk rule
            if has_stress_risk and "Manager" in career["title"]:
                career["warning"] = "High-stress role - consider work-life balance"
            
            # Apply user preferences
            preferred_categories = user_context.get("preferred_categories", [])
            if preferred_categories and career["category"] not in preferred_categories:
                career["combined_score"] *= 0.9  # Penalize non-preferred categories
            
            filtered.append(career)
        
        # Re-sort after applying rules
        filtered.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return filtered[:5]  # Return top 5
    
    def _generate_recommendations(self, careers: List[Dict], outputs: Dict, context: Dict) -> List[Dict[str, Any]]:
        """
        Generate final career recommendations.
        
        Args:
            careers: Filtered career matches
            outputs: Normalized agent outputs
            context: User context
        
        Returns:
            List of detailed recommendations
        """
        recommendations = []
        
        for i, career in enumerate(careers):
            recommendation = {
                "rank": i + 1,
                "career": career["title"],
                "category": career["category"],
                "match_score": career["combined_score"],
                "description": career["description"],
                "key_skills": career["skills"],
                "reasoning": career["insights"],
                "next_steps": self._generate_next_steps(career, outputs, context),
                "warning": career.get("warning", None)
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_next_steps(self, career: Dict, outputs: Dict, context: Dict) -> List[str]:
        """
        Generate next steps for a career recommendation.
        
        Args:
            career: Career data
            outputs: Normalized agent outputs
            context: User context
        
        Returns:
            List of next step strings
        """
        steps = []
        
        # Step 1: Research
        steps.append(f"Research {career['title']} role and requirements")
        
        # Step 2: Skills assessment
        current_skills = context.get("current_skills", [])
        required_skills = career["skills"]
        skill_gaps = [s for s in required_skills if s not in current_skills]
        
        if skill_gaps:
            steps.append(f"Develop skills in: {', '.join(skill_gaps[:3])}")
        
        # Step 3: Networking
        steps.append(f"Network with professionals in {career['category']}")
        
        # Step 4: Experience
        steps.append(f"Gain relevant experience through projects or internships")
        
        # Step 5: Application
        steps.append(f"Apply for {career['title']} positions when ready")
        
        return steps
    
    def _create_action_plan(self, recommendations: List[Dict], outputs: Dict, context: Dict) -> Dict[str, Any]:
        """
        Create a comprehensive action plan.
        
        Args:
            recommendations: Career recommendations
            outputs: Normalized agent outputs
            context: User context
        
        Returns:
            Dict with action plan
        """
        if not recommendations:
            return {
                "short_term": [],
                "medium_term": [],
                "long_term": [],
                "resources": []
            }
        
        top_career = recommendations[0]
        
        action_plan = {
            "short_term": [
                f"Complete skills assessment for {top_career['career']}",
                "Research top 3 recommended careers in detail",
                "Identify skill gaps and create learning plan",
                "Update resume and LinkedIn profile"
            ],
            "medium_term": [
                f"Develop key skills for {top_career['career']}",
                "Build portfolio with relevant projects",
                "Network with industry professionals",
                "Consider certifications or courses"
            ],
            "long_term": [
                f"Apply for {top_career['career']} positions",
                "Continue professional development",
                "Seek mentorship in chosen field",
                "Evaluate career progression and adjust goals"
            ],
            "resources": self._generate_resources(top_career, outputs)
        }
        
        return action_plan
    
    def _generate_resources(self, career: Dict, outputs: Dict) -> List[Dict[str, str]]:
        """
        Generate learning resources.
        
        Args:
            career: Career recommendation
            outputs: Normalized agent outputs
        
        Returns:
            List of resource dictionaries
        """
        resources = []
        
        # Platform-specific resources
        category_resources = {
            "Technology": [
                {"name": "Coursera", "type": "online_courses", "url": "https://coursera.org"},
                {"name": "GitHub", "type": "projects", "url": "https://github.com"},
                {"name": "Stack Overflow", "type": "community", "url": "https://stackoverflow.com"}
            ],
            "Design": [
                {"name": "Dribbble", "type": "portfolio", "url": "https://dribbble.com"},
                {"name": "Behance", "type": "portfolio", "url": "https://behance.net"},
                {"name": "Figma", "type": "tools", "url": "https://figma.com"}
            ],
            "Business": [
                {"name": "LinkedIn Learning", "type": "courses", "url": "https://linkedin.com/learning"},
                {"name": "Harvard Business Review", "type": "articles", "url": "https://hbr.org"},
                {"name": "Meetup", "type": "networking", "url": "https://meetup.com"}
            ],
            "Finance": [
                {"name": "CFA Institute", "type": "certification", "url": "https://cfainstitute.org"},
                {"name": "Bloomberg", "type": "news", "url": "https://bloomberg.com"},
                {"name": "Investopedia", "type": "education", "url": "https://investopedia.com"}
            ]
        }
        
        category = career.get("category", "Technology")
        if category in category_resources:
            resources.extend(category_resources[category])
        
        # General resources
        resources.extend([
            {"name": "Glassdoor", "type": "salary_info", "url": "https://glassdoor.com"},
            {"name": "Indeed", "type": "job_search", "url": "https://indeed.com"}
        ])
        
        return resources
    
    def _generate_reasoning(self, outputs: Dict, recommendations: List[Dict], action_plan: Dict) -> List[str]:
        """
        Generate reasoning for the recommendations.
        
        Args:
            outputs: Normalized agent outputs
            recommendations: Career recommendations
            action_plan: Action plan
        
        Returns:
            List of reasoning strings
        """
        reasoning = []
        
        # Psychometric reasoning
        psychometric = outputs["psychometric"]
        if psychometric["dominant_traits"]:
            reasoning.append(
                f"Based on dominant traits: {', '.join(psychometric['dominant_traits'])}"
            )
        
        # Pattern reasoning
        pattern = outputs["pattern"]
        if pattern["patterns"]:
            top_pattern = pattern["patterns"][0]
            reasoning.append(
                f"Primary pattern detected: {top_pattern['type']} ({top_pattern['description']})"
            )
        
        # Career match reasoning
        if recommendations:
            top_career = recommendations[0]
            reasoning.append(
                f"Top career match: {top_career['career']} with {top_career['match_score']}% match"
            )
        
        # Insight reasoning
        if pattern["insights"]:
            reasoning.append(f"Key insight: {pattern['insights'][0]}")
        
        return reasoning
    
    def _calculate_overall_confidence(self, outputs: Dict, recommendations: List[Dict]) -> float:
        """
        Calculate overall confidence in the recommendations.
        
        Args:
            outputs: Normalized agent outputs
            recommendations: Career recommendations
        
        Returns:
            float: Confidence score (0-1)
        """
        # Base confidence from agent outputs
        agent_confidences = [
            outputs["psychometric"]["confidence"],
            0.8 if outputs["pattern"]["valid"] else 0.5,
            0.8 if outputs["career_query"]["valid"] else 0.5
        ]
        
        avg_agent_confidence = statistics.mean(agent_confidences)
        
        # Adjust based on recommendation quality
        if recommendations:
            avg_match_score = statistics.mean([r["match_score"] for r in recommendations])
            recommendation_confidence = avg_match_score / 100
        else:
            recommendation_confidence = 0.0
        
        # Combine confidences
        overall_confidence = (avg_agent_confidence * 0.4) + (recommendation_confidence * 0.6)
        
        return round(overall_confidence, 2)
    
    def _validate_input(self, input_data: Dict) -> bool:
        """
        Validate input data structure.
        
        Args:
            input_data: Input dictionary
        
        Returns:
            bool: True if valid
        """
        required_fields = ["psychometric_output", "pattern_output", "career_query_output"]
        return all(field in input_data for field in required_fields)
    
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
            "recommendations": [],
            "action_plan": {},
            "confidence": 0.0,
            "reasoning": []
        }
