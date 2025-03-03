"""Agent orchestrator that manages communication and coordination between AI agents."""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from .base_agent import BaseAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("Initializing Agent Orchestrator")

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by its ID."""
        return self.agents.get(agent_id)

    async def coordinate_response(self, 
                                user_input: str, 
                                primary_agent_id: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate a response involving multiple agents."""
        try:
            primary_agent = self.agents.get(primary_agent_id)
            if not primary_agent:
                raise ValueError(f"Primary agent {primary_agent_id} not found")

            # Get primary agent's response
            primary_response = await primary_agent.process_input(user_input, context)

            # Determine if other agents should be consulted
            related_responses = {}
            for agent_id, agent in self.agents.items():
                if agent_id != primary_agent_id:
                    # Check if this agent should be consulted based on context
                    if self._should_consult_agent(agent, context):
                        response = await agent.process_input(user_input, context)
                        related_responses[agent_id] = response

            return {
                "status": "success",
                "primary_response": primary_response,
                "related_responses": related_responses,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in coordination: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _should_consult_agent(self, agent: BaseAgent, context: Dict[str, Any]) -> bool:
        """Determine if an agent should be consulted based on context."""
        if not context:
            return False

        # Add logic here to determine when to consult additional agents
        # For example, if discussing career changes, consult financial advisor
        topic = context.get("topic", "").lower()
        if topic == "career_change" and agent.name == "Financial Advisor":
            return True
        if topic == "work_life_balance" and agent.name == "Health Coach":
            return True

        return False

    async def generate_holistic_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations from all relevant agents."""
        all_recommendations = {}
        
        try:
            for agent_id, agent in self.agents.items():
                recommendations = await agent.generate_recommendations(user_data)
                all_recommendations[agent_id] = recommendations

            # Analyze recommendations for conflicts or synergies
            integrated_recommendations = self._integrate_recommendations(all_recommendations)
            
            return {
                "status": "success",
                "recommendations": integrated_recommendations,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _integrate_recommendations(self, 
                                 recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Integrate recommendations from multiple agents, resolving conflicts."""
        integrated = []
        conflicts = []

        # Identify and resolve conflicts between recommendations
        # This is a simplified version - you'll need more sophisticated conflict resolution
        for agent_id, agent_recs in recommendations.items():
            for rec in agent_recs:
                if not self._conflicts_with_existing(rec, integrated):
                    integrated.append({
                        "agent_id": agent_id,
                        "recommendation": rec,
                        "priority": rec.get("priority", 0)
                    })
                else:
                    conflicts.append(rec)

        # Sort by priority
        integrated.sort(key=lambda x: x["priority"], reverse=True)

        return integrated

    def _conflicts_with_existing(self, 
                               new_rec: Dict[str, Any], 
                               existing_recs: List[Dict[str, Any]]) -> bool:
        """Check if a new recommendation conflicts with existing ones."""
        # Implement conflict detection logic here
        # For example, check for time conflicts, contradictory advice, etc.
        return False  # Placeholder implementation