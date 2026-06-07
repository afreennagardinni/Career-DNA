class VideoRecommendationAgent:
    """
    Based on student's DNA type and top career,
    recommends curated YouTube videos for:
    1. Motivation videos matching personality
    2. Career-specific learning videos
    3. Skill development videos
    4. Daily inspiration based on DNA type
    """
    
    # Curated video database per DNA type
    VIDEO_DATABASE = {
        "The Analytical Innovator": {
            "motivation": [
                {
                    "title": "How Great Leaders Think",
                    "channel": "TED",
                    "url": "https://youtube.com/watch?v=qp0HIF3SfI4",
                    "duration": "18 min",
                    "why": "Matches your analytical thinking style",
                    "thumbnail": "https://img.youtube.com/vi/qp0HIF3SfI4/mqdefault.jpg"
                },
                {
                    "title": "The Power of Believing You Can Improve",
                    "channel": "TED",
                    "url": "https://youtube.com/watch?v=_X0mgOOSpLU",
                    "duration": "10 min",
                    "why": "Growth mindset for analytical personalities",
                    "thumbnail": "https://img.youtube.com/vi/_X0mgOOSpLU/mqdefault.jpg"
                },
                {
                    "title": "Think Like a Programmer",
                    "channel": "CS Dojo",
                    "url": "https://youtube.com/watch?v=azcrPFhaY9k",
                    "duration": "23 min",
                    "why": "Perfect for your investigative mindset",
                    "thumbnail": "https://img.youtube.com/vi/azcrPFhaY9k/mqdefault.jpg"
                }
            ],
            "career_learning": [
                {
                    "title": "Machine Learning Full Course",
                    "channel": "freeCodeCamp",
                    "url": "https://youtube.com/watch?v=NWONeJKn6kc",
                    "duration": "4 hrs",
                    "skill": "Machine Learning",
                    "thumbnail": "https://img.youtube.com/vi/NWONeJKn6kc/mqdefault.jpg"
                },
                {
                    "title": "Data Structures Easy to Advanced",
                    "channel": "freeCodeCamp",
                    "url": "https://youtube.com/watch?v=RBSGKlAvoiM",
                    "duration": "8 hrs",
                    "skill": "DSA",
                    "thumbnail": "https://img.youtube.com/vi/RBSGKlAvoiM/mqdefault.jpg"
                }
            ],
            "daily_inspiration": [
                {
                    "title": "5 Habits of Highly Analytical People",
                    "channel": "Thomas Frank",
                    "url": "https://youtube.com/watch?v=23FB_7sBl0E",
                    "duration": "12 min",
                    "thumbnail": "https://img.youtube.com/vi/23FB_7sBl0E/mqdefault.jpg"
                }
            ]
        },
        "The Creative Architect": {
            "motivation": [
                {
                    "title": "Your Elusive Creative Genius",
                    "channel": "TED",
                    "url": "https://youtube.com/watch?v=86x-u-tz0MA",
                    "duration": "19 min",
                    "why": "Elizabeth Gilbert on creativity - perfect for you",
                    "thumbnail": "https://img.youtube.com/vi/86x-u-tz0MA/mqdefault.jpg"
                },
                {
                    "title": "How to Build a Creative Career",
                    "channel": "GaryVee",
                    "url": "https://youtube.com/watch?v=MoHT7s7hEwE",
                    "duration": "15 min",
                    "why": "Creative career building strategies",
                    "thumbnail": "https://img.youtube.com/vi/MoHT7s7hEwE/mqdefault.jpg"
                }
            ],
            "career_learning": [
                {
                    "title": "UI/UX Design Full Course",
                    "channel": "DesignCourse",
                    "url": "https://youtube.com/watch?v=c9Wg6Cb_YlU",
                    "duration": "3 hrs",
                    "skill": "UI/UX Design",
                    "thumbnail": "https://img.youtube.com/vi/c9Wg6Cb_YlU/mqdefault.jpg"
                }
            ],
            "daily_inspiration": [
                {
                    "title": "Design Thinking Process",
                    "channel": "IDEO",
                    "url": "https://youtube.com/watch?v=a7sEoEvT8l8",
                    "duration": "8 min",
                    "thumbnail": "https://img.youtube.com/vi/a7sEoEvT8l8/mqdefault.jpg"
                }
            ]
        },
        "The Social Strategist": {
            "motivation": [
                {
                    "title": "How to Talk to Anyone",
                    "channel": "Charisma on Command",
                    "url": "https://youtube.com/watch?v=wB0B6piRFqI",
                    "duration": "14 min",
                    "why": "Perfect for your social personality",
                    "thumbnail": "https://img.youtube.com/vi/wB0B6piRFqI/mqdefault.jpg"
                }
            ],
            "career_learning": [
                {
                    "title": "Product Management Full Guide",
                    "channel": "Product School",
                    "url": "https://youtube.com/watch?v=aN4xLCGOBeM",
                    "duration": "2 hrs",
                    "skill": "Product Management",
                    "thumbnail": "https://img.youtube.com/vi/aN4xLCGOBeM/mqdefault.jpg"
                }
            ],
            "daily_inspiration": [
                {
                    "title": "Leadership Lessons from Great CEOs",
                    "channel": "Inc.",
                    "url": "https://youtube.com/watch?v=FGz_9-sKBpE",
                    "duration": "20 min",
                    "thumbnail": "https://img.youtube.com/vi/FGz_9-sKBpE/mqdefault.jpg"
                }
            ]
        },
        "The Systematic Builder": {
            "motivation": [
                {
                    "title": "Why Constraints Are Good for Innovation",
                    "channel": "TED",
                    "url": "https://youtube.com/watch?v=v5FL9VTBZzQ",
                    "duration": "11 min",
                    "why": "Systematic thinkers thrive with structure",
                    "thumbnail": "https://img.youtube.com/vi/v5FL9VTBZzQ/mqdefault.jpg"
                }
            ],
            "career_learning": [
                {
                    "title": "DevOps Full Course",
                    "channel": "freeCodeCamp",
                    "url": "https://youtube.com/watch?v=j5Zsa_eOXeY",
                    "duration": "5 hrs",
                    "skill": "DevOps",
                    "thumbnail": "https://img.youtube.com/vi/j5Zsa_eOXeY/mqdefault.jpg"
                }
            ],
            "daily_inspiration": [
                {
                    "title": "Engineering Problem Solving",
                    "channel": "Mark Rober",
                    "url": "https://youtube.com/watch?v=cLVCGEmkDs0",
                    "duration": "15 min",
                    "thumbnail": "https://img.youtube.com/vi/cLVCGEmkDs0/mqdefault.jpg"
                }
            ]
        },
        "The Entrepreneurial Visionary": {
            "motivation": [
                {
                    "title": "How to Start a Startup",
                    "channel": "Y Combinator",
                    "url": "https://youtube.com/watch?v=CBYhVcO4WgI",
                    "duration": "47 min",
                    "why": "Perfect for your entrepreneurial drive",
                    "thumbnail": "https://img.youtube.com/vi/CBYhVcO4WgI/mqdefault.jpg"
                },
                {
                    "title": "Elon Musk on First Principles",
                    "channel": "TED",
                    "url": "https://youtube.com/watch?v=NV3sBlRgzTI",
                    "duration": "22 min",
                    "why": "Visionary thinking matched to your DNA",
                    "thumbnail": "https://img.youtube.com/vi/NV3sBlRgzTI/mqdefault.jpg"
                }
            ],
            "career_learning": [
                {
                    "title": "Business Strategy Full Course",
                    "channel": "Harvard Business School",
                    "url": "https://youtube.com/watch?v=vE_wJ8sTJTM",
                    "duration": "3 hrs",
                    "skill": "Business Strategy",
                    "thumbnail": "https://img.youtube.com/vi/vE_wJ8sTJTM/mqdefault.jpg"
                }
            ],
            "daily_inspiration": [
                {
                    "title": "Daily Habits of Successful Entrepreneurs",
                    "channel": "GaryVee",
                    "url": "https://youtube.com/watch?v=4-PO_-Dbo1E",
                    "duration": "10 min",
                    "thumbnail": "https://img.youtube.com/vi/4-PO_-Dbo1E/mqdefault.jpg"
                }
            ]
        }
    }
    
    # Career-specific videos
    CAREER_VIDEOS = {
        "Software Engineer": [
            {
                "title": "Software Engineering Full Roadmap 2026",
                "channel": "Traversy Media",
                "url": "https://youtube.com/watch?v=ysEN5RaKOlA",
                "duration": "1 hr",
                "thumbnail": "https://img.youtube.com/vi/ysEN5RaKOlA/mqdefault.jpg"
            },
            {
                "title": "System Design Interview",
                "channel": "Gaurav Sen",
                "url": "https://youtube.com/watch?v=xpDnVSmNFX0",
                "duration": "45 min",
                "thumbnail": "https://img.youtube.com/vi/xpDnVSmNFX0/mqdefault.jpg"
            }
        ],
        "Data Scientist": [
            {
                "title": "Data Science Roadmap 2026",
                "channel": "Ken Jee",
                "url": "https://youtube.com/watch?v=PhYqx0MKnrw",
                "duration": "20 min",
                "thumbnail": "https://img.youtube.com/vi/PhYqx0MKnrw/mqdefault.jpg"
            }
        ],
        "ML Engineer": [
            {
                "title": "Machine Learning Roadmap",
                "channel": "Andrej Karpathy",
                "url": "https://youtube.com/watch?v=VMj-3S1tku0",
                "duration": "2 hrs",
                "thumbnail": "https://img.youtube.com/vi/VMj-3S1tku0/mqdefault.jpg"
            }
        ],
        "UI/UX Designer": [
            {
                "title": "UI/UX Design Portfolio",
                "channel": "DesignCourse",
                "url": "https://youtube.com/watch?v=_Hp_dI0__qg",
                "duration": "30 min",
                "thumbnail": "https://img.youtube.com/vi/_Hp_dI0__qg/mqdefault.jpg"
            }
        ],
        "Cloud Engineer": [
            {
                "title": "AWS Full Course for Beginners",
                "channel": "freeCodeCamp",
                "url": "https://youtube.com/watch?v=ulprqHHWlng",
                "duration": "5 hrs",
                "thumbnail": "https://img.youtube.com/vi/ulprqHHWlng/mqdefault.jpg"
            }
        ]
    }
    
    def run(self, decision_output: dict) -> dict:
        dna_type = decision_output.get('dna_type', '')
        top_career = decision_output.get('top_career', '')
        
        # Get personality videos
        personality_videos = self.VIDEO_DATABASE.get(
            dna_type,
            self.VIDEO_DATABASE.get('The Analytical Innovator')
        )
        
        # Get career-specific videos
        career_videos = self._get_career_videos(top_career)
        
        # Get today's daily video (rotates daily)
        from datetime import date
        day_num = date.today().timetuple().tm_yday
        motivation_list = personality_videos.get('motivation', [])
        daily_video = motivation_list[
            day_num % len(motivation_list)
        ] if motivation_list else None
        
        return {
            'motivation_videos': personality_videos.get(
                'motivation', []
            )[:3],
            'career_videos': career_videos[:3],
            'daily_inspiration': personality_videos.get(
                'daily_inspiration', []
            )[:2],
            'daily_video': daily_video,
            'learning_videos': personality_videos.get(
                'career_learning', []
            )[:3],
            'dna_type': dna_type
        }
    
    def _get_career_videos(self, career_title):
        for key in self.CAREER_VIDEOS:
            if key.lower() in career_title.lower():
                return self.CAREER_VIDEOS[key]
        return self.CAREER_VIDEOS.get('Software Engineer', [])
    
    def get_daily_video(self, dna_type: str) -> dict:
        """Called daily for dashboard widget"""
        from datetime import date
        day_num = date.today().timetuple().tm_yday
        videos = self.VIDEO_DATABASE.get(
            dna_type,
            self.VIDEO_DATABASE['The Analytical Innovator']
        )
        all_vids = (
            videos.get('motivation', []) + 
            videos.get('daily_inspiration', [])
        )
        if all_vids:
            return all_vids[day_num % len(all_vids)]
        return {}
