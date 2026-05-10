---
description: Run the complete Career DNA multi-agent pipeline
---

# Run Career DNA Pipeline

This workflow runs the complete Career DNA pipeline through all agents to generate comprehensive career recommendations.

## Pipeline Flow

The pipeline executes agents in sequence:

1. **Psychometric Agent** - Extracts personality traits from assessment data
2. **Pattern Analysis Agent** - Detects patterns and correlations in traits
3. **Career Query Agent** - Generates career matches using RAG or static database
4. **RAG Retrieval Agent** - Retrieves relevant career and skill documents
5. **Decision Agent** - Combines all outputs into final recommendations

## Usage

### Via API Endpoint

**Endpoint:** `POST /assessment/pipeline`

**Request Body:**
```json
{
  "source": "profile",
  "user_context": {
    "location": "San Francisco",
    "experience_level": "mid_level",
    "current_skills": ["Python", "SQL"],
    "preferred_categories": ["Technology"]
  }
}
```

**Response:**
```json
{
  "personality": {
    "traits": {
      "big_five": {...},
      "riasec": {...}
    },
    "dominant_traits": ["openness", "conscientiousness"],
    "trait_profile": "A creative and conscientious individual...",
    "confidence": 0.95
  },
  "top_careers": [
    {
      "rank": 1,
      "career": "Software Engineer",
      "match_score": 82.5,
      "description": "...",
      "skills": ["Programming", "Problem Solving"]
    }
  ],
  "confidence_scores": {
    "psychometric": 0.95,
    "pattern": 0.8,
    "career_query": 0.8,
    "rag": 0.8,
    "overall": 0.87
  },
  "explanation": "Based on dominant traits: openness, conscientiousness...",
  "action_plan": {
    "short_term": [...],
    "medium_term": [...],
    "long_term": [...]
  },
  "metadata": {
    "pipeline_complete": true,
    "rag_enabled": true
  }
}
```

### Via Python Code

```python
from app.agents import run_career_dna_pipeline, run_career_dna_pipeline_from_profile

# Run from assessment data
assessment_data = {
    "assessment_type": "big_five_ocean",
    "answers": [{"question_id": "O1", "value": 4}, ...],
    "user_id": 1
}
result = run_career_dna_pipeline(assessment_data, user_context)

# Run from existing profile
profile_data = {
    "career_dna": {
        "personality": {"big_five": {...}},
        "interests": {"riasec": {...}, "holland_code": "RIS"}
    },
    "user_id": 1
}
result = run_career_dna_pipeline_from_profile(profile_data, user_context)
```

## Source Options

- **profile** (default): Runs pipeline from user's existing profile data
- **assessment**: Runs pipeline from raw assessment answers

## Requirements

- User must be logged in
- Profile must have completed both Big Five and RIASEC assessments (if using profile source)
- RAG components must be initialized (optional, falls back to static database if unavailable)
