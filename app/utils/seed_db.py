"""
Seed Database
Provides helper function to populate default Mentors and Videos in the database.
"""

from app.extensions import db
from app.models.mentor import Mentor
from app.models.video import Video


def seed_database():
    """
    Populate database with initial Mentors and Videos if they don't exist.
    """
    # Seed Mentors
    if Mentor.query.count() == 0:
        mentors_to_seed = [
            # Analytical
            {
                "name": "Sundar Pichai",
                "role": "CEO, Google",
                "college": "IIT Kharagpur → Stanford",
                "dna_match": "Investigative + Analytical",
                "photo_initial": "SP",
                "color": "#0d9488",
                "story": "From IIT Kharagpur to leading Google. His analytical mindset transformed Chrome and Android into billion-user products.",
                "quote": "It's important to follow your dreams and heart. Do something that excites you.",
                "advice": [
                    "Master one technical skill deeply",
                    "Always think from user's perspective",
                    "Communication is as important as coding"
                ],
                "his_path": "Engineering → MS Stanford → McKinsey → Google → CEO",
                "personality_type": "Analytical",
                "is_available": True
            },
            {
                "name": "Demis Hassabis",
                "role": "CEO, Google DeepMind",
                "college": "Cambridge University",
                "dna_match": "Investigative + Creative",
                "photo_initial": "DH",
                "color": "#0d9488",
                "story": "Chess prodigy turned AI researcher. Created AlphaGo and AlphaFold, solving 50-year-old biology problems.",
                "quote": "Science is the best tool we have for understanding the world.",
                "advice": [
                    "Study multiple disciplines deeply",
                    "Work on problems that matter",
                    "Combine creativity with rigor"
                ],
                "his_path": "Chess → Cambridge → Neuroscience → AI Research → DeepMind",
                "personality_type": "Analytical",
                "is_available": True
            },
            # Visionary
            {
                "name": "Elon Musk",
                "role": "CEO, Tesla & SpaceX",
                "college": "UPenn",
                "dna_match": "Enterprising + Investigative",
                "photo_initial": "EM",
                "color": "#3b82f6",
                "story": "Co-founded PayPal, then went on to revolutionize space travel with SpaceX and electric vehicles with Tesla using first-principles thinking.",
                "quote": "When something is important enough, you do it even if the odds are not in your favor.",
                "advice": [
                    "Use first-principles thinking",
                    "Work super hard (80-100 hours a week)",
                    "Focus on signal over noise"
                ],
                "his_path": "UPenn Physics/Economics → Stanford (dropped out) → Zip2 → PayPal → SpaceX & Tesla",
                "personality_type": "Visionary",
                "is_available": True
            },
            {
                "name": "Steve Jobs",
                "role": "Co-founder, Apple",
                "college": "Reed College (dropped out)",
                "dna_match": "Artistic + Enterprising",
                "photo_initial": "SJ",
                "color": "#3b82f6",
                "story": "Co-founded Apple in a garage, revolutionized computing, music, and phones, proving that art and technology must intersect.",
                "quote": "The only way to do great work is to love what you do.",
                "advice": [
                    "Stay hungry, stay foolish",
                    "Design is not just what it looks like, it is how it works",
                    "Put a dent in the universe"
                ],
                "his_path": "Atari → Co-founded Apple → NeXT / Pixar → Apple CEO",
                "personality_type": "Visionary",
                "is_available": True
            },
            # Creative
            {
                "name": "Jony Ive",
                "role": "Former CDO, Apple",
                "college": "Northumbria University",
                "dna_match": "Artistic + Investigative",
                "photo_initial": "JI",
                "color": "#ec4899",
                "story": "Designed iPhone, iMac, MacBook. Changed how billions interact with technology through obsessive attention to design.",
                "quote": "Design is not just what it looks like. Design is how it works.",
                "advice": [
                    "Obsess over the details others ignore",
                    "Simplicity is the ultimate sophistication",
                    "Question every assumption about your design"
                ],
                "his_path": "Art School → Design Agency → Apple → Led design for 27 years",
                "personality_type": "Creative",
                "is_available": True
            },
            {
                "name": "Coco Chanel",
                "role": "Founder, Chanel",
                "college": "Aubazine",
                "dna_match": "Artistic + Enterprising",
                "photo_initial": "CC",
                "color": "#ec4899",
                "story": "Liberated women from the constraints of the 'corseted silhouette' and popularized a sporty, casual chic as the feminine standard.",
                "quote": "In order to be irreplaceable one must always be different.",
                "advice": [
                    "Simplicity is the keynote of all true elegance",
                    "Be irreplaceable; be different",
                    "Fashion fades, only style remains"
                ],
                "his_path": "Seamstress → Millinery → Founded Chanel → Global Fashion Icon",
                "personality_type": "Creative",
                "is_available": True
            },
            # Strategist
            {
                "name": "Jeff Bezos",
                "role": "Founder, Amazon",
                "college": "Princeton University",
                "dna_match": "Enterprising + Conventional",
                "photo_initial": "JB",
                "color": "#8b5cf6",
                "story": "Started Amazon as an online bookstore from his garage and scaled it into the global infrastructure giant of e-commerce and cloud computing.",
                "quote": "Work hard, have fun, make history.",
                "advice": [
                    "Obsess over customers, not competitors",
                    "Focus on things that won't change in 10 years",
                    "Disagree and commit to move fast"
                ],
                "his_path": "Princeton EE/CS → D. E. Shaw → Founded Amazon → Blue Origin",
                "personality_type": "Strategist",
                "is_available": True
            },
            {
                "name": "Sheryl Sandberg",
                "role": "Former COO, Meta",
                "college": "Harvard University",
                "dna_match": "Enterprising + Social",
                "photo_initial": "SS",
                "color": "#8b5cf6",
                "story": "Scaled Facebook from a money-losing social network to a highly profitable advertising powerhouse while authoring Lean In.",
                "quote": "Done is better than perfect.",
                "advice": [
                    "Lean into opportunities even if you feel unready",
                    "Seek feedback early and constantly",
                    "Build resilient teams through emotional connection"
                ],
                "his_path": "Harvard Economics → World Bank → US Treasury → Google → Facebook COO",
                "personality_type": "Strategist",
                "is_available": True
            },
            # Empath
            {
                "name": "Oprah Winfrey",
                "role": "Media Mogul & Philanthropist",
                "college": "Tennessee State University",
                "dna_match": "Social + Enterprising",
                "photo_initial": "OW",
                "color": "#f59e0b",
                "story": "Overcame extreme poverty to build the world's most successful talk show, establishing deep connections with millions through vulnerability.",
                "quote": "The biggest adventure you can take is to live the life of your dreams.",
                "advice": [
                    "Trust your instincts above all else",
                    "Connect through empathy and vulnerability",
                    "Turn your wounds into wisdom"
                ],
                "his_path": "Radio Host → Local TV News → The Oprah Winfrey Show → HARPO Productions",
                "personality_type": "Empath",
                "is_available": True
            },
            {
                "name": "Melinda Gates",
                "role": "Co-chair, Gates Foundation",
                "college": "Duke University",
                "dna_match": "Social + Conventional",
                "photo_initial": "MG",
                "color": "#f59e0b",
                "story": "Former Microsoft executive who co-founded the world's largest private charitable foundation, focusing on global health and women's empowerment.",
                "quote": "If you are successful, it is because somewhere, sometime, someone gave you a life or an idea that started you in the right direction.",
                "advice": [
                    "Empower women to lift up entire societies",
                    "Use data to guide philanthropic impact",
                    "Always listen to those you are trying to help"
                ],
                "his_path": "Duke MBA → Microsoft Manager → Co-founded Gates Foundation → Pivotal Ventures",
                "personality_type": "Empath",
                "is_available": True
            },
            # Leader
            {
                "name": "Satya Nadella",
                "role": "CEO, Microsoft",
                "college": "Manipal Institute → UW-Milwaukee",
                "dna_match": "Social + Enterprising",
                "photo_initial": "SN",
                "color": "#10b981",
                "story": "Transformed Microsoft from a declining giant to a $3 trillion company through empathy-led leadership and cloud vision.",
                "quote": "Empathy makes you a better innovator. It is the foundation of everything.",
                "advice": [
                    "Lead with empathy first",
                    "Embrace a growth mindset daily",
                    "Build coalitions, not just products"
                ],
                "his_path": "Manipal → MS USA → Sun → Microsoft (30 yrs) → CEO",
                "personality_type": "Leader",
                "is_available": True
            },
            {
                "name": "Indra Nooyi",
                "role": "Former CEO, PepsiCo",
                "college": "Madras Christian College → Yale",
                "dna_match": "Enterprising + Social",
                "photo_initial": "IN",
                "color": "#10b981",
                "story": "Lead PepsiCo for 12 years, successfully steering the company toward healthier options ('Performance with Purpose') and boosting revenue by 80%.",
                "quote": "Leadership is hard to define and good leadership even harder. But if you can get people to follow you to the ends of the earth, you are a great leader.",
                "advice": [
                    "Develop a unique capability or 'hip-pocket skill'",
                    "Look at business through a design lens",
                    "Lead with both your brain and your heart"
                ],
                "his_path": "IIM Calcutta → Yale SOM → BCG → Motorola → PepsiCo CEO",
                "personality_type": "Leader",
                "is_available": True
            }
        ]
        
        for m in mentors_to_seed:
            db.session.add(Mentor(**m))
        db.session.commit()
        print(f"Seeded {len(mentors_to_seed)} Mentors successfully.")

    # Seed Videos
    if Video.query.count() == 0:
        videos_to_seed = [
            {
                "title": "How Great Leaders Think",
                "channel": "TED",
                "url": "https://youtube.com/watch?v=qp0HIF3SfI4",
                "duration": "18 min",
                "why": "Unlocks the core communication and strategic mindset of premium leaders.",
                "thumbnail": "https://img.youtube.com/vi/qp0HIF3SfI4/mqdefault.jpg",
                "personality_tags": ["Leader", "Analytical", "Strategist"]
            },
            {
                "title": "The Power of Believing You Can Improve",
                "channel": "TED",
                "url": "https://youtube.com/watch?v=_X0mgOOSpLU",
                "duration": "10 min",
                "why": "Growth mindset training tailored to help analytical minds overcome perfectionism.",
                "thumbnail": "https://img.youtube.com/vi/_X0mgOOSpLU/mqdefault.jpg",
                "personality_tags": ["Analytical", "Empath", "Creative"]
            },
            {
                "title": "Think Like a Programmer",
                "channel": "CS Dojo",
                "url": "https://youtube.com/watch?v=azcrPFhaY9k",
                "duration": "23 min",
                "why": "Perfect systematic deconstruction of programming problems.",
                "thumbnail": "https://img.youtube.com/vi/azcrPFhaY9k/mqdefault.jpg",
                "personality_tags": ["Analytical", "Strategist"]
            },
            {
                "title": "Your Elusive Creative Genius",
                "channel": "TED",
                "url": "https://youtube.com/watch?v=86x-u-tz0MA",
                "duration": "19 min",
                "why": "Elizabeth Gilbert's masterpiece on nurturing creativity without burn-out.",
                "thumbnail": "https://img.youtube.com/vi/86x-u-tz0MA/mqdefault.jpg",
                "personality_tags": ["Creative", "Visionary", "Empath"]
            },
            {
                "title": "How to Build a Creative Career",
                "channel": "GaryVee",
                "url": "https://youtube.com/watch?v=MoHT7s7hEwE",
                "duration": "15 min",
                "why": "A strategic guide to monetizing and scaling creative ideas.",
                "thumbnail": "https://img.youtube.com/vi/MoHT7s7hEwE/mqdefault.jpg",
                "personality_tags": ["Creative", "Leader", "Visionary"]
            },
            {
                "title": "UI/UX Design Full Course",
                "channel": "DesignCourse",
                "url": "https://youtube.com/watch?v=c9Wg6Cb_YlU",
                "duration": "3 hrs",
                "why": "Comprehensive UI/UX principles for visual builders.",
                "thumbnail": "https://img.youtube.com/vi/c9Wg6Cb_YlU/mqdefault.jpg",
                "personality_tags": ["Creative", "Analytical"]
            },
            {
                "title": "How to Talk to Anyone",
                "channel": "Charisma on Command",
                "url": "https://youtube.com/watch?v=wB0B6piRFqI",
                "duration": "14 min",
                "why": "Master social interaction and active listening.",
                "thumbnail": "https://img.youtube.com/vi/wB0B6piRFqI/mqdefault.jpg",
                "personality_tags": ["Empath", "Leader"]
            },
            {
                "title": "Product Management Full Guide",
                "channel": "Product School",
                "url": "https://youtube.com/watch?v=aN4xLCGOBeM",
                "duration": "2 hrs",
                "why": "Great primer for understanding the sweet spot between technology and business strategy.",
                "thumbnail": "https://img.youtube.com/vi/aN4xLCGOBeM/mqdefault.jpg",
                "personality_tags": ["Strategist", "Leader", "Visionary"]
            },
            {
                "title": "How to Start a Startup",
                "channel": "Y Combinator",
                "url": "https://youtube.com/watch?v=CBYhVcO4WgI",
                "duration": "47 min",
                "why": "Dustin Moskovitz on startup strategy and vision validation.",
                "thumbnail": "https://img.youtube.com/vi/CBYhVcO4WgI/mqdefault.jpg",
                "personality_tags": ["Visionary", "Leader", "Strategist"]
            },
            {
                "title": "Elon Musk on First Principles",
                "channel": "TED",
                "url": "https://youtube.com/watch?v=NV3sBlRgzTI",
                "duration": "22 min",
                "why": "Deep dive on deconstructing complex problems to build visionary companies.",
                "thumbnail": "https://img.youtube.com/vi/NV3sBlRgzTI/mqdefault.jpg",
                "personality_tags": ["Visionary", "Analytical"]
            },
            {
                "title": "Design Thinking Process",
                "channel": "IDEO",
                "url": "https://youtube.com/watch?v=a7sEoEvT8l8",
                "duration": "8 min",
                "why": "Deeply human-centric problem-solving framework.",
                "thumbnail": "https://img.youtube.com/vi/a7sEoEvT8l8/mqdefault.jpg",
                "personality_tags": ["Creative", "Empath"]
            },
            {
                "title": "Leadership Lessons from Great CEOs",
                "channel": "Inc.",
                "url": "https://youtube.com/watch?v=FGz_9-sKBpE",
                "duration": "20 min",
                "why": "Learn direct team management, scaling strategies and leadership traits.",
                "thumbnail": "https://img.youtube.com/vi/FGz_9-sKBpE/mqdefault.jpg",
                "personality_tags": ["Leader", "Strategist"]
            }
        ]
        
        for v in videos_to_seed:
            db.session.add(Video(**v))
        db.session.commit()
        print(f"Seeded {len(videos_to_seed)} Videos successfully.")
