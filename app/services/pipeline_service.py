"""
Career DNA Pipeline Service
Handles the complete assessment-to-results pipeline with multi-agent analysis.
"""

import json
from typing import Dict, List, Any
from app.services.scoring_service import ScoringService
from app.models.assessment import Assessment
from app.models.answer import Answer
from app.models.profile import Profile


class PipelineService:
    """
    Service for running the complete Career DNA analysis pipeline.
    """
    
    def __init__(self):
        """Initialize the pipeline service."""
        self.scoring_service = ScoringService()
    
    def run_career_dna_pipeline(self, assessment_data: Dict, user_context: Dict = None) -> Dict:
        """
        Run the complete Career DNA pipeline from assessment data.
        
        Args:
            assessment_data: Dictionary containing assessment answers and metadata
            user_context: Additional user context (location, experience, etc.)
        
        Returns:
            Dict: Complete pipeline results with personality analysis, careers, and recommendations
        """
        try:
            # Extract data
            user_id = assessment_data.get('user_id')
            assessment_type = assessment_data.get('assessment_type')
            answers = assessment_data.get('answers', [])
            
            # Score the assessment
            if assessment_type == 'big_five_ocean':
                big_five_scores = self.scoring_service.score_big_five(answers)
                
                # Get user profile for RIASEC data if available
                riasec_data = self._get_riasec_data(user_id)
                
                # Generate complete analysis
                result = self._generate_complete_analysis(
                    big_five_scores=big_five_scores,
                    riasec_data=riasec_data,
                    user_context=user_context or {}
                )
                
            elif assessment_type == 'riasec':
                riasec_result = self.scoring_service.score_riasec(answers)
                
                # Get user profile for Big Five data if available
                big_five_scores = self._get_big_five_data(user_id)
                
                # Generate complete analysis
                result = self._generate_complete_analysis(
                    big_five_scores=big_five_scores,
                    riasec_data=riasec_result,
                    user_context=user_context or {}
                )
            
            else:
                raise ValueError(f"Unsupported assessment type: {assessment_type}")
            
            return result
            
        except Exception as e:
            print(f"Pipeline error: {str(e)}")
            return {
                'error': 'Pipeline failed',
                'message': str(e),
                'personality': {},
                'top_careers': [],
                'confidence_scores': {'overall': 0.0},
                'explanation': f'Analysis failed: {str(e)}',
                'action_plan': {},
                'metadata': {'status': 'failed'}
            }
    
    def run_career_dna_pipeline_from_profile(self, profile_data: Dict, user_context: Dict = None) -> Dict:
        """
        Run the Career DNA pipeline from user profile data.
        
        Args:
            profile_data: Dictionary containing user's Career DNA profile
            user_context: Additional user context
        
        Returns:
            Dict: Complete pipeline results
        """
        try:
            career_dna = profile_data.get('career_dna', {})
            
            # Extract Big Five and RIASEC data
            big_five_scores = career_dna.get('personality', {}).get('big_five', {})
            riasec_data = career_dna.get('interests', {})
            
            # Generate complete analysis
            result = self._generate_complete_analysis(
                big_five_scores=big_five_scores,
                riasec_data=riasec_data,
                user_context=user_context or {}
            )
            
            return result
            
        except Exception as e:
            print(f"Profile pipeline error: {str(e)}")
            return {
                'error': 'Profile pipeline failed',
                'message': str(e),
                'personality': {},
                'top_careers': [],
                'confidence_scores': {'overall': 0.0},
                'explanation': f'Profile analysis failed: {str(e)}',
                'action_plan': {},
                'metadata': {'status': 'failed'}
            }
    
    def _get_big_five_data(self, user_id: int) -> Dict:
        """Get Big Five scores from user profile."""
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile and profile.career_dna:
                return profile.career_dna.get('personality', {}).get('big_five', {})
            return {}
        except:
            return {}
    
    def _get_riasec_data(self, user_id: int) -> Dict:
        """Get RIASEC data from user profile."""
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile and profile.career_dna:
                interests = profile.career_dna.get('interests', {})
                return {
                    'scores': interests.get('riasec', {}),
                    'holland_code': interests.get('holland_code', ''),
                    'top_interests': interests.get('top_interests', [])
                }
            return {}
        except:
            return {}
    
    def _generate_complete_analysis(
        self, 
        big_five_scores: Dict, 
        riasec_data: Dict, 
        user_context: Dict
    ) -> Dict:
        """
        Generate complete Career DNA analysis from Big Five and RIASEC data.
        
        Args:
            big_five_scores: Big Five trait scores
            riasec_data: RIASEC scores and Holland code
            user_context: Additional user context
        
        Returns:
            Dict: Complete analysis results
        """
        # Generate career recommendations
        career_recommendations = []
        if big_five_scores and riasec_data.get('scores'):
            career_recommendations = self.scoring_service._generate_career_recommendations(
                big_five_scores,
                riasec_data['scores'],
                riasec_data.get('holland_code', '')
            )
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(
            big_five_scores, 
            riasec_data, 
            len(career_recommendations)
        )
        
        # Generate dominant traits
        dominant_traits = self.scoring_service._get_dominant_traits(big_five_scores, threshold=60)
        
        # Generate explanation
        explanation = self._generate_explanation(
            big_five_scores, 
            riasec_data, 
            career_recommendations[:3]
        )
        
        # Generate action plan
        action_plan = self._generate_action_plan(
            big_five_scores, 
            riasec_data, 
            career_recommendations[:3]
        )
        
        # Prepare result structure
        result = {
            'personality': {
                'traits': {
                    'big_five': big_five_scores,
                    'riasec': riasec_data.get('scores', {}),
                    'holland_code': riasec_data.get('holland_code', '')
                },
                'dominant_traits': dominant_traits,
                'summary': self._generate_personality_summary(big_five_scores, riasec_data)
            },
            'top_careers': self._format_career_recommendations(career_recommendations),
            'confidence_scores': confidence_scores,
            'explanation': explanation,
            'action_plan': action_plan,
            'metadata': {
                'status': 'completed',
                'data_sources': self._get_data_sources(big_five_scores, riasec_data),
                'user_context': user_context
            }
        }
        
        return result
    
    def _calculate_confidence_scores(
        self, 
        big_five_scores: Dict, 
        riasec_data: Dict, 
        career_count: int
    ) -> Dict:
        """Calculate confidence scores for different aspects of the analysis."""
        scores = {}
        
        # Psychometric confidence (based on data completeness)
        psychometric_data = 0
        total_data = 10  # 5 Big Five + 5 RIASEC
        
        if big_five_scores:
            psychometric_data += len([s for s in big_five_scores.values() if s > 0])
        
        if riasec_data.get('scores'):
            psychometric_data += len([s for s in riasec_data['scores'].values() if s > 0])
        
        scores['psychometric'] = psychometric_data / total_data
        
        # Pattern confidence (based on clear patterns in data)
        pattern_confidence = 0.0
        if big_five_scores:
            # Check for clear personality patterns
            high_traits = len([s for s in big_five_scores.values() if s >= 70])
            pattern_confidence = min(high_traits / 3, 1.0)  # Max confidence if 3+ high traits
        
        scores['pattern'] = pattern_confidence
        
        # Career query confidence (based on number of quality matches)
        scores['career_query'] = min(career_count / 5, 1.0)  # Max confidence if 5+ careers
        
        # RAG confidence (placeholder for future RAG implementation)
        scores['rag'] = 0.7  # Fixed confidence for now
        
        # Overall confidence (weighted average)
        weights = {'psychometric': 0.3, 'pattern': 0.2, 'career_query': 0.3, 'rag': 0.2}
        overall = sum(scores[key] * weights[key] for key in scores)
        scores['overall'] = round(overall, 2)
        
        return scores
    
    def _generate_explanation(
        self, 
        big_five_scores: Dict, 
        riasec_data: Dict, 
        top_careers: List
    ) -> str:
        """Generate personalized explanation of the results."""
        explanation_parts = []
        
        # Personality summary
        if big_five_scores:
            dominant = self.scoring_service._get_dominant_traits(big_five_scores, threshold=60)
            if dominant and dominant != ['balanced']:
                explanation_parts.append(
                    f"Your personality shows strong {', '.join(dominant)} traits, "
                    f"indicating you tend to be particularly {self._trait_descriptions(dominant)}."
                )
            else:
                explanation_parts.append(
                    "Your personality shows a balanced profile across multiple traits, "
                    "suggesting versatility in different work environments."
                )
        
        # Interests summary
        if riasec_data.get('holland_code'):
            holland_code = riasec_data['holland_code']
            explanation_parts.append(
                f"Your Holland code is {holland_code}, which indicates "
                f"strong interest in {self._holland_code_description(holland_code)} environments."
            )
        
        # Career connection
        if top_careers:
            top_career = top_careers[0].get('title', 'various fields')
            explanation_parts.append(
                f"Based on this combination, {top_career} emerges as your top career match, "
                f"aligning well with both your personality traits and interests."
            )
        
        return " ".join(explanation_parts)
    
    def _generate_action_plan(
        self, 
        big_five_scores: Dict, 
        riasec_data: Dict, 
        top_careers: List
    ) -> Dict:
        """Generate personalized action plan."""
        plan = {
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }
        
        # Short-term actions (next 3 months)
        plan['short_term'].extend([
            "Research your top 3 career recommendations in detail",
            "Update your resume to highlight relevant skills and experiences",
            "Connect with professionals in your recommended career fields"
        ])
        
        # Medium-term actions (3-12 months)
        plan['medium_term'].extend([
            "Take relevant courses or certifications to strengthen your profile",
            "Gain practical experience through projects or volunteering",
            "Build your professional network in target industries"
        ])
        
        # Long-term actions (1+ years)
        plan['long_term'].extend([
            "Pursue advanced education if required for your target career",
            "Seek leadership roles or specialized positions",
            "Consider mentorship opportunities to guide others"
        ])
        
        # Add personalized suggestions based on traits
        if big_five_scores:
            if big_five_scores.get('openness', 0) >= 70:
                plan['short_term'].append("Explore creative and innovative projects")
            
            if big_five_scores.get('conscientiousness', 0) >= 70:
                plan['short_term'].append("Create a structured development plan")
            
            if big_five_scores.get('extraversion', 0) >= 70:
                plan['short_term'].append("Join professional associations and networking groups")
        
        return plan
    
    def _format_career_recommendations(self, recommendations: List) -> List:
        """Format career recommendations for the frontend."""
        formatted = []
        
        for rec in recommendations:
            formatted.append({
                'career': rec.get('title', 'Unknown Career'),
                'title': rec.get('title', 'Unknown Career'),
                'match_score': rec.get('match_score', 0),
                'description': self._get_career_description(rec.get('title', '')),
                'skills': self._get_career_skills(rec.get('title', '')),
                'holland_match': rec.get('holland_match', 0),
                'personality_match': rec.get('personality_match', 0)
            })
        
        return formatted
    
    def _get_career_description(self, career_title: str) -> str:
        """Get description for a career title."""
        descriptions = {
            'Software Engineer': 'Design, develop, and maintain software systems and applications.',
            'Data Scientist': 'Analyze complex data to help organizations make better decisions.',
            'Product Manager': 'Lead product development and strategy from conception to launch.',
            'UX Designer': 'Create user-centered designs for digital products and experiences.',
            'Marketing Manager': 'Develop and execute marketing strategies to promote products and services.',
            'Financial Analyst': 'Analyze financial data and provide investment recommendations.',
            'Human Resources Manager': 'Oversee recruitment, employee relations, and organizational development.',
            'Research Scientist': 'Conduct scientific research to advance knowledge in specific fields.'
        }
        return descriptions.get(career_title, 'A career path that aligns with your profile.')
    
    def _get_career_skills(self, career_title: str) -> List[str]:
        """Get required skills for a career title."""
        skills = {
            'Software Engineer': ['Programming', 'Problem Solving', 'System Design'],
            'Data Scientist': ['Statistics', 'Machine Learning', 'Data Analysis'],
            'Product Manager': ['Strategy', 'Communication', 'Leadership'],
            'UX Designer': ['Design Thinking', 'User Research', 'Prototyping'],
            'Marketing Manager': ['Marketing Strategy', 'Analytics', 'Communication'],
            'Financial Analyst': ['Financial Modeling', 'Excel', 'Attention to Detail'],
            'Human Resources Manager': ['People Skills', 'Communication', 'Organizational Skills'],
            'Research Scientist': ['Research Methods', 'Critical Thinking', 'Domain Expertise']
        }
        return skills.get(career_title, ['Communication', 'Problem Solving', 'Adaptability'])
    
    def _trait_descriptions(self, traits: List[str]) -> str:
        """Get descriptions for personality traits."""
        descriptions = {
            'openness': 'creative and open to new experiences',
            'conscientiousness': 'organized and goal-oriented',
            'extraversion': 'outgoing and energetic',
            'agreeableness': 'cooperative and empathetic',
            'neuroticism': 'emotionally sensitive'  # Note: high neuroticism is generally negative
        }
        
        trait_descs = [descriptions.get(trait, trait) for trait in traits]
        if len(trait_descs) == 1:
            return trait_descs[0]
        elif len(trait_descs) == 2:
            return f"{trait_descs[0]} and {trait_descs[1]}"
        else:
            return f"{', '.join(trait_descs[:-1])}, and {trait_descs[-1]}"
    
    def _holland_code_description(self, code: str) -> str:
        """Get description for Holland code."""
        code_descriptions = {
            'R': 'practical, hands-on',
            'I': 'analytical, investigative',
            'A': 'creative, artistic',
            'S': 'helping, social',
            'E': 'enterprising, leadership',
            'C': 'organized, detail-oriented'
        }
        
        descriptions = []
        for letter in code[:3]:  # Take first 3 letters
            descriptions.append(code_descriptions.get(letter, 'versatile'))
        
        if len(descriptions) == 1:
            return descriptions[0]
        elif len(descriptions) == 2:
            return f"{descriptions[0]} and {descriptions[1]}"
        else:
            return f"{', '.join(descriptions[:-1])}, and {descriptions[-1]}"
    
    def _generate_personality_summary(self, big_five_scores: Dict, riasec_data: Dict) -> str:
        """Generate a brief personality summary."""
        if not big_five_scores:
            return "Personality data not available"
        
        # Find top traits
        sorted_traits = sorted(big_five_scores.items(), key=lambda x: x[1], reverse=True)
        top_2 = sorted_traits[:2]
        
        trait_names = {
            'openness': 'Open',
            'conscientiousness': 'Conscientious',
            'extraversion': 'Extraverted',
            'agreeableness': 'Agreeable',
            'neuroticism': 'Emotionally Sensitive'
        }
        
        if top_2:
            top_names = [trait_names.get(trait, trait) for trait, score in top_2]
            return f"Primarily {top_names[0].lower()} and {top_names[1].lower()}"
        
        return "Balanced personality profile"
    
    def _get_data_sources(self, big_five_scores: Dict, riasec_data: Dict) -> List[str]:
        """Get list of data sources used in analysis."""
        sources = []
        if big_five_scores:
            sources.append('Big Five Assessment')
        if riasec_data.get('scores'):
            sources.append('RIASEC Assessment')
        return sources


# Global pipeline service instance
pipeline_service = PipelineService()


def run_career_dna_pipeline(assessment_data: Dict, user_context: Dict = None) -> Dict:
    """Run Career DNA pipeline from assessment data."""
    return pipeline_service.run_career_dna_pipeline(assessment_data, user_context)


def run_career_dna_pipeline_from_profile(profile_data: Dict, user_context: Dict = None) -> Dict:
    """Run Career DNA pipeline from profile data."""
    return pipeline_service.run_career_dna_pipeline_from_profile(profile_data, user_context)
