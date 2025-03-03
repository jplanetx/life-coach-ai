"""CLI interface for the Life Coach AI system."""
import asyncio
import argparse
import json
from pathlib import Path
from typing import Dict, Any
import logging
from dotenv import load_dotenv

from .core.orchestrator import AgentOrchestrator
from .agents.career_coach import CareerCoachAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LifeCoachCLI:
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.session_data: Dict[str, Any] = {}
        self._setup_agents()

    def _setup_agents(self) -> None:
        """Initialize and register AI agents."""
        # For MVP, we only initialize the CareerCoach agent
        career_coach = CareerCoachAgent("career-coach-1")
        self.orchestrator.register_agent(career_coach)
        self.primary_agent_id = career_coach.agent_id

    async def start_session(self) -> None:
        """Start an interactive coaching session."""
        print("\nWelcome to Life Coach AI! 🚀")
        print("For MVP, I'm specialized in career guidance. Let me help you with your career journey.")
        
        # Collect initial context
        await self._collect_user_context()
        
        while True:
            try:
                user_input = input("\nWhat would you like to know about your career? (type 'exit' to quit)\n> ")
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\nThank you for using Life Coach AI! Good luck with your career journey! 👋")
                    break
                
                # Process the query through the orchestrator
                response = await self.orchestrator.coordinate_response(
                    user_input,
                    self.primary_agent_id,
                    self.session_data
                )
                
                if response["status"] == "success":
                    print(f"\n{response['integrated_response']}")
                else:
                    print(f"\nError: {response['error']}")
                    
            except KeyboardInterrupt:
                print("\nSession terminated by user.")
                break
            except Exception as e:
                logger.error(f"Error in session: {e}")
                print("\nSorry, I encountered an error. Please try again.")

    async def _collect_user_context(self) -> None:
        """Collect initial user context for better recommendations."""
        print("\nTo provide better guidance, I'd like to know a bit about you.")
        
        # Collect industry information
        print("\nWhat industry are you in or interested in?")
        print("Available industries: technology, healthcare, finance")
        industry = input("> ").lower()
        
        # Collect skills
        print("\nWhat are your key skills? (comma-separated list)")
        skills_input = input("> ")
        skills = [skill.strip() for skill in skills_input.split(",")]
        
        # Collect career goals
        print("\nWhat role are you targeting? (e.g., data_scientist, software_engineer, product_manager)")
        target_role = input("> ").lower()
        
        self.session_data = {
            "industry": industry,
            "skills": skills,
            "career_goals": {
                "target_role": target_role
            }
        }
        
        print("\nThanks! I'll use this information to provide personalized guidance.")

def main():
    """Main entry point for the CLI application."""
    load_dotenv()  # Load environment variables
    
    print("Initializing Life Coach AI system...")
    cli = LifeCoachCLI()
    
    # Run the async session in the event loop
    asyncio.run(cli.start_session())

if __name__ == "__main__":
    main()