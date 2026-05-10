"""
Resume Analyzer Service
Analyzes uploaded resumes to extract skills, experience, and career information.
"""

import os
import re
from typing import Dict, List, Any
import json


class ResumeAnalyzer:
    """
    Analyzes resume documents to extract relevant career information.
    
    Supports:
    - Text extraction from resumes
    - Skill extraction
    - Experience parsing
    - Education parsing
    - Keyword matching against career database
    """
    
    def __init__(self):
        """Initialize the resume analyzer."""
        self.skill_keywords = self._load_skill_keywords()
        self.technical_skills = self._load_technical_skills()
    
    def _load_skill_keywords(self) -> List[str]:
        """Load common skill keywords for extraction."""
        return [
            # Programming languages
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin',
            'php', 'typescript', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'bash', 'shell',
            
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node.js', 'jquery',
            'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scikit-learn', 'django rest',
            
            # Tools & Platforms
            'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'travis', 'circleci',
            'jira', 'confluence', 'slack', 'figma', 'sketch', 'photoshop', 'illustrator',
            
            # Soft skills
            'leadership', 'communication', 'teamwork', 'problem-solving', 'analytical',
            'critical thinking', 'project management', 'agile', 'scrum', 'collaboration',
            'presentation', 'negotiation', 'time management', 'organization',
            
            # Data & Analytics
            'data analysis', 'machine learning', 'data science', 'analytics', 'statistics',
            'visualization', 'reporting', 'business intelligence', 'etl', 'data mining',
            
            # DevOps & Infrastructure
            'devops', 'ci/cd', 'infrastructure', 'monitoring', 'logging', 'security',
            'networking', 'cloud computing', 'serverless', 'microservices',
            
            # Design
            'ui design', 'ux design', 'graphic design', 'web design', 'product design',
            'user research', 'prototyping', 'wireframing', 'design systems',
            
            # Marketing
            'digital marketing', 'seo', 'sem', 'content marketing', 'social media',
            'email marketing', 'branding', 'copywriting', 'marketing strategy',
            
            # Business
            'business development', 'sales', 'account management', 'customer success',
            'operations', 'finance', 'accounting', 'strategy', 'consulting'
        ]
    
    def _load_technical_skills(self) -> Dict[str, List[str]]:
        """Load technical skills by category."""
        return {
            'programming': ['python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust', 'typescript'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'express'],
            'data': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'sql', 'r', 'matlab'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'git', 'ci/cd'],
            'design': ['figma', 'sketch', 'photoshop', 'illustrator', 'ui design', 'ux design'],
            'marketing': ['seo', 'sem', 'google analytics', 'facebook ads', 'content marketing']
        }
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze resume text to extract information.
        
        Args:
            text: Resume text content
        
        Returns:
            Dict with extracted information
        """
        # Extract skills
        skills = self._extract_skills(text)
        
        # Extract experience
        experience = self._extract_experience(text)
        
        # Extract education
        education = self._extract_education(text)
        
        # Calculate skill categories
        skill_categories = self._categorize_skills(skills)
        
        return {
            'skills': skills,
            'skill_categories': skill_categories,
            'experience': experience,
            'education': education,
            'total_skills': len(skills),
            'skill_count_by_category': {cat: len(skills_list) for cat, skills_list in skill_categories.items()}
        }
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return sorted(list(set(found_skills)))
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """
        Categorize skills by domain.
        
        Args:
            skills: List of skills
        
        Returns:
            Dict with skills by category
        """
        categorized = {}
        skills_lower = [s.lower() for s in skills]
        
        for category, category_skills in self.technical_skills.items():
            matched = [skill for skill in skills if skill.lower() in category_skills]
            if matched:
                categorized[category] = matched
        
        # Uncategorized skills
        all_tech_skills = [s for skills in self.technical_skills.values() for s in skills]
        uncategorized = [skill for skill in skills if skill.lower() not in all_tech_skills]
        if uncategorized:
            categorized['other'] = uncategorized
        
        return categorized
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            List of experience entries
        """
        experiences = []
        
        # Look for common patterns
        # This is a simplified version - production would use NLP
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|work)',
            r'(?:worked|employed|position|role)[:\s]+([^.]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                experiences.append({
                    'type': 'extracted',
                    'value': match.group(0),
                    'confidence': 0.7
                })
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract education information from resume text.
        
        Args:
            text: Resume text
        
        Returns:
            List of education entries
        """
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(?:bachelor|master|phd|doctorate|associate)[\s\w]+',
            r'(?:bs|ba|ms|ma|mba|ph\.d)[\s\w]*',
            r'university|college|institute'
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'type': 'extracted',
                    'value': match.group(0),
                    'confidence': 0.7
                })
        
        return education
    
    def compare_with_career_requirements(self, resume_skills: List[str], career_requirements: List[str]) -> Dict[str, Any]:
        """
        Compare resume skills with career requirements.
        
        Args:
            resume_skills: Skills extracted from resume
            career_requirements: Required skills for a career
        
        Returns:
            Dict with comparison results
        """
        resume_skills_lower = [s.lower() for s in resume_skills]
        career_requirements_lower = [s.lower() for s in career_requirements]
        
        # Find matching skills
        matched = [skill for skill in resume_skills if skill.lower() in career_requirements_lower]
        
        # Find missing skills
        missing = [skill for skill in career_requirements if skill.lower() not in resume_skills_lower]
        
        # Calculate match percentage
        match_percentage = (len(matched) / len(career_requirements)) * 100 if career_requirements else 0
        
        return {
            'matched_skills': matched,
            'missing_skills': missing,
            'match_percentage': round(match_percentage, 2),
            'total_matched': len(matched),
            'total_required': len(career_requirements)
        }
