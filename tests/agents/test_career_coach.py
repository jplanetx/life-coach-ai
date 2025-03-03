"""Tests for the CareerCoach agent implementation."""
import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from pathlib import Path

from src.agents.career_coach import CareerCoachAgent

@pytest.fixture
def career_coach():
    """Create a CareerCoach agent for testing."""
    return CareerCoachAgent("test-career-coach")

@pytest.fixture
def mock_industry_data():
    """Mock industry trends data."""
    return {
        "technology": {
            "trends": [
                {
                    "name": "Artificial Intelligence",
                    "growth_rate": 0.34,
                    "demand_level": "high",
                    "skills_in_demand": ["machine learning", "python"]
                }
            ],
            "market_outlook": "very positive",
            "remote_work_availability": "high",
            "average_salary_growth": 0.15
        }
    }

@pytest.fixture
def mock_skill_data():
    """Mock skill marketplace data."""
    return {
        "roles": {
            "data_scientist": {
                "required_skills": ["python", "machine learning"],
                "recommended_skills": ["deep learning"],
                "learning_paths": {
                    "beginner": [
                        {
                            "skill": "python",
                            "resources": [
                                {
                                    "type": "course",
                                    "name": "Python for Data Science",
                                    "platform": "Coursera",
                                    "duration": "4 weeks"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

@pytest.mark.asyncio
async def test_process_input_career_path(career_coach, mock_industry_data):
    """Test career path analysis."""
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_industry_data)
        
        response = await career_coach.process_input(
            "What career path should I take in technology?",
            {"industry": "technology"}
        )
        
        assert response is not None
        assert len(response) > 0

@pytest.mark.asyncio
async def test_analyze_skill_gaps(career_coach, mock_skill_data):
    """Test skill gap analysis."""
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_skill_data)
        
        context = {
            "skills": ["python"],
            "career_goals": {"target_role": "data_scientist"}
        }
        
        response = await career_coach._analyze_skill_gaps(context)
        assert "machine learning" in response.lower()

@pytest.mark.asyncio
async def test_generate_recommendations(career_coach, mock_industry_data, mock_skill_data):
    """Test recommendation generation."""
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_industry_data)
        
        recommendations = await career_coach.generate_recommendations({
            "industry": "technology",
            "skills": ["python"],
            "career_goals": {"target_role": "data_scientist"}
        })
        
        assert len(recommendations) > 0
        assert any(r for r in recommendations if "machine learning" in str(r).lower())

@pytest.mark.asyncio
async def test_validate_response(career_coach):
    """Test response validation."""
    # Test valid response
    valid_response = "Based on your background in technology, I recommend focusing on machine learning skills through courses on Coursera."
    is_valid = await career_coach.validate_response(valid_response)
    assert is_valid
    
    # Test invalid response
    invalid_response = ""
    is_valid = await career_coach.validate_response(invalid_response)
    assert not is_valid

@pytest.mark.asyncio
async def test_context_enhancement(career_coach, mock_industry_data):
    """Test context enhancement with industry trends."""
    with patch('builtins.open', MagicMock()) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_industry_data)
        
        context = {"industry": "technology"}
        enhanced = await career_coach.analyze_context(context)
        
        assert "temporal_context" in enhanced
        assert "user_preferences" in enhanced
        assert enhanced.get("industry") == "technology"

@pytest.mark.asyncio
async def test_learning_system(career_coach):
    """Test the agent's learning capabilities."""
    # Simulate multiple interactions
    interactions = [
        ("What skills do I need for AI?", {"industry": "technology"}),
        ("How can I become a data scientist?", {"industry": "technology"}),
        ("Should I learn Python?", {"industry": "technology"})
    ]
    
    for question, context in interactions:
        await career_coach.interact(question, context)
    
    # Verify learning history
    assert len(career_coach.learning_history) == len(interactions)
    
    # Verify knowledge base updates
    assert career_coach.knowledge_base is not None

@pytest.mark.asyncio
async def test_multi_agent_integration(career_coach):
    """Test integration with other agents."""
    # Create mock agents
    mock_financial = MagicMock()
    mock_financial.expertise_domains = {"finance"}
    
    mock_health = MagicMock()
    mock_health.expertise_domains = {"health"}
    
    # Test integration
    await career_coach.integrate_with_agents([mock_financial, mock_health])
    
    # Verify agent relationships
    assert hasattr(career_coach, "financial_advisor")
    assert hasattr(career_coach, "health_coach")