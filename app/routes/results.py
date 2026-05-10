"""
Results Routes
Handles displaying assessment results and career analysis.
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models.assessment import Assessment
from app.models.profile import Profile
from app.services.pipeline_service import run_career_dna_pipeline_from_profile

# Create blueprint
results_bp = Blueprint('results', __name__)


@results_bp.route('/results/<int:assessment_id>')
@login_required
def view_assessment_result(assessment_id):
    """
    View results for a specific assessment.
    
    Args:
        assessment_id: ID of the assessment to view results for
        
    Returns:
        Rendered results template with assessment data
    """
    # Get assessment
    assessment = Assessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id
    ).first()
    
    if not assessment:
        return render_template('error.html', 
                           error='Assessment not found',
                           message='The assessment you are looking for does not exist or does not belong to you.'), 404
    
    # Get user profile for complete analysis
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    if not profile or not profile.career_dna:
        return render_template('error.html',
                           error='Profile incomplete',
                           message='Please complete both Big Five and RIASEC assessments to view detailed results.'), 400
    
    # Prepare profile data for pipeline
    profile_data = {
        'career_dna': profile.career_dna,
        'user_id': current_user.id
    }
    
    # Get user context from request
    user_context = request.args.to_dict() or {}
    
    # Run pipeline analysis
    try:
        result = run_career_dna_pipeline_from_profile(profile_data, user_context)
        
        # Add assessment-specific data
        result['assessment'] = assessment.to_dict()
        result['assessment_type'] = assessment.assessment_type
        
        return render_template('results.html', 
                           result_data=result,
                           assessment=assessment)
    
    except Exception as e:
        return render_template('error.html',
                           error='Analysis failed',
                           message=f'Failed to generate results: {str(e)}'), 500


@results_bp.route('/results')
@login_required
def view_latest_results():
    """
    View results for the user's latest completed assessment.
    
    Returns:
        Rendered results template with latest assessment data
    """
    # Get latest completed assessment
    assessment = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(Assessment.completed_at.desc()).first()
    
    if not assessment:
        return render_template('error.html',
                           error='No completed assessments',
                           message='Please complete an assessment to view your results.'), 404
    
    # Redirect to specific assessment result
    return view_assessment_result(assessment.id)


@results_bp.route('/api/results/<int:assessment_id>')
@login_required
def get_assessment_result_api(assessment_id):
    """
    Get assessment results as JSON API.
    
    Args:
        assessment_id: ID of the assessment
        
    Returns:
        JSON response with assessment results
    """
    # Get assessment
    assessment = Assessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id
    ).first()
    
    if not assessment:
        return jsonify({
            'error': 'Assessment not found',
            'message': 'Assessment does not exist or does not belong to you'
        }), 404
    
    # Get user profile
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    if not profile or not profile.career_dna:
        return jsonify({
            'error': 'Profile incomplete',
            'message': 'Please complete both assessments to view results'
        }), 400
    
    # Prepare profile data
    profile_data = {
        'career_dna': profile.career_dna,
        'user_id': current_user.id
    }
    
    # Get user context from request
    user_context = request.args.to_dict() or {}
    
    try:
        # Run pipeline analysis
        result = run_career_dna_pipeline_from_profile(profile_data, user_context)
        
        # Add assessment data
        result['assessment'] = assessment.to_dict()
        result['assessment_type'] = assessment.assessment_type
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Analysis failed',
            'message': f'Failed to generate results: {str(e)}'
        }), 500


@results_bp.route('/api/results/latest')
@login_required
def get_latest_results_api():
    """
    Get latest assessment results as JSON API.
    
    Returns:
        JSON response with latest assessment results
    """
    # Get latest completed assessment
    assessment = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(Assessment.completed_at.desc()).first()
    
    if not assessment:
        return jsonify({
            'error': 'No completed assessments',
            'message': 'Please complete an assessment to view results'
        }), 404
    
    # Redirect to specific assessment API
    return get_assessment_result_api(assessment.id)
