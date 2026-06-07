class MentorMatchAgent:
    """
    Matches student to famous mentors/role models
    based on their DNA type and career.
    Shows: who thinks like you, their story,
    their advice quotes, their learning path.
    """
    
    MENTOR_DATABASE = {
        "The Analytical Innovator": [
            {
                "name": "Sundar Pichai",
                "role": "CEO, Google",
                "college": "IIT Kharagpur → Stanford",
                "dna_match": "Investigative + Analytical",
                "photo_initial": "SP",
                "color": "#0d9488",
                "story": "From IIT Kharagpur to leading Google. "
                         "His analytical mindset transformed Chrome "
                         "and Android into billion-user products.",
                "quote": "It's important to follow your dreams "
                         "and heart. Do something that excites you.",
                "advice": [
                    "Master one technical skill deeply",
                    "Always think from user's perspective",
                    "Communication is as important as coding"
                ],
                "his_path": "Engineering → MS Stanford → "
                            "McKinsey → Google → CEO"
            },
            {
                "name": "Demis Hassabis",
                "role": "CEO, Google DeepMind",
                "college": "Cambridge University",
                "dna_match": "Investigative + Creative",
                "photo_initial": "DH",
                "color": "#0d9488",
                "story": "Chess prodigy turned AI researcher. "
                         "Created AlphaGo and AlphaFold, "
                         "solving 50-year-old biology problems.",
                "quote": "Science is the best tool we have "
                         "for understanding the world.",
                "advice": [
                    "Study multiple disciplines deeply",
                    "Work on problems that matter",
                    "Combine creativity with rigor"
                ],
                "his_path": "Chess → Cambridge → Neuroscience "
                            "→ AI Research → DeepMind"
            }
        ],
        "The Creative Architect": [
            {
                "name": "Jony Ive",
                "role": "Former CDO, Apple",
                "college": "Northumbria University",
                "dna_match": "Artistic + Investigative",
                "photo_initial": "JI",
                "color": "#0d9488",
                "story": "Designed iPhone, iMac, MacBook. "
                         "Changed how billions interact with technology "
                         "through obsessive attention to design.",
                "quote": "Design is not just what it looks like. "
                         "Design is how it works.",
                "advice": [
                    "Obsess over the details others ignore",
                    "Simplicity is the ultimate sophistication",
                    "Question every assumption about your design"
                ],
                "his_path": "Art School → Design Agency "
                            "→ Apple → Led design for 27 years"
            }
        ],
        "The Social Strategist": [
            {
                "name": "Satya Nadella",
                "role": "CEO, Microsoft",
                "college": "Manipal Institute → UW-Milwaukee",
                "dna_match": "Social + Enterprising",
                "photo_initial": "SN",
                "color": "#0d9488",
                "story": "Transformed Microsoft from declining "
                         "giant to $3 trillion company through "
                         "empathy-led leadership and cloud vision.",
                "quote": "Empathy makes you a better innovator. "
                         "It is the foundation of everything.",
                "advice": [
                    "Lead with empathy first",
                    "Embrace a growth mindset daily",
                    "Build coalitions, not just products"
                ],
                "his_path": "Manipal → MS USA → Sun → "
                            "Microsoft (30 yrs) → CEO"
            }
        ],
        "The Systematic Builder": [
            {
                "name": "Linus Torvalds",
                "role": "Creator, Linux",
                "college": "University of Helsinki",
                "dna_match": "Realistic + Investigative",
                "photo_initial": "LT",
                "color": "#0d9488",
                "story": "Built Linux as a student project. "
                         "Now powers 90% of the world's servers, "
                         "Android phones, and supercomputers.",
                "quote": "Talk is cheap. Show me the code.",
                "advice": [
                    "Build things that scratch your own itch",
                    "Code quality matters more than speed",
                    "Contribute to open source early"
                ],
                "his_path": "Student Project → Open Source "
                            "→ Linux Foundation → Changed the world"
            }
        ],
        "The Entrepreneurial Visionary": [
            {
                "name": "Narayana Murthy",
                "role": "Founder, Infosys",
                "college": "IIT Kanpur → IIM Ahmedabad",
                "dna_match": "Enterprising + Conventional",
                "photo_initial": "NM",
                "color": "#0d9488",
                "story": "Started Infosys with ₹10,000. "
                         "Built it into a $80B company that "
                         "put Indian IT on the global map.",
                "quote": "Growth is painful. Change is painful. "
                         "But nothing is as painful as staying "
                         "stuck somewhere you don't belong.",
                "advice": [
                    "Integrity is non-negotiable",
                    "Think global from day one",
                    "Surround yourself with people smarter than you"
                ],
                "his_path": "IIT → IIM → Software jobs "
                            "→ Founded Infosys → Global IT leader"
            }
        ]
    }
    
    def run(self, decision_output: dict) -> dict:
        dna_type = decision_output.get('dna_type', '')
        mentors = self.MENTOR_DATABASE.get(
            dna_type,
            self.MENTOR_DATABASE.get(
                'The Analytical Innovator', []
            )
        )
        return {
            'mentors': mentors[:2],
            'primary_mentor': mentors[0] if mentors else None,
            'message': (
                f"People with {dna_type} DNA think like these "
                f"leaders. Study their journey."
            )
        }
