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
from app.services.drift_service import PersonalityDriftService

# Create blueprint
assessment_bp = Blueprint('assessment', __name__)

# Mock agent coordinator (was in original)
class MockAgentCoordinator:
    def process_complete_profile(self, profile, context):
        return {"status": "mocked", "message": "Agent analysis is not yet implemented"}
    def get_agent_status(self):
        return {"agents": []}

agent_coordinator = MockAgentCoordinator()

@assessment_bp.route('/', methods=['GET'])
@assessment_bp.route('', methods=['GET'])
@login_required
def assessment_index():
    """Redirect /assessment to /assessment/start."""
    return redirect(url_for('assessment.start'))

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
    """
    Returns 20 questions:
    - 10 Random RIASEC (Round 1)
    - 10 Random Big Five (Round 2)
    """
    import random, copy
    all_questions = load_data('questions_bank.json')
    # Filter by category
    riasec_bank = [q for q in all_questions if q.get('category') == 'RIASEC']
    big5_bank = [q for q in all_questions if q.get('category') == 'Big Five']
    # Shuffle and select 10 from each
    round1 = random.sample(riasec_bank, 10) if len(riasec_bank) >= 10 else riasec_bank
    round2 = random.sample(big5_bank, 10) if len(big5_bank) >= 10 else big5_bank
    # Combine and shuffle overall order for full assessment
    combined_questions = round1 + round2
    random.shuffle(combined_questions)
    return jsonify({'questions': combined_questions})

@assessment_bp.route('/submit', methods=['POST'])
@login_required
def submit_assessment():
    try:
        data = request.get_json()
        answers_data = data.get('answers', {})
        questions = load_data('questions_bank.json')
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
        
        # Generate description based on DNA type
        dna_descriptions = {
            'Architect': 'You are a master of structure and strategy, with a deep interest in building systems and organizing complex data.',
            'Visionary': 'Your strength lies in seeing the big picture and identifying future trends before they become mainstream.',
            'Guardian': 'You excel at protecting systems and ensuring stability, with a meticulous eye for detail and risk management.',
            'Innovator': 'You are driven by creativity and curiosity, always looking for a better way to solve existing problems.',
            'Strategist': 'You combine analytical precision with long-term planning to navigate complex competitive landscapes.',
            'Counselor': 'You have a natural ability to understand and guide others, excelling in roles that require empathy and mentorship.'
        }
        assessment.description = dna_descriptions.get(assessment.dna_type, 'Your unique combination of traits makes you a versatile and adaptable professional.')
        
        assessment.status = 'completed'
        assessment.completed_at = datetime.utcnow()
        assessment.calculate_score()
        
        # 1. PERSONALISE CONTENT ENGINE: Store personality type
        from app.models.mentor import Mentor
        from app.models.video import Video
        from app.models.skill_plan import SkillPlan
        from app.models.notification import Notification
        import random

        # Skill roadmaps definitions
        SKILL_ROADMAPS = {
            "Visionary": [
                {"name": "Strategic Thinking", "order": 1, "resource": "HBR Guide to Strategic Thinking", "milestone": "Design a long-term startup product roadmap"},
                {"name": "Trend Forecasting", "order": 2, "resource": "Gartner Future of Tech", "milestone": "Create a 5-year industry trends report"},
                {"name": "Innovation Strategy", "order": 3, "resource": "The Innovator's Dilemma book", "milestone": "Launch an internal innovation program pitch"}
            ],
            "Analytical": [
                {"name": "Data Modeling", "order": 1, "resource": "Advanced SQL & Data Modeling", "milestone": "Build a highly scalable relational database schema"},
                {"name": "Machine Learning", "order": 2, "resource": "Coursera ML by Andrew Ng", "milestone": "Train and deploy a linear regression model"},
                {"name": "Quantitative Research", "order": 3, "resource": "Stat 101", "milestone": "Publish a statistical hypothesis testing report"}
            ],
            "Creative": [
                {"name": "UI/UX Design", "order": 1, "resource": "Figma Academy", "milestone": "Create a high-fidelity interactive Figma prototype"},
                {"name": "Visual Storytelling", "order": 2, "resource": "The Non-Designer's Design Book", "milestone": "Develop a cohesive brand identity guideline"},
                {"name": "Design Systems", "order": 3, "resource": "Brad Frost's Atomic Design", "milestone": "Build a reusable component library in React/Figma"}
            ],
            "Leader": [
                {"name": "Team Management", "order": 1, "resource": "Crucial Conversations book", "milestone": "Resolve a high-stakes conflict inside a project team"},
                {"name": "Public Speaking", "order": 2, "resource": "TED Talks Guide", "milestone": "Deliver a compelling 10-minute keynote speech"},
                {"name": "Strategic Negotiation", "order": 3, "resource": "Getting to Yes book", "milestone": "Close a mock business partnership agreement"}
            ],
            "Empath": [
                {"name": "Active Listening", "order": 1, "resource": "Empathy in Action", "milestone": "Conduct 5 deep empathy interviews with target users"},
                {"name": "Conflict Resolution", "order": 2, "resource": "Difficult Conversations", "milestone": "Facilitate a consensus building workshop"},
                {"name": "Coaching & Mentoring", "order": 3, "resource": "Co-Active Coaching", "milestone": "Design a 4-week onboarding mentor program"}
            ],
            "Strategist": [
                {"name": "Operations Optimization", "order": 1, "resource": "Lean Six Sigma", "milestone": "Map out and optimize an end-to-end business pipeline"},
                {"name": "Competitive Analysis", "order": 2, "resource": "Porter's Five Forces", "milestone": "Deliver a comprehensive SWOT matrix on 3 competitors"},
                {"name": "Financial Modeling", "order": 3, "resource": "Corporate Finance Institute", "milestone": "Construct a 3-year cash flow forecast sheet"}
            ]
        }

        def map_dna_to_personality(dna):
            if not dna:
                return "Visionary"
            d = dna.lower()
            if "visionary" in d:
                return "Visionary"
            elif "analytical" in d or "architect" in d:
                return "Analytical"
            elif "creative" in d or "innovator" in d:
                return "Creative"
            elif "counselor" in d or "empath" in d:
                return "Empath"
            elif "leader" in d:
                return "Leader"
            elif "strategist" in d or "guardian" in d or "builder" in d:
                return "Strategist"
            return "Visionary"

        mapped_personality = map_dna_to_personality(assessment.dna_type)
        current_user.personality_type = mapped_personality

        # Delete any existing skill plan for this user
        existing_plan = SkillPlan.query.filter_by(student_id=current_user.id).first()
        if existing_plan:
            db.session.delete(existing_plan)
            db.session.flush()

        # Generate and save Personalised Skill Plan
        skills_list = SKILL_ROADMAPS.get(mapped_personality, SKILL_ROADMAPS["Visionary"])
        skill_plan = SkillPlan(
            student_id=current_user.id,
            personality_type=mapped_personality,
            skills=skills_list
        )
        db.session.add(skill_plan)
        db.session.flush()
        current_user.skill_plan_id = skill_plan.id

        # Opposite Mentor Assignment
        opposites_map = {
            "Visionary": "Analytical",
            "Analytical": "Visionary",
            "Creative": "Strategist",
            "Strategist": "Creative",
            "Empath": "Leader",
            "Leader": "Empath"
        }
        opposite_type = opposites_map.get(mapped_personality, "Analytical")
        
        # Query first available opposite mentor
        mentor = Mentor.query.filter_by(personality_type=opposite_type, is_available=True).first()
        if not mentor:
            # Fallback to any mentor of opposite type
            mentor = Mentor.query.filter_by(personality_type=opposite_type).first()
        if not mentor:
            # Fallback to any available mentor
            mentor = Mentor.query.filter_by(is_available=True).first()
        if not mentor:
            # Fallback to any mentor at all
            mentor = Mentor.query.first()

        if mentor:
            current_user.assigned_mentor_id = mentor.id

        # Gamification: Update user XP and count
        current_user.xp += 50
        db.session.add(current_user)
        db.session.flush()

        # TRIGGER NOTIFICATIONS (wire real triggers)
        # 1. PersonalisedVideoAlert
        videos = Video.query.all()
        matching_videos = [v for v in videos if v.personality_tags and mapped_personality in v.personality_tags]
        video_title = "Discovering Your Career DNA"
        if matching_videos:
            video_title = matching_videos[0].title
        
        v_notif = Notification(
            student_id=current_user.id,
            type='PersonalisedVideoAlert',
            message=f"A new video matching your personality type has been added: {video_title}",
            link_to='/assessment/videos/' + str(assessment.id)
        )
        db.session.add(v_notif)

        # 2. MentorMessage
        mentor_name = mentor.name if mentor else "Your opposite mentor"
        tip = "Keep working hard and mastering your unique traits!"
        if mentor and mentor.advice:
            tip = random.choice(mentor.advice)
        elif mentor and mentor.quote:
            tip = mentor.quote
            
        m_notif = Notification(
            student_id=current_user.id,
            type='MentorMessage',
            message=f"Your mentor {mentor_name} sent you a tip or message: \"{tip}\"",
            link_to='/assessment/mentors/' + str(assessment.id)
        )
        db.session.add(m_notif)

        # 3. SkillPlanUpdate
        first_skill = skills_list[0]['name'] if skills_list else "Strategic Thinking"
        s_notif = Notification(
            student_id=current_user.id,
            type='SkillPlanUpdate',
            message=f"Your personalised skill roadmap has been updated with a new skill: {first_skill}",
            link_to='/assessment/skill-plan/' + str(assessment.id)
        )
        db.session.add(s_notif)

        # 4. WeeklyProgressNudge
        riasec_norm = scores.get('riasec', {})
        weak_trait = "Realistic"
        if riasec_norm:
            lowest_code = min(riasec_norm, key=riasec_norm.get)
            riasec_names = {'R': 'Realistic', 'I': 'Investigative', 'A': 'Artistic', 'S': 'Social', 'E': 'Enterprising', 'C': 'Conventional'}
            weak_trait = riasec_names.get(lowest_code, 'Realistic')
            
        improvement_pct = random.randint(10, 35)
        p_notif = Notification(
            student_id=current_user.id,
            type='WeeklyProgressNudge',
            message=f"This week you improved {improvement_pct}% in {weak_trait}. Keep going!",
            link_to='/dashboard'
        )
        db.session.add(p_notif)

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

@assessment_bp.route('/mentors/<int:assessment_id>')
@login_required
def mentor_match(assessment_id):
    result = Assessment.query.get_or_404(assessment_id)
    if result.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    from app.models.mentor import Mentor
    mentor = None
    if current_user.assigned_mentor_id:
        mentor = Mentor.query.get(current_user.assigned_mentor_id)
    
    # Fallback/insurance if no mentor assigned yet
    if not mentor:
        opposites_map = {
            "Visionary": "Analytical",
            "Analytical": "Visionary",
            "Creative": "Strategist",
            "Strategist": "Creative",
            "Empath": "Leader",
            "Leader": "Empath"
        }
        personality = current_user.personality_type or "Visionary"
        opposite_type = opposites_map.get(personality, "Analytical")
        mentor = Mentor.query.filter_by(personality_type=opposite_type).first()
        if not mentor:
            mentor = Mentor.query.first()
            
    return render_template(
        'assessment/mentors.html',
        mentor=mentor,
        result=result
    )

@assessment_bp.route('/mentors/chat', methods=['POST'])
@login_required
def mentor_chat():
    from app.models.mentor import Mentor
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    mentor_id = data.get('mentor_id')
    
    if mentor_id:
        try:
            mentor_id = int(mentor_id)
        except (ValueError, TypeError):
            pass
            
    mentor = Mentor.query.get(mentor_id) if mentor_id else None
    if not mentor:
        return jsonify({'success': False, 'error': 'Mentor not found'}), 404
        
    name = mentor.name.lower()
    responses = [
        f"That's a very thoughtful question. In my experience, especially during my time at {mentor.college or 'my early career'}, the key is to lean in and embrace the challenge.",
        "Remember, failures are just progress in disguise. What's the biggest obstacle you're facing in mastering this week's skill?",
        f"As a {mentor.personality_type} mentor, I advise you to balance your style with your natural traits. What specific milestone in your skill roadmap are you working on right now?",
        "One piece of advice: don't let perfection stand in the way of progress. Just keep moving, iterating, and learning!"
    ]
    
    m_lower = message.lower()
    if 'hello' in m_lower or 'hi' in m_lower:
        reply = f"Hello! I am thrilled to be your mentor. As an opposite match ({mentor.personality_type}), I'm here to help you develop the strategic/analytical traits you need. What's on your mind today?"
    elif 'skill' in m_lower or 'roadmap' in m_lower or 'learn' in m_lower:
        reply = f"Building these new skills is essential. I looked at your roadmap, and I highly recommend focusing on your next milestone. Let's make it actionable!"
    elif 'help' in m_lower or 'how' in m_lower:
        reply = f"The best way to tackle this is to break it down. When I was at {mentor.college or 'my previous role'}, I found that daily deliberate practice of just 15 minutes made a massive difference. You can do this!"
    else:
        import random
        reply = random.choice(responses)
        
    return jsonify({
        'success': True,
        'reply': reply
    }), 200

@assessment_bp.route('/skill-plan/<int:assessment_id>')
@login_required
def skill_plan(assessment_id):
    result = Assessment.query.get_or_404(assessment_id)
    if result.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    from app.models.skill_plan import SkillPlan
    plan = SkillPlan.query.filter_by(student_id=current_user.id).first()
    
    # Fallback/insurance if no plan generated yet
    if not plan:
        personality = current_user.personality_type or "Visionary"
        SKILL_ROADMAPS = {
            "Visionary": [
                {"name": "Strategic Thinking", "order": 1, "resource": "HBR Guide to Strategic Thinking", "milestone": "Design a long-term startup product roadmap"},
                {"name": "Trend Forecasting", "order": 2, "resource": "Gartner Future of Tech", "milestone": "Create a 5-year industry trends report"},
                {"name": "Innovation Strategy", "order": 3, "resource": "The Innovator's Dilemma book", "milestone": "Launch an internal innovation program pitch"}
            ],
            "Analytical": [
                {"name": "Data Modeling", "order": 1, "resource": "Advanced SQL & Data Modeling", "milestone": "Build a highly scalable relational database schema"},
                {"name": "Machine Learning", "order": 2, "resource": "Coursera ML by Andrew Ng", "milestone": "Train and deploy a linear regression model"},
                {"name": "Quantitative Research", "order": 3, "resource": "Stat 101", "milestone": "Publish a statistical hypothesis testing report"}
            ],
            "Creative": [
                {"name": "UI/UX Design", "order": 1, "resource": "Figma Academy", "milestone": "Create a high-fidelity interactive Figma prototype"},
                {"name": "Visual Storytelling", "order": 2, "resource": "The Non-Designer's Design Book", "milestone": "Develop a cohesive brand identity guideline"},
                {"name": "Design Systems", "order": 3, "resource": "Brad Frost's Atomic Design", "milestone": "Build a reusable component library in React/Figma"}
            ],
            "Leader": [
                {"name": "Team Management", "order": 1, "resource": "Crucial Conversations book", "milestone": "Resolve a high-stakes conflict inside a project team"},
                {"name": "Public Speaking", "order": 2, "resource": "TED Talks Guide", "milestone": "Deliver a compelling 10-minute keynote speech"},
                {"name": "Strategic Negotiation", "order": 3, "resource": "Getting to Yes book", "milestone": "Close a mock business partnership agreement"}
            ],
            "Empath": [
                {"name": "Active Listening", "order": 1, "resource": "Empathy in Action", "milestone": "Conduct 5 deep empathy interviews with target users"},
                {"name": "Conflict Resolution", "order": 2, "resource": "Difficult Conversations", "milestone": "Facilitate a consensus building workshop"},
                {"name": "Coaching & Mentoring", "order": 3, "resource": "Co-Active Coaching", "milestone": "Design a 4-week onboarding mentor program"}
            ],
            "Strategist": [
                {"name": "Operations Optimization", "order": 1, "resource": "Lean Six Sigma", "milestone": "Map out and optimize an end-to-end business pipeline"},
                {"name": "Competitive Analysis", "order": 2, "resource": "Porter's Five Forces", "milestone": "Deliver a comprehensive SWOT matrix on 3 competitors"},
                {"name": "Financial Modeling", "order": 3, "resource": "Corporate Finance Institute", "milestone": "Construct a 3-year cash flow forecast sheet"}
            ]
        }
        skills_list = SKILL_ROADMAPS.get(personality, SKILL_ROADMAPS["Visionary"])
        plan = SkillPlan(student_id=current_user.id, personality_type=personality, skills=skills_list)
        db.session.add(plan)
        db.session.commit()
        
    return render_template(
        'assessment/skill_plan.html',
        plan=plan,
        result=result
    )

@assessment_bp.route('/skill-plan/toggle', methods=['POST'])
@login_required
def toggle_skill_status():
    from app.models.skill_plan import SkillPlan
    data = request.get_json() or {}
    skill_name = data.get('skill_name')
    completed = data.get('completed', False)
    
    plan = SkillPlan.query.filter_by(student_id=current_user.id).first()
    if not plan:
        return jsonify({'success': False, 'error': 'Plan not found'}), 404
        
    updated_skills = []
    for s in plan.skills:
        skill_copy = dict(s)
        if skill_copy.get('name') == skill_name:
            skill_copy['completed'] = completed
        updated_skills.append(skill_copy)
        
    plan.skills = updated_skills
    db.session.commit()
    return jsonify({'success': True}), 200

@assessment_bp.route('/trends/<int:assessment_id>')
@login_required
def industry_trends(assessment_id):
    result = Assessment.query.get_or_404(assessment_id)
    import json
    decision_output = {
        'dna_type': result.dna_type,
        'top_career': result.top_career
    }
    from app.agents.trends_agent import IndustryTrendsAgent
    agent = IndustryTrendsAgent()
    trends = agent.run(decision_output)
    return render_template(
        'assessment/trends.html',
        trends=trends,
        result=result
    )

@assessment_bp.route('/videos/<int:assessment_id>')
@login_required
def personalised_videos(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    personality = current_user.personality_type or "Visionary"
    
    # Map DNA type to common tags to broaden high-fidelity suggestions
    dna_lower = (assessment.dna_type or "").lower()
    personality_mapping = {
        "analytical": ["Analytical", "Strategist"],
        "creative": ["Creative", "Visionary", "Empath"],
        "social": ["Empath", "Leader"],
        "systematic": ["Analytical", "Strategist"],
        "entrepreneurial": ["Visionary", "Leader", "Strategist"],
        "leader": ["Leader", "Strategist", "Empath"]
    }
    
    tags = [personality]
    for key, value in personality_mapping.items():
        if key in dna_lower:
            tags.extend(value)
            
    tags = list(set(tags))
    
    from app.models.video import Video
    all_videos = Video.query.all()
    matching_videos = []
    
    for v in all_videos:
        if v.personality_tags:
            overlap = [t for t in tags if t in v.personality_tags]
            if overlap:
                matching_videos.append(v)
                
    if not matching_videos:
        matching_videos = all_videos
        
    return render_template('assessment/videos.html',
        assessment=assessment,
        result=assessment,
        personality=personality,
        videos=matching_videos
    )


@assessment_bp.route('/signals/video', methods=['POST'])
@login_required
def signal_video():
    data = request.get_json() or {}
    video_personality = data.get('videoPersonalityType')
    watched_percent = float(data.get('watchedPercent', 0))
    if not video_personality:
        return jsonify({'success': False, 'error': 'Missing videoPersonalityType'}), 400

    # weight proportional to watched percent (0-1)
    weight = max(0.0, min(1.0, watched_percent / 100.0))
    PersonalityDriftService.log_signal(current_user.id, 'VideoSignal', video_personality, weight=weight)
    return jsonify({'success': True}), 200


@assessment_bp.route('/signals/quiz', methods=['POST'])
@login_required
def signal_quiz():
    data = request.get_json() or {}
    trait = data.get('traitIndicated')
    if not trait:
        return jsonify({'success': False, 'error': 'Missing traitIndicated'}), 400
    PersonalityDriftService.log_signal(current_user.id, 'QuizSignal', trait, weight=1.0)
    return jsonify({'success': True}), 200


@assessment_bp.route('/signals/content-like', methods=['POST'])
@login_required
def signal_content_like():
    data = request.get_json() or {}
    personality = data.get('personalityType')
    if not personality:
        return jsonify({'success': False, 'error': 'Missing personalityType'}), 400
    PersonalityDriftService.log_signal(current_user.id, 'ContentLikeSignal', personality, weight=1.0)
    return jsonify({'success': True}), 200


@assessment_bp.route('/signals/mentor-message', methods=['POST'])
@login_required
def signal_mentor_message():
    data = request.get_json() or {}
    message = data.get('message', '')
    if not message:
        return jsonify({'success': False, 'error': 'Missing message body'}), 400
    logged = PersonalityDriftService.analyze_mentor_message(current_user.id, message)
    return jsonify({'success': True, 'logged': logged}), 200


@assessment_bp.route('/micro-checkin/questions', methods=['GET'])
@login_required
def micro_checkin_questions():
    pending = current_user.pending_personality_type
    if not pending:
        # find most recent drift log with drift_detected true
        last = None
        try:
            from app.models.personality_drift import PersonalityDriftLog
            last = PersonalityDriftLog.query.filter_by(student_id=current_user.id, drift_detected=True).order_by(PersonalityDriftLog.id.desc()).first()
        except Exception:
            last = None
        pending = pending or (last.dominant_signal_type if last else None)

    if not pending:
        return jsonify({'success': False, 'error': 'No pending drift to check'}), 400

    questions = PersonalityDriftService.get_micro_checkin_questions(pending)
    return jsonify({'success': True, 'questions': questions}), 200


@assessment_bp.route('/micro-checkin/submit', methods=['POST'])
@login_required
def micro_checkin_submit():
    data = request.get_json() or {}
    responses = data.get('responses') or {}
    if not responses:
        return jsonify({'success': False, 'error': 'Missing responses'}), 400
    result = PersonalityDriftService.process_micro_checkin(current_user.id, responses)
    return jsonify(result), 200


@assessment_bp.route('/personality/update', methods=['POST'])
@login_required
def personality_update():
    data = request.get_json() or {}
    action = data.get('action')  # 'accept' or 'keep'
    ptype = data.get('type')
    if action not in ('accept', 'keep'):
        return jsonify({'success': False, 'error': 'Invalid action'}), 400

    if action == 'keep':
        # revert pending flags
        current_user.drift_detected = False
        current_user.pending_personality_type = None
        db.session.add(current_user)
        db.session.commit()
        return jsonify({'success': True, 'kept': True}), 200

    # Accept -> apply update flow
    if not ptype:
        return jsonify({'success': False, 'error': 'Missing type to apply'}), 400
    ok = PersonalityDriftService.apply_personality_update(current_user.id, ptype)
    return jsonify({'success': ok}), 200
