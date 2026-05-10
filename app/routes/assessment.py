"""
Assessment Routes
Handles the 20-question mixed assessment, submission, and analysis.
"""

import json
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.assessment import Assessment
from app.models.answer import Answer
from app.models.profile import Profile
from app.utils.scoring import calculate_scores, load_data, find_question, find_option
from app.services.pipeline_service import run_career_dna_pipeline, run_career_dna_pipeline_from_profile

# Create blueprint
assessment_bp = Blueprint('assessment', __name__)

# Mock agent coordinator (was in original)
class MockAgentCoordinator:
    def process_complete_profile(self, profile, context):
        return {"status": "mocked", "message": "Agent analysis is not yet implemented"}
    def get_agent_status(self):
        return {"agents": []}

agent_coordinator = MockAgentCoordinator()

@assessment_bp.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'success': True, 'message': 'Assessment blueprint working'})

@assessment_bp.route('/start')
@login_required
def start():
    completed_count = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).count()
    
    if completed_count >= 2:
        flash('You have reached the maximum of 2 assessments.', 'warning')
        return render_template('assessment/limit_reached.html', count=completed_count)
    
    return render_template('assessment/take.html', attempt_number=completed_count + 1)

@assessment_bp.route('/api/questions', methods=['GET'])
def get_questions_api():
    questions = load_data('questions.json')
    return jsonify({'questions': questions})

@assessment_bp.route('/submit', methods=['POST'])
@login_required
def submit_assessment():
    try:
        data = request.get_json()
        answers_data = data.get('answers', {})
        questions = load_data('questions.json')
        if isinstance(questions, dict) and 'questions' in questions:
            questions = questions['questions']
        
        # Create assessment record
        assessment = Assessment(
            user_id=current_user.id,
            title='Career DNA Assessment',
            assessment_type='mixed',
            status='in_progress'
        )
        db.session.add(assessment)
        db.session.flush()  # get assessment.id
        
        # Save each answer with ALL fields populated
        for q_id, answer_val in answers_data.items():
            question = find_question(q_id, questions)
            question_text = question['text'] if question else f"Question {q_id}"
            
            # Determine answer text based on question type
            answer_text = str(answer_val)
            if question and question['type'] == 'card_select':
                opt = find_option(question, str(answer_val))
                if opt:
                    answer_text = opt['text']
            
            answer = Answer(
                assessment_id=assessment.id,
                question_id=str(q_id),
                question_text=question_text,    # NEVER pass None
                answer_text=answer_text,   # NEVER pass None
                answer_value=float(answer_val) if str(answer_val).replace('.','',1).isdigit() else 3.0,
                score=float(answer_val) if str(answer_val).replace('.','',1).isdigit() else 3.0,
                category='mixed',
                question_type=question['type'] if question else 'unknown'
            )
            db.session.add(answer)
        
        # Calculate scores
        scores = calculate_scores(answers_data, questions)
        assessment.riasec_scores = json.dumps(scores['riasec'])
        assessment.big5_scores = json.dumps(scores['big5'])
        assessment.dna_type = scores['dna_type']
        assessment.top_career = scores['top_career']
        assessment.status = 'completed'
        assessment.completed_at = datetime.utcnow()
        assessment.calculate_score()
        
        # Gamification: Update user XP and count
        current_user.xp += 50
        db.session.add(current_user)
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'redirect': f'/results/{assessment.id}'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Assessment submit error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@assessment_bp.route('/results/compare')
@login_required
def compare_results():
    assessments = Assessment.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).order_by(Assessment.created_at.asc()).all()
    
    if len(assessments) < 2:
        flash('You need 2 assessments to compare.', 'warning')
        return redirect(url_for('main.dashboard'))
        
    a1 = assessments[0]
    a2 = assessments[1]
    
    a1_riasec = json.loads(a1.riasec_scores) if a1.riasec_scores else {}
    a2_riasec = json.loads(a2.riasec_scores) if a2.riasec_scores else {}
    
    # Calculate shifts
    shifts = {}
    for k in a1_riasec:
        diff = a2_riasec.get(k, 0) - a1_riasec.get(k, 0)
        shifts[k] = diff
        
    return render_template('assessment/compare.html', a1=a1, a2=a2, shifts=shifts,
                           a1_riasec=a1_riasec, a2_riasec=a2_riasec)

@assessment_bp.route('/agent-analysis', methods=['POST'])
@login_required
def agent_analysis():
    # Retained from original
    return jsonify(agent_coordinator.process_complete_profile({}, {}))

@assessment_bp.route('/agent-status', methods=['GET'])
def agent_status():
    return jsonify(agent_coordinator.get_agent_status())

@assessment_bp.route('/pipeline', methods=['POST'])
@login_required
def run_pipeline():
    data = request.get_json() or {}
    source = data.get("source", "profile")
    user_context = data.get("user_context", {})
    
    if source == "assessment":
        assessment_data = data.get("assessment_data")
        if not assessment_data:
            return jsonify({'error': 'Missing assessment_data'}), 400
        assessment_data["user_id"] = current_user.id
        result = run_career_dna_pipeline(assessment_data, user_context)
    else:
        profile = Profile.query.filter_by(user_id=current_user.id).first()
        if not profile or not profile.career_dna:
            return jsonify({'error': 'Profile incomplete'}), 400
        profile_data = {
            'career_dna': profile.career_dna,
            'user_id': current_user.id
        }
        result = run_career_dna_pipeline_from_profile(profile_data, user_context)
        
    return jsonify(result), 200
