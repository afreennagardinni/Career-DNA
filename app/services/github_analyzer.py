"""
GitHub Profile Analyzer Service
Analyzes GitHub profiles to extract skills, experience, and activity patterns.
"""

import re
from typing import Dict, List, Any
from datetime import datetime, timedelta


class GitHubAnalyzer:
    """
    Analyzes GitHub profiles to extract career-relevant information.
    
    Supports:
    - Repository analysis
    - Language detection
    - Commit activity patterns
    - Contribution analysis
    - Skill extraction from code
    """
    
    def __init__(self):
        """Initialize the GitHub analyzer."""
        self.language_skill_map = {
            'Python': 'python',
            'JavaScript': 'javascript',
            'TypeScript': 'typescript',
            'Java': 'java',
            'C++': 'c++',
            'C#': 'c#',
            'Ruby': 'ruby',
            'Go': 'go',
            'Rust': 'rust',
            'PHP': 'php',
            'Swift': 'swift',
            'Kotlin': 'kotlin',
            'R': 'r',
            'SQL': 'sql',
            'HTML': 'html',
            'CSS': 'css',
            'Shell': 'bash',
            'Dockerfile': 'docker',
            'Jupyter Notebook': 'data science',
            'Vue': 'vue',
            'React': 'react',
            'Angular': 'angular'
        }
    
    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze GitHub profile data.
        
        Args:
            profile_data: GitHub profile data from API
        
        Returns:
            Dict with analysis results
        """
        # Extract basic info
        basic_info = self._extract_basic_info(profile_data)
        
        # Analyze repositories
        repos = profile_data.get('repos', [])
        repo_analysis = self._analyze_repositories(repos)
        
        # Extract skills from languages
        skills = self._extract_skills_from_repos(repos)
        
        # Analyze activity patterns
        activity = self._analyze_activity(profile_data)
        
        # Calculate developer profile
        developer_profile = self._calculate_developer_profile(skills, repo_analysis)
        
        return {
            'basic_info': basic_info,
            'skills': skills,
            'repo_analysis': repo_analysis,
            'activity': activity,
            'developer_profile': developer_profile,
            'total_repos': len(repos),
            'total_languages': len(skills)
        }
    
    def _extract_basic_info(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic profile information."""
        return {
            'username': profile_data.get('login', ''),
            'name': profile_data.get('name', ''),
            'bio': profile_data.get('bio', ''),
            'location': profile_data.get('location', ''),
            'company': profile_data.get('company', ''),
            'followers': profile_data.get('followers', 0),
            'following': profile_data.get('following', 0),
            'public_repos': profile_data.get('public_repos', 0),
            'account_age_days': self._calculate_account_age(profile_data.get('created_at'))
        }
    
    def _calculate_account_age(self, created_at: str) -> int:
        """Calculate account age in days."""
        if not created_at:
            return 0
        try:
            created = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
            return (datetime.now() - created).days
        except:
            return 0
    
    def _analyze_repositories(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze repository data."""
        if not repos:
            return {'total': 0, 'stars': 0, 'forks': 0, 'avg_size': 0}
        
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        total_size = sum(repo.get('size', 0) for repo in repos)
        
        # Count by language
        language_counts = {}
        for repo in repos:
            lang = repo.get('language', 'Unknown')
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total': len(repos),
            'stars': total_stars,
            'forks': total_forks,
            'avg_size': total_size / len(repos) if repos else 0,
            'language_distribution': language_counts,
            'top_languages': sorted(language_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _extract_skills_from_repos(self, repos: List[Dict[str, Any]]) -> List[str]:
        """Extract skills from repository languages."""
        skills = set()
        
        for repo in repos:
            language = repo.get('language', '')
            if language and language in self.language_skill_map:
                skills.add(self.language_skill_map[language])
            elif language:
                skills.add(language.lower())
        
        return sorted(list(skills))
    
    def _analyze_activity(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user activity patterns."""
        repos = profile_data.get('repos', [])
        
        # Calculate recent activity (repos updated in last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_repos = [
            repo for repo in repos
            if repo.get('updated_at') and datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ') > six_months_ago
        ]
        
        return {
            'recent_repos': len(recent_repos),
            'activity_rate': len(recent_repos) / len(repos) if repos else 0,
            'last_updated': repos[0].get('updated_at') if repos else None
        }
    
    def _calculate_developer_profile(self, skills: List[str], repo_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate developer profile type."""
        profile_type = 'general'
        specialization = []
        
        # Detect specialization based on skills
        if any(skill in ['python', 'tensorflow', 'pytorch', 'pandas', 'numpy'] for skill in skills):
            profile_type = 'data_science'
            specialization.append('Data Science')
        
        if any(skill in ['react', 'angular', 'vue', 'javascript', 'typescript'] for skill in skills):
            if profile_type == 'data_science':
                profile_type = 'full_stack'
            else:
                profile_type = 'frontend'
            specialization.append('Web Development')
        
        if any(skill in ['docker', 'kubernetes', 'aws', 'azure', 'gcp'] for skill in skills):
            profile_type = 'devops'
            specialization.append('DevOps')
        
        if any(skill in ['java', 'spring', 'c#', '.net'] for skill in skills):
            if profile_type == 'general':
                profile_type = 'backend'
            specialization.append('Backend Development')
        
        return {
            'type': profile_type,
            'specialization': specialization,
            'experience_level': self._estimate_experience_level(repo_analysis)
        }
    
    def _estimate_experience_level(self, repo_analysis: Dict[str, Any]) -> str:
        """Estimate experience level based on repository data."""
        total_repos = repo_analysis.get('total', 0)
        stars = repo_analysis.get('stars', 0)
        
        if total_repos >= 50 or stars >= 100:
            return 'senior'
        elif total_repos >= 20 or stars >= 50:
            return 'mid-level'
        elif total_repos >= 5:
            return 'junior'
        else:
            return 'beginner'
