"""Base agent class that defines the common interface and functionality for all AI agents."""
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.state: Dict[str, Any] = {}
        self.last_interaction: Optional[datetime] = None
        self.conversation_history: List[Dict[str, Any]] = []
        logger.info(f"Initializing {name} agent with ID {agent_id}")

    @abstractmethod
    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process user input and return a response."""
        pass

    @abstractmethod
    async def generate_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on user data."""
        pass

    async def interact(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle a single interaction with the user."""
        try:
            self.last_interaction = datetime.now()
            
            # Process the input
            response = await self.process_input(user_input, context)
            
            # Record the interaction
            interaction = {
                "timestamp": self.last_interaction,
                "user_input": user_input,
                "response": response,
                "context": context
            }
            self.conversation_history.append(interaction)
            
            return {
                "status": "success",
                "response": response,
                "timestamp": self.last_interaction.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in {self.name} agent interaction: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Return the agent's conversation history."""
        return self.conversation_history

    def clear_conversation_history(self) -> None:
        """Clear the agent's conversation history."""
        self.conversation_history = []
        logger.info(f"Cleared conversation history for {self.name} agent")

    @abstractmethod
    async def validate_response(self, response: str) -> bool:
        """Validate the agent's response before sending it to the user."""
        pass

    @abstractmethod
    async def integrate_with_agents(self, other_agents: List['BaseAgent']) -> None:
        """Define how this agent integrates with other agents."""
        pass