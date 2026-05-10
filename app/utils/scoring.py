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
        # Assuming career has a riasec code or holland_code
        h_code = c.get('holland_code', '')
        if top_code in h_code:
            matches.append({
                'name': c.get('title', c.get('name', 'Unknown Career')),
                'match_score': 90
            })
    
    # Fallback if no match
    if not matches:
        matches = [{'name': 'Software Engineer', 'match_score': 94}]
        
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)

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
            
            dim = question['big5_dimension'][0].upper()
            big5[dim] += score
            big5_counts[dim] += 1
            
            # RIASEC from scale answers
            if score >= 4 and 'high' in question.get('riasec_map',{}):
                riasec[question['riasec_map']['high']] += 1
            elif score <= 2 and 'low' in question.get('riasec_map',{}):
                riasec[question['riasec_map']['low']] += 1
    
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
        'top_career': top_careers[0]['name'],
        'career_matches': top_careers
    }

def determine_dna_type(riasec, big5):
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
