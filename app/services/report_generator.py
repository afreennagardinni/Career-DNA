"""
Report Generator Service
Generates PDF reports for career analysis results.
"""

import os
from typing import Dict, List, Any
from datetime import datetime


class ReportGenerator:
    """
    Generates PDF reports for career analysis.
    
    Supports:
    - Career recommendations report
    - Skills analysis report
    - Personality profile report
    - Action plan report
    - Comprehensive analysis report
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_career_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive career analysis report.
        
        Args:
            analysis_data: Complete analysis data from pipeline
        
        Returns:
            Dict with report metadata and content
        """
        report_content = {
            'title': 'Career DNA Analysis Report',
            'generated_at': datetime.now().isoformat(),
            'sections': []
        }
        
        # Executive Summary
        report_content['sections'].append({
            'title': 'Executive Summary',
            'content': self._generate_executive_summary(analysis_data)
        })
        
        # Personality Profile
        report_content['sections'].append({
            'title': 'Personality Profile',
            'content': self._generate_personality_section(analysis_data)
        })
        
        # Career Recommendations
        report_content['sections'].append({
            'title': 'Career Recommendations',
            'content': self._generate_careers_section(analysis_data)
        })
        
        # Skills Analysis
        report_content['sections'].append({
            'title': 'Skills Analysis',
            'content': self._generate_skills_section(analysis_data)
        })
        
        # Action Plan
        report_content['sections'].append({
            'title': 'Action Plan',
            'content': self._generate_action_plan_section(analysis_data)
        })
        
        # Confidence Scores
        report_content['sections'].append({
            'title': 'Analysis Confidence',
            'content': self._generate_confidence_section(analysis_data)
        })
        
        return report_content
    
    def _generate_executive_summary(self, data: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        personality = data.get('personality', {})
        top_careers = data.get('top_careers', [])
        confidence = data.get('confidence_scores', {})
        
        dominant_traits = personality.get('dominant_traits', [])
        top_career = top_careers[0] if top_careers else None
        overall_confidence = confidence.get('overall', 0)
        
        summary = f"""
Based on comprehensive psychometric analysis and AI-powered career matching, 
this report provides personalized career recommendations.

Your dominant personality traits are: {', '.join(dominant_traits) if dominant_traits else 'Not assessed'}.

Top recommended career: {top_career.get('career', 'Not determined') if top_career else 'Not determined'} 
with a match score of {top_career.get('match_score', 0):.1f}% if top_career else 0%.

Overall analysis confidence: {overall_confidence * 100:.0f}%.
"""
        return summary.strip()
    
    def _generate_personality_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personality profile section."""
        personality = data.get('personality', {})
        traits = personality.get('traits', {})
        
        big_five = traits.get('big_five', {})
        riasec = traits.get('riasec', {})
        
        return {
            'big_five_traits': big_five,
            'riasec_scores': riasec,
            'dominant_traits': personality.get('dominant_traits', []),
            'trait_profile': personality.get('trait_profile', ''),
            'confidence': personality.get('confidence', 0)
        }
    
    def _generate_careers_section(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate career recommendations section."""
        top_careers = data.get('top_careers', [])
        
        return [
            {
                'rank': i + 1,
                'career': career.get('career', career.get('title', 'Unknown')),
                'match_score': career.get('match_score', 0),
                'description': career.get('description', ''),
                'skills': career.get('skills', [])
            }
            for i, career in enumerate(top_careers)
        ]
    
    def _generate_skills_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate skills analysis section."""
        # This would be populated from resume or GitHub analysis
        return {
            'assessed_skills': [],
            'skill_categories': {},
            'skill_gaps': [],
            'recommended_skills': []
        }
    
    def _generate_action_plan_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate action plan section."""
        action_plan = data.get('action_plan', {})
        
        return {
            'short_term': action_plan.get('short_term', []),
            'medium_term': action_plan.get('medium_term', []),
            'long_term': action_plan.get('long_term', [])
        }
    
    def _generate_confidence_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate confidence scores section."""
        confidence = data.get('confidence_scores', {})
        
        return {
            'psychometric': confidence.get('psychometric', 0),
            'pattern_analysis': confidence.get('pattern', 0),
            'career_query': confidence.get('career_query', 0),
            'rag_retrieval': confidence.get('rag', 0),
            'overall': confidence.get('overall', 0)
        }
    
    def generate_skill_gap_report(self, user_skills: List[str], target_career: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a skill gap analysis report.
        
        Args:
            user_skills: User's current skills
            target_career: Target career with required skills
        
        Returns:
            Dict with skill gap analysis
        """
        required_skills = target_career.get('required_skills', [])
        preferred_skills = target_career.get('preferred_skills', [])
        
        # Calculate gaps
        user_skills_lower = [s.lower() for s in user_skills]
        required_lower = [s.lower() for s in required_skills]
        preferred_lower = [s.lower() for s in preferred_skills]
        
        missing_required = [s for s in required_skills if s.lower() not in user_skills_lower]
        missing_preferred = [s for s in preferred_skills if s.lower() not in user_skills_lower]
        
        matched_required = [s for s in required_skills if s.lower() in user_skills_lower]
        
        return {
            'target_career': target_career.get('title', 'Unknown'),
            'current_skills': user_skills,
            'required_skills': required_skills,
            'matched_required': matched_required,
            'missing_required': missing_required,
            'missing_preferred': missing_preferred,
            'skill_match_percentage': (len(matched_required) / len(required_skills) * 100) if required_skills else 0,
            'priority_gaps': missing_required[:5]  # Top 5 priority gaps
        }
    
    def generate_roadmap_report(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a career roadmap report.
        
        Args:
            current_state: Current skills and experience
            target_state: Target career requirements
        
        Returns:
            Dict with roadmap steps
        """
        roadmap = {
            'current_level': current_state.get('level', 'beginner'),
            'target_level': target_state.get('level', 'senior'),
            'estimated_duration': self._estimate_duration(current_state, target_state),
            'milestones': []
        }
        
        # Generate milestones based on skill gaps
        skill_gaps = target_state.get('skill_gaps', [])
        
        for i, gap in enumerate(skill_gaps):
            milestone = {
                'phase': f'Phase {i + 1}',
                'focus': gap,
                'duration_weeks': 4,
                'resources': self._get_learning_resources(gap),
                'deliverables': [f'Master {gap}', f'Complete project using {gap}']
            }
            roadmap['milestones'].append(milestone)
        
        return roadmap
    
    def _estimate_duration(self, current: Dict[str, Any], target: Dict[str, Any]) -> str:
        """Estimate duration to reach target."""
        skill_gaps = len(target.get('skill_gaps', []))
        weeks = skill_gaps * 4  # 4 weeks per skill gap
        
        if weeks < 12:
            return f"{weeks} weeks"
        elif weeks < 52:
            return f"{weeks // 4} months"
        else:
            return f"{weeks // 52}+ years"
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resources for a skill."""
        # This would connect to a learning resources database
        return [
            f"Online course for {skill}",
            f"Documentation for {skill}",
            f"Practice projects for {skill}"
        ]
