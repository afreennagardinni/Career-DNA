"""
Career Query Agent
Generates dynamic career queries based on psychometric profile using RAG.
"""

from typing import Dict, List, Any
import json
import os

# Try to import RAG components, fall back to static if unavailable
try:
    from app.rag.embedding_pipeline import EmbeddingPipeline
    from app.rag.vector_store import VectorStoreManager
    from app.rag.retriever import Retriever, RAGPipeline
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class CareerQueryAgent:
    """
    Agent responsible for generating career queries from psychometric data using RAG.
    
    Flow: Input (traits + patterns) → Process (RAG retrieval + query generation) → Output (structured queries)
    """
    
    def __init__(self, use_rag: bool = True):
        """
        Initialize the career query agent.
        
        Args:
            use_rag: Whether to use RAG for dynamic retrieval (default: True)
        """
        self.agent_name = "CareerQueryAgent"
        
        # Check if RAG is available
        if use_rag and not RAG_AVAILABLE:
            print("RAG components not available, falling back to static database")
            use_rag = False
        
        self.use_rag = use_rag
        
        # Initialize RAG components
        if use_rag:
            try:
                self._init_rag()
            except Exception as e:
                print(f"RAG initialization failed: {e}, falling back to static database")
                self.use_rag = False
                self.career_database = self._load_career_database()
        else:
            # Fallback to static career database
            self.career_database = self._load_career_database()
    
    def _init_rag(self):
        """Initialize RAG components for dynamic retrieval."""
        # Get paths to data files
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        careers_path = os.path.join(base_dir, 'data', 'careers.json')
        skills_path = os.path.join(base_dir, 'data', 'skills.json')
        
        # Initialize vector store manager
        vector_stores_dir = os.path.join(base_dir, 'data', 'vector_stores')
        
        # Try to load existing stores, or initialize new ones
        self.vector_store_manager = VectorStoreManager(vector_stores_dir)
        
        if os.path.exists(os.path.join(vector_stores_dir, 'career_index.faiss')):
            self.vector_store_manager.load_stores()
        else:
            self.vector_store_manager.initialize(careers_path, skills_path)
        
        # Initialize retriever
        self.retriever = Retriever(self.vector_store_manager)
        
        # Initialize RAG pipeline
        self.rag_pipeline = RAGPipeline(self.retriever)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process trait and pattern data to generate career queries.
        
        Input:
            {
                "traits": {
                    "big_five": {...},
                    "riasec": {...}
                },
                "patterns": [...],
                "holland_code": "RIS",
                "user_preferences": {...} (optional)
            }
        
        Process:
            1. Analyze trait profile
            2. Generate career queries based on patterns
            3. Rank careers by match score
            4. Create dynamic search queries
        
        Output:
            {
                "agent": "CareerQueryAgent",
                "queries": [...],
                "career_matches": [...],
                "search_terms": [...],
                "metadata": {...}
            }
        """
        # Validate input
        if not self._validate_input(input_data):
            return self._error_response("Invalid input data")
        
        traits = input_data.get("traits", {})
        patterns = input_data.get("patterns", [])
        holland_code = input_data.get("holland_code", "")
        user_preferences = input_data.get("user_preferences", {})
        
        # Generate career matches using RAG or static database
        if self.use_rag:
            career_matches = self._generate_career_matches_rag(traits, patterns, holland_code)
        else:
            career_matches = self._generate_career_matches(traits, holland_code, patterns)
        
        # Generate search queries
        search_queries = self._generate_search_queries(traits, patterns, career_matches)
        
        # Generate structured queries for external APIs
        api_queries = self._generate_api_queries(traits, patterns, user_preferences)
        
        # Build response
        result = {
            "agent": self.agent_name,
            "queries": api_queries,
            "career_matches": career_matches,
            "search_terms": search_queries,
            "metadata": {
                "career_count": len(career_matches),
                "query_count": len(api_queries),
                "holland_code": holland_code,
                "processing_time": self._get_processing_time()
            }
        }
        
        return result
    
    def _generate_career_matches(self, traits: Dict, holland_code: str, patterns: List) -> List[Dict[str, Any]]:
        """
        Generate career matches based on traits and patterns.
        
        Args:
            traits: Trait scores
            holland_code: Holland code
            patterns: Detected patterns
        
        Returns:
            List of career matches with scores
        """
        big_five = traits.get("big_five", {})
        riasec = traits.get("riasec", {})
        
        matches = []
        
        for career in self.career_database:
            # Calculate Holland code match
            holland_score = self._calculate_holland_match(holland_code, career["holland_codes"])
            
            # Calculate personality match
            personality_score = self._calculate_personality_match(big_five, career["personality_match"])
            
            # Calculate pattern bonus
            pattern_bonus = self._calculate_pattern_bonus(patterns, career["patterns"])
            
            # Overall match score
            overall_score = (holland_score * 0.5) + (personality_score * 0.3) + (pattern_bonus * 0.2)
            
            if overall_score >= 40:  # Minimum threshold
                matches.append({
                    "title": career["title"],
                    "category": career["category"],
                    "match_score": round(overall_score, 2),
                    "holland_match": round(holland_score, 2),
                    "personality_match": round(personality_score, 2),
                    "pattern_bonus": round(pattern_bonus, 2),
                    "description": career["description"],
                    "skills": career["skills"]
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:10]  # Return top 10
    
    def _generate_career_matches_rag(self, traits: Dict, patterns: List, holland_code: str) -> List[Dict[str, Any]]:
        """
        Generate career matches using RAG for dynamic retrieval.
        
        Args:
            traits: Trait scores
            patterns: Detected patterns
            holland_code: Holland code
        
        Returns:
            List of career matches with scores
        """
        # Use RAG to retrieve careers based on traits
        if patterns:
            # Use pattern-based retrieval if patterns available
            rag_results = self.retriever.retrieve_by_patterns(patterns, k=10)
        else:
            # Use trait-based retrieval
            combined_traits = {**traits.get("big_five", {}), **traits.get("riasec", {})}
            rag_results = self.retriever.retrieve_by_traits(combined_traits, k=10)
        
        # Convert RAG results to career matches format
        matches = []
        for result in rag_results:
            # Convert similarity score (0-1) to match score (0-100)
            similarity_score = result.get("similarity_score", 0)
            match_score = similarity_score * 100
            
            matches.append({
                "title": result.get("title", ""),
                "category": result.get("metadata", {}).get("industries", ["General"])[0] if result.get("metadata", {}).get("industries") else "General",
                "match_score": round(match_score, 2),
                "holland_match": round(match_score * 0.8, 2),  # Approximate
                "personality_match": round(match_score * 0.9, 2),  # Approximate
                "pattern_bonus": 0.0,
                "description": result.get("snippet", ""),
                "skills": [],  # Skills would need to be loaded from full document
                "rag_retrieved": True
            })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches[:10]  # Return top 10
    
    def _calculate_holland_match(self, user_code: str, career_codes: List[str]) -> float:
        """
        Calculate Holland code match score.
        
        Args:
            user_code: User's Holland code (e.g., "RIS")
            career_codes: List of career Holland codes
        
        Returns:
            float: Match score (0-100)
        """
        if not user_code:
            return 50.0
        
        max_match = 0
        for career_code in career_codes:
            match_count = sum(1 for i, letter in enumerate(career_code) 
                            if i < len(user_code) and letter == user_code[i])
            max_match = max(max_match, match_count)
        
        return (max_match / 3) * 100
    
    def _calculate_personality_match(self, user_traits: Dict, career_profile: Dict) -> float:
        """
        Calculate personality match score.
        
        Args:
            user_traits: User's Big Five scores
            career_profile: Career's ideal personality profile
        
        Returns:
            float: Match score (0-100)
        """
        total_score = 0
        
        for trait, ideal_score in career_profile.items():
            user_score = user_traits.get(trait, 50) / 100  # Normalize to 0-1
            diff = abs(user_score - ideal_score)
            trait_score = (1 - diff) * 20  # Each trait worth 20 points
            total_score += trait_score
        
        return total_score
    
    def _calculate_pattern_bonus(self, patterns: List, career_patterns: List[str]) -> float:
        """
        Calculate pattern bonus score.
        
        Args:
            patterns: User's detected patterns
            career_patterns: Patterns that match this career
        
        Returns:
            float: Bonus score (0-100)
        """
        if not patterns:
            return 0.0
        
        user_pattern_types = [p["type"] for p in patterns]
        matches = sum(1 for cp in career_patterns if cp in user_pattern_types)
        
        if matches > 0:
            return (matches / len(career_patterns)) * 100
        return 0.0
    
    def _generate_search_queries(self, traits: Dict, patterns: List, career_matches: List) -> List[str]:
        """
        Generate natural language search queries.
        
        Args:
            traits: Trait scores
            patterns: Detected patterns
            career_matches: Career matches
        
        Returns:
            List of search query strings
        """
        queries = []
        
        # Query 1: Based on top career matches
        if career_matches:
            top_career = career_matches[0]["title"]
            queries.append(f"careers similar to {top_career}")
        
        # Query 2: Based on Holland code
        riasec = traits.get("riasec", {})
        top_interests = sorted(riasec.items(), key=lambda x: x[1], reverse=True)[:2]
        if top_interests:
            queries.append(f"careers for {top_interests[0][0]} and {top_interests[1][0]} interests")
        
        # Query 3: Based on patterns
        if patterns:
            pattern_types = [p["type"] for p in patterns[:2]]
            queries.append(f"careers for {pattern_types[0]} personality type")
        
        # Query 4: Based on personality traits
        big_five = traits.get("big_five", {})
        dominant_traits = [t for t, s in big_five.items() if s >= 70]
        if dominant_traits:
            queries.append(f"careers for people with high {dominant_traits[0]}")
        
        # Query 5: Industry-specific
        if career_matches:
            categories = set(c["category"] for c in career_matches[:3])
            for category in categories:
                queries.append(f"{category} career opportunities")
        
        return queries
    
    def _generate_api_queries(self, traits: Dict, patterns: List, preferences: Dict) -> List[Dict[str, Any]]:
        """
        Generate structured queries for external career APIs.
        
        Args:
            traits: Trait scores
            patterns: Detected patterns
            preferences: User preferences
        
        Returns:
            List of structured API queries
        """
        queries = []
        
        # Query 1: Job board API query
        job_query = {
            "type": "job_search",
            "platform": "linkedin",
            "parameters": {
                "keywords": self._extract_keywords(traits, patterns),
                "location": preferences.get("location", ""),
                "experience_level": preferences.get("experience_level", "entry_level"),
                "job_type": preferences.get("job_type", "full_time")
            }
        }
        queries.append(job_query)
        
        # Query 2: Salary API query
        salary_query = {
            "type": "salary_lookup",
            "platform": "glassdoor",
            "parameters": {
                "job_titles": self._extract_job_titles(traits, patterns),
                "location": preferences.get("location", "United States"),
                "experience": preferences.get("years_of_experience", 0)
            }
        }
        queries.append(salary_query)
        
        # Query 3: Skills API query
        skills_query = {
            "type": "skills_analysis",
            "platform": "internal",
            "parameters": {
                "target_careers": self._extract_target_careers(traits),
                "current_skills": preferences.get("current_skills", []),
                "skill_gaps": True
            }
        }
        queries.append(skills_query)
        
        # Query 4: Education API query
        education_query = {
            "type": "education_search",
            "platform": "coursera",
            "parameters": {
                "domain": self._extract_domain(traits, patterns),
                "level": preferences.get("education_level", "bachelor"),
                "format": preferences.get("learning_format", "online")
            }
        }
        queries.append(education_query)
        
        return queries
    
    def _extract_keywords(self, traits: Dict, patterns: List) -> List[str]:
        """
        Extract search keywords from traits and patterns.
        
        Args:
            traits: Trait scores
            patterns: Detected patterns
        
        Returns:
            List of keyword strings
        """
        keywords = []
        
        # From RIASEC
        riasec = traits.get("riasec", {})
        top_interests = sorted(riasec.items(), key=lambda x: x[1], reverse=True)[:2]
        keywords.extend([interest for interest, score in top_interests])
        
        # From patterns
        for pattern in patterns[:2]:
            keywords.extend(pattern.get("traits", []))
        
        return keywords
    
    def _extract_job_titles(self, traits: Dict, patterns: List) -> List[str]:
        """
        Extract relevant job titles from traits and patterns.
        
        Args:
            traits: Trait scores
            patterns: Detected patterns
        
        Returns:
            List of job title strings
        """
        titles = []
        
        # Pattern-based titles
        pattern_to_titles = {
            "creative_personality": ["Designer", "Artist", "Writer", "Content Creator"],
            "analytical_thinker": ["Data Scientist", "Researcher", "Analyst", "Engineer"],
            "social_leader": ["Manager", "Team Lead", "HR Specialist", "Consultant"],
            "practical_problem_solver": ["Developer", "Technician", "Engineer", "Specialist"],
            "entrepreneurial": ["Founder", "Business Developer", "Sales Manager", "Entrepreneur"]
        }
        
        for pattern in patterns:
            pattern_type = pattern.get("type")
            if pattern_type in pattern_to_titles:
                titles.extend(pattern_to_titles[pattern_type][:2])
        
        return titles[:5]
    
    def _extract_target_careers(self, traits: Dict) -> List[str]:
        """
        Extract target careers from traits.
        
        Args:
            traits: Trait scores
        
        Returns:
            List of career strings
        """
        careers = []
        
        big_five = traits.get("big_five", {})
        riasec = traits.get("riasec", {})
        
        # High openness → creative careers
        if big_five.get("openness", 0) >= 70:
            careers.extend(["UX Designer", "Product Designer", "Creative Director"])
        
        # High conscientiousness + investigative → analytical careers
        if big_five.get("conscientiousness", 0) >= 70 and riasec.get("investigative", 0) >= 70:
            careers.extend(["Data Scientist", "Research Scientist", "Financial Analyst"])
        
        # High extraversion + social → leadership careers
        if big_five.get("extraversion", 0) >= 70 and riasec.get("social", 0) >= 70:
            careers.extend(["Product Manager", "Marketing Manager", "Sales Director"])
        
        return careers[:5]
    
    def _extract_domain(self, traits: Dict, patterns: List) -> str:
        """
        Extract learning domain from traits and patterns.
        
        Args:
            traits: Trait scores
            patterns: Detected patterns
        
        Returns:
            str: Domain name
        """
        riasec = traits.get("riasec", {})
        top_interest = max(riasec.items(), key=lambda x: x[1])[0] if riasec else "technology"
        
        domain_mapping = {
            "realistic": "engineering",
            "investigative": "data_science",
            "artistic": "design",
            "social": "psychology",
            "enterprising": "business",
            "conventional": "finance"
        }
        
        return domain_mapping.get(top_interest, "technology")
    
    def _load_career_database(self) -> List[Dict[str, Any]]:
        """
        Load expanded career database.
        
        Returns:
            List of career definitions
        """
        return [
            {
                "title": "Software Engineer",
                "category": "Technology",
                "holland_codes": ["IRE", "IRS", "IER"],
                "personality_match": {
                    "openness": 0.8,
                    "conscientiousness": 0.9,
                    "extraversion": 0.4,
                    "agreeableness": 0.5,
                    "neuroticism": 0.3
                },
                "patterns": ["analytical_thinker", "practical_problem_solver"],
                "description": "Design and develop software applications and systems",
                "skills": ["Programming", "Problem Solving", "System Design"]
            },
            {
                "title": "Data Scientist",
                "category": "Technology",
                "holland_codes": ["IRE", "IRS", "ISR"],
                "personality_match": {
                    "openness": 0.9,
                    "conscientiousness": 0.8,
                    "extraversion": 0.3,
                    "agreeableness": 0.4,
                    "neuroticism": 0.3
                },
                "patterns": ["analytical_thinker"],
                "description": "Analyze complex data to drive business decisions",
                "skills": ["Statistics", "Machine Learning", "Data Visualization"]
            },
            {
                "title": "UX Designer",
                "category": "Design",
                "holland_codes": ["AIE", "AIS", "AES"],
                "personality_match": {
                    "openness": 0.9,
                    "conscientiousness": 0.7,
                    "extraversion": 0.5,
                    "agreeableness": 0.7,
                    "neuroticism": 0.4
                },
                "patterns": ["creative_personality"],
                "description": "Design user-centered digital experiences",
                "skills": ["User Research", "Visual Design", "Prototyping"]
            },
            {
                "title": "Product Manager",
                "category": "Business",
                "holland_codes": ["EIS", "ESR", "ERS"],
                "personality_match": {
                    "openness": 0.7,
                    "conscientiousness": 0.8,
                    "extraversion": 0.8,
                    "agreeableness": 0.6,
                    "neuroticism": 0.4
                },
                "patterns": ["social_leader", "entrepreneurial"],
                "description": "Lead product strategy and development",
                "skills": ["Strategy", "Communication", "Analytics"]
            },
            {
                "title": "Marketing Manager",
                "category": "Marketing",
                "holland_codes": ["ESA", "EAS", "ECS"],
                "personality_match": {
                    "openness": 0.7,
                    "conscientiousness": 0.7,
                    "extraversion": 0.9,
                    "agreeableness": 0.6,
                    "neuroticism": 0.5
                },
                "patterns": ["social_leader", "entrepreneurial"],
                "description": "Develop and execute marketing strategies",
                "skills": ["Marketing", "Leadership", "Creativity"]
            },
            {
                "title": "Financial Analyst",
                "category": "Finance",
                "holland_codes": ["CIE", "CIR", "CER"],
                "personality_match": {
                    "openness": 0.5,
                    "conscientiousness": 0.9,
                    "extraversion": 0.4,
                    "agreeableness": 0.5,
                    "neuroticism": 0.4
                },
                "patterns": ["analytical_thinker", "practical_problem_solver"],
                "description": "Analyze financial data and provide recommendations",
                "skills": ["Financial Analysis", "Excel", "Modeling"]
            },
            {
                "title": "Human Resources Manager",
                "category": "Human Resources",
                "holland_codes": ["SCE", "SEC", "SER"],
                "personality_match": {
                    "openness": 0.6,
                    "conscientiousness": 0.8,
                    "extraversion": 0.7,
                    "agreeableness": 0.9,
                    "neuroticism": 0.4
                },
                "patterns": ["social_leader"],
                "description": "Manage employee relations and organizational development",
                "skills": ["Communication", "Conflict Resolution", "Strategic Planning"]
            },
            {
                "title": "Research Scientist",
                "category": "Research",
                "holland_codes": ["IRE", "IRS", "ISR"],
                "personality_match": {
                    "openness": 0.9,
                    "conscientiousness": 0.9,
                    "extraversion": 0.3,
                    "agreeableness": 0.5,
                    "neuroticism": 0.3
                },
                "patterns": ["analytical_thinker"],
                "description": "Conduct scientific research and experiments",
                "skills": ["Research Methods", "Data Analysis", "Critical Thinking"]
            },
            {
                "title": "Entrepreneur",
                "category": "Business",
                "holland_codes": ["EAS", "ECS", "ERS"],
                "personality_match": {
                    "openness": 0.9,
                    "conscientiousness": 0.7,
                    "extraversion": 0.9,
                    "agreeableness": 0.5,
                    "neuroticism": 0.6
                },
                "patterns": ["entrepreneurial", "creative_personality"],
                "description": "Start and manage business ventures",
                "skills": ["Innovation", "Risk Management", "Leadership"]
            },
            {
                "title": "Clinical Psychologist",
                "category": "Healthcare",
                "holland_codes": ["SIA", "SIS", "SIE"],
                "personality_match": {
                    "openness": 0.8,
                    "conscientiousness": 0.8,
                    "extraversion": 0.5,
                    "agreeableness": 0.9,
                    "neuroticism": 0.4
                },
                "patterns": ["social_leader"],
                "description": "Diagnose and treat mental health disorders",
                "skills": ["Empathy", "Active Listening", "Assessment"]
            }
        ]
    
    def _validate_input(self, input_data: Dict) -> bool:
        """
        Validate input data structure.
        
        Args:
            input_data: Input dictionary
        
        Returns:
            bool: True if valid
        """
        return "traits" in input_data
    
    def _get_processing_time(self) -> str:
        """
        Get simulated processing time.
        
        Returns:
            str: Processing time string
        """
        import time
        return f"{time.time():.3f}s"
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """
        Generate error response.
        
        Args:
            message: Error message
        
        Returns:
            Dict: Error response
        """
        return {
            "agent": self.agent_name,
            "error": True,
            "message": message,
            "queries": [],
            "career_matches": [],
            "search_terms": []
        }
