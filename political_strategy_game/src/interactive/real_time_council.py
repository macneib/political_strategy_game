"""
Real-Time Council Meeting Interface

Provides interactive council meetings where players can watch live advisor debates
and intervene at any point to guide discussions and make strategic decisions.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from ..llm.dialogue import MultiAdvisorDialogue, DialogueSession, DialogueContext, DialogueType, DialogueTurn, EmotionalState
from ..llm.advisors import AdvisorCouncil
from ..llm.llm_providers import LLMManager, LLMMessage


class InterventionType(Enum):
    """Types of player interventions during council meetings."""
    SUPPORT_ADVISOR = "support_advisor"
    CHALLENGE_ADVISOR = "challenge_advisor"
    INTRODUCE_INFORMATION = "introduce_information"
    CALL_FOR_VOTE = "call_for_vote"
    REDIRECT_DISCUSSION = "redirect_discussion"
    REQUEST_ADVISOR_INPUT = "request_advisor_input"
    PROPOSE_COMPROMISE = "propose_compromise"
    END_MEETING = "end_meeting"


@dataclass
class PlayerIntervention:
    """Represents a player intervention in the council meeting."""
    intervention_type: InterventionType
    target_advisor: Optional[str] = None
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MeetingState:
    """Current state of the council meeting."""
    topic: str
    participants: List[str]
    current_speaker: Optional[str] = None
    is_active: bool = True
    player_can_intervene: bool = True
    last_turn_timestamp: datetime = field(default_factory=datetime.now)
    emotional_climate: Dict[str, EmotionalState] = field(default_factory=dict)
    discussion_focus: str = ""
    urgency_level: float = 0.5  # 0.0 = calm, 1.0 = crisis


class RealTimeCouncilInterface:
    """Interactive council meeting interface with live advisor debates and player intervention."""
    
    def __init__(self, llm_manager: LLMManager, advisor_council: AdvisorCouncil,
                 dialogue_system: MultiAdvisorDialogue):
        self.llm_manager = llm_manager
        self.advisor_council = advisor_council
        self.dialogue_system = dialogue_system
        
        self.active_sessions: Dict[str, DialogueSession] = {}
        self.meeting_states: Dict[str, MeetingState] = {}
        self.intervention_callbacks: List[Callable] = []
        self.update_callbacks: List[Callable] = []
        
        # Real-time configuration
        self.turn_delay_seconds = 5.0  # Delay between advisor responses
        self.max_turns_before_intervention = 3  # Force intervention opportunities
        
    def register_intervention_callback(self, callback: Callable):
        """Register callback for when player intervention is possible."""
        self.intervention_callbacks.append(callback)
        
    def register_update_callback(self, callback: Callable):
        """Register callback for real-time meeting updates."""
        self.update_callbacks.append(callback)
    
    async def start_council_meeting(self, topic: str, urgency: float = 0.5,
                                   participants: Optional[List[str]] = None,
                                   background_context: str = "") -> str:
        """Start an interactive council meeting with real-time updates."""
        if participants is None:
            participants = list(self.advisor_council.advisors.keys())
        
        # Create meeting state
        meeting_id = f"interactive_council_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        meeting_state = MeetingState(
            topic=topic,
            participants=participants,
            urgency_level=urgency,
            discussion_focus=topic
        )
        
        # Initialize emotional climate
        for advisor_name in participants:
            emotional_model = self.dialogue_system.emotional_models.get(advisor_name)
            if emotional_model:
                meeting_state.emotional_climate[advisor_name] = emotional_model.current_emotion
        
        self.meeting_states[meeting_id] = meeting_state
        
        # Create dialogue context
        context = DialogueContext(
            dialogue_type=DialogueType.COUNCIL_MEETING,
            topic=topic,
            participants=participants,
            game_state=None,  # Will be updated with current game state
            max_turns=50  # Extended for interactive sessions
        )
        
        # Create dialogue session
        session = DialogueSession(dialogue_id=meeting_id, context=context)
        self.active_sessions[meeting_id] = session
        
        # Notify callbacks about meeting start
        await self._notify_update_callbacks(meeting_id, "meeting_started", {
            "topic": topic,
            "participants": participants,
            "urgency": urgency,
            "background": background_context
        })
        
        # Start the interactive dialogue loop
        asyncio.create_task(self._run_interactive_dialogue(meeting_id))
        
        return meeting_id
    
    async def _run_interactive_dialogue(self, meeting_id: str):
        """Run the main interactive dialogue loop."""
        session = self.active_sessions[meeting_id]
        meeting_state = self.meeting_states[meeting_id]
        
        current_speaker_idx = 0
        turns_since_intervention = 0
        
        while meeting_state.is_active and len(session.turns) < session.context.max_turns:
            # Check if meeting should continue
            if not meeting_state.is_active:
                break
            
            # Determine current speaker
            current_speaker = meeting_state.participants[current_speaker_idx]
            meeting_state.current_speaker = current_speaker
            
            # Notify about current speaker
            await self._notify_update_callbacks(meeting_id, "speaker_change", {
                "current_speaker": current_speaker,
                "emotional_state": meeting_state.emotional_climate.get(current_speaker, EmotionalState.CALM).value
            })
            
            # Generate advisor response
            response = await self._generate_real_time_response(session, current_speaker)
            
            if response:
                # Create dialogue turn
                emotional_tone = self.dialogue_system._analyze_emotional_tone(response)
                turn = DialogueTurn(
                    speaker=current_speaker,
                    content=response,
                    turn_number=len(session.turns) + 1,
                    emotional_tone=emotional_tone
                )
                
                session.add_turn(turn)
                meeting_state.last_turn_timestamp = datetime.now()
                
                # Update emotional effects
                await self.dialogue_system._process_emotional_effects(session, turn)
                
                # Update emotional climate
                await self._update_emotional_climate(meeting_id)
                
                # Notify callbacks about new turn
                await self._notify_update_callbacks(meeting_id, "new_turn", {
                    "speaker": current_speaker,
                    "content": response,
                    "emotional_tone": emotional_tone.value if emotional_tone else "calm",
                    "turn_number": turn.turn_number
                })
                
                turns_since_intervention += 1
                
                # Check for intervention opportunity
                if (turns_since_intervention >= self.max_turns_before_intervention or 
                    self._should_offer_intervention(meeting_id, turn)):
                    await self._offer_intervention_opportunity(meeting_id)
                    turns_since_intervention = 0
                
                # Move to next speaker
                current_speaker_idx = self._select_next_speaker(session, current_speaker_idx)
                
                # Wait before next turn (simulates natural conversation pace)
                await asyncio.sleep(self.turn_delay_seconds)
            
            else:
                # If no response, end meeting
                meeting_state.is_active = False
                break
        
        # Process meeting conclusion
        await self._conclude_meeting(meeting_id)
    
    async def _generate_real_time_response(self, session: DialogueSession, speaker_name: str) -> Optional[str]:
        """Generate a response for real-time council meeting."""
        advisor = self.advisor_council.advisors.get(speaker_name)
        if not advisor:
            return None
        
        # Get current meeting state
        meeting_state = self.meeting_states[session.dialogue_id]
        
        # Enhanced prompt for real-time interaction
        emotional_model = self.dialogue_system.emotional_models[speaker_name]
        emotion_modifiers = emotional_model.get_emotion_modifier()
        
        # Build enhanced dialogue prompt with real-time context
        prompt = self._build_real_time_prompt(session, speaker_name, emotion_modifiers, meeting_state)
        
        try:
            from ..llm.llm_providers import LLMMessage
            messages = [
                LLMMessage(role="system", content=prompt),
                LLMMessage(role="user", content=f"What is your response as {speaker_name}?")
            ]
            
            response = await self.llm_manager.generate(messages, max_tokens=150, temperature=0.8)
            if response and response.content:
                return response.content.strip()
        except Exception as e:
            print(f"Error generating real-time response for {speaker_name}: {e}")
        
        return None
    
    def _build_real_time_prompt(self, session: DialogueSession, speaker_name: str,
                               emotion_modifiers: Dict[str, float], meeting_state: MeetingState) -> str:
        """Build enhanced prompt for real-time council meeting."""
        advisor = self.advisor_council.advisors[speaker_name]
        personality = advisor.personality
        emotional_model = self.dialogue_system.emotional_models[speaker_name]
        
        # Get recent conversation (last 3 turns)
        recent_turns = session.turns[-3:] if len(session.turns) >= 3 else session.turns
        conversation_context = ""
        for turn in recent_turns:
            conversation_context += f"{turn.speaker}: {turn.content}\n"
        
        prompt = f"""You are {personality.name}, {advisor.role.value.title()} Advisor in a LIVE council meeting.

PERSONALITY & ROLE:
- Background: {personality.background}
- Communication Style: {personality.communication_style}
- Expertise: {', '.join(personality.expertise_areas)}

CURRENT EMOTIONAL STATE:
- Emotion: {emotional_model.current_emotion.value} (intensity: {emotional_model.emotion_intensity:.1f})
- Your behavior is modified by: {emotion_modifiers}

MEETING CONTEXT:
- Topic: {meeting_state.topic}
- Current Focus: {meeting_state.discussion_focus}
- Urgency Level: {meeting_state.urgency_level:.1f}/1.0 {"(HIGH URGENCY)" if meeting_state.urgency_level > 0.7 else ""}
- Other Participants: {', '.join([p for p in meeting_state.participants if p != speaker_name])}

RECENT DISCUSSION:
{conversation_context or "Meeting just started."}

EMOTIONAL CLIMATE:
{self._format_emotional_climate(meeting_state)}

INSTRUCTIONS:
1. Respond in character as {personality.name} with your current emotional state
2. React to the most recent statements and the overall discussion
3. Consider the urgency level - {"speak decisively and urgently" if meeting_state.urgency_level > 0.7 else "maintain measured discussion"}
4. Keep response concise (1-2 sentences) for natural dialogue flow
5. Show your expertise in {advisor.role.value} matters
6. Your emotional state affects how you express your ideas

Your response as {personality.name}:"""
        
        return prompt
    
    def _format_emotional_climate(self, meeting_state: MeetingState) -> str:
        """Format the emotional climate for the prompt."""
        climate_lines = []
        for advisor, emotion in meeting_state.emotional_climate.items():
            climate_lines.append(f"- {advisor}: {emotion.value}")
        return "\n".join(climate_lines)
    
    async def _update_emotional_climate(self, meeting_id: str):
        """Update the emotional climate tracking."""
        meeting_state = self.meeting_states[meeting_id]
        
        for advisor_name in meeting_state.participants:
            emotional_model = self.dialogue_system.emotional_models.get(advisor_name)
            if emotional_model:
                meeting_state.emotional_climate[advisor_name] = emotional_model.current_emotion
    
    def _select_next_speaker(self, session: DialogueSession, current_speaker_idx: int) -> int:
        """Select next speaker with enhanced logic for real-time meetings."""
        participants = session.context.participants
        
        # For now, use round-robin (could be enhanced with LLM-based selection)
        return (current_speaker_idx + 1) % len(participants)
    
    def _should_offer_intervention(self, meeting_id: str, turn: DialogueTurn) -> bool:
        """Determine if player intervention should be offered."""
        meeting_state = self.meeting_states[meeting_id]
        
        # Offer intervention on high urgency topics
        if meeting_state.urgency_level > 0.8:
            return True
        
        # Offer intervention on strong emotional responses
        if turn.emotional_tone in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED, EmotionalState.SUSPICIOUS]:
            return True
        
        # Offer intervention on contentious keywords
        contentious_keywords = ["disagree", "unacceptable", "impossible", "refuse", "outrage"]
        if any(keyword in turn.content.lower() for keyword in contentious_keywords):
            return True
        
        return False
    
    async def _offer_intervention_opportunity(self, meeting_id: str):
        """Offer player the opportunity to intervene."""
        meeting_state = self.meeting_states[meeting_id]
        
        if not meeting_state.player_can_intervene:
            return
        
        intervention_options = [
            InterventionType.SUPPORT_ADVISOR,
            InterventionType.CHALLENGE_ADVISOR,
            InterventionType.INTRODUCE_INFORMATION,
            InterventionType.REDIRECT_DISCUSSION,
            InterventionType.REQUEST_ADVISOR_INPUT,
            InterventionType.PROPOSE_COMPROMISE
        ]
        
        # Notify callbacks about intervention opportunity
        for callback in self.intervention_callbacks:
            try:
                await callback(meeting_id, intervention_options)
            except Exception as e:
                print(f"Error in intervention callback: {e}")
    
    async def handle_player_intervention(self, meeting_id: str, intervention: PlayerIntervention) -> bool:
        """Process player intervention in the council meeting."""
        if meeting_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[meeting_id]
        meeting_state = self.meeting_states[meeting_id]
        
        # Process the intervention
        intervention_effect = await self._process_intervention(meeting_id, intervention)
        
        # Create a special turn for player intervention
        player_turn = DialogueTurn(
            speaker="Player",
            content=f"[INTERVENTION: {intervention.intervention_type.value}] {intervention.content}",
            turn_number=len(session.turns) + 1,
            emotional_tone=EmotionalState.CONFIDENT  # Player interventions are typically confident
        )
        
        session.add_turn(player_turn)
        
        # Update meeting focus if redirecting discussion
        if intervention.intervention_type == InterventionType.REDIRECT_DISCUSSION:
            meeting_state.discussion_focus = intervention.content
        
        # Notify callbacks about intervention
        await self._notify_update_callbacks(meeting_id, "player_intervention", {
            "intervention_type": intervention.intervention_type.value,
            "target_advisor": intervention.target_advisor,
            "content": intervention.content,
            "effect": intervention_effect
        })
        
        # Continue dialogue with intervention effects
        return True
    
    async def _process_intervention(self, meeting_id: str, intervention: PlayerIntervention) -> Dict[str, Any]:
        """Process the effects of player intervention."""
        meeting_state = self.meeting_states[meeting_id]
        effect = {"type": intervention.intervention_type.value, "impact": {}}
        
        if intervention.intervention_type == InterventionType.SUPPORT_ADVISOR:
            # Boost target advisor's confidence
            if intervention.target_advisor and intervention.target_advisor in self.dialogue_system.emotional_models:
                emotional_model = self.dialogue_system.emotional_models[intervention.target_advisor]
                emotional_model.update_emotion(EmotionalState.CONFIDENT, 
                                             min(1.0, emotional_model.emotion_intensity + 0.2),
                                             "player support")
                effect["impact"]["advisor_confidence"] = 0.2
        
        elif intervention.intervention_type == InterventionType.CHALLENGE_ADVISOR:
            # Make target advisor defensive or frustrated
            if intervention.target_advisor and intervention.target_advisor in self.dialogue_system.emotional_models:
                emotional_model = self.dialogue_system.emotional_models[intervention.target_advisor]
                emotional_model.update_emotion(EmotionalState.FRUSTRATED,
                                             min(1.0, emotional_model.emotion_intensity + 0.15),
                                             "player challenge")
                effect["impact"]["advisor_frustration"] = 0.15
        
        elif intervention.intervention_type == InterventionType.REDIRECT_DISCUSSION:
            # Change meeting focus
            meeting_state.discussion_focus = intervention.content
            effect["impact"]["focus_change"] = intervention.content
        
        elif intervention.intervention_type == InterventionType.CALL_FOR_VOTE:
            # Increase urgency and move toward resolution
            meeting_state.urgency_level = min(1.0, meeting_state.urgency_level + 0.3)
            effect["impact"]["urgency_increase"] = 0.3
        
        return effect
    
    async def _notify_update_callbacks(self, meeting_id: str, update_type: str, data: Dict[str, Any]):
        """Notify all registered update callbacks."""
        update_data = {
            "meeting_id": meeting_id,
            "update_type": update_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        for callback in self.update_callbacks:
            try:
                await callback(update_data)
            except Exception as e:
                print(f"Error in update callback: {e}")
    
    async def _conclude_meeting(self, meeting_id: str):
        """Conclude the council meeting and process outcomes."""
        session = self.active_sessions[meeting_id]
        meeting_state = self.meeting_states[meeting_id]
        
        # Process dialogue outcomes
        await self.dialogue_system._process_dialogue_outcomes(session)
        
        # Generate meeting summary
        summary = await self._generate_meeting_summary(meeting_id)
        
        # Mark meeting as completed
        meeting_state.is_active = False
        
        # Notify callbacks about meeting conclusion
        await self._notify_update_callbacks(meeting_id, "meeting_concluded", {
            "summary": summary,
            "outcomes": session.outcomes,
            "total_turns": len(session.turns),
            "duration_minutes": (datetime.now() - meeting_state.last_turn_timestamp).total_seconds() / 60
        })
    
    async def _generate_meeting_summary(self, meeting_id: str) -> str:
        """Generate a summary of the council meeting."""
        session = self.active_sessions[meeting_id]
        meeting_state = self.meeting_states[meeting_id]
        
        # Simple summary for now - could be enhanced with LLM summarization
        summary_parts = [
            f"Council Meeting: {meeting_state.topic}",
            f"Participants: {', '.join(meeting_state.participants)}",
            f"Total Discussion Turns: {len(session.turns)}",
            f"Final Emotional Climate: {dict(meeting_state.emotional_climate)}"
        ]
        
        if session.outcomes:
            summary_parts.append(f"Outcomes: {session.outcomes}")
        
        return "\n".join(summary_parts)
    
    def get_meeting_state(self, meeting_id: str) -> Optional[MeetingState]:
        """Get current state of a meeting."""
        return self.meeting_states.get(meeting_id)
    
    def get_active_meetings(self) -> List[str]:
        """Get list of active meeting IDs."""
        return [mid for mid, state in self.meeting_states.items() if state.is_active]
    
    async def end_meeting(self, meeting_id: str) -> bool:
        """Manually end a council meeting."""
        if meeting_id in self.meeting_states:
            self.meeting_states[meeting_id].is_active = False
            await self._conclude_meeting(meeting_id)
            return True
        return False
