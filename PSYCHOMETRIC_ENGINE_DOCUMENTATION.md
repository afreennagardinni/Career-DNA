# Career DNA Psychometric Engine Documentation

## Overview

The Career DNA backend includes a comprehensive psychometric engine implementing two well-established assessment models:

1. **Big Five Personality Traits (OCEAN)** - Measures personality dimensions
2. **RIASEC Interest Inventory** - Measures career interests based on Holland's theory

## Question Dataset

### Location
`data/questions.json`

### Structure

The JSON file contains three main sections:

#### 1. Big Five (OCEAN) Questions
- **20 questions total** (4 per trait)
- **Traits measured:**
  - Openness to Experience
  - Conscientiousness
  - Extraversion
  - Agreeableness
  - Neuroticism

- **Question format:**
  ```json
  {
    "id": "O1",
    "text": "I see myself as someone who has an active imagination",
    "trait": "openness",
    "direction": "positive",
    "scale": "likert_5"
  }
  ```

- **Direction types:**
  - `positive`: Score as-is (higher = more of the trait)
  - `negative`: Reverse scored (6 - original_score)

#### 2. RIASEC Questions
- **24 questions total** (4 per interest)
- **Interests measured:**
  - Realistic (R)
  - Investigative (I)
  - Artistic (A)
  - Social (S)
  - Enterprising (E)
  - Conventional (C)

- **All questions are positive direction**

#### 3. Scale Definitions
- **5-point Likert scale:**
  - 1: Strongly Disagree
  - 2: Disagree
  - 3: Neutral
  - 4: Agree
  - 5: Strongly Agree

## Scoring Service

### Location
`app/services/scoring_service.py`

### Class: ScoringService

#### Big Five Scoring Algorithm

**Method:** `score_big_five(answers: List[Dict]) -> Dict`

**Scoring Logic:**

1. **Raw Score Calculation:**
   - For each answer, map to its trait
   - If direction is `positive`: score = value (1-5)
   - If direction is `negative`: score = 6 - value (reverses the scale)
   - Sum scores per trait

2. **Normalization:**
   - Raw sum / (number of questions × 5) × 100
   - Result: 0-100 scale per trait

3. **Example Calculation:**
   ```
   Openness questions: O1, O2, O3 (positive), O4 (negative)
   User answers: [4, 5, 3, 2]
   
   O1 (positive): 4
   O2 (positive): 5
   O3 (positive): 3
   O4 (negative): 6 - 2 = 4
   
   Raw sum = 4 + 5 + 3 + 4 = 16
   Max possible = 4 × 5 = 20
   Normalized = (16 / 20) × 100 = 80.0
   ```

**Output:**
```python
{
    'openness': 80.0,
    'conscientiousness': 75.0,
    'extraversion': 60.0,
    'agreeableness': 85.0,
    'neuroticism': 45.0
}
```

#### RIASEC Scoring Algorithm

**Method:** `score_riasec(answers: List[Dict]) -> Dict`

**Scoring Logic:**

1. **Raw Score Calculation:**
   - Sum values per interest (all positive direction)
   - 4 questions per interest

2. **Normalization:**
   - Raw sum / (4 × 5) × 100
   - Result: 0-100 scale per interest

3. **Holland Code Generation:**
   - Sort interests by score (descending)
   - Take top 3 interests
   - Create 3-letter code (e.g., "RIS")

**Example Calculation:**
```
Realistic answers: [4, 5, 3, 4]
Raw sum = 16
Normalized = (16 / 20) × 100 = 80.0

[Similar for other interests]

Top 3: Realistic (80), Investigative (75), Social (70)
Holland Code: "RIS"
```

**Output:**
```python
{
    'scores': {
        'realistic': 80.0,
        'investigative': 75.0,
        'artistic': 60.0,
        'social': 70.0,
        'enterprising': 55.0,
        'conventional': 65.0
    },
    'holland_code': 'RIS',
    'top_interests': ['realistic', 'investigative', 'social']
}
```

#### Career DNA Calculation

**Method:** `calculate_career_dna(big_five_scores: Dict, riasec_scores: Dict) -> Dict`

**Logic:**

1. **Dominant Traits Identification:**
   - Traits scoring ≥ 70.0 are considered dominant
   - If none, marked as "balanced"

2. **Career Matching Algorithm:**
   - **Holland Code Match (60% weight):**
     - Compare user's Holland code with career codes
     - Count matching letters in position
     - Score = (matches / 3) × 100
   
   - **Personality Match (40% weight):**
     - Compare user's Big Five scores with career ideal profiles
     - Calculate absolute difference per trait
     - Score = Σ(1 - difference) × 20 per trait
   
   - **Overall Match:**
     - (Holland Match × 0.6) + (Personality Match × 0.4)
     - Only careers with ≥ 50% match are returned

3. **Career Database:**
   - 8 predefined careers with:
     - Holland codes (multiple variations)
     - Ideal personality profiles (0-1 scale per trait)

**Output:**
```python
{
    'personality': {
        'big_five': {...},
        'dominant_traits': ['openness', 'conscientiousness']
    },
    'interests': {
        'riasec': {...},
        'holland_code': 'RIS',
        'top_interests': ['realistic', 'investigative', 'social']
    },
    'career_recommendations': [
        {
            'title': 'Software Engineer',
            'match_score': 78.5,
            'holland_match': 66.67,
            'personality_match': 95.0
        },
        ...
    ]
}
```

## API Endpoints

### 1. Get Questions

**Endpoint:** `GET /questions/<assessment_type>`

**Parameters:**
- `assessment_type`: "big_five_ocean" or "riasec"

**Response:**
```json
{
    "assessment_type": "big_five_ocean",
    "questions": [...],
    "traits": {
        "openness": {
            "name": "Openness to Experience",
            "description": "Curiosity, creativity, preference for variety and novelty"
        },
        ...
    }
}
```

### 2. Submit Answers

**Endpoint:** `POST /submit-answers`

**Authentication:** Required (login_required)

**Request Body:**
```json
{
    "assessment_type": "big_five_ocean",
    "answers": [
        {"question_id": "O1", "value": 4},
        {"question_id": "O2", "value": 5},
        ...
    ]
}
```

**Response (Big Five):**
```json
{
    "message": "Assessment completed successfully",
    "assessment_id": 1,
    "result": {
        "assessment_type": "big_five_ocean",
        "scores": {
            "openness": 80.0,
            "conscientiousness": 75.0,
            "extraversion": 60.0,
            "agreeableness": 85.0,
            "neuroticism": 45.0
        },
        "dominant_traits": ["openness", "agreeableness"]
    }
}
```

**Response (RIASEC):**
```json
{
    "message": "Assessment completed successfully",
    "assessment_id": 2,
    "result": {
        "scores": {
            "realistic": 80.0,
            "investigative": 75.0,
            "artistic": 60.0,
            "social": 70.0,
            "enterprising": 55.0,
            "conventional": 65.0
        },
        "holland_code": "RIS",
        "top_interests": ["realistic", "investigative", "social"]
    }
}
```

**Side Effects:**
- Creates Assessment record in database
- Creates Answer records for each response
- Updates user's Profile.career_dna with results
- Calculates profile completion percentage

### 3. Analyze Profile

**Endpoint:** `GET /analyze-profile`

**Authentication:** Required (login_required)

**Prerequisites:**
- User must have completed both Big Five and RIASEC assessments
- Profile must contain both personality and interests data

**Response:**
```json
{
    "message": "Profile analysis completed",
    "career_dna": {
        "personality": {
            "big_five": {...},
            "dominant_traits": [...]
        },
        "interests": {
            "riasec": {...},
            "holland_code": "RIS",
            "top_interests": [...]
        },
        "career_recommendations": [
            {
                "title": "Software Engineer",
                "match_score": 78.5,
                "holland_match": 66.67,
                "personality_match": 95.0
            },
            ...
        ]
    },
    "profile_completion": 100
}
```

### 4. Get Assessments

**Endpoint:** `GET /assessments`

**Authentication:** Required (login_required)

**Response:**
```json
{
    "assessments": [
        {
            "id": 1,
            "title": "Big Five Ocean Assessment",
            "assessment_type": "big_five_ocean",
            "status": "completed",
            "completed_at": "2024-01-15T10:30:00",
            "total_score": 345.0,
            "max_score": 500.0,
            "answer_count": 20
        },
        ...
    ]
}
```

### 5. Get Specific Assessment

**Endpoint:** `GET /assessments/<assessment_id>`

**Authentication:** Required (login_required)

**Response:**
```json
{
    "assessment": {...},
    "answers": [
        {
            "question_id": "O1",
            "answer_value": "4",
            "score": 4.0,
            ...
        },
        ...
    ]
}
```

## Database Models

### Assessment Model
- **Table:** `assessments`
- **Fields:**
  - `title`: Assessment name
  - `assessment_type`: "big_five_ocean" or "riasec"
  - `status`: "in_progress", "completed", "abandoned"
  - `completed_at`: Timestamp
  - `total_score`: Sum of answer scores
  - `max_score`: Maximum possible score
  - `user_id`: Foreign key to users

### Answer Model
- **Table:** `answers`
- **Fields:**
  - `question_id`: External question identifier
  - `answer_value`: User's response (as string)
  - `score`: Numeric score value
  - `assessment_id`: Foreign key to assessments

### Profile Model
- **Table:** `profiles`
- **Fields:**
  - `career_dna`: JSON field storing psychometric results
  - `completion_percentage`: Profile completion (0-100)
  - `user_id`: Foreign key to users (unique)

**Career DNA Structure:**
```json
{
    "personality": {
        "big_five": {
            "openness": 80.0,
            "conscientiousness": 75.0,
            "extraversion": 60.0,
            "agreeableness": 85.0,
            "neuroticism": 45.0
        },
        "dominant_traits": ["openness", "agreeableness"]
    },
    "interests": {
        "riasec": {
            "realistic": 80.0,
            "investigative": 75.0,
            "artistic": 60.0,
            "social": 70.0,
            "enterprising": 55.0,
            "conventional": 65.0
        },
        "holland_code": "RIS",
        "top_interests": ["realistic", "investigative", "social"]
    },
    "analysis": {
        "career_recommendations": [...]
    }
}
```

## Scoring Logic Summary

### Big Five (OCEAN)
1. **20 questions** (4 per trait × 5 traits)
2. **Mixed direction** (positive and negative items)
3. **Reverse scoring** for negative items: `6 - value`
4. **Normalization:** `(sum / max_possible) × 100`
5. **Dominant trait threshold:** ≥ 70.0

### RIASEC
1. **24 questions** (4 per interest × 6 interests)
2. **All positive direction**
3. **No reverse scoring needed**
4. **Normalization:** `(sum / max_possible) × 100`
5. **Holland code:** Top 3 interests by score

### Career Matching
1. **Holland code match:** 60% weight
2. **Personality match:** 40% weight
3. **Minimum threshold:** 50% overall match
4. **Top 5 recommendations** returned

## Usage Example

### Complete Workflow

```python
# 1. Get Big Five questions
GET /questions/big_five_ocean

# 2. Submit Big Five answers
POST /submit-answers
{
    "assessment_type": "big_five_ocean",
    "answers": [
        {"question_id": "O1", "value": 4},
        {"question_id": "O2", "value": 5},
        ...
    ]
}

# 3. Get RIASEC questions
GET /questions/riasec

# 4. Submit RIASEC answers
POST /submit-answers
{
    "assessment_type": "riasec",
    "answers": [
        {"question_id": "R1", "value": 4},
        {"question_id": "R2", "value": 5},
        ...
    ]
}

# 5. Analyze complete profile
GET /analyze-profile
```

## Technical Notes

### Reverse Scoring Explanation
Negative-direction questions are reverse-scored to prevent response bias:
- Original scale: 1 (Strongly Disagree) → 5 (Strongly Agree)
- Reversed scale: 5 (Strongly Disagree) → 1 (Strongly Agree)
- Formula: `6 - original_value`

Example:
- Question: "I see myself as someone who is reserved, quiet" (Extraversion, negative)
- User answers: 4 (Agree)
- Reversed score: 6 - 4 = 2 (Disagrees with being quiet = high extraversion)

### Normalization Formula
```
normalized_score = (raw_sum / (num_questions × max_scale_value)) × 100
```

This ensures:
- Scores are on a consistent 0-100 scale
- Comparisons across traits/assessments are valid
- Results are intuitive for users

### Career Database Extension
To add more careers, extend the `career_database` list in `scoring_service.py`:

```python
{
    'title': 'New Career',
    'holland_codes': ['ABC', 'DEF'],
    'personality_match': {
        'openness': 0.7,
        'conscientiousness': 0.8,
        'extraversion': 0.6,
        'agreeableness': 0.7,
        'neuroticism': 0.4
    }
}
```

## Validation

### Input Validation
- Assessment type must be "big_five_ocean" or "riasec"
- Answers must include question_id and value
- Value must be 1-5 (Likert scale)
- User must be authenticated for submission

### Error Handling
- Invalid assessment type: 400 Bad Request
- Missing required fields: 400 Bad Request
- Incomplete profile for analysis: 400 Bad Request
- Assessment not found: 404 Not Found

## References

### Big Five (OCEAN)
- Based on the Five-Factor Model of personality
- Widely used in psychological research
- Validated across cultures and populations

### RIASEC
- Holland's Theory of Career Choice
- RIASEC = Realistic, Investigative, Artistic, Social, Enterprising, Conventional
- Used in career counseling worldwide
- Strong empirical support for career prediction

## Future Enhancements

Potential improvements:
1. Add more questions per trait for higher reliability
2. Implement adaptive testing (adjust questions based on responses)
3. Add confidence intervals to scores
4. Expand career database with more occupations
5. Add industry-specific career matching
6. Implement longitudinal tracking of trait changes
7. Add comparative analytics (user vs. population norms)
