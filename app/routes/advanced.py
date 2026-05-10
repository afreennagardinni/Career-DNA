"""
Advanced Features Routes
Handles resume analysis, GitHub analysis, report generation, skill gap detection, and roadmap generation.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.resume_analyzer import ResumeAnalyzer
from app.services.github_analyzer import GitHubAnalyzer
from app.services.report_generator import ReportGenerator
from app.services.skill_gap_detector import SkillGapDetector
from app.services.roadmap_generator import RoadmapGenerator

# Create blueprint
advanced_bp = Blueprint('advanced', __name__)

# Initialize services
resume_analyzer = ResumeAnalyzer()
github_analyzer = GitHubAnalyzer()
report_generator = ReportGenerator()
skill_gap_detector = SkillGapDetector()
roadmap_generator = RoadmapGenerator()


@advanced_bp.route('/resume/analyze', methods=['POST'])
@login_required
def analyze_resume():
    """
    Analyze uploaded resume text.
    
    Expected JSON payload:
    {
        "resume_text": "Full text content of resume"
    }
    
    Returns:
        JSON response with resume analysis
    """
    data = request.get_json()
    resume_text = data.get('resume_text', '')
    
    if not resume_text:
        return jsonify({
            'error': 'Missing resume_text',
            'message': 'Please provide resume text for analysis'
        }), 400
    
    try:
        analysis = resume_analyzer.analyze_text(resume_text)
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/github/analyze', methods=['POST'])
@login_required
def analyze_github():
    """
    Analyze GitHub profile.
    
    Expected JSON payload:
    {
        "username": "github_username",
        "profile_data": {...}  (optional, if already fetched)
    }
    
    Returns:
        JSON response with GitHub analysis
    """
    data = request.get_json()
    username = data.get('username', '')
    profile_data = data.get('profile_data')
    
    if not username and not profile_data:
        return jsonify({
            'error': 'Missing username or profile_data',
            'message': 'Please provide GitHub username or profile data'
        }), 400
    
    try:
        # If profile_data not provided, would need to fetch from GitHub API
        # For now, assume profile_data is provided
        if not profile_data:
            return jsonify({
                'error': 'GitHub API integration required',
                'message': 'Please provide profile_data or implement GitHub API fetching'
            }), 400
        
        analysis = github_analyzer.analyze_profile(profile_data)
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/report/generate', methods=['POST'])
@login_required
def generate_report():
    """
    Generate career analysis report.
    
    Expected JSON payload:
    {
        "analysis_data": {...}  (from pipeline)
    }
    
    Returns:
        JSON response with report content
    """
    data = request.get_json()
    analysis_data = data.get('analysis_data')
    
    if not analysis_data:
        return jsonify({
            'error': 'Missing analysis_data',
            'message': 'Please provide analysis data from pipeline'
        }), 400
    
    try:
        report = report_generator.generate_career_report(analysis_data)
        return jsonify({
            'success': True,
            'report': report
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Report generation failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/skill-gap/detect', methods=['POST'])
@login_required
def detect_skill_gap():
    """
    Detect skill gaps for a target career.
    
    Expected JSON payload:
    {
        "user_skills": ["python", "javascript", ...],
        "target_career": {
            "title": "Software Engineer",
            "required_skills": ["python", "java", ...],
            "preferred_skills": [...]
        }
    }
    
    Returns:
        JSON response with skill gap analysis
    """
    data = request.get_json()
    user_skills = data.get('user_skills', [])
    target_career = data.get('target_career')
    
    if not user_skills:
        return jsonify({
            'error': 'Missing user_skills',
            'message': 'Please provide user skills'
        }), 400
    
    if not target_career:
        return jsonify({
            'error': 'Missing target_career',
            'message': 'Please provide target career information'
        }), 400
    
    try:
        gap_analysis = skill_gap_detector.detect_gaps(user_skills, target_career)
        return jsonify({
            'success': True,
            'gap_analysis': gap_analysis
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Skill gap detection failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/skill-gap/compare', methods=['POST'])
@login_required
def compare_careers():
    """
    Compare user skills against multiple career options.
    
    Expected JSON payload:
    {
        "user_skills": ["python", "javascript", ...],
        "careers": [
            {"title": "Software Engineer", "required_skills": [...]},
            {"title": "Data Scientist", "required_skills": [...]}
        ]
    }
    
    Returns:
        JSON response with career comparison
    """
    data = request.get_json()
    user_skills = data.get('user_skills', [])
    careers = data.get('careers', [])
    
    if not user_skills:
        return jsonify({
            'error': 'Missing user_skills',
            'message': 'Please provide user skills'
        }), 400
    
    if not careers:
        return jsonify({
            'error': 'Missing careers',
            'message': 'Please provide career options to compare'
        }), 400
    
    try:
        comparison = skill_gap_detector.compare_multiple_careers(user_skills, careers)
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Career comparison failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/roadmap/generate', methods=['POST'])
@login_required
def generate_roadmap():
    """
    Generate career development roadmap.
    
    Expected JSON payload:
    {
        "current_state": {
            "level": "junior",
            "skills": ["python", "javascript"]
        },
        "target_career": {
            "title": "Software Engineer",
            "level": "senior",
            "required_skills": [...]
        },
        "skill_gaps": ["java", "kubernetes"]  (optional)
    }
    
    Returns:
        JSON response with roadmap
    """
    data = request.get_json()
    current_state = data.get('current_state', {})
    target_career = data.get('target_career')
    skill_gaps = data.get('skill_gaps')
    
    if not target_career:
        return jsonify({
            'error': 'Missing target_career',
            'message': 'Please provide target career information'
        }), 400
    
    try:
        roadmap = roadmap_generator.generate_roadmap(current_state, target_career, skill_gaps)
        return jsonify({
            'success': True,
            'roadmap': roadmap
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Roadmap generation failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/roadmap/transition', methods=['POST'])
@login_required
def generate_transition_roadmap():
    """
    Generate career transition roadmap.
    
    Expected JSON payload:
    {
        "from_career": {
            "title": "Current Role",
            "required_skills": [...]
        },
        "to_career": {
            "title": "Target Role",
            "required_skills": [...]
        },
        "current_skills": ["python", "javascript", ...]
    }
    
    Returns:
        JSON response with transition roadmap
    """
    data = request.get_json()
    from_career = data.get('from_career')
    to_career = data.get('to_career')
    current_skills = data.get('current_skills', [])
    
    if not from_career or not to_career:
        return jsonify({
            'error': 'Missing from_career or to_career',
            'message': 'Please provide both current and target career information'
        }), 400
    
    try:
        transition_roadmap = roadmap_generator.generate_transition_roadmap(
            from_career, to_career, current_skills
        )
        return jsonify({
            'success': True,
            'transition_roadmap': transition_roadmap
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Transition roadmap generation failed',
            'message': str(e)
        }), 500


@advanced_bp.route('/report/skill-gap', methods=['POST'])
@login_required
def generate_skill_gap_report():
    """
    Generate skill gap analysis report.
    
    Expected JSON payload:
    {
        "user_skills": ["python", "javascript", ...],
        "target_career": {
            "title": "Software Engineer",
            "required_skills": [...],
            "preferred_skills": [...]
        }
    }
    
    Returns:
        JSON response with skill gap report
    """
    data = request.get_json()
    user_skills = data.get('user_skills', [])
    target_career = data.get('target_career')
    
    if not user_skills or not target_career:
        return jsonify({
            'error': 'Missing user_skills or target_career',
            'message': 'Please provide both user skills and target career'
        }), 400
    
    try:
        report = report_generator.generate_skill_gap_report(user_skills, target_career)
        return jsonify({
            'success': True,
            'report': report
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Report generation failed',
            'message': str(e)
        }), 500
