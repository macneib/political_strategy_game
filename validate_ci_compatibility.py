#!/usr/bin/env python3
"""
CI Compatibility Validation Script

This script validates all the constructor patterns and import paths
that are used in the GitHub Actions CI workflows to ensure they work correctly.
"""

import sys
import time
import traceback

def test_basic_imports():
    """Test that all core imports work correctly."""
    print("Testing basic imports...")
    try:
        # Import from the correct path for CI compatibility
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'political_strategy_game'))
        
        from src.core.civilization import Civilization
        from src.core.leader import Leader, LeadershipStyle
        from src.core.advisor import PersonalityProfile
        from src.llm.advisors import AdvisorPersonality
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_civilization_creation():
    """Test civilization creation with proper constructor."""
    print("Testing civilization creation...")
    try:
        from src.core.civilization import Civilization
        from src.core.leader import Leader, LeadershipStyle
        from src.core.advisor import PersonalityProfile
        
        # Create personality profile
        personality = PersonalityProfile(
            ambition=0.7, loyalty=0.8, cunning=0.5, wisdom=0.6,
            aggression=0.4, caution=0.7, charisma=0.8, integrity=0.9
        )
        
        # Create leader
        leader = Leader(
            name='Test Leader',
            civilization_id='test_empire',
            personality=personality,
            leadership_style=LeadershipStyle.COLLABORATIVE
        )
        
        # Create civilization - this is the critical test
        civ = Civilization(name='Test Empire', leader=leader)
        
        print(f"✅ Civilization created: {civ.name}")
        return True
    except Exception as e:
        print(f"❌ Civilization creation failed: {e}")
        traceback.print_exc()
        return False

def test_multiple_civilizations():
    """Test creating multiple civilizations as done in CI benchmarks."""
    print("Testing multiple civilization creation...")
    try:
        from src.core.civilization import Civilization
        from src.core.leader import Leader, LeadershipStyle
        from src.core.advisor import PersonalityProfile
        
        civs = []
        for i in range(5):
            personality = PersonalityProfile(
                ambition=0.7, loyalty=0.8, cunning=0.5, wisdom=0.6,
                aggression=0.4, caution=0.7, charisma=0.8, integrity=0.9
            )
            
            leader = Leader(
                name=f'Leader_{i}',
                civilization_id=f'empire_{i}',
                personality=personality,
                leadership_style=LeadershipStyle.COLLABORATIVE
            )
            
            civ = Civilization(name=f'Empire_{i}', leader=leader)
            civs.append(civ)
        
        print(f"✅ Created {len(civs)} civilizations successfully")
        return True
    except Exception as e:
        print(f"❌ Multiple civilization creation failed: {e}")
        traceback.print_exc()
        return False

def test_advisor_integration():
    """Test advisor integration as used in CI workflows."""
    print("Testing advisor integration...")
    try:
        from src.core.civilization import Civilization
        from src.core.leader import Leader, LeadershipStyle
        from src.core.advisor import PersonalityProfile
        from src.llm.advisors import AdvisorPersonality, AdvisorRole
        
        # Create test civilization
        personality = PersonalityProfile(
            ambition=0.7, loyalty=0.8, cunning=0.5, wisdom=0.6,
            aggression=0.4, caution=0.7, charisma=0.8, integrity=0.9
        )
        
        leader = Leader(
            name='Integration Test Leader',
            civilization_id='integration_test_empire',
            personality=personality,
            leadership_style=LeadershipStyle.COLLABORATIVE
        )
        
        civ = Civilization(name='Integration Test Empire', leader=leader)
        
        # Test advisor creation
        advisor_personality = AdvisorPersonality(
            name="Test Advisor",
            role=AdvisorRole.MILITARY,
            personality_traits=["Direct", "Pragmatic"],
            communication_style="Military precision",
            expertise_areas=["Strategy", "Defense"],
            background="Test advisor background"
        )
        
        print("✅ Advisor integration successful")
        return True
    except Exception as e:
        print(f"❌ Advisor integration failed: {e}")
        traceback.print_exc()
        return False

def test_performance_benchmark():
    """Test the performance benchmark pattern used in CI."""
    print("Testing performance benchmark pattern...")
    try:
        from src.core.civilization import Civilization
        from src.core.leader import Leader, LeadershipStyle
        from src.core.advisor import PersonalityProfile
        
        start = time.time()
        civs = []
        for i in range(10):
            personality = PersonalityProfile(
                ambition=0.7, loyalty=0.8, cunning=0.5, wisdom=0.6,
                aggression=0.4, caution=0.7, charisma=0.8, integrity=0.9
            )
            
            leader = Leader(
                name=f'Leader_{i}',
                civilization_id=f'empire_{i}',
                personality=personality,
                leadership_style=LeadershipStyle.COLLABORATIVE
            )
            
            civ = Civilization(name=f'Empire_{i}', leader=leader)
            civs.append(civ)
        
        creation_time = time.time() - start
        print(f"✅ Performance benchmark: Created 10 civilizations in {creation_time:.3f}s")
        
        # Test summary generation
        start = time.time()
        for civ in civs:
            summary = civ.get_diplomatic_summary()
        
        processing_time = time.time() - start
        print(f"✅ Generated 10 summaries in {processing_time:.3f}s")
        
        return True
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all CI compatibility tests."""
    print("=== CI Compatibility Validation ===")
    print()
    
    tests = [
        test_basic_imports,
        test_civilization_creation,
        test_multiple_civilizations,
        test_advisor_integration,
        test_performance_benchmark
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()
            print()
    
    print("=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All CI compatibility tests passed!")
        return 0
    else:
        print("⚠️  Some CI compatibility tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
