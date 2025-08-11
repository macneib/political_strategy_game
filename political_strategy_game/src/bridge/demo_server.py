"""
Demo Bridge Server

This script demonstrates the complete Game Engine Bridge system by running
a demo political simulation that generates events and state changes for
connected game engine clients to observe.
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from . import (
    GameState, CivilizationState, AdvisorState, TurnState, PoliticalEvent,
    EventPriority
)
from .bridge_manager import GameEngineBridgeManager


class DemoPoliticalSimulation:
    """
    Demo political simulation that generates realistic political events
    and state changes for the bridge demonstration.
    """
    
    def __init__(self):
        """Initialize demo simulation."""
        self.current_turn = 1
        self.advisors = self._create_demo_advisors()
        self.civilizations = self._create_demo_civilizations()
        self.recent_events = []
        
        # Event generation probabilities
        self.event_probabilities = {
            'advisor_loyalty_change': 0.3,
            'advisor_conflict': 0.2,
            'crisis_emergence': 0.15,
            'conspiracy_discovered': 0.1,
            'diplomatic_incident': 0.25,
            'economic_shift': 0.2,
            'military_action': 0.15
        }
        
        # Logging
        self.logger = logging.getLogger("DemoSimulation")
    
    def _create_demo_advisors(self) -> List[AdvisorState]:
        """Create demo advisors with varied personalities."""
        advisors = [
            AdvisorState(
                advisor_id="general_marcus",
                name="General Marcus",
                role="military",
                loyalty=0.85,
                influence=0.9,
                stress_level=0.4,
                current_mood="determined",
                personality_traits={"aggressive": 0.8, "cautious": 0.2, "diplomatic": 0.3},
                relationships={"advisor_elena": 0.6, "advisor_zhang": -0.2}
            ),
            AdvisorState(
                advisor_id="advisor_elena",
                name="Advisor Elena",
                role="diplomatic",
                loyalty=0.9,
                influence=0.7,
                stress_level=0.2,
                current_mood="calm",
                personality_traits={"aggressive": 0.2, "cautious": 0.8, "diplomatic": 0.9},
                relationships={"general_marcus": 0.6, "advisor_zhang": 0.8}
            ),
            AdvisorState(
                advisor_id="advisor_zhang",
                name="Advisor Zhang",
                role="economic",
                loyalty=0.7,
                influence=0.8,
                stress_level=0.6,
                current_mood="concerned",
                personality_traits={"aggressive": 0.4, "cautious": 0.7, "diplomatic": 0.6},
                relationships={"general_marcus": -0.2, "advisor_elena": 0.8}
            ),
            AdvisorState(
                advisor_id="spymaster_alex",
                name="Spymaster Alex",
                role="intelligence",
                loyalty=0.6,
                influence=0.7,
                stress_level=0.8,
                current_mood="suspicious",
                personality_traits={"aggressive": 0.6, "cautious": 0.9, "diplomatic": 0.4},
                relationships={"general_marcus": 0.3, "advisor_elena": 0.1}
            )
        ]
        return advisors
    
    def _create_demo_civilizations(self) -> List[CivilizationState]:
        """Create demo civilizations."""
        civilizations = [
            CivilizationState(
                civilization_id="player_empire",
                name="Player Empire",
                leader_name="Emperor Augustus",
                political_stability=0.75,
                economic_strength=0.8,
                military_power=0.7,
                diplomatic_relations={
                    "northern_kingdom": 0.6,
                    "eastern_republic": -0.3,
                    "southern_alliance": 0.8
                },
                active_crises=["border_tension"],
                active_conspiracies=[],
                recent_events=[]
            ),
            CivilizationState(
                civilization_id="northern_kingdom",
                name="Northern Kingdom",
                leader_name="King Harald",
                political_stability=0.6,
                economic_strength=0.5,
                military_power=0.9,
                diplomatic_relations={
                    "player_empire": 0.6,
                    "eastern_republic": 0.2,
                    "southern_alliance": -0.4
                },
                active_crises=[],
                active_conspiracies=["royal_succession"],
                recent_events=[]
            )
        ]
        return civilizations
    
    def generate_game_state(self) -> GameState:
        """Generate current game state."""
        turn_state = TurnState(
            turn_number=self.current_turn,
            civilization_id="player_empire",
            phase="execution"
        )
        
        return GameState(
            turn_state=turn_state,
            civilizations=self.civilizations,
            advisors=self.advisors,
            global_events=self.recent_events[-10:],  # Last 10 events
            metadata={
                "demo_mode": True,
                "simulation_time": datetime.now().isoformat(),
                "turn_duration": 30.0
            }
        )
    
    def simulate_turn_events(self) -> List[PoliticalEvent]:
        """Simulate political events for the current turn."""
        events = []
        
        # Generate random events based on probabilities
        for event_type, probability in self.event_probabilities.items():
            if random.random() < probability:
                event = self._generate_event(event_type)
                if event:
                    events.append(event)
                    self.recent_events.append(event.to_dict())
        
        # Apply events to simulation state
        for event in events:
            self._apply_event_effects(event)
        
        return events
    
    def _generate_event(self, event_type: str) -> PoliticalEvent:
        """Generate a specific type of political event."""
        event_id = f"{event_type}_{self.current_turn}_{int(time.time())}"
        timestamp = datetime.now()
        
        if event_type == "advisor_loyalty_change":
            advisor = random.choice(self.advisors)
            change = random.uniform(-0.2, 0.2)
            
            return PoliticalEvent(
                event_id=event_id,
                event_type=event_type,
                civilization_id="player_empire",
                title=f"{advisor.name}'s Loyalty Shifts",
                description=f"{advisor.name}'s loyalty has {'increased' if change > 0 else 'decreased'} due to recent political developments.",
                severity="moderate" if abs(change) > 0.1 else "minor",
                participants=[advisor.advisor_id],
                consequences={"loyalty_change": change},
                timestamp=timestamp
            )
        
        elif event_type == "advisor_conflict":
            advisor1, advisor2 = random.sample(self.advisors, 2)
            
            return PoliticalEvent(
                event_id=event_id,
                event_type=event_type,
                civilization_id="player_empire",
                title=f"Conflict Between {advisor1.name} and {advisor2.name}",
                description=f"A disagreement has emerged between {advisor1.name} and {advisor2.name} over policy direction.",
                severity="moderate",
                participants=[advisor1.advisor_id, advisor2.advisor_id],
                consequences={"relationship_damage": -0.1},
                timestamp=timestamp
            )
        
        elif event_type == "crisis_emergence":
            crisis_types = ["economic_downturn", "natural_disaster", "external_threat", "civil_unrest"]
            crisis_type = random.choice(crisis_types)
            
            return PoliticalEvent(
                event_id=event_id,
                event_type=event_type,
                civilization_id="player_empire",
                title=f"Crisis: {crisis_type.replace('_', ' ').title()}",
                description=f"A {crisis_type.replace('_', ' ')} has emerged, requiring immediate attention from the leadership.",
                severity="major",
                participants=[],
                consequences={"stability_impact": -0.1, "new_crisis": crisis_type},
                timestamp=timestamp
            )
        
        elif event_type == "conspiracy_discovered":
            conspirator = random.choice(self.advisors)
            
            return PoliticalEvent(
                event_id=event_id,
                event_type=event_type,
                civilization_id="player_empire",
                title="Conspiracy Uncovered",
                description=f"Intelligence reports suggest {conspirator.name} may be involved in plotting against the leadership.",
                severity="major",
                participants=[conspirator.advisor_id],
                consequences={"loyalty_impact": -0.3, "trust_damage": True},
                timestamp=timestamp
            )
        
        elif event_type == "diplomatic_incident":
            target_civ = random.choice(["northern_kingdom", "eastern_republic", "southern_alliance"])
            
            return PoliticalEvent(
                event_id=event_id,
                event_type=event_type,
                civilization_id="player_empire",
                title=f"Diplomatic Incident with {target_civ.replace('_', ' ').title()}",
                description=f"A diplomatic incident has occurred affecting relations with {target_civ.replace('_', ' ')}.",
                severity="moderate",
                participants=[],
                consequences={"diplomatic_impact": random.uniform(-0.2, -0.05)},
                timestamp=timestamp
            )
        
        return None
    
    def _apply_event_effects(self, event: PoliticalEvent):
        """Apply event effects to the simulation state."""
        consequences = event.consequences
        
        # Apply loyalty changes
        if "loyalty_change" in consequences:
            for advisor in self.advisors:
                if advisor.advisor_id in event.participants:
                    advisor.loyalty = max(0.0, min(1.0, advisor.loyalty + consequences["loyalty_change"]))
        
        # Apply relationship changes
        if "relationship_damage" in consequences and len(event.participants) >= 2:
            advisor1_id, advisor2_id = event.participants[:2]
            for advisor in self.advisors:
                if advisor.advisor_id == advisor1_id and advisor2_id in advisor.relationships:
                    advisor.relationships[advisor2_id] += consequences["relationship_damage"]
                    advisor.relationships[advisor2_id] = max(-1.0, min(1.0, advisor.relationships[advisor2_id]))
        
        # Apply stability impacts
        if "stability_impact" in consequences:
            for civ in self.civilizations:
                if civ.civilization_id == event.civilization_id:
                    civ.political_stability = max(0.0, min(1.0, civ.political_stability + consequences["stability_impact"]))
        
        # Add new crises
        if "new_crisis" in consequences:
            for civ in self.civilizations:
                if civ.civilization_id == event.civilization_id:
                    civ.active_crises.append(consequences["new_crisis"])
    
    def advance_turn(self):
        """Advance to the next turn."""
        self.current_turn += 1
        
        # Gradually evolve advisor states
        for advisor in self.advisors:
            # Small random changes to stress and mood
            advisor.stress_level += random.uniform(-0.05, 0.05)
            advisor.stress_level = max(0.0, min(1.0, advisor.stress_level))
            
            # Mood changes based on stress
            if advisor.stress_level > 0.7:
                advisor.current_mood = random.choice(["stressed", "anxious", "overwhelmed"])
            elif advisor.stress_level < 0.3:
                advisor.current_mood = random.choice(["calm", "confident", "optimistic"])
            else:
                advisor.current_mood = random.choice(["focused", "concerned", "determined"])
        
        self.logger.info(f"Advanced to turn {self.current_turn}")


async def run_demo_server():
    """Run the demo bridge server with simulated political events."""
    print("\n🏛️  POLITICAL STRATEGY GAME - BRIDGE SERVER DEMO 🏛️")
    print("="*65)
    print("Starting bridge server with simulated political events...")
    print("Connect with demo_client.py to see the bridge in action!")
    print("="*65)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create bridge manager
    bridge_manager = GameEngineBridgeManager(
        host="localhost",
        port=8888,
        auto_advance_turns=True,
        enable_performance_monitoring=True
    )
    
    # Create demo simulation
    simulation = DemoPoliticalSimulation()
    
    try:
        print("\n🚀 Starting bridge server...")
        await bridge_manager.start()
        
        print("✅ Bridge server started successfully!")
        print(f"🌐 WebSocket server running on ws://localhost:8888")
        print(f"📊 Performance monitoring: {'Enabled' if bridge_manager.enable_performance_monitoring else 'Disabled'}")
        print(f"⚡ Auto-advance turns: {'Enabled' if bridge_manager.auto_advance_turns else 'Disabled'}")
        
        # Setup event handlers
        def handle_player_decision(data):
            print(f"🎮 Player Decision: {data['decision']['type']}")
        
        def handle_turn_advanced(data):
            print(f"⏭️  Turn Advanced: {data['old_turn']} → {data['new_turn']}")
            
            # Generate new turn events
            events = simulation.simulate_turn_events()
            for event in events:
                bridge_manager.broadcast_political_event(event, EventPriority.NORMAL)
            
            # Update game state
            game_state = simulation.generate_game_state()
            bridge_manager.update_game_state(game_state)
            
            # Advance simulation
            simulation.advance_turn()
        
        bridge_manager.subscribe_to_event("player_decision", handle_player_decision)
        bridge_manager.subscribe_to_event("turn_advanced", handle_turn_advanced)
        
        # Start first turn
        print("\n🎯 Starting initial turn...")
        bridge_manager.start_new_turn(1)
        
        # Initial state and events
        initial_events = simulation.simulate_turn_events()
        for event in initial_events:
            bridge_manager.broadcast_political_event(event, EventPriority.NORMAL)
        
        initial_state = simulation.generate_game_state()
        bridge_manager.update_game_state(initial_state)
        
        print(f"📢 Generated {len(initial_events)} initial events")
        print("\n💡 The demo is running! You can now:")
        print("   1. Connect with: python -m src.bridge.demo_client")
        print("   2. Observe real-time political events")
        print("   3. See turn synchronization in action")
        print("   4. Monitor performance metrics")
        print("\n⏹️  Press Ctrl+C to stop the demo")
        
        # Demo event loop
        turn_interval = 30  # seconds per turn
        last_turn_time = time.time()
        
        while True:
            await asyncio.sleep(1)
            
            # Check for turn advancement
            current_time = time.time()
            if current_time - last_turn_time >= turn_interval:
                # Signal political engine ready for turn advancement
                bridge_manager.set_political_engine_ready(True)
                last_turn_time = current_time
                
                # Print status every few turns
                if simulation.current_turn % 3 == 0:
                    status = bridge_manager.get_bridge_status()
                    print(f"\n📊 Status - Turn: {simulation.current_turn}, "
                          f"Clients: {status['connected_clients']}, "
                          f"Events: {len(simulation.recent_events)}")
            
            # Occasionally generate random events between turns
            if random.random() < 0.1:  # 10% chance per second
                events = simulation.simulate_turn_events()
                for event in events[:2]:  # Limit to 2 events
                    bridge_manager.broadcast_political_event(event, EventPriority.LOW)
    
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo server error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🛑 Stopping bridge server...")
        await bridge_manager.stop()
        
        # Print final statistics
        if bridge_manager.performance_profiler:
            summary = bridge_manager.performance_profiler.get_performance_summary()
            print(f"\n📈 Final Performance Summary:")
            print(f"   Turns Processed: {len(bridge_manager.performance_profiler.turn_profiles)}")
            print(f"   Total Events: {len(simulation.recent_events)}")
            print(f"   Active Alerts: {summary.get('active_alerts', 0)}")
        
        print("✨ Demo server stopped successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(run_demo_server())
    except KeyboardInterrupt:
        print("\n👋 Bridge server demo shutting down...")
    
    print("\n🎉 Thanks for trying the Political Strategy Game Bridge Demo!")
