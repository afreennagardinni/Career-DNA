"""
Personality Drift Detection Service
Handles passive signal logging, weekly drift score computations,
targeted micro check-ins scoring, and the complete personality evolution update flow.
"""

from datetime import datetime, timedelta
import random
from app.extensions import db
from app.models.user import User
from app.models.mentor import Mentor
from app.models.notification import Notification
from app.models.skill_plan import SkillPlan
from app.models.personality_drift import (
    PersonalitySignal, PersonalityDriftLog, MicroCheckIn,
    PersonalityHistory, MentorHistory
)

# Constants
OPPOSITES_MAP = {
    "Visionary": "Analytical",
    "Analytical": "Visionary",
    "Creative": "Strategist",
    "Strategist": "Creative",
    "Leader": "Empath",
    "Empath": "Leader"
}

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
        {"name": "Interaction Choreography", "order": 3, "resource": "Motion Design in Web UI", "milestone": "Build an interface with smooth micro-interactions"}
    ],
    "Leader": [
        {"name": "Engineering Management", "order": 1, "resource": "The Manager's Path book", "milestone": "Formulate high-performance OKRs for a dev squad"},
        {"name": "OKR Planning", "order": 2, "resource": "Measure What Matters by John Doerr", "milestone": "Establish quarterly team alignment strategy"},
        {"name": "Agile Scale Frameworks", "order": 3, "resource": "Scaled Agile Guide", "milestone": "Run a multi-squad planning simulation session"}
    ],
    "Empath": [
        {"name": "Developer Relations", "order": 1, "resource": "DevRel Guidebook", "milestone": "Author a high-quality community onboarding tutorial"},
        {"name": "Qualitative Research", "order": 2, "resource": "UX Research Methods", "milestone": "Conduct 5 structured student user empathy interviews"},
        {"name": "Empathy Mapping", "order": 3, "resource": "Design Thinking Empathy Guide", "milestone": "Draft an accessibility roadmap for VTU portal"}
    ],
    "Strategist": [
        {"name": "Management Consulting", "order": 1, "resource": "Case In Point book", "milestone": "Write a 3-year cash flow forecast model for a startup"},
        {"name": "Operations Optimization", "order": 2, "resource": "Lean Six Sigma Toolbox", "milestone": "Perform a bottleneck audit on a real production line"},
        {"name": "SWOT Audit Strategy", "order": 3, "resource": "SWOT Matrix Analysis Guide", "milestone": "Publish a competitive strategy audit on 3 direct rivals"}
    ]
}

MENTOR_KEYWORDS = {
    "Visionary": ["startup", "founder", "future", "innovate", "vision", "disrupt", "roadmap", "strategy", "scale", "market"],
    "Analytical": ["code", "data", "algorithms", "system", "database", "test", "model", "statistics", "math", "analysis"],
    "Creative": ["design", "ui", "ux", "art", "creative", "branding", "prototype", "color", "figma", "layout"],
    "Leader": ["manage", "lead", "team", "negotiate", "okr", "agile", "scrum", "project", "inspire", "culture"],
    "Empath": ["help", "support", "user", "community", "empathy", "research", "inclusive", "accessibility", "feedback"],
    "Strategist": ["swot", "consulting", "finance", "excel", "competitor", "optimization", "operations", "business", "risk"]
}

class PersonalityDriftService:
    """
    Main orchestrator service for the Personality Drift Detection system.
    """

    @staticmethod
    def log_signal(student_id, signal_type, personality_type, weight=1.0):
        """
        Phase 1: Log passive user signal into the PersonalitySignal database.
        """
        signal = PersonalitySignal(
            student_id=student_id,
            signal_type=signal_type,
            personality_type_indicated=personality_type,
            weight=weight,
            created_at=datetime.utcnow()
        )
        db.session.add(signal)
        db.session.commit()
        return signal

    @staticmethod
    def analyze_mentor_message(student_id, message_text):
        """
        Phase 1: Scan student's mentor message for targeted keywords to log MentorTopicSignals.
        """
        text_lower = message_text.lower()
        logged_any = False
        
        for trait, keywords in MENTOR_KEYWORDS.items():
            overlap = [kw for kw in keywords if kw in text_lower]
            if overlap:
                # Log signal for every matching category
                weight = 1.0 + (0.1 * len(overlap))
                PersonalityDriftService.log_signal(
                    student_id=student_id,
                    signal_type="MentorTopicSignal",
                    personality_type_indicated=trait,
                    weight=weight
                )
                logged_any = True
        return logged_any

    @staticmethod
    def calculate_drift(student_id):
        """
        Phase 2: Aggregate signals from the past 7 days, compute score, and check for 2-week consecutive drift.
        Runs as a background/cron simulation helper.
        """
        student = User.query.get(student_id)
        if not student:
            return None

        # Fetch signals from past 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        signals = PersonalitySignal.query.filter(
            PersonalitySignal.student_id == student_id,
            PersonalitySignal.created_at >= seven_days_ago
        ).all()

        if not signals:
            return {
                "success": False,
                "message": "No signals collected in the past 7 days to evaluate drift."
            }

        # Calculate weighted frequencies
        scores = {}
        total_weight = 0.0
        for s in signals:
            ptype = s.personality_type_indicated
            scores[ptype] = scores.get(ptype, 0.0) + s.weight
            total_weight += s.weight

        if total_weight == 0.0:
            return {"success": False, "message": "Total weighted signals sum is zero."}

        # Find dominant type
        dominant_type = max(scores, key=scores.get)
        dominant_weight = scores[dominant_type]
        
        # Drift percentage calculation
        drift_score = (dominant_weight / total_weight) * 100.0
        
        # Check against previous drift logs to track consecutive weeks
        consecutive = 1
        last_log = PersonalityDriftLog.query.filter_by(student_id=student_id).order_by(PersonalityDriftLog.id.desc()).first()
        
        if last_log and last_log.drift_score >= 40.0 and dominant_type == last_log.dominant_signal_type:
            consecutive = last_log.consecutive_weeks + 1

        drift_detected = False
        # If drift percentage >= 40% for 2 consecutive weeks -> flag true
        if drift_score >= 40.0 and consecutive >= 2 and dominant_type != student.personality_type:
            drift_detected = True
            student.drift_detected = True
            student.pending_personality_type = dominant_type
            db.session.add(student)

        # Save result to log
        week_str = datetime.utcnow().strftime('%Y-%m-%d')
        log = PersonalityDriftLog(
            student_id=student_id,
            week_of=week_str,
            dominant_signal_type=dominant_type,
            drift_score=drift_score,
            consecutive_weeks=consecutive,
            drift_detected=drift_detected
        )
        db.session.add(log)
        db.session.commit()

        return {
            "success": True,
            "drift_score": drift_score,
            "dominant_type": dominant_type,
            "consecutive_weeks": consecutive,
            "drift_detected": drift_detected
        }

    @staticmethod
    def get_micro_checkin_questions(dominant_type):
        """
        Phase 3: Returns 5 short scale personality questions mapped to the new dominant type.
        """
        pool = {
            "Visionary": [
                "I constantly generate business or startup concept outlines.",
                "I prioritize innovative, disruptive ideas over step-by-step executions.",
                "I enjoy forecasting long-term industry progressions.",
                "I am comfortable driving project goals when paths are ambiguous.",
                "I focus on high-level goals and delegate operational processes."
            ],
            "Analytical": [
                "I enjoy reading complex system diagrams and structural code layouts.",
                "I rely heavily on mathematical metrics and hypothesis testing rather than intuition.",
                "I prefer breaking coding solutions down into small, structural blocks.",
                "I double-check data integrity and write comprehensive test scripts.",
                "I thrive when diving deep into data modeling or machine learning algorithms."
            ],
            "Creative": [
                "I have high visual sensitivity and notice tiny micro-interaction bugs.",
                "I prioritize visual layout designs, brand aesthetics, and typography highly.",
                "I enjoy prototyping layouts in Figma before starting engineering setups.",
                "I appreciate motion choreography and animated UI transitions.",
                "I love finding unique visual storytelling methods to convey facts."
            ],
            "Leader": [
                "I am comfortable assigning milestones to different project members.",
                "I enjoy structuring agile sprint plans and monitoring squad performance metrics.",
                "I focus on unblocking team issues and resolving collaborative conflicts.",
                "I establish long-term strategic OKRs for my projects.",
                "I take charge of presentation pitches and team architecture."
            ],
            "Empath": [
                "I place deep user empathy interviews over technical performance speed.",
                "I advocate strongly for accessible, inclusive web layout guidelines.",
                "I love organizing, onboarding, and leading developer community forums.",
                "I gather qualitative customer feedback and map out customer empathy matrices.",
                "I enjoy explaining technology to beginners and onboarding newcomers."
            ],
            "Strategist": [
                "I perform detailed SWOT matrix models on competitor startups regularly.",
                "I map project resources in clean Excel operational plans.",
                "I focus heavily on risk management and optimization analytics.",
                "I prefer management consulting over hands-on pixel-pushing layouts.",
                "I follow strict lean processes to organize my daily schedule."
            ]
        }
        
        # Load questions for dominant type (or mix with Visionary/Analytical)
        target_qs = pool.get(dominant_type, pool["Visionary"])
        questions = []
        for i, q in enumerate(target_qs):
            questions.append({
                "id": i + 1,
                "text": q,
                "options": [
                    {"label": "Strongly Disagree", "value": 1},
                    {"label": "Disagree", "value": 2},
                    {"label": "Neutral", "value": 3},
                    {"label": "Agree", "value": 4},
                    {"label": "Strongly Agree", "value": 5}
                ]
            })
        return questions

    @staticmethod
    def process_micro_checkin(student_id, responses):
        """
        Phase 3: Score the 5 micro questions. If average score is >= 3.6, drift is confirmed!
        """
        student = User.query.get(student_id)
        if not student or not student.pending_personality_type:
            return {"success": False, "message": "No pending personality drift detected to confirm."}

        pending_type = student.pending_personality_type
        
        # Calculate score (average of the responses values)
        total_score = sum(int(r) for r in responses.values())
        avg_score = total_score / len(responses)

        confirmed = False
        result_type = "No Change"
        if avg_score >= 3.6:
            confirmed = True
            result_type = pending_type
            
            # Send Notification of Type PersonalityEvolved containing the action links!
            notif = Notification(
                student_id=student_id,
                type="PersonalityEvolved",
                message="Your personality profile has evolved. We've updated your videos, skill plan, and matched you with a new mentor. You can review your personality journey anytime.",
                link_to=f"/profile/journey-update?type={pending_type}",
                is_read=False,
                created_at=datetime.utcnow()
            )
            db.session.add(notif)
        else:
            # Score contradicts signals: reset drift flags, keep current personality
            student.drift_detected = False
            student.pending_personality_type = None
            db.session.add(student)

        # Log to MicroCheckIn database
        checkin_log = MicroCheckIn(
            student_id=student_id,
            questions=PersonalityDriftService.get_micro_checkin_questions(pending_type),
            responses=responses,
            result_type=result_type,
            confirmed_drift=confirmed,
            created_at=datetime.utcnow()
        )
        db.session.add(checkin_log)
        db.session.commit()

        return {
            "success": True,
            "confirmed": confirmed,
            "avg_score": avg_score,
            "result_type": result_type
        }

    @staticmethod
    def apply_personality_update(student_id, new_personality):
        """
        Phase 4: Run the complete system update when the student clicks Accept!
        """
        student = User.query.get(student_id)
        if not student:
            return False

        old_personality = student.personality_type

        # 1. PERSONALITY HISTORY - Archive old profile, do NOT overwrite
        last_hist = PersonalityHistory.query.filter_by(student_id=student_id, end_date=None).first()
        if last_hist:
            last_hist.end_date = datetime.utcnow()
            db.session.add(last_hist)
            
        new_hist = PersonalityHistory(
            student_id=student_id,
            personality_type=new_personality,
            start_date=datetime.utcnow(),
            end_date=None,
            reason="drift_confirmed"
        )
        db.session.add(new_hist)

        # Update student current profile
        student.personality_type = new_personality
        student.drift_detected = False
        student.pending_personality_type = None
        student.personality_changed_at = datetime.utcnow()

        # 2. VIDEOS - Old suggestions stay, new ones are blended
        # Done dynamically in the controller/views!

        # 3. SKILL PLAN - Keep old completed, add new branches labeled 'newly unlocked'
        plan = SkillPlan.query.filter_by(student_id=student_id).first()
        if plan:
            current_skills = list(plan.skills)
            # Fetch new skill roadmap
            target_skills = SKILL_ROADMAPS.get(new_personality, [])
            
            # Map existing skill names to identify duplicates
            existing_names = [s["name"] for s in current_skills]
            
            # Append new branches
            for skill in target_skills:
                if skill["name"] not in existing_names:
                    # Mark new branches
                    new_skill_node = {
                        "name": skill["name"],
                        "order": len(current_skills) + 1,
                        "resource": skill["resource"],
                        "milestone": skill["milestone"],
                        "completed": False,
                        "newly_unlocked": True  # Flag to show in template!
                    }
                    current_skills.append(new_skill_node)
            
            # Update plan JSON
            plan.skills = current_skills
            plan.personality_type = new_personality
            db.session.add(plan)

        # 4. MENTOR RE-MATCH - Assign opposite, archive old
        opposite_trait = OPPOSITES_MAP.get(new_personality, "Analytical")
        new_mentor = Mentor.query.filter_by(personality_type=opposite_trait, is_available=True).first()
        if not new_mentor:
            new_mentor = Mentor.query.filter_by(personality_type=opposite_trait).first()
        if not new_mentor:
            new_mentor = Mentor.query.first()

        if new_mentor and student.assigned_mentor_id != new_mentor.id:
            old_mentor_id = student.assigned_mentor_id
            
            # Archive old mentor assignment in MentorHistory
            if old_mentor_id:
                old_hist = MentorHistory.query.filter_by(student_id=student_id, mentor_id=old_mentor_id, end_date=None).first()
                if old_hist:
                    old_hist.end_date = datetime.utcnow()
                    db.session.add(old_hist)
                else:
                    # fallback
                    db.session.add(MentorHistory(
                        student_id=student_id,
                        mentor_id=old_mentor_id,
                        personality_type=old_personality or "Unknown",
                        start_date=datetime.utcnow() - timedelta(days=14),
                        end_date=datetime.utcnow()
                    ))

            # Assign new mentor
            student.assigned_mentor_id = new_mentor.id
            
            # Log new mentor assignment in MentorHistory
            db.session.add(MentorHistory(
                student_id=student_id,
                mentor_id=new_mentor.id,
                personality_type=new_personality,
                start_date=datetime.utcnow(),
                end_date=None
            ))

        db.session.add(student)
        db.session.commit()
        return True
