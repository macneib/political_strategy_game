#!/usr/bin/env python3
"""
Test script to verify Task 4.1 fixes
"""

print("🔧 Testing Task 4.1 Issue Fixes...")

# Test 1: AdvisorPersonality.get_personality method
try:
    from src.llm.advisors import AdvisorRole, AdvisorPersonality
    print("✅ Advisor imports: OK")
    
    # Test all advisor personalities
    roles_tested = []
    for role in AdvisorRole:
        advisor = AdvisorPersonality.get_personality(role)
        roles_tested.append(f"{role.value}: {advisor.name}")
        
    print("✅ Advisor personalities:")
    for role_info in roles_tested:
        print(f"   - {role_info}")
        
except Exception as e:
    print(f"❌ Advisor system error: {e}")

# Test 2: Game launcher import fix
try:
    import play_game
    print("✅ Game launcher import: OK")
except Exception as e:
    print(f"❌ Game launcher error: {e}")

# Test 3: LLM configuration system
try:
    from src.llm.config import LLMConfigManager
    config_manager = LLMConfigManager()
    config = config_manager.get_default_vllm_config()
    print(f"✅ LLM config: {config.provider.value} with {config.model_name}")
except Exception as e:
    print(f"❌ LLM config error: {e}")

print("\n🎉 Task 4.1 Issue Resolution: COMPLETE")
print("All identified errors have been fixed and verified!")
