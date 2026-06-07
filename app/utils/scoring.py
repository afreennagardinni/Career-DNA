import json
import os

def load_data(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filepath = os.path.join(base_dir, 'data', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_question(q_id, questions):
    if isinstance(questions, dict) and 'questions' in questions:
        questions = questions['questions']
    for q in questions:
        if isinstance(q, dict) and str(q.get('id')) == str(q_id):
            return q
    return None

def find_option(question, option_id):
    for opt in question.get('options', []):
        if str(opt.get('id')) == str(option_id):
            return opt
    return None

def match_careers(riasec_scores, big5_scores):
    careers = load_data('careers.json')
    if isinstance(careers, dict) and 'careers' in careers:
        careers = careers['careers']
    # Simple matching algorithm based on top RIASEC code
    top_code = sorted(riasec_scores, key=riasec_scores.get, reverse=True)[0]
    matches = []
    
    for c in careers:
        h_codes = c.get('holland_codes', [])
        # Check if top RIASEC code is in any of the career's Holland codes
        if any(top_code in h_code for h_code in h_codes):
            match = c.copy()
            # Simple scoring: 90% if it matches the top code
            match['match_score'] = "95%" if h_codes and h_codes[0].startswith(top_code) else "88%"
            matches.append(match)
    
    # Fallback if no match
    if not matches:
        matches = [careers[0].copy()] if careers else []
        if matches:
            matches[0]['match_score'] = "94%"
        
    return sorted(matches, key=lambda x: x.get('match_score', '0%'), reverse=True)

def calculate_scores(answers: dict, questions: list) -> dict:
    # Initialize scores
    riasec = {'R':0,'I':0,'A':0,'S':0,'E':0,'C':0}
    big5 = {'O':0,'C':0,'E':0,'A':0,'N':0}
    big5_counts = {'O':0,'C':0,'E':0,'A':0,'N':0}
    
    for q_id, answer_val in answers.items():
        question = find_question(q_id, questions)
        if not question:
            continue
            
        if question['type'] == 'card_select':
            # Find which option was selected
            selected_option = find_option(
                question, str(answer_val)
            )
            if selected_option:
                # Add RIASEC weights from selected option
                for dim, weight in selected_option.get('riasec', {}).items():
                    riasec[dim] += weight
                # Add Big Five weights
                for dim, weight in selected_option.get('big5', {}).items():
                    big5[dim] += weight
                    big5_counts[dim] += 1
                    
        elif question['type'] == 'scale_5':
            # answer_val is 1-5
            try:
                score = float(answer_val)
            except (ValueError, TypeError):
                score = 3.0
            
            # Reverse if negative direction
            if question.get('direction') == 'negative':
                score = 6 - score
            
            # Big Five scoring
            dim_key = question.get('big5_dimension')
            if dim_key:
                dim = dim_key[0].upper()
                big5[dim] += score
                big5_counts[dim] += 1
            
            # RIASEC scoring from scale answers
            riasec_map = question.get('riasec_map', {})
            if score >= 4 and 'high' in riasec_map:
                riasec[riasec_map['high']] += (score - 3) # Weighted
            elif score <= 2 and 'low' in riasec_map:
                riasec[riasec_map['low']] += (3 - score) # Weighted
    
    # Normalize RIASEC to 0-100
    max_riasec = max(riasec.values()) if any(riasec.values()) else 1
    riasec_normalized = {
        k: round((v/max_riasec)*100) 
        for k,v in riasec.items()
    }
    
    # Normalize Big5 to 0-100
    big5_normalized = {}
    for dim in big5:
        count = big5_counts[dim] if big5_counts[dim] > 0 else 1
        raw_avg = big5[dim] / count  # 1-5 scale
        big5_normalized[dim] = round(((raw_avg-1)/4)*100)
    
    # Determine DNA type from actual scores
    dna_type = determine_dna_type(riasec_normalized, big5_normalized)
    top_careers = match_careers(riasec_normalized, big5_normalized)
    
    return {
        'riasec': riasec_normalized,
        'big5': big5_normalized,
        'dna_type': dna_type,
        'top_career': top_careers[0].get('title', 'Unknown Career') if top_careers else 'Generalist',
        'career_matches': top_careers
    }

def determine_dna_type(riasec, big5):
    # Get top 2 RIASEC codes
    top2 = sorted(riasec, key=riasec.get, reverse=True)[:2]
    code = ''.join(top2)
    
    # Base mapping
    dna_map = {
        'IR': 'Analytical Innovator', 'RI': 'Analytical Innovator',
        'IA': 'Research Creative', 'AI': 'Research Creative',
        'IC': 'Systematic Investigator', 'CI': 'Systematic Investigator',
        'IS': 'Social Scientist', 'SI': 'Social Scientist',
        'EA': 'Creative Entrepreneur', 'AE': 'Creative Entrepreneur',
        'ES': 'Social Leader', 'SE': 'Social Leader',
        'EC': 'Business Strategist', 'CE': 'Business Strategist',
        'RA': 'Technical Artist', 'AR': 'Technical Artist',
        'RC': 'Systematic Builder', 'CR': 'Systematic Builder',
        'SA': 'Empathetic Designer', 'AS': 'Empathetic Designer',
    }
    
    base_name = dna_map.get(code, 'Versatile Explorer')
    
    # Add Big Five Modifiers
    if big5.get('O', 0) > 70:
        base_name = "Visionary " + base_name
    elif big5.get('C', 0) > 70:
        base_name = "Strategic " + base_name
    elif big5.get('E', 0) > 70:
        base_name = "Dynamic " + base_name
    
    return "The " + base_name

def match_careers(riasec, big5):
    data = load_data('careers.json')
    careers = data.get('careers', []) if isinstance(data, dict) else data
    
    top_code = sorted(riasec, key=riasec.get, reverse=True)[0]
    
    scored_careers = []
    for c in careers:
        if not isinstance(c, dict): continue
        score = 0
        h_codes = c.get('holland_codes', [])
        
        # RIASEC Match (0-60 points)
        if any(top_code in h_code for h_code in h_codes):
            score += 40
            if h_codes and h_codes[0].startswith(top_code):
                score += 20
        
        # Big Five Traits Match (0-40 points)
        # Example: Data roles benefit from high Conscientiousness
        if "data" in c['title'].lower() or "engineer" in c['title'].lower():
            if big5.get('C', 0) > 60: score += 20
            if big5.get('I', 0) > 60: score += 20
        
        # Creative roles benefit from high Openness
        if "design" in c['title'].lower() or "creative" in c['title'].lower():
            if big5.get('O', 0) > 60: score += 20
            if big5.get('A', 0) > 60: score += 20

        # Social roles benefit from high Agreeableness
        if "social" in c['title'].lower() or "manager" in c['title'].lower():
            if big5.get('A', 0) > 60: score += 20
            if big5.get('E', 0) > 60: score += 20

        c['match_percent'] = min(score + 30, 98) # Base 30% + traits
        c['match_score'] = f"{c['match_percent']}%"
        scored_careers.append(c)
        
    return sorted(scored_careers, key=lambda x: x['match_percent'], reverse=True)
