"""Career Coach agent that provides career guidance and professional development advice."""
import os
from typing import Dict, Any, List, Set
from datetime import datetime
import logging
import json
from langchain_google import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CareerCoachAgent(BaseAgent):
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "CareerCoach")
        self.expertise_domains = {"career", "professional_development", "job_market"}
        
        # Initialize LLM based on configuration
        self.llm = self._initialize_llm()
        
        # Load career-specific resources
        self._load_career_resources()
        
        # Initialize career analysis tools
        self._initialize_analysis_tools()

    def _initialize_llm(self):
        """Initialize the Google Gemini model."""
        temperature = float(os.getenv("TEMPERATURE", "0.7"))
        model = os.getenv("MODEL_NAME", "gemini-pro")
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            convert_system_message_to_human=True
        )

    def _load_career_resources(self) -> None:
        """Load career-specific resources and data."""
        try:
            # Load industry trends
            with open("data/career/industry_trends.json", "r") as f:
                self.industry_trends = json.load(f)
                
            # Load skill marketplace data
            with open("data/career/skill_marketplace.json", "r") as f:
                self.skill_marketplace = json.load(f)
                
            logger.info("Loaded career resources successfully")
        except Exception as e:
            logger.warning(f"Could not load some career resources: {e}")
            self.industry_trends = {}
            self.skill_marketplace = {}

    def _initialize_analysis_tools(self) -> None:
        """Initialize tools for career analysis."""
        self.career_prompts = {
            "path_analysis": ChatPromptTemplate.from_template(
                "Based on the user's background in {background} and goals in {goals}, "
                "analyze potential career paths considering current market trends in {industry}."
            ),
            "skill_assessment": ChatPromptTemplate.from_template(
                "Given the user's current skills: {current_skills}, "
                "and target role: {target_role}, identify key skill gaps "
                "and learning priorities."
            )
        }

    async def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process career-related queries and provide guidance."""
        try:
            # Analyze input for career-related intents
            intent = self._identify_career_intent(user_input)
            
            # Get relevant career context
            career_context = self._extract_career_context(context)
            
            # Generate response based on intent
            if intent == "career_path":
                response = await self._analyze_career_path(career_context)
            elif intent == "skill_development":
                response = await self._analyze_skill_gaps(career_context)
            elif intent == "job_market":
                response = await self._analyze_market_trends(career_context)
            else:
                response = await self._generate_general_advice(user_input, career_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing career input: {e}")
            return "I apologize, but I need more information to provide career guidance."

    def _identify_career_intent(self, user_input: str) -> str:
        """Identify the career-related intent from user input."""
        # Add intent classification logic
        if "career path" in user_input.lower() or "future" in user_input.lower():
            return "career_path"
        elif "skill" in user_input.lower() or "learn" in user_input.lower():
            return "skill_development"
        elif "market" in user_input.lower() or "industry" in user_input.lower():
            return "job_market"
        return "general"

    def _extract_career_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract career-relevant information from context."""
        career_context = {
            "professional_history": context.get("professional_history", {}),
            "skills": context.get("skills", []),
            "career_goals": context.get("career_goals", {}),
            "industry": context.get("industry", "general")
        }
        
        # Enhance with industry trends
        if career_context["industry"] in self.industry_trends:
            career_context["industry_trends"] = self.industry_trends[career_context["industry"]]
            
        return career_context

    async def _analyze_career_path(self, context: Dict[str, Any]) -> str:
        """Analyze and suggest career path options."""
        try:
            prompt = self.career_prompts["path_analysis"].format(
                background=context.get("professional_history", ""),
                goals=context.get("career_goals", ""),
                industry=context.get("industry", "general")
            )
            
            response = await self.llm.agenerate([prompt])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"Error in career path analysis: {e}")
            return "Unable to analyze career path at this moment."

    async def _analyze_skill_gaps(self, context: Dict[str, Any]) -> str:
        """Analyze skill gaps and provide development recommendations."""
        try:
            current_skills = set(context.get("skills", []))
            target_role = context.get("career_goals", {}).get("target_role", "")
            
            if not target_role:
                return "Please specify your target role for skill gap analysis."
            
            # Get required skills for target role
            required_skills = self._get_role_requirements(target_role)
            
            # Identify gaps
            skill_gaps = required_skills - current_skills
            
            # Generate learning recommendations
            recommendations = self._generate_learning_path(skill_gaps)
            
            return self._format_skill_recommendations(recommendations)
            
        except Exception as e:
            logger.error(f"Error in skill gap analysis: {e}")
            return "Unable to analyze skill gaps at this moment."

    async def _analyze_market_trends(self, context: Dict[str, Any]) -> str:
        """Analyze job market trends relevant to the user's context."""
        try:
            industry = context.get("industry", "general")
            trends = self.industry_trends.get(industry, {})
            
            if not trends:
                return "I don't have enough market data for your specific industry."
            
            analysis = self._analyze_industry_trends(trends, context)
            return self._format_market_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error in market trend analysis: {e}")
            return "Unable to analyze market trends at this moment."

    async def generate_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate career-related recommendations."""
        try:
            recommendations = []
            
            # Career path recommendations
            career_recs = await self._generate_career_recommendations(user_data)
            recommendations.extend(career_recs)
            
            # Skill development recommendations
            skill_recs = await self._generate_skill_recommendations(user_data)
            recommendations.extend(skill_recs)
            
            # Market opportunity recommendations
            market_recs = self._generate_market_recommendations(user_data)
            recommendations.extend(market_recs)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating career recommendations: {e}")
            return []

    async def validate_response(self, response: str) -> bool:
        """Validate career advice before sending to user."""
        if not response:
            return False
            
        try:
            # Check response quality
            is_actionable = self._check_actionable_advice(response)
            is_relevant = self._check_career_relevance(response)
            is_professional = self._check_professional_tone(response)
            
            return all([is_actionable, is_relevant, is_professional])
            
        except Exception as e:
            logger.error(f"Error validating response: {e}")
            return False

    async def integrate_with_agents(self, other_agents: List[BaseAgent]) -> None:
        """Integrate with other agents for holistic advice."""
        for agent in other_agents:
            if "finance" in agent.expertise_domains:
                # Register for financial impact insights
                self.financial_advisor = agent
            elif "health" in agent.expertise_domains:
                # Register for work-life balance insights
                self.health_coach = agent

    def _get_role_requirements(self, role: str) -> Set[str]:
        """Get required skills for a target role."""
        role_data = self.skill_marketplace.get("roles", {}).get(role.lower(), {})
        required_skills = set(role_data.get("required_skills", []))
        return required_skills

    def _generate_learning_path(self, skill_gaps: Set[str]) -> List[Dict[str, Any]]:
        """Generate a learning path for identified skill gaps."""
        learning_path = []
        
        for skill in skill_gaps:
            # Find courses for this skill across all roles
            for role_data in self.skill_marketplace.get("roles", {}).values():
                for level, path_data in role_data.get("learning_paths", {}).items():
                    for item in path_data:
                        if item["skill"].lower() == skill.lower():
                            learning_path.append({
                                "skill": skill,
                                "level": level,
                                "resources": item["resources"]
                            })
                            break
                            
        return learning_path

    def _format_skill_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format skill recommendations into a readable response."""
        if not recommendations:
            return "No specific learning recommendations found."
            
        response = "Here's your personalized learning path:\n\n"
        
        for rec in recommendations:
            response += f"📚 {rec['skill']} ({rec['level']}):\n"
            for resource in rec['resources']:
                response += f"  • {resource['name']} on {resource['platform']} ({resource['duration']})\n"
            response += "\n"
            
        return response

    def _analyze_industry_trends(self, trends: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze industry trends in context."""
        return {
            "growth_areas": [
                trend for trend in trends.get("trends", [])
                if trend.get("growth_rate", 0) > 0.2
            ],
            "market_outlook": trends.get("market_outlook"),
            "remote_work": trends.get("remote_work_availability"),
            "salary_growth": trends.get("average_salary_growth")
        }

    def _format_market_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format market analysis into a readable response."""
        response = "Industry Analysis:\n\n"
        
        # Growth Areas
        response += "🚀 High Growth Areas:\n"
        for area in analysis.get("growth_areas", []):
            response += f"  • {area['name']} (Growth: {area['growth_rate']*100}%)\n"
            response += f"    Skills in demand: {', '.join(area['skills_in_demand'])}\n"
        
        # Market Outlook
        response += f"\n📈 Market Outlook: {analysis.get('market_outlook', 'Unknown')}\n"
        
        # Remote Work
        response += f"🏠 Remote Work Availability: {analysis.get('remote_work', 'Unknown')}\n"
        
        # Salary Growth
        salary_growth = analysis.get('salary_growth', 0)
        response += f"💰 Average Salary Growth: {salary_growth*100}% annually\n"
        
        return response

    async def _generate_general_advice(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generate general career advice based on context."""
        try:
            template = (
                "Given the user's query: '{query}', "
                "and their context in {industry} industry, "
                "provide general career guidance and advice."
            )
            
            prompt = ChatPromptTemplate.from_template(template).format(
                query=user_input,
                industry=context.get("industry", "general")
            )
            
            response = await self.llm.agenerate([prompt])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"Error generating general advice: {e}")
            return "I apologize, I need more context to provide meaningful career advice."

    def _check_actionable_advice(self, response: str) -> bool:
        """Check if the response contains actionable advice."""
        # Look for action-oriented language
        action_words = ["should", "could", "recommend", "suggest", "try", "consider", "focus", "learn"]
        return any(word in response.lower() for word in action_words)

    def _check_career_relevance(self, response: str) -> bool:
        """Check if the response is career-relevant."""
        # Look for career-related terms
        career_terms = ["career", "job", "skill", "industry", "role", "professional", "work"]
        return any(term in response.lower() for term in career_terms)

    def _check_professional_tone(self, response: str) -> bool:
        """Check if the response maintains a professional tone."""
        # Look for unprofessional language or tone
        unprofessional_terms = ["dunno", "gonna", "wanna", "stuff", "things", "like", "um", "uh"]
        return not any(term in response.lower() for term in unprofessional_terms)

    async def _generate_career_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate career path recommendations."""
        try:
            industry = user_data.get("industry", "general")
            current_skills = set(user_data.get("skills", []))
            
            recommendations = []
            
            # Analyze industry trends
            if industry in self.industry_trends:
                trends = self.industry_trends[industry]["trends"]
                for trend in trends:
                    match_score = len(current_skills & set(trend["skills_in_demand"])) / len(trend["skills_in_demand"])
                    if match_score > 0.3:  # If user has >30% of required skills
                        recommendations.append({
                            "type": "career_path",
                            "path": trend["name"],
                            "confidence": match_score,
                            "growth_rate": trend["growth_rate"],
                            "required_skills": trend["skills_in_demand"],
                            "priority": trend["growth_rate"] * match_score
                        })
            
            return sorted(recommendations, key=lambda x: x["priority"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating career recommendations: {e}")
            return []

    async def _generate_skill_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate skill development recommendations."""
        try:
            current_skills = set(user_data.get("skills", []))
            industry = user_data.get("industry", "general")
            
            recommendations = []
            
            # Get high-demand skills for the industry
            if industry in self.industry_trends:
                industry_skills = set()
                for trend in self.industry_trends[industry]["trends"]:
                    industry_skills.update(trend["skills_in_demand"])
                
                # Identify skill gaps
                skill_gaps = industry_skills - current_skills
                
                # Prioritize skills by demand
                for skill in skill_gaps:
                    demand_score = sum(
                        1 for trend in self.industry_trends[industry]["trends"]
                        if skill in trend["skills_in_demand"]
                    )
                    
                    recommendations.append({
                        "type": "skill_development",
                        "skill": skill,
                        "demand_score": demand_score,
                        "priority": demand_score * self.industry_trends[industry]["average_salary_growth"]
                    })
            
            return sorted(recommendations, key=lambda x: x["priority"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating skill recommendations: {e}")
            return []

    def _generate_market_recommendations(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate market opportunity recommendations."""
        recommendations = []
        try:
            industry = user_data.get("industry", "general")
            
            if (industry in self.industry_trends):
                trends = self.industry_trends[industry]
                
                # Recommend based on market outlook
                if trends["market_outlook"] == "very positive":
                    recommendations.append({
                        "type": "market_opportunity",
                        "recommendation": "Industry Expansion",
                        "details": f"The {industry} sector shows strong growth potential with {trends['average_salary_growth']*100}% annual salary growth",
                        "priority": 0.9
                    })
                
                # Recommend based on remote work opportunities
                if trends["remote_work_availability"] == "high":
                    recommendations.append({
                        "type": "market_opportunity",
                        "recommendation": "Remote Work Opportunities",
                        "details": f"Strong remote work opportunities available in {industry}",
                        "priority": 0.8
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating market recommendations: {e}")
            return []