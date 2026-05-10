# Career DNA Multi-Agent System Documentation

## Overview

The Career DNA platform implements a sophisticated multi-agent system for comprehensive career analysis and recommendations. The system uses four specialized agents that work in concert to transform raw assessment data into actionable career insights.

## Architecture

### Agent Pipeline Flow

```
Input Data
    ↓
┌─────────────────────────────────────────────────────────┐
│  1. Psychometric Agent                                  │
│     Input: Raw assessment answers                        │
│     Process: Trait extraction and scoring               │
│     Output: Structured traits with confidence           │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  2. Pattern Analysis Agent                              │
│     Input: Trait data from Psychometric Agent           │
│     Process: Pattern detection and correlation analysis  │
│     Output: Patterns, insights, and anomalies            │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  3. Career Query Agent                                  │
│     Input: Traits + Patterns                             │
│     Process: Career matching and query generation       │
│     Output: Career matches and search queries           │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│  4. Decision Agent                                      │
│     Input: All agent outputs                             │
│     Process: Synthesis and recommendation generation    │
│     Output: Final recommendations and action plan        │
└─────────────────────────────────────────────────────────┘
    ↓
Final Recommendations
```

## Agent Specifications

### 1. Psychometric Agent

**File:** `app/agents/psychometric_agent.py`

**Purpose:** Extracts and processes psychometric traits from user assessment data.

**Input:**
```python
{
    "assessment_type": "big_five_ocean" or "riasec",
    "answers": [
        {"question_id": "O1", "value": 4},
        {"question_id": "O2", "value": 5},
        ...
    ],
    "user_id": int
}
```

**Process:**
1. Validates input data structure
2. Routes to appropriate scoring algorithm (Big Five or RIASEC)
3. Calculates normalized trait scores (0-100)
4. Identifies dominant traits (≥ 70 threshold)
5. Generates human-readable trait profiles
6. Calculates confidence score based on answer completeness

**Output:**
```python
{
    "agent": "PsychometricAgent",
    "traits": {
        "big_five": {
            "openness": 80.0,
            "conscientiousness": 75.0,
            "extraversion": 60.0,
            "agreeableness": 85.0,
            "neuroticism": 45.0
        }
    },
    "dominant_traits": ["openness", "agreeableness"],
    "trait_profile": "A creative and curious, cooperative and empathetic individual",
    "confidence": 0.95,
    "metadata": {
        "assessment_type": "big_five_ocean",
        "answer_count": 20,
        "processing_time": "1234567890.123s"
    }
}
```

**Key Methods:**
- `process(input_data)` - Main processing method
- `_process_big_five(answers)` - Big Five scoring
- `_process_riasec(answers)` - RIASEC scoring
- `_generate_trait_profile(scores)` - Human-readable profile
- `get_traits_summary(profile_data)` - Extract from existing profile

---

### 2. Pattern Analysis Agent

**File:** `app/agents/pattern_analysis_agent.py`

**Purpose:** Detects patterns and correlations in psychometric data.

**Input:**
```python
{
    "traits": {
        "big_five": {...},
        "riasec": {...}
    },
    "user_id": int
}
```

**Process:**
1. Analyzes trait distributions and combinations
2. Detects predefined patterns (e.g., creative personality, analytical thinker)
3. Calculates correlations between personality traits and interests
4. Generates insights based on patterns
5. Identifies anomalies or unusual trait combinations
6. Flags potential response bias

**Output:**
```python
{
    "agent": "PatternAnalysisAgent",
    "patterns": [
        {
            "type": "creative_personality",
            "description": "High openness combined with strong artistic interests",
            "traits": ["openness", "artistic"],
            "strength": 0.85
        }
    ],
    "correlations": {
        "openness_artistic": 0.7,
        "conscientiousness_investigative": 0.5,
        ...
    },
    "insights": [
        "Strong openness, agreeableness traits suggest natural aptitude in related areas",
        "Primary interests in realistic and investigative indicate career preferences",
        "Pattern detected: High openness combined with strong artistic interests"
    ],
    "anomalies": [],
    "metadata": {
        "trait_count": 11,
        "pattern_count": 2,
        "processing_time": "1234567890.123s"
    }
}
```

**Detected Patterns:**
- **Creative Personality:** High openness + high artistic
- **Analytical Thinker:** High conscientiousness + high investigative
- **Social Leader:** High extraversion + high social
- **Practical Problem Solver:** High conscientiousness + high realistic
- **Entrepreneurial:** High extraversion + high enterprising
- **Balanced Profile:** Low variance across all traits

**Key Methods:**
- `process(input_data)` - Main processing method
- `_detect_patterns(big_five, riasec)` - Pattern detection
- `_calculate_correlations(big_five, riasec)` - Correlation analysis
- `_generate_insights(big_five, riasec, patterns)` - Insight generation
- `_detect_anomalies(big_five, riasec)` - Anomaly detection
- `compare_with_population(user_traits, population_data)` - Population comparison

---

### 3. Career Query Agent

**File:** `app/agents/career_query_agent.py`

**Purpose:** Generates dynamic career queries based on psychometric profile.

**Input:**
```python
{
    "traits": {
        "big_five": {...},
        "riasec": {...}
    },
    "patterns": [...],
    "holland_code": "RIS",
    "user_preferences": {
        "location": "San Francisco",
        "experience_level": "mid_level",
        "job_type": "full_time"
    }
}
```

**Process:**
1. Matches traits against career database (10 careers)
2. Calculates Holland code match (50% weight)
3. Calculates personality match (30% weight)
4. Applies pattern bonuses (20% weight)
5. Generates natural language search queries
6. Creates structured API queries for external services
7. Extracts keywords, job titles, and learning domains

**Output:**
```python
{
    "agent": "CareerQueryAgent",
    "queries": [
        {
            "type": "job_search",
            "platform": "linkedin",
            "parameters": {
                "keywords": ["investigative", "realistic"],
                "location": "San Francisco",
                "experience_level": "mid_level",
                "job_type": "full_time"
            }
        },
        {
            "type": "salary_lookup",
            "platform": "glassdoor",
            "parameters": {...}
        }
    ],
    "career_matches": [
        {
            "title": "Software Engineer",
            "category": "Technology",
            "match_score": 78.5,
            "holland_match": 66.67,
            "personality_match": 95.0,
            "pattern_bonus": 15.0,
            "description": "Design and develop software applications and systems",
            "skills": ["Programming", "Problem Solving", "System Design"]
        }
    ],
    "search_terms": [
        "careers similar to Software Engineer",
        "careers for investigative and realistic interests",
        "careers for analytical_thinker personality type"
    ],
    "metadata": {
        "career_count": 10,
        "query_count": 4,
        "holland_code": "RIS",
        "processing_time": "1234567890.123s"
    }
}
```

**Career Database:**
- 10 predefined careers across Technology, Design, Business, Finance, Healthcare, Research
- Each career has: Holland codes, personality profile, pattern associations, description, skills

**Key Methods:**
- `process(input_data)` - Main processing method
- `_generate_career_matches(traits, holland_code, patterns)` - Career matching
- `_calculate_holland_match(user_code, career_codes)` - Holland code scoring
- `_calculate_personality_match(user_traits, career_profile)` - Personality scoring
- `_generate_search_queries(traits, patterns, career_matches)` - Query generation
- `_generate_api_queries(traits, patterns, preferences)` - API query generation

---

### 4. Decision Agent

**File:** `app/agents/decision_agent.py`

**Purpose:** Combines outputs from all agents to make final career recommendations.

**Input:**
```python
{
    "psychometric_output": {...},
    "pattern_output": {...},
    "career_query_output": {...},
    "user_context": {
        "current_skills": ["Python", "SQL"],
        "preferred_categories": ["Technology", "Design"],
        "min_score": 50
    }
}
```

**Process:**
1. Normalizes and validates all agent outputs
2. Combines career matches using weighted algorithm:
   - Base score: 60%
   - Pattern bonus: 20%
   - Psychometric bonus: 20%
3. Applies decision rules:
   - Minimum score threshold
   - Stress risk warnings
   - User preference penalties
4. Generates detailed recommendations with reasoning
5. Creates action plan (short-term, medium-term, long-term)
6. Provides learning resources
7. Calculates overall confidence

**Output:**
```python
{
    "agent": "DecisionAgent",
    "recommendations": [
        {
            "rank": 1,
            "career": "Software Engineer",
            "category": "Technology",
            "match_score": 82.5,
            "description": "Design and develop software applications and systems",
            "key_skills": ["Programming", "Problem Solving", "System Design"],
            "reasoning": [
                "Pattern match: analytical_thinker",
                "Trait alignment: conscientiousness, openness"
            ],
            "next_steps": [
                "Research Software Engineer role and requirements",
                "Develop skills in: Programming, Problem Solving",
                "Network with professionals in Technology",
                "Gain relevant experience through projects or internships",
                "Apply for Software Engineer positions when ready"
            ],
            "warning": null
        }
    ],
    "action_plan": {
        "short_term": [
            "Complete skills assessment for Software Engineer",
            "Research top 3 recommended careers in detail",
            "Identify skill gaps and create learning plan",
            "Update resume and LinkedIn profile"
        ],
        "medium_term": [
            "Develop key skills for Software Engineer",
            "Build portfolio with relevant projects",
            "Network with industry professionals",
            "Consider certifications or courses"
        ],
        "long_term": [
            "Apply for Software Engineer positions",
            "Continue professional development",
            "Seek mentorship in chosen field",
            "Evaluate career progression and adjust goals"
        ],
        "resources": [
            {"name": "Coursera", "type": "online_courses", "url": "https://coursera.org"},
            {"name": "GitHub", "type": "projects", "url": "https://github.com"},
            {"name": "Glassdoor", "type": "salary_info", "url": "https://glassdoor.com"}
        ]
    },
    "confidence": 0.87,
    "reasoning": [
        "Based on dominant traits: openness, conscientiousness",
        "Primary pattern detected: analytical_thinker (High conscientiousness with strong investigative interests)",
        "Top career match: Software Engineer with 82.5% match",
        "Key insight: Strong openness, conscientiousness traits suggest natural aptitude in related areas"
    ],
    "metadata": {
        "career_count": 5,
        "agent_outputs": ["psychometric", "pattern", "career_query"],
        "processing_time": "1234567890.123s"
    }
}
```

**Decision Weights:**
- Psychometric output: 30%
- Pattern output: 25%
- Career query output: 45%

**Key Methods:**
- `process(input_data)` - Main processing method
- `_normalize_outputs(...)` - Output normalization
- `_combine_career_matches(...)` - Career combination
- `_apply_decision_rules(...)` - Rule application
- `_generate_recommendations(...)` - Recommendation generation
- `_create_action_plan(...)` - Action plan creation
- `_calculate_overall_confidence(...)` - Confidence calculation

---

### 5. Agent Coordinator

**File:** `app/agents/agent_coordinator.py`

**Purpose:** Orchestrates the multi-agent system for comprehensive career DNA analysis.

**Process:**
1. Instantiates all four agents
2. Manages data flow between agents
3. Handles two pipeline types:
   - **Assessment Pipeline:** Processes raw assessment data
   - **Profile Pipeline:** Processes complete user profiles
4. Aggregates all agent outputs
5. Returns unified response

**Usage Example:**

```python
from app.agents import AgentCoordinator

# Initialize coordinator
coordinator = AgentCoordinator()

# Process assessment
assessment_data = {
    "assessment_type": "big_five_ocean",
    "answers": [{"question_id": "O1", "value": 4}, ...],
    "user_id": 1
}
result = coordinator.process_assessment(assessment_data)

# Process complete profile
profile_data = {
    "career_dna": {
        "personality": {"big_five": {...}},
        "interests": {"riasec": {...}, "holland_code": "RIS"}
    },
    "user_id": 1
}
result = coordinator.process_complete_profile(profile_data)

# Get agent status
status = coordinator.get_agent_status()
```

**Key Methods:**
- `process_assessment(assessment_data, user_context)` - Assessment pipeline
- `process_complete_profile(profile_data, user_context)` - Profile pipeline
- `run_agent_pipeline(input_data, pipeline_type)` - Generic pipeline runner
- `get_agent_status()` - Agent status information

---

## Integration with API

### New Endpoint for Multi-Agent System

Add to `app/routes/assessment.py`:

```python
from app.agents import AgentCoordinator

# Initialize coordinator
agent_coordinator = AgentCoordinator()

@assessment_bp.route('/agent-analysis', methods=['POST'])
@login_required
def agent_analysis():
    """
    Run multi-agent analysis on user profile.
    
    Expected JSON payload:
    {
        "user_context": {
            "location": "San Francisco",
            "experience_level": "mid_level",
            "current_skills": ["Python", "SQL"],
            "preferred_categories": ["Technology"]
        }
    }
    
    Returns:
        JSON response with complete multi-agent analysis
    """
    from flask_login import current_user
    from app.models.profile import Profile
    
    # Get user's profile
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    
    if not profile or not profile.career_dna:
        return jsonify({
            'error': 'Profile incomplete',
            'message': 'Please complete both Big Five and RIASEC assessments first'
        }), 400
    
    # Get user context
    data = request.get_json() or {}
    user_context = data.get('user_context', {})
    
    # Run agent pipeline
    profile_data = {
        'career_dna': profile.career_dna,
        'user_id': current_user.id
    }
    
    result = agent_coordinator.process_complete_profile(profile_data, user_context)
    
    return jsonify(result), 200
```

---

## Data Flow Example

### Complete Workflow

```python
# Step 1: User completes Big Five assessment
POST /assessment/submit-answers
{
    "assessment_type": "big_five_ocean",
    "answers": [
        {"question_id": "O1", "value": 4},
        {"question_id": "O2", "value": 5},
        ...
    ]
}

# Step 2: User completes RIASEC assessment
POST /assessment/submit-answers
{
    "assessment_type": "riasec",
    "answers": [
        {"question_id": "R1", "value": 4},
        {"question_id": "R2", "value": 5},
        ...
    ]
}

# Step 3: Run multi-agent analysis
POST /assessment/agent-analysis
{
    "user_context": {
        "location": "San Francisco",
        "experience_level": "mid_level",
        "current_skills": ["Python", "SQL"],
        "preferred_categories": ["Technology"]
    }
}

# Response includes:
# - Psychometric agent output (traits, dominant traits)
# - Pattern analysis agent output (patterns, insights, correlations)
# - Career query agent output (career matches, search queries)
# - Decision agent output (recommendations, action plan)
# - Overall confidence score
```

---

## Agent Communication

### Data Passing Between Agents

1. **Psychometric → Pattern Analysis**
   - Passes: `traits` (big_five, riasec)
   - Pattern analysis uses traits for pattern detection

2. **Pattern Analysis → Career Query**
   - Passes: `patterns`, `insights`, `correlations`
   - Career query uses patterns for matching bonuses

3. **Career Query → Decision**
   - Passes: `career_matches`, `search_terms`, `queries`
   - Decision uses career matches as base recommendations

4. **All Agents → Decision**
   - Decision receives all outputs for synthesis
   - Applies weighted combination algorithm

---

## Error Handling

Each agent includes error handling:

- **Input validation:** Checks required fields
- **Error responses:** Returns structured error with message
- **Graceful degradation:** Continues with partial data if possible
- **Confidence scoring:** Low confidence for incomplete/invalid data

Example error response:
```python
{
    "agent": "PsychometricAgent",
    "error": True,
    "message": "Invalid input data",
    "traits": {},
    "dominant_traits": [],
    "confidence": 0.0
}
```

---

## Extending the System

### Adding a New Agent

1. Create new agent class in `app/agents/`
2. Implement `process(input_data)` method
3. Follow input → process → output pattern
4. Add to `AgentCoordinator`
5. Update `__init__.py` exports

### Adding New Patterns

Edit `PatternAnalysisAgent._detect_patterns()`:
```python
# Add new pattern
if big_five.get("trait", 0) >= self.dominant_threshold:
    if riasec.get("interest", 0) >= self.dominant_threshold:
        patterns.append({
            "type": "new_pattern",
            "description": "Pattern description",
            "traits": ["trait", "interest"],
            "strength": (big_five["trait"] + riasec["interest"]) / 200
        })
```

### Adding New Careers

Edit `CareerQueryAgent._load_career_database()`:
```python
{
    "title": "New Career",
    "category": "Category",
    "holland_codes": ["ABC", "DEF"],
    "personality_match": {
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.6,
        "agreeableness": 0.7,
        "neuroticism": 0.4
    },
    "patterns": ["pattern_type"],
    "description": "Career description",
    "skills": ["Skill1", "Skill2"]
}
```

---

## Performance Considerations

### Processing Time
- Each agent processes in < 100ms for standard data
- Total pipeline: ~300-500ms
- Can be optimized with async processing for parallel agent execution

### Memory Usage
- Minimal: Each agent processes data independently
- No shared state between agents
- Coordinator aggregates results at end

### Scalability
- Stateless design allows horizontal scaling
- Each agent can be deployed as separate microservice
- Coordinator can manage distributed agent instances

---

## Testing

### Unit Testing Each Agent

```python
# Test Psychometric Agent
agent = PsychometricAgent()
input_data = {
    "assessment_type": "big_five_ocean",
    "answers": [{"question_id": "O1", "value": 4}]
}
result = agent.process(input_data)
assert result["agent"] == "PsychometricAgent"
assert "traits" in result

# Test Pattern Analysis Agent
agent = PatternAnalysisAgent()
input_data = {
    "traits": {
        "big_five": {"openness": 80, "conscientiousness": 75},
        "riasec": {"artistic": 85, "investigative": 70}
    }
}
result = agent.process(input_data)
assert result["agent"] == "PatternAnalysisAgent"
assert "patterns" in result

# Test Career Query Agent
agent = CareerQueryAgent()
input_data = {
    "traits": {...},
    "patterns": [...],
    "holland_code": "RIS"
}
result = agent.process(input_data)
assert result["agent"] == "CareerQueryAgent"
assert "career_matches" in result

# Test Decision Agent
agent = DecisionAgent()
input_data = {
    "psychometric_output": {...},
    "pattern_output": {...},
    "career_query_output": {...}
}
result = agent.process(input_data)
assert result["agent"] == "DecisionAgent"
assert "recommendations" in result

# Test Coordinator
coordinator = AgentCoordinator()
result = coordinator.process_assessment(assessment_data)
assert result["coordinator"] == "AgentCoordinator"
assert "pipeline" in result
```

---

## Future Enhancements

### Potential Improvements

1. **Parallel Agent Execution**
   - Run agents concurrently where possible
   - Reduce total processing time

2. **Machine Learning Integration**
   - Train models on user outcomes
   - Improve pattern detection accuracy
   - Personalize career matching

3. **External API Integration**
   - Connect to real job boards (LinkedIn, Indeed)
   - Fetch live salary data (Glassdoor)
   - Integrate learning platforms (Coursera, Udemy)

4. **Feedback Loop**
   - Track user career decisions
   - Measure recommendation accuracy
   - Continuously improve algorithms

5. **Advanced Pattern Detection**
   - Use clustering algorithms
   - Discover new patterns automatically
   - Handle edge cases better

6. **Natural Language Generation**
   - Generate detailed career reports
   - Create personalized explanations
   - Provide interview preparation tips

---

## Summary

The Career DNA multi-agent system provides:

- **Modular Design:** Each agent has a single responsibility
- **Clear Data Flow:** Input → Process → Output pattern
- **Comprehensive Analysis:** Combines psychometric, pattern, and career data
- **Actionable Outputs:** Recommendations with action plans and resources
- **Extensible Architecture:** Easy to add new agents or modify existing ones
- **Production Ready:** Error handling, validation, and confidence scoring

The system transforms raw assessment data into personalized career guidance through a sophisticated pipeline of specialized AI agents.
