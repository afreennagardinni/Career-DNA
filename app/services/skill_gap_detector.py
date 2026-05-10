"""
Skill Gap Detector Service
Detects skill gaps between user's current skills and target career requirements.
"""

from typing import Dict, List, Any
from app.services.resume_analyzer import ResumeAnalyzer


class SkillGapDetector:
    """
    Detects and analyzes skill gaps for career transitions.
    
    Supports:
    - Skill gap analysis
    - Priority ranking of gaps
    - Learning path generation
    - Resource recommendations
    """
    
    def __init__(self):
        """Initialize the skill gap detector."""
        self.resume_analyzer = ResumeAnalyzer()
        self.skill_difficulty = self._load_skill_difficulty()
    
    def _load_skill_difficulty(self) -> Dict[str, int]:
        """Load skill difficulty ratings (1-5 scale)."""
        return {
            # Easy to learn (1-2)
            'html': 1, 'css': 1, 'markdown': 1, 'git': 2,
            
            # Moderate (2-3)
            'javascript': 2, 'python': 2, 'sql': 2, 'bash': 2,
            'react': 3, 'vue': 3, 'angular': 3, 'django': 3, 'flask': 3,
            
            # Advanced (3-4)
            'java': 3, 'c++': 4, 'rust': 4, 'go': 3,
            'docker': 3, 'kubernetes': 4, 'aws': 4, 'azure': 4,
            
            # Expert (4-5)
            'machine learning': 5, 'deep learning': 5, 'data science': 4,
            'devops': 4, 'system design': 5, 'architecture': 5
        }
    
    def detect_gaps(self, user_skills: List[str], target_career: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect skill gaps between user skills and target career.
        
        Args:
            user_skills: User's current skills
            target_career: Target career with requirements
        
        Returns:
            Dict with skill gap analysis
        """
        required_skills = target_career.get('required_skills', [])
        preferred_skills = target_career.get('preferred_skills', [])
        
        # Normalize to lowercase for comparison
        user_skills_lower = [s.lower() for s in user_skills]
        required_lower = [s.lower() for s in required_skills]
        preferred_lower = [s.lower() for s in preferred_skills]
        
        # Find missing skills
        missing_required = [
            skill for skill in required_skills
            if skill.lower() not in user_skills_lower
        ]
        
        missing_preferred = [
            skill for skill in preferred_skills
            if skill.lower() not in user_skills_lower
        ]
        
        # Calculate match percentage
        required_match = len(required_skills) - len(missing_required)
        match_percentage = (required_match / len(required_skills) * 100) if required_skills else 0
        
        # Rank gaps by priority and difficulty
        ranked_gaps = self._rank_gaps(missing_required, missing_preferred)
        
        # Generate learning recommendations
        learning_path = self._generate_learning_path(ranked_gaps)
        
        return {
            'target_career': target_career.get('title', 'Unknown'),
            'user_skills': user_skills,
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'matched_required': [s for s in required_skills if s.lower() in user_skills_lower],
            'missing_required': missing_required,
            'missing_preferred': missing_preferred,
            'match_percentage': round(match_percentage, 2),
            'total_gaps': len(missing_required) + len(missing_preferred),
            'critical_gaps': missing_required,  # Required skills
            'ranked_gaps': ranked_gaps,
            'learning_path': learning_path,
            'estimated_completion_time': self._estimate_completion_time(ranked_gaps)
        }
    
    def _rank_gaps(self, required_gaps: List[str], preferred_gaps: List[str]) -> List[Dict[str, Any]]:
        """
        Rank skill gaps by priority and difficulty.
        
        Args:
            required_gaps: Missing required skills
            preferred_gaps: Missing preferred skills
        
        Returns:
            List of ranked gaps with metadata
        """
        ranked = []
        
        # Add required gaps (higher priority)
        for skill in required_gaps:
            difficulty = self.skill_difficulty.get(skill.lower(), 3)
            ranked.append({
                'skill': skill,
                'priority': 'high',
                'difficulty': difficulty,
                'estimated_weeks': difficulty * 2
            })
        
        # Add preferred gaps (lower priority)
        for skill in preferred_gaps:
            difficulty = self.skill_difficulty.get(skill.lower(), 3)
            ranked.append({
                'skill': skill,
                'priority': 'medium',
                'difficulty': difficulty,
                'estimated_weeks': difficulty * 2
            })
        
        # Sort by priority then difficulty
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        ranked.sort(key=lambda x: (priority_order[x['priority']], x['difficulty']))
        
        return ranked
    
    def _generate_learning_path(self, ranked_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate a structured learning path from skill gaps.
        
        Args:
            ranked_gaps: Ranked skill gaps
        
        Returns:
            List of learning phases
        """
        phases = []
        current_phase = []
        current_week = 0
        
        for gap in ranked_gaps:
            gap_weeks = gap['estimated_weeks']
            
            # Start new phase if current phase is too long
            if sum(g['estimated_weeks'] for g in current_phase) + gap_weeks > 12:
                if current_phase:
                    phases.append({
                        'phase': len(phases) + 1,
                        'duration_weeks': sum(g['estimated_weeks'] for g in current_phase),
                        'skills': [g['skill'] for g in current_phase],
                        'focus': self._determine_phase_focus(current_phase)
                    })
                current_phase = []
            
            current_phase.append(gap)
        
        # Add final phase
        if current_phase:
            phases.append({
                'phase': len(phases) + 1,
                'duration_weeks': sum(g['estimated_weeks'] for g in current_phase),
                'skills': [g['skill'] for g in current_phase],
                'focus': self._determine_phase_focus(current_phase)
            })
        
        return phases
    
    def _determine_phase_focus(self, gaps: List[Dict[str, Any]]) -> str:
        """Determine the focus area for a learning phase."""
        skill_categories = {
            'programming': ['python', 'javascript', 'java', 'c++', 'go', 'rust'],
            'web': ['html', 'css', 'react', 'vue', 'angular'],
            'data': ['pandas', 'numpy', 'machine learning', 'data science'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd']
        }
        
        skill_names = [g['skill'].lower() for g in gaps]
        
        for category, skills in skill_categories.items():
            if any(skill in skill_names for skill in skills):
                return category
        
        return 'general'
    
    def _estimate_completion_time(self, ranked_gaps: List[Dict[str, Any]]) -> str:
        """Estimate total completion time for all gaps."""
        total_weeks = sum(g['estimated_weeks'] for g in ranked_gaps)
        
        if total_weeks < 4:
            return f"{total_weeks} weeks"
        elif total_weeks < 12:
            return f"{total_weeks // 4} months"
        elif total_weeks < 52:
            return f"{total_weeks // 4} months"
        else:
            return f"{total_weeks // 52}+ years"
    
    def compare_multiple_careers(self, user_skills: List[str], careers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare user skills against multiple career options.
        
        Args:
            user_skills: User's current skills
            careers: List of career options
        
        Returns:
            Dict with comparison results
        """
        comparisons = []
        
        for career in careers:
            gap_analysis = self.detect_gaps(user_skills, career)
            comparisons.append({
                'career': career.get('title', 'Unknown'),
                'match_percentage': gap_analysis['match_percentage'],
                'total_gaps': gap_analysis['total_gaps'],
                'critical_gaps': len(gap_analysis['critical_gaps']),
                'estimated_time': gap_analysis['estimated_completion_time']
            })
        
        # Sort by match percentage
        comparisons.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return {
            'user_skills': user_skills,
            'comparisons': comparisons,
            'best_match': comparisons[0] if comparisons else None,
            'recommended_career': comparisons[0]['career'] if comparisons else None
        }
