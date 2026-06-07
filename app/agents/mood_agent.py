class MoodMotivationAgent:
    """
    Tracks student mood daily.
    Gives personalized motivation based on:
    - Their DNA type
    - Current mood
    - Streak status
    - Progress in roadmap
    Shows motivational quote + action + video.
    """
    
    MOOD_RESPONSES = {
        "motivated": {
            "message": "You're on fire! 🔥 Use this energy!",
            "action": "Tackle the hardest task on your roadmap today",
            "quote": "Success is not final, failure is not fatal. "
                     "It is the courage to continue that counts.",
            "author": "Winston Churchill"
        },
        "stressed": {
            "message": "Take a breath. You've got this. 💪",
            "action": "Do 5 min breathing, then tackle ONE small task",
            "quote": "You don't have to be great to start, "
                     "but you have to start to be great.",
            "author": "Zig Ziglar"
        },
        "confused": {
            "message": "Confusion is the beginning of understanding 🧠",
            "action": "Watch today's recommended video, "
                     "then write 3 things you learned",
            "quote": "The more I learn, the more I realize "
                     "how much I don't know.",
            "author": "Albert Einstein"
        },
        "bored": {
            "message": "Boredom = time to level up! ⚡",
            "action": "Start a new mini-project in your skill area",
            "quote": "Boredom is the feeling that everything "
                     "is a waste of time; serenity that nothing is.",
            "author": "Thomas Szasz"
        },
        "excited": {
            "message": "Channel that excitement into action! 🚀",
            "action": "Set 3 specific goals for this week right now",
            "quote": "The secret of getting ahead is getting started.",
            "author": "Mark Twain"
        },
        "tired": {
            "message": "Rest is part of the journey too 😴",
            "action": "Watch 1 light motivational video, "
                     "rest, come back tomorrow stronger",
            "quote": "Almost everything will work again "
                     "if you unplug it for a few minutes, "
                     "including you.",
            "author": "Anne Lamott"
        }
    }
    
    DNA_AFFIRMATIONS = {
        "The Analytical Innovator": [
            "Your analytical mind sees patterns others miss.",
            "Complex problems are your playground.",
            "You don't just think outside the box - "
            "you redesign the box.",
        ],
        "The Creative Architect": [
            "Your creativity is a superpower in tech.",
            "You see beauty where others see only function.",
            "The world needs more creative engineers like you.",
        ],
        "The Social Strategist": [
            "Your ability to connect with people is rare.",
            "Technology needs human-centered thinkers like you.",
            "You make tech more human.",
        ],
        "The Systematic Builder": [
            "Your precision and reliability are invaluable.",
            "You build things that last.",
            "Systems thinking is the future of engineering.",
        ],
        "The Entrepreneurial Visionary": [
            "Your vision will create opportunities for thousands.",
            "You see what others cannot yet imagine.",
            "The next great Indian startup could be yours.",
        ]
    }
    
    def run(self, decision_output: dict,
            mood: str = "motivated") -> dict:
        dna_type = decision_output.get('dna_type', '')
        mood_data = self.MOOD_RESPONSES.get(
            mood, self.MOOD_RESPONSES['motivated']
        )
        
        # Get DNA-specific affirmation
        affirmations = self.DNA_AFFIRMATIONS.get(
            dna_type,
            self.DNA_AFFIRMATIONS['The Analytical Innovator']
        )
        from datetime import date
        day_num = date.today().timetuple().tm_yday
        affirmation = affirmations[day_num % len(affirmations)]
        
        return {
            'mood': mood,
            'mood_message': mood_data['message'],
            'action_today': mood_data['action'],
            'quote': mood_data['quote'],
            'quote_author': mood_data['author'],
            'dna_affirmation': affirmation,
            'energy_tip': self._get_energy_tip(mood)
        }
    
    def _get_energy_tip(self, mood):
        tips = {
            "motivated": "Strike while the iron is hot! "
                        "Deep work session: 90 min, no phone.",
            "stressed": "Try the 2-minute rule: "
                       "if it takes less than 2 min, do it now.",
            "confused": "Write your confusion down. "
                       "Explaining it on paper often solves it.",
            "bored": "Change your environment. "
                    "Study from a new place today.",
            "excited": "Capture this energy in a journal. "
                      "Write your 1-year vision right now.",
            "tired": "Sleep 8 hours. Your brain consolidates "
                    "learning during sleep."
        }
        return tips.get(mood, tips['motivated'])
