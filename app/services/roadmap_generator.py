"""
Roadmap Generator Service
Generates personalized career development roadmaps.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


class RoadmapGenerator:
    """
    Generates personalized career development roadmaps.
    
    Supports:
    - Career transition roadmaps
    - Skill development roadmaps
    - Milestone tracking
    - Resource recommendations
    """
    
    def __init__(self):
        """Initialize the roadmap generator."""
        self.milestone_templates = self._load_milestone_templates()
    
    def _load_milestone_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load milestone templates for different career paths."""
        return {
            'software_engineer': [
                {
                    'phase': 'Foundation',
                    'duration_weeks': 8,
                    'skills': ['programming fundamentals', 'data structures', 'algorithms'],
                    'projects': ['Build 3 small projects', 'Contribute to open source']
                },
                {
                    'phase': 'Web Development',
                    'duration_weeks': 12,
                    'skills': ['html', 'css', 'javascript', 'framework'],
                    'projects': ['Build full-stack application', 'Deploy to cloud']
                },
                {
                    'phase': 'Advanced Topics',
                    'duration_weeks': 16,
                    'skills': ['system design', 'testing', 'devops'],
                    'projects': ['Build scalable system', 'Lead a project']
                }
            ],
            'data_scientist': [
                {
                    'phase': 'Mathematics & Statistics',
                    'duration_weeks': 8,
                    'skills': ['statistics', 'linear algebra', 'calculus'],
                    'projects': ['Complete 5 statistical analysis projects']
                },
                {
                    'phase': 'Programming & Tools',
                    'duration_weeks': 12,
                    'skills': ['python', 'pandas', 'numpy', 'sql'],
                    'projects': ['Build data pipeline', 'Analyze real dataset']
                },
                {
                    'phase': 'Machine Learning',
                    'duration_weeks': 16,
                    'skills': ['machine learning', 'deep learning', 'nlp'],
                    'projects': ['Build ML model', 'Publish research']
                }
            ],
            'product_manager': [
                {
                    'phase': 'Foundation',
                    'duration_weeks': 8,
                    'skills': ['product thinking', 'user research', 'analytics'],
                    'projects': ['Conduct user research', 'Analyze product metrics']
                },
                {
                    'phase': 'Strategy & Execution',
                    'duration_weeks': 12,
                    'skills': ['roadmapping', 'prioritization', 'stakeholder management'],
                    'projects': ['Create product roadmap', 'Launch feature']
                },
                {
                    'phase': 'Leadership',
                    'duration_weeks': 16,
                    'skills': ['team leadership', 'business strategy', 'growth'],
                    'projects': ['Lead product team', 'Drive growth initiative']
                }
            ]
        }
    
    def generate_roadmap(self, current_state: Dict[str, Any], target_career: Dict[str, Any], skill_gaps: List[str] = None) -> Dict[str, Any]:
        """
        Generate a personalized career roadmap.
        
        Args:
            current_state: Current skills, experience, level
            target_career: Target career information
            skill_gaps: List of skill gaps to address
        
        Returns:
            Dict with complete roadmap
        """
        career_title = target_career.get('title', 'software_engineer').lower().replace(' ', '_')
        
        # Get template or use generic
        template = self.milestone_templates.get(career_title, self._get_generic_template())
        
        # Customize based on current state
        customized_roadmap = self._customize_roadmap(template, current_state, skill_gaps)
        
        # Calculate timeline
        total_weeks = sum(m['duration_weeks'] for m in customized_roadmap)
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=total_weeks)
        
        return {
            'target_career': target_career.get('title', 'Unknown'),
            'current_level': current_state.get('level', 'beginner'),
            'target_level': target_career.get('level', 'senior'),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_duration_weeks': total_weeks,
            'total_duration_months': round(total_weeks / 4, 1),
            'milestones': customized_roadmap,
            'checkpoints': self._generate_checkpoints(customized_roadmap, start_date),
            'resources': self._generate_resources(customized_roadmap),
            'success_metrics': self._generate_success_metrics(target_career)
        }
    
    def _get_generic_template(self) -> List[Dict[str, Any]]:
        """Get a generic career roadmap template."""
        return [
            {
                'phase': 'Foundation',
                'duration_weeks': 8,
                'skills': ['core fundamentals', 'basic tools'],
                'projects': ['Complete foundational project']
            },
            {
                'phase': 'Intermediate',
                'duration_weeks': 12,
                'skills': ['intermediate skills', 'best practices'],
                'projects': ['Build intermediate project']
            },
            {
                'phase': 'Advanced',
                'duration_weeks': 16,
                'skills': ['advanced topics', 'specialization'],
                'projects': ['Build advanced project', 'Lead initiative']
            }
        ]
    
    def _customize_roadmap(self, template: List[Dict[str, Any]], current_state: Dict[str, Any], skill_gaps: List[str] = None) -> List[Dict[str, Any]]:
        """Customize roadmap based on current state and skill gaps."""
        customized = []
        current_level = current_state.get('level', 'beginner')
        
        # Skip phases based on current level
        level_mapping = {
            'beginner': 0,
            'junior': 1,
            'mid-level': 1,
            'senior': 2,
            'expert': 3
        }
        
        start_phase = level_mapping.get(current_level, 0)
        
        for i, phase in enumerate(template):
            if i >= start_phase:
                # Add skill gaps to relevant phases
                if skill_gaps and i == start_phase:
                    phase['skills'].extend(skill_gaps[:3])  # Add top 3 gaps to first phase
                
                customized.append({
                    **phase,
                    'phase_number': i - start_phase + 1,
                    'status': 'pending' if i > start_phase else 'in_progress'
                })
        
        return customized
    
    def _generate_checkpoints(self, roadmap: List[Dict[str, Any]], start_date: datetime) -> List[Dict[str, Any]]:
        """Generate checkpoints for tracking progress."""
        checkpoints = []
        current_date = start_date
        
        for milestone in roadmap:
            checkpoint_date = current_date + timedelta(weeks=milestone['duration_weeks'])
            checkpoints.append({
                'phase': milestone['phase'],
                'date': checkpoint_date.isoformat(),
                'deliverables': milestone['projects'],
                'skills_to_master': milestone['skills']
            })
            current_date = checkpoint_date
        
        return checkpoints
    
    def _generate_resources(self, roadmap: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate learning resources for each phase."""
        resources = {}
        
        for milestone in roadmap:
            phase_name = milestone['phase']
            resources[phase_name] = []
            
            for skill in milestone['skills']:
                resources[phase_name].extend([
                    f"Online course: {skill}",
                    f"Documentation: {skill}",
                    f"Practice project: {skill}"
                ])
        
        return resources
    
    def _generate_success_metrics(self, target_career: Dict[str, Any]) -> List[str]:
        """Generate success metrics for the roadmap."""
        return [
            f"Master all required skills for {target_career.get('title', 'target career')}",
            "Complete all phase projects",
            "Build portfolio of 3+ relevant projects",
            "Contribute to open source",
            "Network with professionals in the field",
            "Obtain relevant certifications if applicable"
        ]
    
    def generate_transition_roadmap(self, from_career: Dict[str, Any], to_career: Dict[str, Any], current_skills: List[str]) -> Dict[str, Any]:
        """
        Generate a roadmap for career transition.
        
        Args:
            from_career: Current career
            to_career: Target career
            current_skills: Current skills
        
        Returns:
            Dict with transition roadmap
        """
        # Identify transferable skills
        from_skills = from_career.get('required_skills', [])
        to_skills = to_career.get('required_skills', [])
        
        transferable = [s for s in current_skills if s.lower() in [ts.lower() for ts in to_skills]]
        
        # Identify new skills needed
        new_skills = [s for s in to_skills if s.lower() not in [cs.lower() for cs in current_skills]]
        
        # Generate transition phases
        transition_roadmap = [
            {
                'phase': 'Assessment & Planning',
                'duration_weeks': 4,
                'focus': 'Understand target role and plan transition',
                'actions': [
                    'Research target career in depth',
                    'Network with professionals in target field',
                    'Identify skill gaps',
                    'Create learning plan'
                ]
            },
            {
                'phase': 'Skill Acquisition',
                'duration_weeks': len(new_skills) * 3,
                'focus': 'Learn missing skills',
                'skills': new_skills,
                'actions': [
                    f'Learn {len(new_skills)} new skills',
                    'Complete relevant courses',
                    'Build transition projects'
                ]
            },
            {
                'phase': 'Experience Building',
                'duration_weeks': 12,
                'focus': 'Gain relevant experience',
                'actions': [
                    'Work on transition projects',
                    'Freelance or volunteer in target field',
                    'Build portfolio for new career'
                ]
            },
            {
                'phase': 'Job Search',
                'duration_weeks': 8,
                'focus': 'Apply for target roles',
                'actions': [
                    'Update resume and LinkedIn',
                    'Apply to target roles',
                    'Prepare for interviews',
                    'Network with hiring managers'
                ]
            }
        ]
        
        total_weeks = sum(p['duration_weeks'] for p in transition_roadmap)
        
        return {
            'from_career': from_career.get('title', 'Unknown'),
            'to_career': to_career.get('title', 'Unknown'),
            'transferable_skills': transferable,
            'new_skills_needed': new_skills,
            'total_duration_weeks': total_weeks,
            'total_duration_months': round(total_weeks / 4, 1),
            'roadmap': transition_roadmap,
            'success_criteria': [
                f'Successfully transition to {to_career.get("title")}',
                'Secure role in target field',
                'Maintain or improve compensation',
                'Achieve job satisfaction'
            ]
        }
