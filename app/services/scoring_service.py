"""
Psychometric Scoring Service
Implements scoring algorithms for Big Five (OCEAN) and RIASEC assessments.
"""

import json
import os
from typing import Dict, List, Tuple
from collections import defaultdict


class ScoringService:
    """
    Service for psychometric scoring and analysis.
    Handles Big Five (OCEAN) and RIASEC scoring algorithms.
    """
    
    def __init__(self):
        """Initialize scoring service with questions data."""
        self.questions_data = self.load_questions()
        # Load mixed questions for combined assessment
        self.mixed_questions = self.load_mixed_questions()
    
    def load_questions(self) -> Dict:
        """
        Load questions from JSON file.
        
        Returns:
            Dict: Questions data containing Big Five and RIASEC questions
        """
        questions_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data',
            'questions.json'
        )
        
        with open(questions_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_mixed_questions(self) -> Dict:
        """
        Load mixed questions that combine Big Five and RIASEC.
        
        Returns:
            Dict: Mixed questions data
        """
        # For now, use original questions to avoid Unicode issues
        # TODO: Implement proper mixed questions later
        print("Using original questions for now")
        return self.load_questions()
    
    def score_big_five(self, answers: List[Dict]) -> Dict:
        """
        Calculate Big Five (OCEAN) personality trait scores.
        
        Scoring Logic:
        - Each trait has 4 questions (2 positive, 2 negative)
        - Likert scale: 1-5 (Strongly Disagree to Strongly Agree)
        - Positive direction: score as-is
        - Negative direction: reverse score (6 - original_score)
        - Raw scores summed per trait
        - Normalized to 0-100 scale
        
        Args:
            answers: List of answer dicts with 'question_id' and 'value'
        
        Returns:
            Dict: Normalized scores for each OCEAN trait
        """
        # Initialize trait scores
        trait_scores = defaultdict(list)
        question_map = {q['id']: q for q in self.questions_data['big_five_ocean']['questions']}
        
        # Process each answer
        for answer in answers:
            question_id = answer.get('question_id')
            value = answer.get('value')
            
            if question_id not in question_map:
                continue
            
            question = question_map[question_id]
            trait = question['trait']
            direction = question['direction']
            
            # Reverse score for negative direction questions
            if direction == 'negative':
                score = 6 - value
            else:
                score = value
            
            trait_scores[trait].append(score)
        
        # Calculate normalized scores
        normalized_scores = {}
        for trait, scores in trait_scores.items():
            if scores:
                raw_sum = sum(scores)
                max_possible = len(scores) * 5  # 5 is max Likert value
                normalized = (raw_sum / max_possible) * 100
                normalized_scores[trait] = round(normalized, 2)
            else:
                normalized_scores[trait] = 0.0
        
        # Ensure all traits are present (even if 0)
        for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            if trait not in normalized_scores:
                normalized_scores[trait] = 0.0
        
        return normalized_scores
    
    def score_riasec(self, answers: List[Dict]) -> Dict:
        """
        Calculate RIASEC interest scores.
        
        Scoring Logic:
        - Each interest has 4 questions (all positive direction)
        - Likert scale: 1-5
        - Raw scores summed per interest
        - Normalized to 0-100 scale
        - Calculate Holland code (top 3 interests)
        
        Args:
            answers: List of answer dicts with 'question_id' and 'value'
        
        Returns:
            Dict: Normalized scores and Holland code
        """
        # Initialize interest scores
        interest_scores = defaultdict(list)
        question_map = {q['id']: q for q in self.questions_data['riasec']['questions']}
        
        # Process each answer
        for answer in answers:
            question_id = answer.get('question_id')
            value = answer.get('value')
            
            if question_id not in question_map:
                continue
            
            question = question_map[question_id]
            interest = question['trait']
            
            interest_scores[interest].append(value)
        
        # Calculate normalized scores
        normalized_scores = {}
        for interest, scores in interest_scores.items():
            if scores:
                raw_sum = sum(scores)
                max_possible = len(scores) * 5
                normalized = (raw_sum / max_possible) * 100
                normalized_scores[interest] = round(normalized, 2)
            else:
                normalized_scores[interest] = 0.0
        
        # Ensure all interests are present
        for interest in ['realistic', 'investigative', 'artistic', 'social', 'enterprising', 'conventional']:
            if interest not in normalized_scores:
                normalized_scores[interest] = 0.0
        
        # Calculate Holland code (top 3 interests)
        sorted_interests = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        holland_code = ''.join([interest[0].upper() for interest, score in sorted_interests[:3]])
        
        return {
            'scores': normalized_scores,
            'holland_code': holland_code,
            'top_interests': [interest for interest, score in sorted_interests[:3]]
        }
    
    def calculate_career_dna(self, big_five_scores: Dict, riasec_scores: Dict) -> Dict:
        """
        Combine Big Five and RIASEC scores into a comprehensive Career DNA profile.
        
        Args:
            big_five_scores: Normalized OCEAN scores
            riasec_scores: RIASEC scores with Holland code
        
        Returns:
            Dict: Comprehensive Career DNA profile
        """
        career_dna = {
            'personality': {
                'big_five': big_five_scores,
                'dominant_traits': self._get_dominant_traits(big_five_scores)
            },
            'interests': {
                'riasec': riasec_scores['scores'],
                'holland_code': riasec_scores['holland_code'],
                'top_interests': riasec_scores['top_interests']
            },
            'career_recommendations': self._generate_career_recommendations(
                big_five_scores,
                riasec_scores['scores'],
                riasec_scores['holland_code']
            )
        }
        
        return career_dna
    
    def _get_dominant_traits(self, scores: Dict, threshold: float = 70.0) -> List[str]:
        """
        Get dominant personality traits above threshold.
        
        Args:
            scores: Trait scores
            threshold: Minimum score to be considered dominant
        
        Returns:
            List: Dominant trait names
        """
        dominant = [trait for trait, score in scores.items() if score >= threshold]
        return dominant if dominant else ['balanced']
    
    def _generate_career_recommendations(
        self,
        big_five: Dict,
        riasec: Dict,
        holland_code: str
    ) -> List[Dict]:
        """
        Generate career recommendations based on psychometric profile.
        
        Args:
            big_five: OCEAN scores
            riasec: RIASEC scores
            holland_code: 3-letter Holland code
        
        Returns:
            List: Career recommendations with match scores
        """
        # Career database mapped to Holland codes and personality traits
        career_database = [
            {
                'title': 'Software Engineer',
                'holland_codes': ['IRE', 'IRS', 'IER'],
                'personality_match': {
                    'openness': 0.8,
                    'conscientiousness': 0.9,
                    'extraversion': 0.4,
                    'agreeableness': 0.5,
                    'neuroticism': 0.3
                }
            },
            {
                'title': 'Data Scientist',
                'holland_codes': ['IRE', 'IRS', 'ISR'],
                'personality_match': {
                    'openness': 0.9,
                    'conscientiousness': 0.8,
                    'extraversion': 0.3,
                    'agreeableness': 0.4,
                    'neuroticism': 0.3
                }
            },
            {
                'title': 'Product Manager',
                'holland_codes': ['EIS', 'ESR', 'ERS'],
                'personality_match': {
                    'openness': 0.7,
                    'conscientiousness': 0.8,
                    'extraversion': 0.8,
                    'agreeableness': 0.6,
                    'neuroticism': 0.4
                }
            },
            {
                'title': 'UX Designer',
                'holland_codes': ['AIE', 'AIS', 'AES'],
                'personality_match': {
                    'openness': 0.9,
                    'conscientiousness': 0.7,
                    'extraversion': 0.5,
                    'agreeableness': 0.7,
                    'neuroticism': 0.4
                }
            },
            {
                'title': 'Marketing Manager',
                'holland_codes': ['ESA', 'EAS', 'ECS'],
                'personality_match': {
                    'openness': 0.7,
                    'conscientiousness': 0.7,
                    'extraversion': 0.9,
                    'agreeableness': 0.6,
                    'neuroticism': 0.5
                }
            },
            {
                'title': 'Financial Analyst',
                'holland_codes': ['CIE', 'CIR', 'CER'],
                'personality_match': {
                    'openness': 0.5,
                    'conscientiousness': 0.9,
                    'extraversion': 0.4,
                    'agreeableness': 0.5,
                    'neuroticism': 0.4
                }
            },
            {
                'title': 'Human Resources Manager',
                'holland_codes': ['SCE', 'SEC', 'SER'],
                'personality_match': {
                    'openness': 0.6,
                    'conscientiousness': 0.8,
                    'extraversion': 0.7,
                    'agreeableness': 0.9,
                    'neuroticism': 0.4
                }
            },
            {
                'title': 'Research Scientist',
                'holland_codes': ['IRE', 'IRS', 'ISR'],
                'personality_match': {
                    'openness': 0.9,
                    'conscientiousness': 0.9,
                    'extraversion': 0.3,
                    'agreeableness': 0.5,
                    'neuroticism': 0.3
                }
            }
        ]
        
        recommendations = []
        
        for career in career_database:
            # Calculate Holland code match
            holland_match = 0
            for code in career['holland_codes']:
                # Check how many letters match
                match_count = sum(1 for i, letter in enumerate(code) if i < len(holland_code) and letter == holland_code[i])
                holland_match = max(holland_match, match_count)
            
            holland_score = (holland_match / 3) * 100
            
            # Calculate personality match
            personality_score = 0
            for trait, ideal_score in career['personality_match'].items():
                user_score = big_five.get(trait, 0) / 100  # Normalize to 0-1
                diff = abs(user_score - ideal_score)
                personality_score += (1 - diff) * 20  # Each trait worth 20 points
            
            # Calculate overall match score
            overall_match = (holland_score * 0.6) + (personality_score * 0.4)
            
            if overall_match >= 50:  # Only include matches above 50%
                recommendations.append({
                    'title': career['title'],
                    'match_score': round(overall_match, 2),
                    'holland_match': round(holland_score, 2),
                    'personality_match': round(personality_score, 2)
                })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_questions(self, assessment_type: str) -> List[Dict]:
        """
        Get questions for a specific assessment type.
        
        Args:
            assessment_type: 'big_five_ocean' or 'riasec'
        
        Returns:
            List: Question data
        """
        if assessment_type in self.questions_data:
            return self.questions_data[assessment_type]['questions']
        return []
    
    def get_traits_info(self, assessment_type: str) -> Dict:
        """
        Get trait information for a specific assessment type.
        
        Args:
            assessment_type: 'big_five_ocean' or 'riasec'
        
        Returns:
            Dict: Trait information
        """
        if assessment_type in self.questions_data:
            return self.questions_data[assessment_type]['traits']
        return {}
    
    def score_mixed_assessment(self, answers: List[Dict]) -> Dict:
        """
        Calculate scores for mixed Big Five + RIASEC assessment.
        
        Scoring Logic:
        - 20 questions total (Q1-Q20)
        - Card select questions: add weights from selected option
        - Scale questions: 1-5 Likert with negative direction handling
        - Different answers = different results
        
        Args:
            answers: List of answer dicts with 'question_id' and 'value'
        
        Returns:
            Dict: Combined Big Five and RIASEC scores
        """
        print('=== MIXED ASSESSMENT SCORING ===')
        print('Answers received:', len(answers))
        
        # Initialize scores
        riasec = {'R':0,'I':0,'A':0,'S':0,'E':0,'C':0}
        big5 = {'O':0,'C':0,'E':0,'A':0,'N':0}
        big5_counts = {'O':0,'C':0,'E':0,'A':0,'N':0}
        
        questions = self.mixed_questions.get('big_five_ocean', {}).get('questions', [])
        
        for answer in answers:
            q_id = answer.get('question_id')
            answer_val = answer.get('value')
            print(f'Processing {q_id}: {answer_val}')
            question = next((q for q in questions if q['id'] == q_id), None)
            
            if not question:
                print(f'Question {q_id} not found!')
                continue
                
            if question['type'] == 'card_select':
                # Find which option was selected
                selected_option = next(
                    (opt for opt in question.get('options', []) 
                     if opt.get('id') == str(answer_val)), None
                )
                if selected_option:
                    print(f'Selected option: {selected_option.get("text", "")}')
                    # Add RIASEC weights from selected option
                    for dim, weight in selected_option.get('riasec', {}).items():
                        riasec[dim] += weight
                    # Add Big Five weights
                    for dim, weight in selected_option.get('big5', {}).items():
                        big5[dim] += weight
                        big5_counts[dim] += 1
                    print(f'RIASEC: {riasec}, Big5: {big5}')
                    
            elif question['type'] == 'scale_5':
                # answer_val is 1-5
                score = float(answer_val)
                # Reverse if negative direction
                if question.get('direction') == 'negative':
                    score = 6 - score
                
                dim = question.get('big5_dimension', '').lower()
                if dim:
                    big5[dim] += score
                    big5_counts[dim] += 1
                    
                # RIASEC from scale answers
                if score >= 4 and 'high' in question.get('riasec_map',{}):
                    riasec[question['riasec_map']['high']] += 1
                elif score <= 2 and 'low' in question.get('riasec_map',{}):
                    riasec[question['riasec_map']['low']] += 1
        
        print(f'Raw RIASEC: {riasec}')
        print(f'Raw Big5: {big5}')
        
        # Normalize RIASEC to 0-100
        max_riasec = max(riasec.values()) if riasec.values() else 1
        riasec_normalized = {
            k: round((v/max_riasec)*100) 
            for k,v in riasec.items()
        }
        
        # Normalize Big5 to 0-100
        big5_normalized = {}
        for dim in big5:
            count = big5_counts.get(dim, 1)
            if count > 0:
                raw_avg = big5[dim] / count  # 1-5 scale
                big5_normalized[dim] = round(((raw_avg-1)/4)*100)
            else:
                big5_normalized[dim] = 0
        
        # Determine DNA type from actual scores
        dna_type = self._determine_dna_type(riasec_normalized, big5_normalized)
        top_careers = self._match_careers(riasec_normalized, big5_normalized)
        
        result = {
            'riasec': riasec_normalized,
            'big_five': big5_normalized,
            'dna_type': dna_type,
            'top_careers': top_careers[:3],
            'career_matches': top_careers
        }
        
        print('Mixed assessment result:', result)
        print('=== END MIXED SCORING ===')
        return result
    
    def _determine_dna_type(self, riasec, big5):
        # Get top 2 RIASEC codes
        top2 = sorted(riasec, key=riasec.get, reverse=True)[:2]
        code = ''.join(top2)
        
        # Map to DNA type name based on ACTUAL scores
        dna_map = {
            'IR': 'The Analytical Innovator',
            'RI': 'The Analytical Innovator',
            'IA': 'The Research Creative',
            'AI': 'The Research Creative',
            'IC': 'The Systematic Investigator',
            'CI': 'The Systematic Investigator',
            'IS': 'The Social Scientist',
            'SI': 'The Social Scientist',
            'EA': 'The Creative Entrepreneur',
            'AE': 'The Creative Entrepreneur',
            'ES': 'The Social Leader',
            'SE': 'The Social Leader',
            'EC': 'The Business Strategist',
            'CE': 'The Business Strategist',
            'RA': 'The Technical Artist',
            'AR': 'The Technical Artist',
            'RC': 'The Systematic Builder',
            'CR': 'The Systematic Builder',
            'SA': 'The Empathetic Designer',
            'AS': 'The Empathetic Designer',
        }
        return dna_map.get(code, 'The Versatile Explorer')
    
    def _match_careers(self, riasec, big5):
        # Simple career matching based on dominant traits
        careers = [
            {'name': 'Software Engineer', 'match': 95, 'category': 'Technology'},
            {'name': 'Data Scientist', 'match': 92, 'category': 'Analytics'},
            {'name': 'Product Manager', 'match': 88, 'category': 'Business'},
            {'name': 'UX Designer', 'match': 85, 'category': 'Design'},
            {'name': 'AI Researcher', 'match': 90, 'category': 'Research'},
            {'name': 'Business Analyst', 'match': 83, 'category': 'Analytics'},
            {'name': 'Project Manager', 'match': 80, 'category': 'Management'},
            {'name': 'Machine Learning Engineer', 'match': 93, 'category': 'Technology'},
            {'name': 'Data Engineer', 'match': 87, 'category': 'Technology'},
            {'name': 'Product Designer', 'match': 82, 'category': 'Design'},
        ]
        
        # Sort by match score and return top matches
        return sorted(careers, key=lambda x: x['match'], reverse=True)
