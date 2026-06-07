class SkillGapAgent:
    """
    Analyzes gap between student's current personality
    strengths and required skills for their top career.
    Generates personalized weekly skill plan.
    """
    
    SKILL_RESOURCES = {
        "Python": {
            "level": "Foundation",
            "time": "4 weeks",
            "free_course": "Python for Everybody - Coursera",
            "youtube": "https://youtube.com/watch?v=rfscVS0vtbw",
            "practice": "HackerRank Python track",
            "milestone": "Build a web scraper"
        },
        "DSA": {
            "level": "Core",
            "time": "8 weeks",
            "free_course": "DSA - Abdul Bari YouTube",
            "youtube": "https://youtube.com/watch?v=RBSGKlAvoiM",
            "practice": "LeetCode easy 50 problems",
            "milestone": "Solve 50 LeetCode problems"
        },
        "Machine Learning": {
            "level": "Advanced",
            "time": "12 weeks",
            "free_course": "Andrew Ng ML Course - Coursera",
            "youtube": "https://youtube.com/watch?v=jGwO_UgTS7I",
            "practice": "Kaggle competitions",
            "milestone": "Complete 1 Kaggle competition"
        },
        "SQL": {
            "level": "Foundation",
            "time": "2 weeks",
            "free_course": "SQL Tutorial - W3Schools",
            "youtube": "https://youtube.com/watch?v=HXV3zeQKqGY",
            "practice": "SQLZoo exercises",
            "milestone": "Build a database project"
        },
        "React": {
            "level": "Core",
            "time": "6 weeks",
            "free_course": "React Full Course - freeCodeCamp",
            "youtube": "https://youtube.com/watch?v=bMknfKXIFA8",
            "practice": "Build 3 React projects",
            "milestone": "Deploy a React app"
        },
        "AWS": {
            "level": "Advanced",
            "time": "8 weeks",
            "free_course": "AWS Cloud Practitioner",
            "youtube": "https://youtube.com/watch?v=ulprqHHWlng",
            "practice": "AWS Free Tier projects",
            "milestone": "Get AWS Cloud Practitioner cert"
        },
        "Figma": {
            "level": "Foundation",
            "time": "3 weeks",
            "free_course": "Figma UI Design Tutorial",
            "youtube": "https://youtube.com/watch?v=FTFaQWZBqQ8",
            "practice": "Redesign 3 existing apps",
            "milestone": "Complete UI portfolio"
        },
        "Docker": {
            "level": "Core",
            "time": "3 weeks",
            "free_course": "Docker Full Course",
            "youtube": "https://youtube.com/watch?v=fqMOX6JJhGo",
            "practice": "Dockerize 2 projects",
            "milestone": "Deploy containerized app"
        },
        "Statistics": {
            "level": "Foundation",
            "time": "4 weeks",
            "free_course": "Statistics for Data Science",
            "youtube": "https://youtube.com/watch?v=xxpc-HPKN28",
            "practice": "Khan Academy statistics",
            "milestone": "Complete statistics project"
        },
        "System Design": {
            "level": "Advanced",
            "time": "6 weeks",
            "free_course": "System Design Primer - GitHub",
            "youtube": "https://youtube.com/watch?v=xpDnVSmNFX0",
            "practice": "Design 5 systems on paper",
            "milestone": "Pass mock system design interview"
        }
    }
    
    def run(self, decision_output: dict) -> dict:
        top_career = decision_output.get('top_career', '')
        riasec = decision_output.get('riasec_scores', {})
        big5 = decision_output.get('big5_scores', {})
        career_recs = decision_output.get(
            'career_recommendations', []
        )
        
        # Get skills needed for top career
        required_skills = []
        if career_recs:
            required_skills = career_recs[0].get(
                'required_skills', []
            )
        
        # Fallback if no skills are found
        if not required_skills:
            required_skills = ["Python", "Problem Solving", "Communication", "Time Management", "Leadership"]
        
        # Build skill plan with resources
        skill_plan = []
        for skill in required_skills[:6]:
            resource = self.SKILL_RESOURCES.get(
                skill,
                {
                    "level": "Core",
                    "time": "4 weeks",
                    "free_course": f"Search: {skill} tutorial",
                    "youtube": "https://youtube.com",
                    "practice": f"Build a {skill} project",
                    "milestone": f"Complete {skill} basics"
                }
            )
            skill_plan.append({
                "skill": skill,
                **resource,
                "priority": self._get_priority(
                    skill, riasec, big5
                )
            })
        
        # Sort by priority
        skill_plan.sort(
            key=lambda x: x['priority'], reverse=True
        )
        
        # Weekly schedule
        weekly_plan = self._build_weekly_plan(skill_plan)
        
        return {
            'required_skills': required_skills,
            'skill_plan': skill_plan,
            'weekly_plan': weekly_plan,
            'total_weeks': sum(
                int(s['time'].split()[0]) 
                for s in skill_plan
            ),
            'start_skill': (
                skill_plan[0]['skill'] if skill_plan else ''
            )
        }
    
    def _get_priority(self, skill, riasec, big5):
        priority_map = {
            "Python": riasec.get('I', 50),
            "DSA": riasec.get('I', 50) * 0.8,
            "Machine Learning": riasec.get('I', 50),
            "SQL": riasec.get('C', 50),
            "React": riasec.get('A', 50),
            "Figma": riasec.get('A', 50) * 1.2,
            "AWS": riasec.get('R', 50),
            "Docker": riasec.get('R', 50) * 0.9,
        }
        return priority_map.get(skill, 50)
    
    def _build_weekly_plan(self, skill_plan):
        weeks = []
        week_num = 1
        for skill_item in skill_plan[:4]:
            skill_weeks = int(
                skill_item['time'].split()[0]
            )
            weeks.append({
                "week_range": (
                    f"Week {week_num}-"
                    f"{week_num + skill_weeks - 1}"
                ),
                "skill": skill_item['skill'],
                "daily_goal": (
                    f"30 mins of {skill_item['skill']} daily"
                ),
                "resource": skill_item['free_course'],
                "milestone": skill_item['milestone']
            })
            week_num += skill_weeks
        return weeks
