"""
Emergent Storytelling System

This module implements AI-driven dynamic narrative generation that creates
emergent stories from political events, advisor interactions, and player
decisions to enhance immersion and narrative depth.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import logging
import random
from collections import defaultdict

from .dialogue import MultiAdvisorDialogue, EmotionalState
from .faction_dynamics import FactionDynamicsManager, PoliticalFaction
from .information_warfare import InformationWarfareManager, PropagandaCampaign
from .advisors import AdvisorRole, AdvisorCouncil, AdvisorAI, AdvisorPersonality
from .llm_providers import LLMManager, LLMMessage, LLMResponse


class NarrativeType(Enum):
    """Types of narrative elements that can be generated."""
    HISTORICAL_CHRONICLE = "historical_chronicle"
    CHARACTER_DEVELOPMENT = "character_development"
    POLITICAL_INTRIGUE = "political_intrigue"
    CULTURAL_EVOLUTION = "cultural_evolution"
    DRAMATIC_TENSION = "dramatic_tension"
    HEROIC_SAGA = "heroic_saga"
    TRAGIC_DOWNFALL = "tragic_downfall"
    REDEMPTION_ARC = "redemption_arc"


class NarrativeTone(Enum):
    """Tone and style of narrative generation."""
    EPIC_FORMAL = "epic_formal"
    INTIMATE_PERSONAL = "intimate_personal"
    DRAMATIC_TENSE = "dramatic_tense"
    COMEDIC_IRONIC = "comedic_ironic"
    MELANCHOLIC_REFLECTIVE = "melancholic_reflective"
    TRIUMPHANT_CELEBRATORY = "triumphant_celebratory"
    OMINOUS_FOREBODING = "ominous_foreboding"
    SCHOLARLY_ANALYTICAL = "scholarly_analytical"


class StoryElement(Enum):
    """Individual story elements that can be tracked."""
    CONFLICT_INTRODUCTION = "conflict_introduction"
    CHARACTER_MOTIVATION = "character_motivation"
    PLOT_TWIST = "plot_twist"
    RESOLUTION_MOMENT = "resolution_moment"
    RELATIONSHIP_CHANGE = "relationship_change"
    POWER_SHIFT = "power_shift"
    MORAL_DILEMMA = "moral_dilemma"
    SYMBOLIC_EVENT = "symbolic_event"


@dataclass
class NarrativeThread:
    """Represents an ongoing narrative thread with characters and themes."""
    thread_id: str
    title: str
    narrative_type: NarrativeType
    central_characters: List[str] = field(default_factory=list)
    key_themes: List[str] = field(default_factory=list)
    plot_points: List[str] = field(default_factory=list)
    emotional_arc: List[EmotionalState] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    tension_level: float = 0.5  # 0.0-1.0
    completion_status: float = 0.0  # 0.0-1.0, how complete the story feels
    predicted_resolution: Optional[str] = None
    
    def add_plot_point(self, plot_point: str, emotional_state: EmotionalState):
        """Add a new plot point to the narrative thread."""
        self.plot_points.append(plot_point)
        self.emotional_arc.append(emotional_state)
        self.last_updated = datetime.now()
        
        # Update tension level based on emotional state
        emotion_intensities = {
            EmotionalState.ANGRY: 0.8,
            EmotionalState.WORRIED: 0.7,
            EmotionalState.EXCITED: 0.6,
            EmotionalState.SUSPICIOUS: 0.7,
            EmotionalState.FRUSTRATED: 0.5,
            EmotionalState.HOPEFUL: 0.4,
            EmotionalState.CONFIDENT: 0.3,
            EmotionalState.CALM: 0.2
        }
        
        self.tension_level = min(1.0, max(0.0, 
            self.tension_level * 0.8 + emotion_intensities.get(emotional_state, 0.5) * 0.3
        ))
    
    def calculate_story_momentum(self) -> float:
        """Calculate how active and engaging this narrative thread is."""
        # Recent activity bonus
        days_since_update = (datetime.now() - self.last_updated).days
        recency_factor = max(0.1, 1.0 - days_since_update * 0.1)
        
        # Length and complexity
        complexity_factor = min(1.0, len(self.plot_points) * 0.1)
        
        # Tension contributes to momentum
        momentum = (self.tension_level * 0.4 + complexity_factor * 0.3 + recency_factor * 0.3)
        
        return max(0.0, min(1.0, momentum))


@dataclass
class NarrativeEvent:
    """Represents a significant event that drives narrative generation."""
    event_id: str
    title: str
    description: str
    involved_characters: List[str] = field(default_factory=list)
    story_elements: List[StoryElement] = field(default_factory=list)
    emotional_impact: Dict[str, EmotionalState] = field(default_factory=dict)  # character -> emotion
    narrative_significance: float = 0.5  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.now)
    related_threads: List[str] = field(default_factory=list)
    
    def calculate_dramatic_weight(self) -> float:
        """Calculate the dramatic weight of this event for story purposes."""
        base_weight = self.narrative_significance
        
        # More characters = more dramatic
        character_factor = min(1.0, len(self.involved_characters) * 0.2)
        
        # High-intensity emotions add drama
        emotion_intensity = 0.0
        if self.emotional_impact:
            high_intensity_emotions = [
                EmotionalState.ANGRY, EmotionalState.EXCITED, 
                EmotionalState.WORRIED, EmotionalState.SUSPICIOUS
            ]
            emotion_intensity = sum(
                0.3 for emotion in self.emotional_impact.values() 
                if emotion in high_intensity_emotions
            ) / max(1, len(self.emotional_impact))
        
        # Story elements add complexity
        element_factor = min(1.0, len(self.story_elements) * 0.15)
        
        return min(1.0, base_weight + character_factor + emotion_intensity + element_factor)


@dataclass
class GeneratedNarrative:
    """Represents a piece of generated narrative content."""
    narrative_id: str
    content: str
    narrative_type: NarrativeType
    tone: NarrativeTone
    featured_characters: List[str] = field(default_factory=list)
    referenced_events: List[str] = field(default_factory=list)
    related_threads: List[str] = field(default_factory=list)
    generation_timestamp: datetime = field(default_factory=datetime.now)
    word_count: int = 0
    literary_devices: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate word count after initialization."""
        self.word_count = len(self.content.split())


class EmergentStorytellingManager:
    """Manages AI-driven dynamic narrative generation from game events."""
    
    def __init__(self, llm_manager: LLMManager, dialogue_system: MultiAdvisorDialogue,
                 faction_manager: Optional[FactionDynamicsManager] = None,
                 information_manager: Optional[InformationWarfareManager] = None):
        self.llm_manager = llm_manager
        self.dialogue_system = dialogue_system
        self.faction_manager = faction_manager
        self.information_manager = information_manager
        
        self.active_threads: Dict[str, NarrativeThread] = {}
        self.narrative_events: List[NarrativeEvent] = []
        self.generated_narratives: List[GeneratedNarrative] = []
        self.character_relationships: Dict[Tuple[str, str], float] = defaultdict(float)  # Relationship strength
        self.narrative_preferences: Dict[str, Any] = {
            "tone_preference": NarrativeTone.EPIC_FORMAL,
            "complexity_level": 0.7,
            "focus_on_characters": True,
            "include_political_intrigue": True,
            "historical_perspective": True
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def analyze_narrative_opportunities(self, game_state: Any) -> Dict[str, float]:
        """Analyze current game state for narrative generation opportunities."""
        opportunities = {
            "character_development": 0.0,
            "political_intrigue": 0.0,
            "dramatic_tension": 0.0,
            "cultural_evolution": 0.0,
            "historical_significance": 0.0,
            "relationship_dynamics": 0.0
        }
        
        # Analyze advisor emotional states for character development
        emotional_complexity = 0.0
        relationship_tensions = 0.0
        
        advisors = list(self.dialogue_system.advisor_council.advisors.keys())
        for advisor in advisors:
            emotional_state = self.dialogue_system.get_advisor_emotional_state(advisor)
            intensity = emotional_state.get("intensity", 0.5)
            emotion = emotional_state.get("emotion", "calm")
            
            # High emotional intensity suggests character development opportunities
            if intensity > 0.6:
                emotional_complexity += 0.15
            
            # Certain emotions suggest intrigue/tension
            if emotion in ["suspicious", "angry", "worried"]:
                relationship_tensions += 0.1
        
        opportunities["character_development"] = min(1.0, emotional_complexity)
        opportunities["relationship_dynamics"] = min(1.0, relationship_tensions)
        
        # Analyze political state for intrigue
        political_instability = (100 - getattr(game_state, 'stability', 75)) / 100
        opportunities["political_intrigue"] = political_instability
        
        # Faction dynamics create intrigue
        if self.faction_manager:
            faction_summary = self.faction_manager.get_all_factions_summary()
            faction_count = faction_summary.get("total_factions", 0)
            opportunities["political_intrigue"] += min(0.5, faction_count * 0.1)
        
        # Information warfare creates dramatic tension
        if self.information_manager:
            warfare_summary = self.information_manager.get_information_warfare_summary()
            active_campaigns = warfare_summary.get("active_campaigns", 0)
            opportunities["dramatic_tension"] = min(1.0, active_campaigns * 0.3)
        
        # Use LLM to analyze additional narrative opportunities
        additional_opportunities = await self._llm_analyze_narrative_opportunities(game_state, opportunities)
        opportunities.update(additional_opportunities)
        
        return opportunities
    
    async def _llm_analyze_narrative_opportunities(self, game_state: Any, 
                                                   base_opportunities: Dict[str, float]) -> Dict[str, float]:
        """Use LLM to analyze narrative opportunities."""
        prompt = f"""Analyze narrative storytelling opportunities in this political situation:

CURRENT POLITICAL STATE:
- Political Power: {getattr(game_state, 'political_power', 100)}
- Stability: {getattr(game_state, 'stability', 75)}
- Legitimacy: {getattr(game_state, 'legitimacy', 70)}

DETECTED OPPORTUNITIES:
{json.dumps(base_opportunities, indent=2)}

RECENT NARRATIVE EVENTS:
{[event.title for event in self.narrative_events[-5:]]}

ACTIVE NARRATIVE THREADS:
{[thread.title for thread in self.active_threads.values()]}

Analyze additional storytelling opportunities and return JSON with values 0.0-1.0:
{{
    "cultural_evolution": 0.0-1.0,
    "historical_significance": 0.0-1.0,
    "heroic_moments": 0.0-1.0,
    "tragic_elements": 0.0-1.0,
    "redemption_arcs": 0.0-1.0
}}

Consider: What stories are emerging? What character arcs are developing? What historical moments are being created?"""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a narrative analysis specialist and storytelling expert."),
                LLMMessage(role="user", content=prompt)
            ])
            
            opportunities_data = json.loads(response.content)
            
            # Validate and clamp values
            additional_opportunities = {}
            for key, value in opportunities_data.items():
                if isinstance(value, (int, float)):
                    additional_opportunities[key] = max(0.0, min(1.0, float(value)))
            
            return additional_opportunities
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to parse LLM narrative analysis: {e}")
            return {
                "cultural_evolution": random.uniform(0.1, 0.4),
                "historical_significance": random.uniform(0.2, 0.6),
                "heroic_moments": random.uniform(0.1, 0.5),
                "tragic_elements": random.uniform(0.0, 0.4),
                "redemption_arcs": random.uniform(0.1, 0.3)
            }
    
    async def create_narrative_event(self, title: str, description: str, 
                                   involved_characters: List[str],
                                   story_elements: List[StoryElement] = None,
                                   narrative_significance: float = 0.5) -> NarrativeEvent:
        """Create a new narrative event from game occurrences."""
        event = NarrativeEvent(
            event_id=f"event_{len(self.narrative_events) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            description=description,
            involved_characters=involved_characters,
            story_elements=story_elements or [],
            narrative_significance=narrative_significance
        )
        
        # Analyze emotional impact on characters
        for character in involved_characters:
            emotional_state = self.dialogue_system.get_advisor_emotional_state(character)
            emotion = EmotionalState(emotional_state.get("emotion", "calm"))
            event.emotional_impact[character] = emotion
        
        # Update character relationships based on shared events
        if len(involved_characters) > 1:
            for i, char1 in enumerate(involved_characters):
                for char2 in involved_characters[i+1:]:
                    relationship_key = (min(char1, char2), max(char1, char2))
                    # Shared events strengthen relationships
                    self.character_relationships[relationship_key] += 0.1
        
        self.narrative_events.append(event)
        self.logger.info(f"Created narrative event: {title}")
        
        # Check if this event should spawn or update narrative threads
        await self._update_narrative_threads_from_event(event)
        
        return event
    
    async def _update_narrative_threads_from_event(self, event: NarrativeEvent):
        """Update existing narrative threads or create new ones based on event."""
        # Find relevant existing threads
        relevant_threads = []
        for thread in self.active_threads.values():
            # Check for character overlap
            character_overlap = len(set(event.involved_characters) & set(thread.central_characters))
            if character_overlap > 0:
                relevant_threads.append(thread)
        
        if relevant_threads:
            # Update existing threads
            for thread in relevant_threads:
                plot_point = await self._generate_plot_point_from_event(event, thread)
                primary_emotion = list(event.emotional_impact.values())[0] if event.emotional_impact else EmotionalState.CALM
                thread.add_plot_point(plot_point, primary_emotion)
                event.related_threads.append(thread.thread_id)
        else:
            # Consider creating new thread if event is significant enough
            if event.calculate_dramatic_weight() > 0.6:
                new_thread = await self._create_narrative_thread_from_event(event)
                if new_thread:
                    self.active_threads[new_thread.thread_id] = new_thread
                    event.related_threads.append(new_thread.thread_id)
    
    async def _generate_plot_point_from_event(self, event: NarrativeEvent, thread: NarrativeThread) -> str:
        """Generate a plot point for a narrative thread based on an event."""
        prompt = f"""Generate a plot point for an ongoing narrative thread based on a recent event:

NARRATIVE THREAD: {thread.title}
Thread Type: {thread.narrative_type.value}
Central Characters: {', '.join(thread.central_characters)}
Key Themes: {', '.join(thread.key_themes)}
Current Tension Level: {thread.tension_level:.1f}

RECENT EVENT: {event.title}
Event Description: {event.description}
Involved Characters: {', '.join(event.involved_characters)}
Dramatic Weight: {event.calculate_dramatic_weight():.1f}

PREVIOUS PLOT POINTS:
{chr(10).join(f"- {point}" for point in thread.plot_points[-3:])}

Generate a single plot point (1-2 sentences) that:
1. Connects this event to the ongoing narrative thread
2. Advances the story in a meaningful way
3. Maintains consistency with established themes and characters
4. Adds appropriate dramatic tension

Return only the plot point text, no explanation."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a master storyteller and plot development specialist."),
                LLMMessage(role="user", content=prompt)
            ])
            
            return response.content.strip().strip('"').strip("'")
            
        except Exception as e:
            self.logger.warning(f"Failed to generate plot point: {e}")
            return f"The events surrounding {event.title} continue to shape the destinies of {', '.join(event.involved_characters)}."
    
    async def _create_narrative_thread_from_event(self, event: NarrativeEvent) -> Optional[NarrativeThread]:
        """Create a new narrative thread inspired by a significant event."""
        if len(event.involved_characters) < 1:
            return None
        
        # Determine narrative type based on story elements and emotional impact
        narrative_type = await self._determine_narrative_type(event)
        
        # Generate thread details
        thread_details = await self._generate_thread_details(event, narrative_type)
        
        thread = NarrativeThread(
            thread_id=f"thread_{len(self.active_threads) + 1}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            title=thread_details.get("title", f"The Tale of {event.involved_characters[0]}"),
            narrative_type=narrative_type,
            central_characters=event.involved_characters.copy(),
            key_themes=thread_details.get("themes", ["Power", "Conflict", "Resolution"]),
            tension_level=event.calculate_dramatic_weight()
        )
        
        # Add initial plot point
        initial_plot = thread_details.get("initial_plot", f"The story begins with {event.title}.")
        primary_emotion = list(event.emotional_impact.values())[0] if event.emotional_impact else EmotionalState.CALM
        thread.add_plot_point(initial_plot, primary_emotion)
        
        self.logger.info(f"Created new narrative thread: {thread.title}")
        return thread
    
    async def _determine_narrative_type(self, event: NarrativeEvent) -> NarrativeType:
        """Determine the best narrative type for an event."""
        # Analyze story elements and emotional impact
        element_mapping = {
            StoryElement.CONFLICT_INTRODUCTION: NarrativeType.DRAMATIC_TENSION,
            StoryElement.CHARACTER_MOTIVATION: NarrativeType.CHARACTER_DEVELOPMENT,
            StoryElement.PLOT_TWIST: NarrativeType.POLITICAL_INTRIGUE,
            StoryElement.POWER_SHIFT: NarrativeType.HEROIC_SAGA,
            StoryElement.MORAL_DILEMMA: NarrativeType.TRAGIC_DOWNFALL,
            StoryElement.RELATIONSHIP_CHANGE: NarrativeType.CHARACTER_DEVELOPMENT
        }
        
        # Check for specific elements
        for element in event.story_elements:
            if element in element_mapping:
                return element_mapping[element]
        
        # Default based on emotional intensity
        if event.emotional_impact:
            high_intensity_emotions = sum(
                1 for emotion in event.emotional_impact.values()
                if emotion in [EmotionalState.ANGRY, EmotionalState.EXCITED, EmotionalState.WORRIED]
            )
            
            if high_intensity_emotions > len(event.emotional_impact) / 2:
                return NarrativeType.DRAMATIC_TENSION
        
        return NarrativeType.HISTORICAL_CHRONICLE
    
    async def _generate_thread_details(self, event: NarrativeEvent, narrative_type: NarrativeType) -> Dict[str, Any]:
        """Generate detailed information for a new narrative thread."""
        prompt = f"""Generate details for a new narrative thread based on a significant event:

EVENT: {event.title}
Description: {event.description}
Characters: {', '.join(event.involved_characters)}
Narrative Type: {narrative_type.value}
Dramatic Weight: {event.calculate_dramatic_weight():.1f}

Generate a narrative thread that will track this story's development.

Return JSON format:
{{
    "title": "Compelling narrative thread title",
    "themes": ["theme1", "theme2", "theme3"],
    "initial_plot": "Opening plot point that sets up the narrative arc",
    "predicted_elements": ["future_element1", "future_element2"]
}}

Make the title evocative and the themes meaningful for a political narrative."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a narrative design specialist creating compelling story frameworks."),
                LLMMessage(role="user", content=prompt)
            ])
            
            return json.loads(response.content)
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to generate thread details: {e}")
            return {
                "title": f"The Chronicles of {event.involved_characters[0] if event.involved_characters else 'Unknown'}",
                "themes": ["Power", "Destiny", "Conflict"],
                "initial_plot": f"The tale begins with {event.title}, setting events in motion.",
                "predicted_elements": ["Rising Action", "Climax", "Resolution"]
            }
    
    async def generate_narrative_content(self, thread: NarrativeThread, 
                                       content_type: NarrativeType = None,
                                       tone: NarrativeTone = None,
                                       length: str = "medium") -> GeneratedNarrative:
        """Generate narrative content for a specific thread."""
        content_type = content_type or thread.narrative_type
        tone = tone or self.narrative_preferences["tone_preference"]
        
        # Determine word count target
        length_targets = {
            "short": (50, 150),
            "medium": (150, 400),
            "long": (400, 800),
            "epic": (800, 1500)
        }
        min_words, max_words = length_targets.get(length, (150, 400))
        
        narrative_content = await self._generate_narrative_text(
            thread, content_type, tone, min_words, max_words
        )
        
        # Analyze generated content for literary devices
        literary_devices = await self._analyze_literary_devices(narrative_content)
        
        generated = GeneratedNarrative(
            narrative_id=f"narrative_{len(self.generated_narratives) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=narrative_content,
            narrative_type=content_type,
            tone=tone,
            featured_characters=thread.central_characters.copy(),
            related_threads=[thread.thread_id],
            literary_devices=literary_devices
        )
        
        self.generated_narratives.append(generated)
        self.logger.info(f"Generated narrative content: {generated.narrative_id} ({generated.word_count} words)")
        
        return generated
    
    async def _generate_narrative_text(self, thread: NarrativeThread, content_type: NarrativeType,
                                     tone: NarrativeTone, min_words: int, max_words: int) -> str:
        """Generate the actual narrative text using LLM."""
        recent_events = [event for event in self.narrative_events 
                        if any(char in event.involved_characters for char in thread.central_characters)][-3:]
        
        prompt = f"""Write a narrative passage for a political story thread:

NARRATIVE THREAD: {thread.title}
Type: {content_type.value}
Tone: {tone.value}
Central Characters: {', '.join(thread.central_characters)}
Key Themes: {', '.join(thread.key_themes)}
Current Tension Level: {thread.tension_level:.1f}

PLOT PROGRESSION:
{chr(10).join(f"- {point}" for point in thread.plot_points[-5:])}

RECENT RELEVANT EVENTS:
{chr(10).join(f"- {event.title}: {event.description}" for event in recent_events)}

CHARACTER EMOTIONAL STATES:
{chr(10).join(f"- {char}: {self.dialogue_system.get_advisor_emotional_state(char).get('emotion', 'calm')}" for char in thread.central_characters)}

Write a compelling narrative passage ({min_words}-{max_words} words) that:
1. Captures the {tone.value} tone
2. Advances the {content_type.value} story
3. Incorporates recent plot developments
4. Reflects character emotional states
5. Maintains thematic consistency

Use rich, immersive language appropriate for political fiction. Focus on character development, political intrigue, and dramatic tension."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a master storyteller specializing in political fiction and character-driven narratives."),
                LLMMessage(role="user", content=prompt)
            ])
            
            return response.content.strip()
            
        except Exception as e:
            self.logger.warning(f"Failed to generate narrative text: {e}")
            return f"The tale of {', '.join(thread.central_characters)} continues to unfold, marked by {', '.join(thread.key_themes)} in these turbulent times."
    
    async def _analyze_literary_devices(self, text: str) -> List[str]:
        """Analyze generated text for literary devices used."""
        prompt = f"""Analyze this narrative text for literary devices and techniques:

TEXT:
{text}

Identify the literary devices used in this passage. Return a JSON list of devices found.

Possible devices include:
- Metaphor
- Symbolism  
- Foreshadowing
- Irony
- Dramatic tension
- Character development
- Political allegory
- Historical parallel
- Emotional resonance
- Descriptive imagery

Return JSON format: ["device1", "device2", "device3"]
Limit to the most prominent 3-5 devices."""
        
        try:
            response = await self.llm_manager.generate([
                LLMMessage(role="system", content="You are a literary analysis expert."),
                LLMMessage(role="user", content=prompt)
            ])
            
            devices = json.loads(response.content)
            return devices if isinstance(devices, list) else []
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to analyze literary devices: {e}")
            return ["Political narrative", "Character development"]
    
    def process_emergent_storytelling_turn(self, game_state: Any) -> Dict[str, Any]:
        """Process narrative generation for one game turn."""
        results = {
            "new_threads": [],
            "updated_threads": [],
            "generated_narratives": [],
            "completed_threads": []
        }
        
        # Update thread momentum and completion
        for thread in list(self.active_threads.values()):
            momentum = thread.calculate_story_momentum()
            
            # Threads with very low momentum might complete
            if momentum < 0.2 and thread.tension_level < 0.3:
                thread.completion_status = 1.0
                results["completed_threads"].append(thread.thread_id)
                # Don't remove immediately - keep for historical reference
            
            # Update thread progression
            if momentum > 0.5 and len(thread.plot_points) > 3:
                thread.completion_status = min(1.0, thread.completion_status + 0.1)
        
        # Decay character relationships over time
        for relationship_key in self.character_relationships:
            self.character_relationships[relationship_key] *= 0.95  # 5% decay per turn
        
        return results
    
    def get_narrative_thread_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a comprehensive summary of a narrative thread."""
        thread = self.active_threads.get(thread_id)
        if not thread:
            return None
        
        return {
            "thread_id": thread.thread_id,
            "title": thread.title,
            "narrative_type": thread.narrative_type.value,
            "central_characters": thread.central_characters,
            "key_themes": thread.key_themes,
            "plot_points": thread.plot_points,
            "emotional_arc": [emotion.value for emotion in thread.emotional_arc],
            "tension_level": thread.tension_level,
            "completion_status": thread.completion_status,
            "story_momentum": thread.calculate_story_momentum(),
            "start_date": thread.start_date.isoformat(),
            "last_updated": thread.last_updated.isoformat(),
            "predicted_resolution": thread.predicted_resolution
        }
    
    def get_emergent_storytelling_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the storytelling system state."""
        active_thread_summaries = {}
        for thread_id in self.active_threads:
            summary = self.get_narrative_thread_summary(thread_id)
            if summary and summary["completion_status"] < 1.0:
                active_thread_summaries[thread_id] = summary
        
        # Recent events analysis
        recent_events = sorted(self.narrative_events[-10:], 
                             key=lambda e: e.calculate_dramatic_weight(), reverse=True)
        
        # Character relationship analysis
        strongest_relationships = sorted(
            self.character_relationships.items(),
            key=lambda x: x[1], reverse=True
        )[:5]
        
        return {
            "active_threads": len(active_thread_summaries),
            "threads": active_thread_summaries,
            "total_events": len(self.narrative_events),
            "recent_significant_events": [
                {
                    "title": event.title,
                    "characters": event.involved_characters,
                    "dramatic_weight": event.calculate_dramatic_weight()
                }
                for event in recent_events[:5]
            ],
            "generated_narratives": len(self.generated_narratives),
            "strongest_relationships": [
                {
                    "characters": list(chars),
                    "strength": strength
                }
                for chars, strength in strongest_relationships
            ],
            "narrative_preferences": self.narrative_preferences
        }
