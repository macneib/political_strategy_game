#!/usr/bin/env python3
"""Debug coup risk detection."""

import sys
from pathlib import Path
import tempfile

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.memory import MemoryManager
from core.advisor_enhanced import AdvisorWithMemory, AdvisorCouncil
from core.advisor import AdvisorRole, PersonalityProfile

def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        memory_manager = MemoryManager(Path(temp_dir))
        council = AdvisorCouncil(civilization_id="test_civ")
        council.set_memory_manager(memory_manager)
        
        # Create high-risk advisors
        advisor1 = AdvisorWithMemory(
            name="Disloyal General",
            role=AdvisorRole.MILITARY,
            civilization_id="test_civ",
            personality=PersonalityProfile(
                ambition=0.9,
                loyalty=0.1,
                paranoia=0.8
            )
        )
        advisor1.loyalty_to_leader = 0.1
        advisor1.influence = 0.2
        
        advisor2 = AdvisorWithMemory(
            name="Plotting Spymaster",
            role=AdvisorRole.SECURITY,
            civilization_id="test_civ",
            personality=PersonalityProfile(
                ambition=0.8,
                loyalty=0.2,
                paranoia=0.6
            )
        )
        advisor2.loyalty_to_leader = 0.2
        advisor2.influence = 0.3
        
        # Create relationship between conspirators
        relationship = advisor1.get_relationship(advisor2.id)
        relationship.trust = 0.8
        relationship.conspiracy_level = 0.7
        
        council.add_advisor(advisor1)
        council.add_advisor(advisor2)
        
        # Check individual motivations
        print(f"Advisor 1 coup motivation: {advisor1.calculate_coup_motivation():.3f}")
        print(f"Advisor 2 coup motivation: {advisor2.calculate_coup_motivation():.3f}")
        
        # Check relationship
        print(f"Relationship trust: {relationship.trust}")
        print(f"Relationship conspiracy: {relationship.conspiracy_level}")
        
        # Assess coup risk
        risk_assessment = council.detect_coup_risk()
        print(f"\nRisk assessment: {risk_assessment}")

if __name__ == "__main__":
    main()
