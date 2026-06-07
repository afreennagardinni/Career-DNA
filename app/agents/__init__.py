"""
Agents Package
Contains AI agent implementations for Career DNA multi-agent system.
"""

try:
    from app.agents.psychometric_agent import PsychometricAgent
except Exception:
    PsychometricAgent = None

try:
    from app.agents.pattern_analysis_agent import PatternAnalysisAgent
except Exception:
    PatternAnalysisAgent = None

try:
    from app.agents.career_query_agent import CareerQueryAgent
except Exception:
    CareerQueryAgent = None

try:
    from app.agents.rag_retrieval_agent import RAGRetrievalAgent
except Exception:
    RAGRetrievalAgent = None

try:
    from app.agents.decision_agent import DecisionAgent
except Exception:
    DecisionAgent = None

from app.agents.video_agent import VideoRecommendationAgent
from app.agents.mentor_agent import MentorMatchAgent
from app.agents.skill_gap_agent import SkillGapAgent
from app.agents.mood_agent import MoodMotivationAgent
from app.agents.trends_agent import IndustryTrendsAgent

try:
    from app.agents.agent_coordinator import AgentCoordinator
    from app.agents.pipeline import run_career_dna_pipeline, run_career_dna_pipeline_from_profile
except Exception:
    AgentCoordinator = None
    run_career_dna_pipeline = None
    run_career_dna_pipeline_from_profile = None

__all__ = [
    'PsychometricAgent',
    'PatternAnalysisAgent',
    'CareerQueryAgent',
    'RAGRetrievalAgent',
    'DecisionAgent',
    'VideoRecommendationAgent',
    'MentorMatchAgent',
    'SkillGapAgent',
    'MoodMotivationAgent',
    'IndustryTrendsAgent',
    'AgentCoordinator',
    'run_career_dna_pipeline',
    'run_career_dna_pipeline_from_profile'
]
