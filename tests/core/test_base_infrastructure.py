"""Tests for the base agent and orchestrator infrastructure."""
import pytest
from datetime import datetime
from src.core.base_agent import BaseAgent
from src.core.orchestrator import AgentOrchestrator

class MockAgent(BaseAgent):
    """Mock agent for testing purposes."""
    async def process_input(self, user_input: str, context=None):
        return f"Processed: {user_input}"

    async def generate_recommendations(self, user_data):
        return [{"recommendation": "Test recommendation", "priority": 1}]

    async def validate_response(self, response: str):
        return True

    async def integrate_with_agents(self, other_agents):
        pass

@pytest.fixture
def mock_agent():
    return MockAgent("test-agent", "Test Agent")

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

@pytest.mark.asyncio
async def test_agent_interaction(mock_agent):
    """Test basic agent interaction."""
    response = await mock_agent.interact("Hello", {"topic": "general"})
    assert response["status"] == "success"
    assert "Processed: Hello" in response["response"]
    assert "timestamp" in response

@pytest.mark.asyncio
async def test_agent_conversation_history(mock_agent):
    """Test agent conversation history management."""
    await mock_agent.interact("Hello")
    await mock_agent.interact("How are you?")
    
    history = mock_agent.get_conversation_history()
    assert len(history) == 2
    assert history[0]["user_input"] == "Hello"
    assert history[1]["user_input"] == "How are you?"

@pytest.mark.asyncio
async def test_orchestrator_coordination(orchestrator, mock_agent):
    """Test orchestrator's ability to coordinate between agents."""
    orchestrator.register_agent(mock_agent)
    
    response = await orchestrator.coordinate_response(
        "Hello",
        mock_agent.agent_id,
        {"topic": "general"}
    )
    
    assert response["status"] == "success"
    assert response["primary_response"] == "Processed: Hello"
    assert isinstance(response["timestamp"], str)

@pytest.mark.asyncio
async def test_holistic_recommendations(orchestrator, mock_agent):
    """Test generation of holistic recommendations."""
    orchestrator.register_agent(mock_agent)
    
    response = await orchestrator.generate_holistic_recommendations({
        "user_id": "test-user",
        "context": "test-context"
    })
    
    assert response["status"] == "success"
    assert len(response["recommendations"]) == 1
    assert response["recommendations"][0]["agent_id"] == mock_agent.agent_id