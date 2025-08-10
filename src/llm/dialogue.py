"""
Advanced Multi-Advisor Dialogue System

This module implements sophisticated advisor-to-advisor interactions, conspiracy
generation, and dynamic political storytelling for the political strategy game.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import asyncio
import logging
import random
from datetime import datetime

from .advisors import AdvisorAI, AdvisorRole, AdvisorCouncil, ConversationMemory
from .llm_providers import LLMManager, LLMMessage, LLMResponse

# Set up logging
logger = logging.getLogger(__name__)


class DialogueType(Enum):
    """Types of advisor-to-advisor dialogues."""
    COUNCIL_MEETING = "council_meeting"
    PRIVATE_CONVERSATION = "private_conversation"
    CONSPIRACY_PLANNING = "conspiracy_planning"
    CONFLICT_RESOLUTION = "conflict_resolution"
    ALLIANCE_FORMATION = "alliance_formation"


class EmotionalState(Enum):
    """Emotional states that affect advisor interactions."""
    CALM = "calm"
    EXCITED = "excited"
    ANGRY = "angry"
    WORRIED = "worried"
    SUSPICIOUS = "suspicious"
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"
    HOPEFUL = "hopeful"


@dataclass
class DialogueContext:
    """Context for a multi-advisor dialogue session."""
    dialogue_type: DialogueType
    topic: str
    participants: List[str]  # Advisor names
    game_state: Any  # Current political situation
    emotional_context: Dict[str, EmotionalState] = field(default_factory=dict)
    turn_number: int = 1
    max_turns: int = 10
    
    def add_emotional_state(self, advisor_name: str, emotion: EmotionalState):
        """Add emotional state for an advisor."""
        self.emotional_context[advisor_name] = emotion


@dataclass
class DialogueTurn:
    """A single turn in an advisor dialogue."""
    speaker: str
    content: str
    turn_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_tone: Optional[EmotionalState] = None
    targets: List[str] = field(default_factory=list)  # Who this message is directed to


@dataclass
class DialogueSession:
    """A complete dialogue session between advisors."""
    dialogue_id: str
    context: DialogueContext
    turns: List[DialogueTurn] = field(default_factory=list)
    outcomes: Dict[str, Any] = field(default_factory=dict)
    relationship_changes: Dict[Tuple[str, str], float] = field(default_factory=dict)
    completed: bool = False
    
    def add_turn(self, turn: DialogueTurn):
        """Add a dialogue turn."""
        self.turns.append(turn)
        if len(self.turns) >= self.context.max_turns:
            self.completed = True
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history."""
        history = []
        for turn in self.turns:
            emotional_indicator = f" [{turn.emotional_tone.value}]" if turn.emotional_tone else ""
            history.append(f"{turn.speaker}{emotional_indicator}: {turn.content}")
        return "\n".join(history)


class AdvisorEmotionalModel:
    """Models emotional states and their effects on advisor behavior."""
    
    def __init__(self, advisor_name: str):
        self.advisor_name = advisor_name
        self.current_emotion = EmotionalState.CALM
        self.emotion_intensity = 0.5  # 0.0 to 1.0
        self.emotion_history: List[Tuple[EmotionalState, float, datetime]] = []
    
    def update_emotion(self, new_emotion: EmotionalState, intensity: float, trigger: str):
        """Update advisor's emotional state."""
        # Store previous emotion
        self.emotion_history.append((self.current_emotion, self.emotion_intensity, datetime.now()))
        
        # Update current emotion
        self.current_emotion = new_emotion
        self.emotion_intensity = max(0.0, min(1.0, intensity))
        
        logger.info(f"{self.advisor_name} emotion changed to {new_emotion.value} "
                   f"(intensity: {intensity:.2f}) due to: {trigger}")
    
    def get_emotion_modifier(self) -> Dict[str, float]:
        """Get emotion-based modifiers for response generation."""
        modifiers = {
            "aggression": 0.0,
            "cooperation": 0.0,
            "suspicion": 0.0,
            "confidence": 0.0
        }
        
        emotion_effects = {
            EmotionalState.ANGRY: {"aggression": 0.8, "cooperation": -0.4, "suspicion": 0.3},
            EmotionalState.WORRIED: {"cooperation": 0.2, "suspicion": 0.6, "confidence": -0.4},
            EmotionalState.SUSPICIOUS: {"suspicion": 0.9, "cooperation": -0.3, "aggression": 0.2},
            EmotionalState.CONFIDENT: {"confidence": 0.8, "aggression": 0.3, "cooperation": 0.2},
            EmotionalState.FRUSTRATED: {"aggression": 0.6, "cooperation": -0.5, "confidence": -0.2},
            EmotionalState.HOPEFUL: {"cooperation": 0.7, "confidence": 0.4, "suspicion": -0.3},
            EmotionalState.EXCITED: {"confidence": 0.5, "cooperation": 0.3, "aggression": 0.2}
        }
        
        if self.current_emotion in emotion_effects:
            base_effects = emotion_effects[self.current_emotion]
            for key, value in base_effects.items():
                modifiers[key] = value * self.emotion_intensity
        
        return modifiers
    
    def emotional_contagion(self, other_advisor_emotion: EmotionalState, relationship_strength: float):
        """Model emotional contagion between advisors."""
        contagion_strength = relationship_strength * 0.3  # Max 30% emotional influence
        
        # Strong emotions are more contagious
        emotion_contagion_rates = {
            EmotionalState.ANGRY: 0.8,
            EmotionalState.EXCITED: 0.7,
            EmotionalState.WORRIED: 0.6,
            EmotionalState.SUSPICIOUS: 0.5,
            EmotionalState.CONFIDENT: 0.4,
            EmotionalState.FRUSTRATED: 0.6,
            EmotionalState.HOPEFUL: 0.5,
            EmotionalState.CALM: 0.2
        }
        
        contagion_rate = emotion_contagion_rates.get(other_advisor_emotion, 0.3)
        total_influence = contagion_strength * contagion_rate
        
        if total_influence > 0.2:  # Significant enough influence
            new_intensity = min(1.0, self.emotion_intensity + total_influence)
            self.update_emotion(other_advisor_emotion, new_intensity, 
                              f"emotional contagion from advisor")


class MultiAdvisorDialogue:
    """Manages sophisticated advisor-to-advisor conversations."""
    
    def __init__(self, llm_manager: LLMManager, advisor_council: AdvisorCouncil):
        self.llm_manager = llm_manager
        self.advisor_council = advisor_council
        self.active_dialogues: Dict[str, DialogueSession] = {}
        self.emotional_models: Dict[str, AdvisorEmotionalModel] = {}
        
        # Initialize emotional models for all advisors
        for advisor_name in advisor_council.advisors.keys():
            self.emotional_models[advisor_name] = AdvisorEmotionalModel(advisor_name)
    
    async def initiate_council_meeting(self, topic: str, game_state: Any, 
                                     participants: Optional[List[str]] = None) -> DialogueSession:
        """Start a council meeting where advisors discuss a topic."""
        if participants is None:
            participants = list(self.advisor_council.advisors.keys())
        
        # Create dialogue context
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic=topic,
            participants=participants,
            game_state=game_state,
            max_turns=min(len(participants) * 3, 15)  # Allow multiple rounds
        )
        
        # Create dialogue session
        dialogue_id = f"council_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = DialogueSession(dialogue_id=dialogue_id, context=context)
        self.active_dialogues[dialogue_id] = session
        
        logger.info(f"Starting council meeting: {topic}")
        logger.info(f"Participants: {', '.join(participants)}")
        
        # Conduct the dialogue
        await self._conduct_dialogue(session)
        
        return session
    
    async def initiate_private_conversation(self, participant1: str, participant2: str,
                                          topic: str, game_state: Any) -> DialogueSession:
        """Start a private conversation between two advisors."""
        context = DialogueContext(
            dialogue_type=DialogueType.PRIVATE_CONVERSATION,
            topic=topic,
            participants=[participant1, participant2],
            game_state=game_state,
            max_turns=8
        )
        
        dialogue_id = f"private_{participant1}_{participant2}_{datetime.now().strftime('%H%M%S')}"
        session = DialogueSession(dialogue_id=dialogue_id, context=context)
        self.active_dialogues[dialogue_id] = session
        
        logger.info(f"Starting private conversation between {participant1} and {participant2}: {topic}")
        
        await self._conduct_dialogue(session)
        
        return session
    
    async def _conduct_dialogue(self, session: DialogueSession):
        """Conduct a multi-turn dialogue session."""
        context = session.context
        participants = context.participants
        
        # Determine initial speaker (random or based on topic relevance)
        current_speaker_idx = 0
        
        while not session.completed and len(session.turns) < context.max_turns:
            current_speaker = participants[current_speaker_idx]
            
            # Generate response for current speaker
            response = await self._generate_advisor_dialogue_response(
                session, current_speaker
            )
            
            if response:
                # Determine emotional tone
                emotional_tone = self._analyze_emotional_tone(response)
                
                # Create dialogue turn
                turn = DialogueTurn(
                    speaker=current_speaker,
                    content=response,
                    turn_number=len(session.turns) + 1,
                    emotional_tone=emotional_tone
                )
                
                session.add_turn(turn)
                
                # Update emotional models based on dialogue
                await self._process_emotional_effects(session, turn)
                
                # Determine next speaker (could be rule-based or LLM-determined)
                current_speaker_idx = self._select_next_speaker(session, current_speaker_idx)
                
            else:
                # If no response generated, end dialogue
                break
        
        # Process dialogue outcomes
        await self._process_dialogue_outcomes(session)
        session.completed = True
        
        logger.info(f"Dialogue {session.dialogue_id} completed with {len(session.turns)} turns")
    
    async def _generate_advisor_dialogue_response(self, session: DialogueSession, 
                                                speaker_name: str) -> Optional[str]:
        """Generate a response for an advisor in dialogue context."""
        advisor = self.advisor_council.advisors.get(speaker_name)
        if not advisor:
            return None
        
        # Get advisor's emotional state
        emotional_model = self.emotional_models[speaker_name]
        emotion_modifiers = emotional_model.get_emotion_modifier()
        
        # Build dialogue-specific prompt
        dialogue_prompt = self._build_dialogue_prompt(session, speaker_name, emotion_modifiers)
        
        # Generate response using LLM
        messages = [
            LLMMessage(role="system", content=dialogue_prompt),
            LLMMessage(role="user", content=f"Respond as {speaker_name} to this discussion.")
        ]
        
        try:
            response = await self.llm_manager.generate(messages)
            if response and response.content:
                return response.content.strip()
        except Exception as e:
            logger.error(f"Error generating dialogue response for {speaker_name}: {e}")
        
        return None
    
    def _build_dialogue_prompt(self, session: DialogueSession, speaker_name: str,
                              emotion_modifiers: Dict[str, float]) -> str:
        """Build a comprehensive prompt for advisor dialogue."""
        advisor = self.advisor_council.advisors[speaker_name]
        context = session.context
        
        # Get advisor personality
        personality = advisor.personality
        
        # Build emotional context
        emotional_state = self.emotional_models[speaker_name].current_emotion
        emotional_intensity = self.emotional_models[speaker_name].emotion_intensity
        
        # Get conversation history
        conversation_history = session.get_conversation_history()
        
        prompt = f"""You are {personality.name}, {personality.title} in a political council.

PERSONALITY TRAITS:
- Background: {personality.background}
- Communication Style: {personality.communication_style}
- Core Values: {', '.join(personality.core_values)}
- Expertise: {advisor.role.value} affairs

CURRENT EMOTIONAL STATE:
- Emotion: {emotional_state.value} (intensity: {emotional_intensity:.1f}/1.0)
- Behavioral modifiers: {emotion_modifiers}

DIALOGUE CONTEXT:
- Type: {context.dialogue_type.value}
- Topic: {context.topic}
- Participants: {', '.join(context.participants)}
- Current turn: {len(session.turns) + 1}/{context.max_turns}

CONVERSATION SO FAR:
{conversation_history or "This is the beginning of the discussion."}

CURRENT POLITICAL SITUATION:
{self._summarize_game_state(context.game_state)}

INSTRUCTIONS:
1. Respond in character as {personality.name} with your current emotional state
2. Consider your {advisor.role.value} expertise and perspective
3. React to what other advisors have said
4. Keep responses focused and realistic (2-3 sentences)
5. Show your personality through your communication style
6. Consider your relationships with other participants

Your response as {personality.name}:"""
        
        return prompt
    
    def _summarize_game_state(self, game_state: Any) -> str:
        """Summarize current game state for dialogue context."""
        if hasattr(game_state, 'political_power'):
            return f"Political Power: {game_state.political_power}, Stability: {getattr(game_state, 'stability', 'Unknown')}, Legitimacy: {getattr(game_state, 'legitimacy', 'Unknown')}"
        return "Current political situation is being monitored."
    
    def _analyze_emotional_tone(self, response: str) -> Optional[EmotionalState]:
        """Analyze the emotional tone of a response (simple keyword-based for now)."""
        response_lower = response.lower()
        
        emotion_keywords = {
            EmotionalState.ANGRY: ["angry", "outraged", "furious", "unacceptable", "demand"],
            EmotionalState.WORRIED: ["concerned", "worried", "anxious", "troubling", "dangerous"],
            EmotionalState.SUSPICIOUS: ["suspicious", "doubt", "question", "unclear", "hidden"],
            EmotionalState.CONFIDENT: ["confident", "certain", "assured", "clearly", "definitely"],
            EmotionalState.FRUSTRATED: ["frustrated", "impossible", "pointless", "waste"],
            EmotionalState.HOPEFUL: ["hopeful", "optimistic", "opportunity", "potential", "promising"],
            EmotionalState.EXCITED: ["exciting", "excellent", "fantastic", "thrilled", "enthusiastic"]
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                return emotion
        
        return EmotionalState.CALM
    
    async def _process_emotional_effects(self, session: DialogueSession, turn: DialogueTurn):
        """Process emotional effects of a dialogue turn on all participants."""
        speaker_name = turn.speaker
        speaker_emotion = self.emotional_models[speaker_name]
        
        # Update speaker's emotion based on their own response
        if turn.emotional_tone and turn.emotional_tone != speaker_emotion.current_emotion:
            speaker_emotion.update_emotion(
                turn.emotional_tone, 
                min(1.0, speaker_emotion.emotion_intensity + 0.1),
                f"expressed {turn.emotional_tone.value} in dialogue"
            )
        
        # Process emotional contagion to other participants
        for participant in session.context.participants:
            if participant != speaker_name:
                # Get relationship strength (simplified for now)
                relationship_strength = 0.5  # Could be retrieved from advisor relationships
                
                participant_emotion = self.emotional_models[participant]
                if turn.emotional_tone:
                    participant_emotion.emotional_contagion(
                        turn.emotional_tone, relationship_strength
                    )
    
    def _select_next_speaker(self, session: DialogueSession, current_speaker_idx: int) -> int:
        """Select the next speaker in the dialogue."""
        participants = session.context.participants
        
        # Simple round-robin for now, could be enhanced with LLM-based selection
        next_idx = (current_speaker_idx + 1) % len(participants)
        
        # Could add logic for:
        # - Advisors responding to direct questions/challenges
        # - Emotional reactions triggering immediate responses
        # - Topic expertise determining speaker priority
        
        return next_idx
    
    async def _process_dialogue_outcomes(self, session: DialogueSession):
        """Process the outcomes and effects of a completed dialogue."""
        context = session.context
        
        # Analyze relationship changes
        for i, participant1 in enumerate(context.participants):
            for participant2 in context.participants[i+1:]:
                # Calculate relationship change based on dialogue content
                change = self._calculate_relationship_change(session, participant1, participant2)
                if abs(change) > 0.1:  # Significant change
                    session.relationship_changes[(participant1, participant2)] = change
        
        # Store dialogue outcomes
        session.outcomes = {
            "consensus_reached": self._analyze_consensus(session),
            "conflicts_identified": self._identify_conflicts(session),
            "action_items": self._extract_action_items(session),
            "emotional_summary": self._summarize_emotional_climate(session)
        }
        
        logger.info(f"Dialogue outcomes: {session.outcomes}")
    
    def _calculate_relationship_change(self, session: DialogueSession, 
                                     advisor1: str, advisor2: str) -> float:
        """Calculate how the dialogue affected the relationship between two advisors."""
        # Simplified calculation - could be enhanced with sentiment analysis
        change = 0.0
        
        # Check for supportive vs. conflicting statements
        for turn in session.turns:
            if turn.speaker == advisor1:
                # Analyze if this turn was supportive or critical of advisor2
                if advisor2.lower() in turn.content.lower():
                    if any(word in turn.content.lower() for word in ["agree", "support", "excellent", "right"]):
                        change += 0.1
                    elif any(word in turn.content.lower() for word in ["disagree", "wrong", "mistake", "foolish"]):
                        change -= 0.1
        
        return max(-0.5, min(0.5, change))  # Cap relationship changes
    
    def _analyze_consensus(self, session: DialogueSession) -> bool:
        """Analyze if consensus was reached in the dialogue."""
        # Simple analysis based on agreement keywords in final turns
        final_turns = session.turns[-3:] if len(session.turns) >= 3 else session.turns
        
        agreement_words = ["agree", "consensus", "settled", "decided", "approved"]
        disagreement_words = ["disagree", "oppose", "reject", "impossible", "never"]
        
        agreement_count = sum(1 for turn in final_turns 
                            if any(word in turn.content.lower() for word in agreement_words))
        disagreement_count = sum(1 for turn in final_turns 
                               if any(word in turn.content.lower() for word in disagreement_words))
        
        return agreement_count > disagreement_count
    
    def _identify_conflicts(self, session: DialogueSession) -> List[Dict[str, Any]]:
        """Identify conflicts that emerged during dialogue."""
        conflicts = []
        
        for turn in session.turns:
            if turn.emotional_tone in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
                conflicts.append({
                    "type": "emotional_conflict",
                    "advisor": turn.speaker,
                    "turn": turn.turn_number,
                    "content": turn.content
                })
        
        return conflicts
    
    def _extract_action_items(self, session: DialogueSession) -> List[str]:
        """Extract action items or decisions from the dialogue."""
        actions = []
        action_keywords = ["should", "must", "will", "propose", "recommend", "action"]
        
        for turn in session.turns:
            if any(keyword in turn.content.lower() for keyword in action_keywords):
                actions.append(f"{turn.speaker}: {turn.content}")
        
        return actions[-3:]  # Return last 3 action items
    
    def _summarize_emotional_climate(self, session: DialogueSession) -> Dict[str, Any]:
        """Summarize the emotional climate of the dialogue."""
        emotions = [turn.emotional_tone for turn in session.turns if turn.emotional_tone]
        
        if not emotions:
            return {"overall_mood": "neutral", "tension_level": "low"}
        
        # Count emotional states
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion.value] = emotion_counts.get(emotion.value, 0) + 1
        
        # Determine overall mood
        negative_emotions = [EmotionalState.ANGRY, EmotionalState.FRUSTRATED, 
                           EmotionalState.WORRIED, EmotionalState.SUSPICIOUS]
        negative_count = sum(1 for emotion in emotions if emotion in negative_emotions)
        
        tension_level = "high" if negative_count > len(emotions) * 0.5 else \
                       "medium" if negative_count > len(emotions) * 0.25 else "low"
        
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "calm"
        
        return {
            "overall_mood": most_common_emotion,
            "tension_level": tension_level,
            "emotion_distribution": emotion_counts
        }
    
    def get_advisor_emotional_state(self, advisor_name: str) -> Dict[str, Any]:
        """Get current emotional state of an advisor."""
        if advisor_name not in self.emotional_models:
            return {"emotion": "unknown", "intensity": 0.0}
        
        model = self.emotional_models[advisor_name]
        return {
            "emotion": model.current_emotion.value,
            "intensity": model.emotion_intensity,
            "modifiers": model.get_emotion_modifier()
        }
    
    def get_dialogue_summary(self, dialogue_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a completed dialogue."""
        if dialogue_id not in self.active_dialogues:
            return None
        
        session = self.active_dialogues[dialogue_id]
        return {
            "dialogue_id": dialogue_id,
            "type": session.context.dialogue_type.value,
            "topic": session.context.topic,
            "participants": session.context.participants,
            "turns": len(session.turns),
            "outcomes": session.outcomes,
            "relationship_changes": dict(session.relationship_changes),
            "completed": session.completed
        }
