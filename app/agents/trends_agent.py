"""
Industry Trends Agent
Provides market insights, emerging tech, hot skills, and top company data
tailored to the student's personality type and DNA profile.
"""

class IndustryTrendsAgent:
    """
    Shows current tech industry trends deeply personalized to
    the student's core personality type.
    """
    
    PERSONALITY_TRENDS = {
        "Visionary": {
            "career": "Product Visionary / AI Product Manager",
            "hot_skills": [
                "Generative AI Integration", "Product Roadmapping",
                "Trend Forecasting", "Venture Architecture", "Growth Hacking"
            ],
            "salary_trend": "↑ 28% YoY in India",
            "avg_salary_india": "₹18-40 LPA (3-5 yrs exp)",
            "top_hiring": [
                "OpenAI", "Google DeepMind", "Tesla", "Razorpay", "CRED"
            ],
            "emerging_tech": "Autonomous Multi-Agent Swarms & Cognitive PM",
            "job_market": "Very High Growth Demand",
            "india_insight": "SaaS and AI-first product companies in Bengaluru/Pune are actively recruiting forward-thinking product leads.",
            "vtu_companies": [
                "Infosys Consulting", "Cognizant R&D", "ThoughtWorks", "Mindtree Future Tech"
            ]
        },
        "Analytical": {
            "career": "AI Scientist / ML Systems Engineer",
            "hot_skills": [
                "PyTorch & JAX", "Vector DBs & RAG",
                "MLOps Pipelines", "Advanced Data Modeling", "CUDA Programming"
            ],
            "salary_trend": "↑ 35% YoY in India",
            "avg_salary_india": "₹22-55 LPA (3-5 yrs exp)",
            "top_hiring": [
                "Microsoft AI", "Google", "Sarvam AI", "Krutrim AI", "NVIDIA India"
            ],
            "emerging_tech": "Small Language Models (SLMs) & Edge AI Computing",
            "job_market": "Critical Shortage of Premium Talent",
            "india_insight": "Deep-tech venture investments in Bengaluru rose 45%, with a massive focus on technical engineering roles.",
            "vtu_companies": [
                "Samsung R&D", "Bosch Research", "Intel India", "Qualcomm India"
            ]
        },
        "Creative": {
            "career": "UI/UX Lead / Spatial Experience Architect",
            "hot_skills": [
                "Figma Advanced Design Systems", "Spatial/AR Prototyping",
                "Motion Design", "Interaction Choreography", "AI-assisted Design"
            ],
            "salary_trend": "↑ 24% YoY in India",
            "avg_salary_india": "₹14-32 LPA (3-5 yrs exp)",
            "top_hiring": [
                "Apple India", "Airbnb Design Labs", "Zomato Design", "Swiggy UX", "PhonePe Studios"
            ],
            "emerging_tech": "Spatial Computing, visionOS Layouts & Generative Motion UX",
            "job_market": "High Demand for Aesthetic Engineers",
            "india_insight": "Fintech and consumer tech hubs are willing to pay top compensation for designers who bridge technical front-ends.",
            "vtu_companies": [
                "TCS Interactive", "Wipro Designit", "Cognizant Digital Experience", "Mphasis Design"
            ]
        },
        "Leader": {
            "career": "Engineering Manager / Venture Architect",
            "hot_skills": [
                "Agile Scale Frameworks", "Team Topologies",
                "OKR Planning", "High-Performance Management", "Strategic Negotiation"
            ],
            "salary_trend": "↑ 20% YoY in India",
            "avg_salary_india": "₹24-60 LPA (5+ yrs exp)",
            "top_hiring": [
                "McKinsey & Co", "Stripe India", "JPMorgan Chase", "Flipkart", "Atlassian"
            ],
            "emerging_tech": "Autonomous AI Team Orchestration & Smart-Contract Governance",
            "job_market": "Strong Global Demand",
            "india_insight": "Rotational leadership and technology governance roles are rapidly expanding in Hyderabad and Mumbai corporate hubs.",
            "vtu_companies": [
                "HCL Technologies", "TCS Enterprise", "Capgemini India", "Accenture Strategy"
            ]
        },
        "Empath": {
            "career": "Developer Relations Manager / UX Researcher",
            "hot_skills": [
                "Developer Relations (DevRel)", "Qualitative User Research",
                "Community Orchestration", "Empathy Mapping", "Technical Evangelism"
            ],
            "salary_trend": "↑ 26% YoY in India",
            "avg_salary_india": "₹15-35 LPA (3-5 yrs exp)",
            "top_hiring": [
                "GitHub India", "Vercel", "Supabase", "Postman", "HashiCorp"
            ],
            "emerging_tech": "AI-driven Sentiment Analysis & Inclusive Design Paradigms",
            "job_market": "Rapidly Emerging Sector",
            "india_insight": "Dev-first SaaS companies are opening major Developer Relations and Customer Success units in Bengaluru and Pune.",
            "vtu_companies": [
                "ThoughtWorks DX", "LTIMindtree Digital", "Wipro Dev Studio", "Hexaware Labs"
            ]
        },
        "Strategist": {
            "career": "Management Consultant / Operations Optimizer",
            "hot_skills": [
                "Six Sigma & Lean", "Competitor SWOT Audit",
                "Financial Modeling", "Corporate Strategy Planning", "BI Analytics"
            ],
            "salary_trend": "↑ 22% YoY in India",
            "avg_salary_india": "₹16-38 LPA (3-5 yrs exp)",
            "top_hiring": [
                "BCG India", "Bain & Company", "Deloitte Tech Strategy", "Amazon Logistics", "Uber Ops"
            ],
            "emerging_tech": "Decision Intelligence Platforms & Hyper-automation Systems",
            "job_market": "Steady Strategic Demand",
            "india_insight": "Supply chain optimization and consultancies in Gurgaon and Mumbai are premium recruiters of strategic thinkers.",
            "vtu_companies": [
                "Tech Mahindra Consulting", "EY India", "PwC Tech Strategy", "Mphasis Analytics"
            ]
        }
    }
    
    def run(self, decision_output: dict) -> dict:
        dna_type = decision_output.get('dna_type', '')
        
        # Map dna_type to a primary personality type
        personality = "Visionary"
        dna_lower = dna_type.lower()
        
        if "analytical" in dna_lower or "investigator" in dna_lower or "research" in dna_lower or "architect" in dna_lower:
            personality = "Analytical"
        elif "creative" in dna_lower or "artist" in dna_lower or "designer" in dna_lower or "innovator" in dna_lower:
            personality = "Creative"
        elif "leader" in dna_lower:
            personality = "Leader"
        elif "empath" in dna_lower or "counselor" in dna_lower or "social" in dna_lower:
            personality = "Empath"
        elif "strategist" in dna_lower or "systematic" in dna_lower or "builder" in dna_lower or "business" in dna_lower or "guardian" in dna_lower:
            personality = "Strategist"
            
        trends = self.PERSONALITY_TRENDS.get(personality, self.PERSONALITY_TRENDS["Visionary"])
        
        return {
            'personality': personality,
            'dna_type': dna_type,
            'career': trends['career'],
            'hot_skills': trends['hot_skills'][:5],
            'salary_trend': trends['salary_trend'],
            'avg_salary': trends['avg_salary_india'],
            'top_companies': trends['top_hiring'][:5],
            'vtu_companies': trends.get('vtu_companies', [])[:4],
            'emerging_tech': trends['emerging_tech'],
            'job_market': trends['job_market'],
            'india_insight': trends['india_insight'],
            'action': f"Master {trends['hot_skills'][0]} to leverage your {personality} superpowers."
        }
