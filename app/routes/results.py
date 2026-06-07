"""
Results Routes
Handles displaying assessment results and career analysis.
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.assessment import Assessment

results_bp = Blueprint('results', __name__)


@results_bp.route('/results/<int:assessment_id>')
@login_required
def view_assessment_result(assessment_id):
    """View full personality results for a specific completed assessment."""
    assessment = Assessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id
    ).first()

    if not assessment:
        flash('Assessment not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    if assessment.status != 'completed':
        flash('This assessment is not yet completed.', 'warning')
        return redirect(url_for('main.dashboard'))

    # Parse stored scores
    riasec = {}
    big5 = {}
    try:
        if assessment.riasec_scores:
            riasec = json.loads(assessment.riasec_scores)
        if assessment.big5_scores:
            big5 = json.loads(assessment.big5_scores)
    except Exception:
        pass

    # Build full name labels
    big5_labels = {
        'O': 'Openness',
        'C': 'Conscientiousness',
        'E': 'Extraversion',
        'A': 'Agreeableness',
        'N': 'Neuroticism'
    }
    riasec_labels = {
        'R': 'Realistic',
        'I': 'Investigative',
        'A': 'Artistic',
        'S': 'Social',
        'E': 'Enterprising',
        'C': 'Conventional'
    }

    # Build sorted lists for display
    big5_display = [
        {'key': k, 'label': big5_labels.get(k, k), 'score': v}
        for k, v in big5.items()
    ]
    riasec_display = [
        {'key': k, 'label': riasec_labels.get(k, k), 'score': v}
        for k, v in sorted(riasec.items(), key=lambda x: x[1], reverse=True)
    ]

    # Top 2 RIASEC codes for Holland Code
    top2_keys = [item['key'] for item in riasec_display[:2]]
    holland_code = ''.join(top2_keys)

    # DNA type descriptions
    dna_descriptions = {
        'The Analytical Innovator': 'You combine sharp investigative thinking with a love for innovation. You thrive in environments where you can research deeply and design novel solutions.',
        'The Research Creative': 'You blend scientific curiosity with artistic vision. You excel at generating original ideas backed by thorough research.',
        'The Systematic Investigator': 'You are methodical, detail-oriented, and driven by logic. You excel in technical roles requiring precision and deep analytical work.',
        'The Social Scientist': 'You combine empathy with intellectual curiosity. You are excellent at understanding people and systems together.',
        'The Creative Entrepreneur': 'You fuse creative energy with business drive. You are a natural innovator with the charisma to turn ideas into ventures.',
        'The Social Leader': 'You lead with empathy and enthusiasm. You inspire teams and build communities with ease.',
        'The Business Strategist': 'You are organized, goal-driven, and commercially minded. You excel at planning, execution, and business growth.',
        'The Technical Artist': 'You merge hands-on skills with creative expression. You build things that are both functional and beautiful.',
        'The Systematic Builder': 'You are practical, reliable, and love building structured systems. Engineering and construction are natural fits.',
        'The Empathetic Designer': 'You combine social sensitivity with creative design skills. You create experiences that deeply resonate with people.',
        'The Versatile Explorer': 'You have a balanced and adaptable personality. You can thrive across many different career paths and environments.',
    }
    dna_description = dna_descriptions.get(
        assessment.dna_type,
        'Your unique combination of traits opens up a wide variety of fulfilling career paths.'
    )

    # Count how many assessments this user has taken
    all_assessments = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(Assessment.created_at.asc()).all()
    assessment_number = next(
        (i + 1 for i, a in enumerate(all_assessments) if a.id == assessment_id), 1
    )

    from app.utils.scoring import match_careers
    careers = match_careers(riasec, big5)

    return render_template('results.html',
        result=assessment, # Changed from assessment to result to match my template
        riasec=riasec,
        big5=big5,
        careers=careers,
        big5_display=big5_display,
        riasec_display=riasec_display,
        holland_code=holland_code,
        dna_description=dna_description,
        assessment_number=assessment_number,
        total_assessments=len(all_assessments)
    )


@results_bp.route('/results')
@login_required
def view_latest_results():
    """Redirect to the latest completed assessment result."""
    assessment = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(Assessment.completed_at.desc()).first()

    if not assessment:
        flash('Please complete an assessment first.', 'info')
        return redirect(url_for('assessment.start'))

    return redirect(url_for('results.view_assessment_result', assessment_id=assessment.id))


@results_bp.route('/results/<int:assessment_id>/print')
@login_required
def print_assessment_result(assessment_id):
    """Render a standalone, print-ready page for a specific assessment."""
    assessment = Assessment.query.filter_by(
        id=assessment_id,
        user_id=current_user.id
    ).first()

    if not assessment:
        flash('Assessment not found.', 'danger')
        return redirect(url_for('main.dashboard'))

    riasec = {}
    big5 = {}
    try:
        if assessment.riasec_scores:
            riasec = json.loads(assessment.riasec_scores)
        if assessment.big5_scores:
            big5 = json.loads(assessment.big5_scores)
    except Exception:
        pass

    big5_labels = {'O':'Openness','C':'Conscientiousness','E':'Extraversion','A':'Agreeableness','N':'Neuroticism'}
    riasec_labels = {'R':'Realistic','I':'Investigative','A':'Artistic','S':'Social','E':'Enterprising','C':'Conventional'}
    riasec_colors = {'R':'#ea580c','I':'#2563eb','A':'#db2777','S':'#059669','E':'#d97706','C':'#7c3aed'}
    big5_colors = {'O':'#7c3aed','C':'#6366f1','E':'#2563eb','A':'#059669','N':'#d97706'}

    big5_display = [{'key':k,'label':big5_labels.get(k,k),'score':v,'color':big5_colors.get(k,'#7c3aed')} for k,v in big5.items()]
    riasec_display = [{'key':k,'label':riasec_labels.get(k,k),'score':v,'color':riasec_colors.get(k,'#7c3aed')} for k,v in sorted(riasec.items(),key=lambda x:x[1],reverse=True)]

    top2_keys = [item['key'] for item in riasec_display[:2]]
    holland_code = ''.join(top2_keys)

    dna_descriptions = {
        'The Analytical Innovator': 'You combine sharp investigative thinking with a love for innovation. You thrive in environments where you can research deeply and design novel solutions.',
        'The Research Creative': 'You blend scientific curiosity with artistic vision. You excel at generating original ideas backed by thorough research.',
        'The Systematic Investigator': 'You are methodical, detail-oriented, and driven by logic. You excel in technical roles requiring precision and deep analytical work.',
        'The Social Scientist': 'You combine empathy with intellectual curiosity. You are excellent at understanding people and systems together.',
        'The Creative Entrepreneur': 'You fuse creative energy with business drive. You are a natural innovator with the charisma to turn ideas into ventures.',
        'The Social Leader': 'You lead with empathy and enthusiasm. You inspire teams and build communities with ease.',
        'The Business Strategist': 'You are organized, goal-driven, and commercially minded. You excel at planning, execution, and business growth.',
        'The Technical Artist': 'You merge hands-on skills with creative expression. You build things that are both functional and beautiful.',
        'The Systematic Builder': 'You are practical, reliable, and love building structured systems. Engineering and construction are natural fits.',
        'The Empathetic Designer': 'You combine social sensitivity with creative design skills. You create experiences that deeply resonate with people.',
        'The Versatile Explorer': 'You have a balanced and adaptable personality. You can thrive across many different career paths and environments.',
    }
    dna_description = dna_descriptions.get(assessment.dna_type, 'Your unique combination of traits opens up a wide variety of fulfilling career paths.')

    all_assessments = Assessment.query.filter_by(user_id=current_user.id, status='completed').order_by(Assessment.created_at.asc()).all()
    assessment_number = next((i+1 for i,a in enumerate(all_assessments) if a.id==assessment_id), 1)

    return render_template('print_report.html',
        assessment=assessment,
        riasec=riasec,
        big5=big5,
        big5_display=big5_display,
        riasec_display=riasec_display,
        riasec_colors=riasec_colors,
        big5_colors=big5_colors,
        holland_code=holland_code,
        dna_description=dna_description,
        assessment_number=assessment_number,
        total_assessments=len(all_assessments)
    )

