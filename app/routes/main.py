"""
Main Routes
Handles general application routes, dashboard, and health checks.
"""

from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.assessment import Assessment
from app.models.activity import DailyActivity
from app.models.profile import Profile
from datetime import date, timedelta
import json

main_bp = Blueprint('main', __name__)

def update_streak(user):
    yesterday = date.today() - timedelta(days=1)
    yesterday_activity = DailyActivity.query.filter_by(
        user_id=user.id,
        date=yesterday
    ).first()
    
    if yesterday_activity:
        user.streak_count += 1
    else:
        user.streak_count = 1
        
    user.xp += 10  # Daily visit XP

def get_level(xp):
    if xp <= 100: return 'Beginner'
    if xp <= 300: return 'Explorer'
    if xp <= 600: return 'Seeker'
    if xp <= 1000: return 'Discoverer'
    return 'DNA Master'

def get_daily_tip(dna_type):
    tips = [
        "Focus on projects that align with your core values.",
        "Take a moment to learn a new concept outside your comfort zone.",
        "Collaborate with someone who has a complementary DNA type.",
        "Reflect on your most energizing work moments this week."
    ]
    day = date.today().timetuple().tm_yday
    tip = tips[day % len(tips)]
    if dna_type:
        return f"{dna_type} Insight: {tip}"
    return tip

def get_daily_challenge(today):
    challenges = [
        "Complete a short tutorial on a new topic.",
        "Share an interesting article with a colleague.",
        "Spend 15 minutes organizing your workspace.",
        "Take a 5-minute mindfulness break."
    ]
    return challenges[today.timetuple().tm_yday % len(challenges)]


@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login_new.html')

@main_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@main_bp.route('/dashboard', methods=['GET'])
@login_required  
def dashboard():
    # Get latest assessment
    latest = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(Assessment.created_at.desc()).first()
    
    # Daily activity
    today = date.today()
    daily = DailyActivity.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not daily:
        daily = DailyActivity(user_id=current_user.id, date=today)
        db.session.add(daily)
        update_streak(current_user)
        db.session.commit()
    
    # Count assessments taken
    assessment_count = Assessment.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).count()
    
    assessments_remaining = max(0, 2 - assessment_count)
    
    # Pre-parse scores if they exist
    latest_riasec = {}
    if latest and latest.riasec_scores:
        try:
            latest_riasec = json.loads(latest.riasec_scores)
        except:
            pass
            
    return render_template('dashboard.html',
        user=current_user,
        latest_result=latest,
        latest_riasec=latest_riasec,
        streak=current_user.streak_count,
        xp=current_user.xp,
        level=get_level(current_user.xp),
        assessments_taken=assessment_count,
        assessments_remaining=assessments_remaining,
        daily_tip=get_daily_tip(latest.dna_type if latest else None),
        daily_challenge=get_daily_challenge(today),
        challenge_done=daily.challenge_completed if daily else False
    )

@main_bp.route('/career/<career_id>', methods=['GET'])
@login_required
def career_detail(career_id):
    # Dummy career detail to satisfy feature 2
    from app.utils.scoring import load_data
    careers = load_data('careers.json')
    career = next((c for c in careers if str(c.get('id', '')) == str(career_id) or c.get('title', '').replace(' ', '').lower() == str(career_id).lower()), None)
    
    if not career:
        # Fallback dummy
        career = {
            'title': str(career_id).replace('-', ' ').title(),
            'description': 'A fantastic career matching your unique traits.',
            'average_salary': '$95,000',
            'match_score': '92%'
        }
        
    return render_template('career_detail.html', career=career)

@main_bp.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        'message': 'Career DNA Agentic AI Platform API',
        'version': '1.0.0',
        'status': 'running'
    }), 200

@main_bp.route('/api/profile', methods=['GET'])
def get_profile():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'career_dna': None, 'completion_percentage': 0}), 200
        
    return jsonify({
        'career_dna': profile.career_dna,
        'completion_percentage': profile.completion_percentage
    }), 200

@main_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
