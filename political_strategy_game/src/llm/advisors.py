"""
AI-Enhanced Advisor System

This module implements AI-powered advisor personalities that provide contextual
advice and commentary during the political strategy game. Each advisor has a
unique personality and area of expertise.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import logging
from datetime import datetime

from .llm_providers import LLMManager, LLMMessage, LLMConfig, LLMProvider

# Simple event and game state classes for testing and development
class Event:
    """Simple event class for advisor memory."""
    def __init__(self, event_type: str, description: str, turn: int = 1):
        self.event_type = event_type
        self.description = description
        self.turn = turn

class EventType:
    """Event type constants."""
    DECISION = "decision"
    BATTLE = "battle"
    DIPLOMACY = "diplomacy"
    ECONOMIC = "economic"

class GameState:
    """Simple game state class for advisor context."""
    def __init__(self, political_power: int = 100, stability: int = 75, 
                 legitimacy: int = 70, current_faction = None):
        self.political_power = political_power
        self.stability = stability
        self.legitimacy = legitimacy
        self.current_faction = current_faction


class AdvisorRole(Enum):
    """Different advisor roles with distinct specializations."""
    MILITARY = "military"
    ECONOMIC = "economic"
    DIPLOMATIC = "diplomatic"
    DOMESTIC = "domestic"
    INTELLIGENCE = "intelligence"


@dataclass
class AdvisorPersonality:
    """Defines an advisor's personality and communication style."""
    name: str
    role: AdvisorRole
    personality_traits: List[str]
    communication_style: str
    expertise_areas: List[str]
    background: str
    catchphrases: List[str] = field(default_factory=list)
    
    @classmethod
    def get_personality(cls, role: AdvisorRole) -> 'AdvisorPersonality':
        """Get the default personality for a given advisor role."""
        personalities = {
            AdvisorRole.MILITARY: AdvisorPersonality(
                name="General Marcus Steel",
                role=AdvisorRole.MILITARY,
                personality_traits=["Direct", "Pragmatic", "Experienced", "Cautious"],
                communication_style="Crisp, military precision with strategic focus",
                expertise_areas=["Military strategy", "Defense planning", "Conflict assessment"],
                background="Veteran general with 30 years of service, known for defensive expertise",
                catchphrases=["Victory through preparation", "A strong defense enables offense"]
            ),
            AdvisorRole.ECONOMIC: AdvisorPersonality(
                name="Dr. Elena Vasquez",
                role=AdvisorRole.ECONOMIC,
                personality_traits=["Analytical", "Forward-thinking", "Data-driven", "Optimistic"],
                communication_style="Precise language with economic terminology and market insights",
                expertise_areas=["Economic policy", "Resource management", "Trade relations"],
                background="Former economics professor turned policy advisor, specializes in sustainable growth",
                catchphrases=["The numbers don't lie", "Investment today, prosperity tomorrow"]
            ),
            AdvisorRole.DIPLOMATIC: AdvisorPersonality(
                name="Ambassador Chen Wei",
                role=AdvisorRole.DIPLOMATIC,
                personality_traits=["Diplomatic", "Patient", "Culturally aware", "Persuasive"],
                communication_style="Polished and nuanced, emphasizing cooperation and mutual benefit",
                expertise_areas=["International relations", "Negotiation", "Cultural diplomacy"],
                background="Career diplomat with expertise in multi-party negotiations and conflict resolution",
                catchphrases=["Diplomacy is the art of letting others have your way", "Trust, but verify"]
            ),
            AdvisorRole.DOMESTIC: AdvisorPersonality(
                name="Minister Sarah Thompson",
                role=AdvisorRole.DOMESTIC,
                personality_traits=["Empathetic", "Practical", "Community-focused", "Balanced"],
                communication_style="Warm but professional, emphasizing public welfare and social harmony",
                expertise_areas=["Public policy", "Social programs", "Civil rights"],
                background="Former mayor with grassroots experience, known for building consensus",
                catchphrases=["Government serves the people", "Strong communities build strong nations"]
            ),
            AdvisorRole.INTELLIGENCE: AdvisorPersonality(
                name="Director Alex Morgan",
                role=AdvisorRole.INTELLIGENCE,
                personality_traits=["Cautious", "Observant", "Methodical", "Discrete"],
                communication_style="Careful and measured, with emphasis on information and security",
                expertise_areas=["Intelligence analysis", "Risk assessment", "Information security"],
                background="Intelligence veteran specializing in strategic analysis and threat assessment",
                catchphrases=["Knowledge is power", "Prepare for what you cannot predict"]
            )
        }
        
        if role not in personalities:
            raise ValueError(f"No default personality available for role: {role}")
        
        return personalities[role]


@dataclass
class ConversationMemory:
    """Stores conversation history and context for an advisor."""
    messages: List[LLMMessage] = field(default_factory=list)
    key_decisions: List[str] = field(default_factory=list)
    player_preferences: Dict[str, Any] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append(LLMMessage(role=role, content=content))
        self.last_updated = datetime.now()
        
        # Keep only last 20 messages to manage context window
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]
    
    def add_decision(self, decision: str):
        """Record a key decision made by the player."""
        self.key_decisions.append(decision)
        self.last_updated = datetime.now()
        
        # Keep only last 10 decisions
        if len(self.key_decisions) > 10:
            self.key_decisions = self.key_decisions[-10:]


class AdvisorAI:
    """AI-powered advisor with personality and memory."""
    
    def __init__(self, personality: AdvisorPersonality, llm_manager: LLMManager):
        self.personality = personality
        self.llm_manager = llm_manager
        self.memory = ConversationMemory()
        self.logger = logging.getLogger(f"advisor.{personality.name.lower()}")
        
        # Initialize system prompt
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt that defines the advisor's personality."""
        traits_str = ", ".join(self.personality.personality_traits)
        expertise_str = ", ".join(self.personality.expertise_areas)
        
        prompt = f"""You are {self.personality.name}, a {self.personality.role.value} advisor in a political strategy game.

PERSONALITY TRAITS: {traits_str}
COMMUNICATION STYLE: {self.personality.communication_style}
EXPERTISE AREAS: {expertise_str}
BACKGROUND: {self.personality.background}

YOUR ROLE:
- Provide strategic advice in your area of expertise
- Maintain your unique personality and communication style
- Reference past decisions and conversations when relevant
- Keep responses concise but insightful (2-3 sentences max)
- Stay in character at all times

IMPORTANT GUIDELINES:
- Focus on your specialized domain ({self.personality.role.value})
- Be helpful but maintain your distinct personality
- Reference game context and previous conversations naturally
- Provide actionable advice when possible
- Use your background knowledge to inform recommendations"""

        if self.personality.catchphrases:
            prompt += f"\nOCCASIONAL CATCHPHRASES: {', '.join(self.personality.catchphrases)}"
        
        return prompt
    
    async def get_advice(self, 
                        game_state: GameState, 
                        situation: str, 
                        recent_events: Optional[List[Event]] = None) -> str:
        """Generate contextual advice based on the current situation."""
        
        # Build context message
        context = self._build_context(game_state, situation, recent_events)
        
        # Prepare messages for LLM
        messages = [LLMMessage(role="system", content=self.system_prompt)]
        
        # Add recent conversation history
        if self.memory.messages:
            # Add last few messages for context
            messages.extend(self.memory.messages[-6:])
        
        # Add current situation
        messages.append(LLMMessage(role="user", content=context))
        
        # Generate response
        try:
            response = await self.llm_manager.generate(messages, max_tokens=200, temperature=0.8)
            
            if response.error:
                self.logger.error(f"LLM generation failed: {response.error}")
                return self._get_fallback_response(situation)
            
            advice = response.content.strip()
            
            # Store in memory
            self.memory.add_message("user", context)
            self.memory.add_message("assistant", advice)
            
            return advice
            
        except Exception as e:
            self.logger.error(f"Error generating advice: {e}")
            return self._get_fallback_response(situation)
    
    def _build_context(self, 
                      game_state: GameState, 
                      situation: str,
                      recent_events: Optional[List[Event]] = None) -> str:
        """Build context message with game state and situation."""
        
        context_parts = []
        
        # Current game state summary
        context_parts.append(f"CURRENT SITUATION: {situation}")
        
        # Key game state metrics
        context_parts.append(f"Political Power: {game_state.political_power}")
        context_parts.append(f"Stability: {game_state.stability}")
        context_parts.append(f"Current Faction: {game_state.current_faction.name if game_state.current_faction else 'None'}")
        
        # Recent events relevant to this advisor's domain
        if recent_events:
            relevant_events = self._filter_relevant_events(recent_events)
            if relevant_events:
                event_summaries = [f"- {event.title}" for event in relevant_events[-3:]]
                context_parts.append(f"RECENT RELEVANT EVENTS:\n" + "\n".join(event_summaries))
        
        # Key decisions from memory
        if self.memory.key_decisions:
            recent_decisions = self.memory.key_decisions[-3:]
            context_parts.append(f"RECENT DECISIONS:\n" + "\n".join(f"- {d}" for d in recent_decisions))
        
        return "\n\n".join(context_parts)
    
    def _filter_relevant_events(self, events: List[Event]) -> List[Event]:
        """Filter events relevant to this advisor's expertise."""
        role_keywords = {
            AdvisorRole.MILITARY: ["military", "army", "defense", "war", "battle", "conflict"],
            AdvisorRole.ECONOMIC: ["economic", "economy", "trade", "budget", "finance", "resource"],
            AdvisorRole.DIPLOMATIC: ["diplomatic", "foreign", "alliance", "treaty", "international"],
            AdvisorRole.DOMESTIC: ["domestic", "civil", "public", "social", "protest", "unrest"],
            AdvisorRole.INTELLIGENCE: ["intelligence", "spy", "information", "secret", "surveillance"]
        }
        
        keywords = role_keywords.get(self.personality.role, [])
        relevant_events = []
        
        for event in events:
            event_text = (event.title + " " + event.description).lower()
            if any(keyword in event_text for keyword in keywords):
                relevant_events.append(event)
        
        return relevant_events
    
    def _get_fallback_response(self, situation: str) -> str:
        """Provide a fallback response when LLM is unavailable."""
        fallback_responses = {
            AdvisorRole.MILITARY: [
                "Our forces need careful consideration before any major action.",
                "Military strength requires both preparation and strategic timing.",
                "Defense should always be our priority in uncertain times."
            ],
            AdvisorRole.ECONOMIC: [
                "We must carefully manage our resources and economic stability.",
                "Economic decisions today will impact our long-term prosperity.",
                "Consider the financial implications of any major policy changes."
            ],
            AdvisorRole.DIPLOMATIC: [
                "Diplomatic relations require patience and careful negotiation.",
                "We should consider how this affects our international standing.",
                "Building alliances takes time, but breaking them happens quickly."
            ],
            AdvisorRole.DOMESTIC: [
                "The people's concerns should guide our domestic policies.",
                "Internal stability is crucial for any successful government.",
                "We must balance different domestic interests carefully."
            ],
            AdvisorRole.INTELLIGENCE: [
                "We need more information before making critical decisions.",
                "Intelligence gathering is essential for strategic planning.",
                "Knowledge is power, but acting on incomplete intelligence is dangerous."
            ]
        }
        
        responses = fallback_responses.get(self.personality.role, ["Let me consider this situation carefully."])
        return f"{self.personality.name}: {responses[0]}"
    
    def record_decision(self, decision: str):
        """Record a player decision for future reference."""
        self.memory.add_decision(decision)
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the advisor's memory."""
        return {
            "conversation_length": len(self.memory.messages),
            "key_decisions": len(self.memory.key_decisions),
            "last_updated": self.memory.last_updated.isoformat() if self.memory.last_updated else None,
            "recent_decisions": self.memory.key_decisions[-3:] if self.memory.key_decisions else []
        }


class AdvisorCouncil:
    """Manages the collection of AI advisors."""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.advisors: Dict[AdvisorRole, AdvisorAI] = {}
        self.logger = logging.getLogger("advisor.council")
        
        # Initialize default advisors
        self._initialize_default_advisors()
    
    def _initialize_default_advisors(self):
        """Create the default set of advisors."""
        
        # Use the class method to get default personalities
        for role in AdvisorRole:
            personality = AdvisorPersonality.get_personality(role)
            advisor = AdvisorAI(personality, self.llm_manager)
            self.advisors[role] = advisor
            self.logger.info(f"Initialized advisor: {personality.name} ({personality.role.value})")
    
    async def get_council_advice(self, 
                                game_state: GameState, 
                                situation: str,
                                specific_roles: Optional[List[AdvisorRole]] = None,
                                recent_events: Optional[List[Event]] = None) -> Dict[AdvisorRole, str]:
        """Get advice from multiple advisors."""
        
        roles_to_consult = specific_roles or list(self.advisors.keys())
        advice_dict = {}
        
        # Generate advice from each requested advisor
        tasks = []
        for role in roles_to_consult:
            if role in self.advisors:
                task = self.advisors[role].get_advice(game_state, situation, recent_events)
                tasks.append((role, task))
        
        # Execute all advisor consultations concurrently
        for role, task in tasks:
            try:
                advice = await task
                advice_dict[role] = advice
            except Exception as e:
                self.logger.error(f"Failed to get advice from {role.value} advisor: {e}")
                advice_dict[role] = f"The {role.value} advisor is currently unavailable."
        
        return advice_dict
    
    async def get_single_advice(self, 
                               role: AdvisorRole, 
                               game_state: GameState, 
                               situation: str,
                               recent_events: Optional[List[Event]] = None) -> str:
        """Get advice from a specific advisor."""
        
        if role not in self.advisors:
            return f"No advisor available for {role.value} role."
        
        return await self.advisors[role].get_advice(game_state, situation, recent_events)
    
    def record_decision_for_all(self, decision: str):
        """Record a decision across all advisors."""
        for advisor in self.advisors.values():
            advisor.record_decision(decision)
    
    def get_advisor_status(self) -> Dict[str, Any]:
        """Get status information for all advisors."""
        status = {
            "llm_status": self.llm_manager.get_status(),
            "advisors": {}
        }
        
        for role, advisor in self.advisors.items():
            status["advisors"][role.value] = {
                "name": advisor.personality.name,
                "memory": advisor.get_memory_summary()
            }
        
        return status
    
    def get_advisor_names(self) -> Dict[AdvisorRole, str]:
        """Get mapping of advisor roles to names."""
        return {role: advisor.personality.name for role, advisor in self.advisors.items()}
