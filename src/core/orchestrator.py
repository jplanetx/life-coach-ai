"""Agent orchestrator that manages communication and coordination between AI agents."""
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import logging
import json
from pathlib import Path
from .base_agent import BaseAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.interaction_patterns: List[Dict[str, Any]] = []
        self.domain_expertise_map: Dict[str, Set[str]] = {}
        self.context_history: List[Dict[str, Any]] = []
        self.decision_history: List[Dict[str, Any]] = []
        logger.info("Initializing Agent Orchestrator")
        
        self._load_orchestration_config()

    def _load_orchestration_config(self) -> None:
        """Load orchestration configuration and rules."""
        try:
            config_path = Path("config/orchestration_rules.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.orchestration_rules = json.load(f)
            logger.info("Loaded orchestration rules")
        except Exception as e:
            logger.warning(f"Could not load orchestration rules: {e}")
            self.orchestration_rules = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        self._update_expertise_map(agent)
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    def _update_expertise_map(self, agent: BaseAgent) -> None:
        """Update the domain expertise map with agent capabilities."""
        for domain in agent.expertise_domains:
            if domain not in self.domain_expertise_map:
                self.domain_expertise_map[domain] = set()
            self.domain_expertise_map[domain].add(agent.agent_id)

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by its ID."""
        return self.agents.get(agent_id)

    async def coordinate_response(self, 
                                user_input: str, 
                                primary_agent_id: str,
                                context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate a response involving multiple agents."""
        try:
            # Track decision point
            decision_point = self._create_decision_point(user_input, primary_agent_id, context)
            
            # Get primary agent
            primary_agent = self.agents.get(primary_agent_id)
            if not primary_agent:
                raise ValueError(f"Primary agent {primary_agent_id} not found")

            # Analyze global context
            enhanced_context = await self._enhance_global_context(context)
            
            # Get primary agent's response
            primary_response = await primary_agent.process_input(user_input, enhanced_context)
            
            # Determine relevant agents based on context and expertise
            relevant_agents = self._identify_relevant_agents(enhanced_context)
            
            # Gather responses from relevant agents
            related_responses = await self._gather_agent_responses(
                user_input, 
                primary_agent_id, 
                relevant_agents, 
                enhanced_context
            )
            
            # Integrate and prioritize responses
            final_response = self._integrate_responses(
                primary_response, 
                related_responses, 
                enhanced_context
            )
            
            # Update context history
            self._update_context_history(enhanced_context, final_response)
            
            # Record decision outcome
            self._record_decision_outcome(decision_point, final_response)
            
            return {
                "status": "success",
                "primary_response": primary_response,
                "related_responses": related_responses,
                "integrated_response": final_response,
                "context": enhanced_context,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in coordination: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _create_decision_point(self, 
                             user_input: str, 
                             primary_agent_id: str,
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a decision point record for tracking orchestration decisions."""
        decision_point = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "primary_agent": primary_agent_id,
            "initial_context": context,
            "decision_factors": {}
        }
        self.decision_history.append(decision_point)
        return decision_point

    async def _enhance_global_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with global patterns and insights."""
        enhanced = context.copy() if context else {}
        
        # Add historical patterns
        enhanced["global_patterns"] = self._analyze_global_patterns()
        
        # Add cross-domain insights
        enhanced["cross_domain_insights"] = self._generate_cross_domain_insights()
        
        # Add temporal context
        enhanced["temporal_context"] = self._analyze_temporal_context()
        
        return enhanced

    def _analyze_global_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across all agent interactions."""
        if not self.context_history:
            return {}
            
        patterns = {
            "common_topics": self._identify_common_topics(),
            "interaction_trends": self._analyze_interaction_trends(),
            "success_patterns": self._analyze_success_patterns()
        }
        return patterns

    def _generate_cross_domain_insights(self) -> Dict[str, Any]:
        """Generate insights by analyzing relationships between different domains."""
        insights = {}
        for domain, agents in self.domain_expertise_map.items():
            domain_data = self._collect_domain_data(domain)
            insights[domain] = self._analyze_domain_relationships(domain_data)
        return insights

    def _collect_domain_data(self, domain: str) -> Dict[str, Any]:
        """Collect data and insights for a specific domain."""
        domain_data = {
            "insights": [],
            "patterns": [],
            "recommendations": []
        }
        
        # Collect data from agents with expertise in this domain
        for agent_id, agent in self.agents.items():
            if domain in agent.expertise_domains:
                # Get relevant domain context from agent's knowledge base
                domain_data["insights"].extend(
                    agent.knowledge_base.get(domain, [])
                )
                
                # Get relevant patterns from agent's learning history
                domain_data["patterns"].extend([
                    pattern for pattern in agent.learning_history
                    if domain in pattern.get("domains", [])
                ])
        
        return domain_data

    def _identify_relevant_agents(self, context: Dict[str, Any]) -> Set[str]:
        """Identify agents that should be consulted based on context."""
        relevant_agents = set()
        
        # Check domain relevance
        relevant_domains = self._identify_relevant_domains(context)
        for domain in relevant_domains:
            if domain in self.domain_expertise_map:
                relevant_agents.update(self.domain_expertise_map[domain])
        
        # Check pattern-based relevance
        pattern_relevant = self._identify_pattern_based_relevance(context)
        relevant_agents.update(pattern_relevant)
        
        return relevant_agents

    async def _gather_agent_responses(self,
                                    user_input: str,
                                    primary_agent_id: str,
                                    relevant_agents: Set[str],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather responses from relevant agents."""
        responses = {}
        for agent_id in relevant_agents:
            if agent_id != primary_agent_id:
                agent = self.agents.get(agent_id)
                if agent:
                    response = await agent.process_input(user_input, context)
                    responses[agent_id] = {
                        "response": response,
                        "confidence": agent._calculate_confidence(response)
                    }
        return responses

    def _integrate_responses(self,
                           primary_response: str,
                           related_responses: Dict[str, Dict[str, Any]],
                           context: Dict[str, Any]) -> str:
        """Integrate responses from multiple agents into a coherent response."""
        # Start with primary response
        integrated = primary_response
        
        # Sort related responses by confidence
        sorted_responses = sorted(
            related_responses.items(),
            key=lambda x: x[1]["confidence"],
            reverse=True
        )
        
        # Integrate high-confidence insights
        for agent_id, response_data in sorted_responses:
            if response_data["confidence"] >= self.agents[agent_id].confidence_threshold:
                insight = self._extract_key_insight(response_data["response"])
                integrated = self._merge_insight(integrated, insight)
        
        return integrated

    def _extract_key_insight(self, response: str) -> str:
        """Extract key insight from a response."""
        # Implement insight extraction logic
        return response

    def _merge_insight(self, base_response: str, insight: str) -> str:
        """Merge an insight into the base response."""
        # Implement insight merging logic
        if insight:
            return f"{base_response}\n\nAdditional insight: {insight}"
        return base_response

    async def generate_holistic_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate coordinated recommendations from relevant agents."""
        try:
            # Enhance user data with global context
            enhanced_data = await self._enhance_global_context(user_data)
            
            # Collect recommendations from all relevant agents
            recommendations = await self._collect_agent_recommendations(enhanced_data)
            
            # Analyze for conflicts and synergies
            analyzed_recommendations = self._analyze_recommendation_relationships(recommendations)
            
            # Prioritize and integrate recommendations
            integrated_recommendations = self._integrate_recommendations(analyzed_recommendations)
            
            return {
                "status": "success",
                "recommendations": integrated_recommendations,
                "context": enhanced_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _collect_agent_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Collect recommendations from all relevant agents."""
        recommendations = {}
        relevant_agents = self._identify_relevant_agents(user_data)
        
        for agent_id in relevant_agents:
            agent = self.agents.get(agent_id)
            if agent:
                agent_recs = await agent.generate_recommendations(user_data)
                recommendations[agent_id] = agent_recs
                
        return recommendations

    def _analyze_recommendation_relationships(self, 
                                           recommendations: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze relationships between recommendations."""
        analysis = {
            "conflicts": self._identify_conflicts(recommendations),
            "synergies": self._identify_synergies(recommendations),
            "dependencies": self._identify_dependencies(recommendations)
        }
        return analysis

    def _integrate_recommendations(self, analyzed_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Integrate recommendations considering relationships."""
        integrated = []
        
        # Sort recommendations by priority and relationships
        sorted_recs = self._sort_recommendations(analyzed_recommendations)
        
        # Build integrated recommendation set
        for rec in sorted_recs:
            if not self._conflicts_with_existing(rec, integrated):
                integrated.append(rec)
        
        return integrated

    def _sort_recommendations(self, analyzed_recommendations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sort recommendations by priority and relationships."""
        # Extract all recommendations
        all_recs = []
        for agent_recs in analyzed_recommendations.values():
            if isinstance(agent_recs, list):
                all_recs.extend(agent_recs)
        
        # Sort by priority and relationship scores
        return sorted(all_recs, key=lambda x: (
            x.get("priority", 0),
            len(x.get("synergies", [])),
            -len(x.get("conflicts", []))
        ), reverse=True)

    def _conflicts_with_existing(self, 
                               new_rec: Dict[str, Any], 
                               existing_recs: List[Dict[str, Any]]) -> bool:
        """Check if a new recommendation conflicts with existing ones."""
        if not existing_recs:
            return False
            
        # Check for direct conflicts
        for existing in existing_recs:
            if self._has_direct_conflict(new_rec, existing):
                return True
                
        # Check for indirect conflicts
        return self._has_indirect_conflict(new_rec, existing_recs)

    def _has_direct_conflict(self, rec1: Dict[str, Any], rec2: Dict[str, Any]) -> bool:
        """Check for direct conflicts between recommendations."""
        # Implement conflict detection logic
        # Example: Check for mutually exclusive actions or contradictory advice
        return False  # Placeholder implementation

    def _has_indirect_conflict(self, rec: Dict[str, Any], existing: List[Dict[str, Any]]) -> bool:
        """Check for indirect conflicts through dependencies."""
        # Implement indirect conflict detection
        # Example: Check for resource conflicts or timing conflicts
        return False  # Placeholder implementation

    def _identify_common_topics(self) -> List[str]:
        """Identify common topics from context history."""
        if not self.context_history:
            return []
            
        topic_frequency = {}
        for context in self.context_history:
            topics = context.get("topics", [])
            for topic in topics:
                topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
                
        return sorted(
            topic_frequency.keys(),
            key=lambda x: topic_frequency[x],
            reverse=True
        )[:5]  # Return top 5 topics

    def _analyze_interaction_trends(self) -> Dict[str, Any]:
        """Analyze trends in user interactions."""
        if not self.context_history:
            return {}
            
        return {
            "frequency": self._calculate_interaction_frequency(),
            "successful_patterns": self._identify_successful_patterns(),
            "common_contexts": self._identify_common_contexts()
        }

    def _analyze_success_patterns(self) -> List[Dict[str, Any]]:
        """Analyze patterns in successful interactions."""
        success_patterns = []
        
        for decision in self.decision_history:
            if self._was_successful_interaction(decision):
                pattern = {
                    "context": decision.get("initial_context", {}),
                    "agents_involved": decision.get("agents_involved", []),
                    "outcome": "success",
                    "confidence": decision.get("confidence", 0)
                }
                success_patterns.append(pattern)
                
        return success_patterns

    def _analyze_domain_relationships(self, domain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships and patterns within domain data."""
        return {
            "frequent_patterns": self._extract_frequent_patterns(domain_data["patterns"]),
            "key_insights": self._summarize_insights(domain_data["insights"]),
            "recommendation_themes": self._identify_recommendation_themes(domain_data["recommendations"])
        }

    def _identify_relevant_domains(self, context: Dict[str, Any]) -> Set[str]:
        """Identify relevant domains based on context."""
        relevant_domains = set()
        
        # Check explicit domain mentions
        if "industry" in context:
            relevant_domains.add(context["industry"])
            
        # Check for domain-specific keywords
        for domain in self.domain_expertise_map.keys():
            if self._context_matches_domain(context, domain):
                relevant_domains.add(domain)
                
        return relevant_domains

    def _context_matches_domain(self, context: Dict[str, Any], domain: str) -> bool:
        """Check if context matches a specific domain."""
        # Implement domain matching logic
        # This is a simple implementation that should be enhanced based on specific needs
        domain_keywords = {
            "career": ["job", "career", "skills", "professional"],
            "finance": ["money", "salary", "compensation", "financial"],
            "health": ["health", "wellness", "stress", "balance"]
        }
        
        if domain not in domain_keywords:
            return False
            
        return any(
            keyword in str(context).lower()
            for keyword in domain_keywords[domain]
        )

    def _identify_pattern_based_relevance(self, context: Dict[str, Any]) -> Set[str]:
        """Identify relevant agents based on interaction patterns."""
        relevant_agents = set()
        
        # Look for similar patterns in history
        for pattern in self.interaction_patterns:
            if self._context_matches_pattern(context, pattern):
                relevant_agents.update(pattern.get("successful_agents", []))
                
        return relevant_agents

    def _context_matches_pattern(self, context: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        """Check if current context matches a historical pattern."""
        pattern_context = pattern.get("context", {})
        
        # Check for key matching elements
        return any(
            context.get(key) == pattern_context.get(key)
            for key in pattern_context
            if key in context
        )

    def _analyze_temporal_context(self) -> Dict[str, Any]:
        """Analyze temporal aspects of the context."""
        if not self.context_history:
            return {}
            
        return {
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "recent_interactions": len([
                ctx for ctx in self.context_history
                if (datetime.now() - datetime.fromisoformat(ctx["timestamp"])).days < 7
            ])
        }

    def _update_context_history(self, context: Dict[str, Any], response: str) -> None:
        """Update the context history with new interaction."""
        context_record = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "response": response,
            "topics": self._extract_topics(context, response)
        }
        self.context_history.append(context_record)

    def _extract_topics(self, context: Dict[str, Any], response: str) -> List[str]:
        """Extract topics from context and response."""
        # Implement topic extraction logic
        # This is a simple implementation that should be enhanced with NLP
        topics = set()
        
        # Add explicit topics from context
        if "industry" in context:
            topics.add(context["industry"])
            
        # Add topics from career goals
        if "career_goals" in context:
            goals = context["career_goals"]
            if isinstance(goals, dict):
                topics.update(goals.keys())
                
        return list(topics)

    def _record_decision_outcome(self, decision_point: Dict[str, Any], response: str) -> None:
        """Record the outcome of a decision point."""
        decision_point.update({
            "response": response,
            "outcome_timestamp": datetime.now().isoformat(),
            "success_metrics": self._calculate_success_metrics(response)
        })

    def _calculate_success_metrics(self, response: str) -> Dict[str, float]:
        """Calculate success metrics for a response."""
        # Implement success metrics calculation
        # This is a simple implementation that should be enhanced
        return {
            "confidence": 0.8 if response else 0.0,
            "relevance": 0.7,
            "actionability": 0.6
        }

    def _identify_conflicts(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify conflicts between recommendations."""
        conflicts = []
        all_recs = []
        
        # Flatten recommendations
        for agent_recs in recommendations.values():
            all_recs.extend(agent_recs)
            
        # Check for conflicts
        for i, rec1 in enumerate(all_recs):
            for rec2 in all_recs[i+1:]:
                if self._recommendations_conflict(rec1, rec2):
                    conflicts.append({
                        "rec1": rec1,
                        "rec2": rec2,
                        "type": "mutually_exclusive"
                    })
                    
        return conflicts

    def _recommendations_conflict(self, rec1: Dict[str, Any], rec2: Dict[str, Any]) -> bool:
        """Check if two recommendations conflict."""
        # Implement conflict detection logic
        # This is a simple implementation that should be enhanced
        if rec1.get("type") == rec2.get("type"):
            if rec1.get("priority", 0) > 0 and rec2.get("priority", 0) > 0:
                return True
        return False

    def _identify_synergies(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify synergies between recommendations."""
        synergies = []
        all_recs = []
        
        # Flatten recommendations
        for agent_recs in recommendations.values():
            all_recs.extend(agent_recs)
            
        # Check for synergies
        for i, rec1 in enumerate(all_recs):
            for rec2 in all_recs[i+1:]:
                if self._recommendations_synergize(rec1, rec2):
                    synergies.append({
                        "rec1": rec1,
                        "rec2": rec2,
                        "type": "complementary"
                    })
                    
        return synergies

    def _recommendations_synergize(self, rec1: Dict[str, Any], rec2: Dict[str, Any]) -> bool:
        """Check if two recommendations have synergy."""
        # Implement synergy detection logic
        # This is a simple implementation that should be enhanced
        if rec1.get("type") != rec2.get("type"):
            if set(rec1.get("skills", [])) & set(rec2.get("skills", [])):
                return True
        return False

    def _identify_dependencies(self, recommendations: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Identify dependencies between recommendations."""
        dependencies = []
        all_recs = []
        
        # Flatten recommendations
        for agent_recs in recommendations.values():
            all_recs.extend(agent_recs)
            
        # Check for dependencies
        for i, rec1 in enumerate(all_recs):
            for rec2 in all_recs[i+1:]:
                if self._recommendations_depend(rec1, rec2):
                    dependencies.append({
                        "dependent": rec1,
                        "prerequisite": rec2,
                        "type": "prerequisite"
                    })
                    
        return dependencies

    def _recommendations_depend(self, rec1: Dict[str, Any], rec2: Dict[str, Any]) -> bool:
        """Check if one recommendation depends on another."""
        # Implement dependency detection logic
        # This is a simple implementation that should be enhanced
        if rec1.get("required_skills", []):
            if any(skill in rec2.get("provided_skills", []) 
                  for skill in rec1["required_skills"]):
                return True
        return False

    def _calculate_interaction_frequency(self) -> Dict[str, float]:
        """Calculate frequency metrics for interactions."""
        if not self.context_history:
            return {"daily": 0, "weekly": 0, "monthly": 0}
            
        now = datetime.now()
        timestamps = [datetime.fromisoformat(ctx["timestamp"]) 
                     for ctx in self.context_history]
        
        daily = len([ts for ts in timestamps 
                    if (now - ts).days < 1])
        weekly = len([ts for ts in timestamps 
                     if (now - ts).days < 7])
        monthly = len([ts for ts in timestamps 
                      if (now - ts).days < 30])
                      
        return {
            "daily": daily,
            "weekly": weekly / 7 if weekly > 0 else 0,
            "monthly": monthly / 30 if monthly > 0 else 0
        }

    def _identify_successful_patterns(self) -> List[Dict[str, Any]]:
        """Identify patterns in successful interactions."""
        patterns = []
        
        for decision in self.decision_history:
            if self._was_successful_interaction(decision):
                pattern = {
                    "context": decision.get("initial_context", {}),
                    "response_type": decision.get("response_type"),
                    "success_metrics": decision.get("success_metrics", {})
                }
                patterns.append(pattern)
                
        return patterns

    def _identify_common_contexts(self) -> List[Dict[str, Any]]:
        """Identify commonly occurring interaction contexts."""
        context_patterns = {}
        
        for entry in self.context_history:
            context_key = self._generate_context_key(entry.get("context", {}))
            if context_key not in context_patterns:
                context_patterns[context_key] = {
                    "count": 0,
                    "context": entry.get("context", {}),
                    "success_rate": 0,
                    "responses": []
                }
            
            pattern = context_patterns[context_key]
            pattern["count"] += 1
            pattern["responses"].append(entry.get("response"))
            
        return sorted(
            context_patterns.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:5]

    def _generate_context_key(self, context: Dict[str, Any]) -> str:
        """Generate a key for context pattern matching."""
        # Implement context key generation
        # This is a simple implementation that should be enhanced
        key_elements = []
        
        if "industry" in context:
            key_elements.append(f"industry:{context['industry']}")
            
        if "career_goals" in context:
            goals = context["career_goals"]
            if isinstance(goals, dict):
                for k, v in sorted(goals.items()):
                    key_elements.append(f"goal:{k}:{v}")
                    
        return "|".join(key_elements)

    def _was_successful_interaction(self, decision: Dict[str, Any]) -> bool:
        """Determine if an interaction was successful."""
        metrics = decision.get("success_metrics", {})
        
        # Check confidence threshold
        if metrics.get("confidence", 0) < 0.7:
            return False
            
        # Check relevance threshold
        if metrics.get("relevance", 0) < 0.6:
            return False
            
        # Check actionability threshold
        if metrics.get("actionability", 0) < 0.5:
            return False
            
        return True

    def _extract_frequent_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract frequently occurring patterns in the data."""
        pattern_frequency = {}
        
        for pattern in patterns:
            pattern_key = self._generate_pattern_key(pattern)
            if pattern_key not in pattern_frequency:
                pattern_frequency[pattern_key] = {
                    "count": 0,
                    "pattern": pattern
                }
            pattern_frequency[pattern_key]["count"] += 1
            
        return sorted(
            pattern_frequency.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:5]

    def _generate_pattern_key(self, pattern: Dict[str, Any]) -> str:
        """Generate a key for pattern matching."""
        # Implement pattern key generation
        # This is a simple implementation that should be enhanced
        key_elements = []
        
        if "type" in pattern:
            key_elements.append(f"type:{pattern['type']}")
            
        if "domains" in pattern:
            domains = sorted(pattern["domains"])
            key_elements.append(f"domains:{','.join(domains)}")
            
        return "|".join(key_elements)

    def _summarize_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize key insights from the data."""
        # Group insights by topic
        topic_insights = {}
        
        for insight in insights:
            topic = insight.get("topic", "general")
            if topic not in topic_insights:
                topic_insights[topic] = []
            topic_insights[topic].append(insight)
            
        # Summarize each topic
        summaries = []
        for topic, topic_data in topic_insights.items():
            summary = {
                "topic": topic,
                "key_points": self._extract_key_points(topic_data),
                "frequency": len(topic_data),
                "confidence": self._calculate_insight_confidence(topic_data)
            }
            summaries.append(summary)
            
        return sorted(summaries, key=lambda x: x["frequency"], reverse=True)

    def _extract_key_points(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from a collection of insights."""
        points = set()
        for insight in insights:
            if "key_points" in insight:
                points.update(insight["key_points"])
        return list(points)

    def _calculate_insight_confidence(self, insights: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for insights."""
        if not insights:
            return 0.0
            
        confidence_sum = sum(
            insight.get("confidence", 0)
            for insight in insights
        )
        return confidence_sum / len(insights)

    def _identify_recommendation_themes(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify common themes in recommendations."""
        theme_data = {}
        
        for rec in recommendations:
            theme = rec.get("theme", "general")
            if theme not in theme_data:
                theme_data[theme] = {
                    "count": 0,
                    "total_priority": 0,
                    "recommendations": []
                }
                
            theme_info = theme_data[theme]
            theme_info["count"] += 1
            theme_info["total_priority"] += rec.get("priority", 0)
            theme_info["recommendations"].append(rec)
            
        # Calculate theme scores
        themes = []
        for theme, data in theme_data.items():
            theme_score = {
                "theme": theme,
                "frequency": data["count"],
                "average_priority": data["total_priority"] / data["count"],
                "example_recommendations": sorted(
                    data["recommendations"],
                    key=lambda x: x.get("priority", 0),
                    reverse=True
                )[:3]
            }
            themes.append(theme_score)
            
        return sorted(themes, key=lambda x: x["frequency"], reverse=True)