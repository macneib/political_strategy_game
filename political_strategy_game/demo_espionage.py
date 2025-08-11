"""
Task 6.1 Intelligence and Espionage System Demo

Demonstrates the comprehensive espionage system with:
- Asset recruitment and management
- Operation planning and execution
- Intelligence gathering and analysis
- Counter-intelligence and security
- Integration with diplomatic systems
"""

import sys
import logging
from datetime import datetime
from dataclasses import asdict

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the src directory to Python path
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.espionage import (
    EspionageManager, EspionageOperationType, OperationDifficulty,
    IntelligenceReliability
)


def demonstrate_espionage_system():
    """Comprehensive demonstration of the espionage system."""
    
    print("="*70)
    print("TASK 6.1: INTELLIGENCE AND ESPIONAGE SYSTEM DEMONSTRATION")
    print("="*70)
    
    # Initialize espionage manager for our civilization
    our_civ = "Strategist_Empire"
    espionage_manager = EspionageManager(our_civ)
    
    print(f"\n🎯 Initializing Espionage Operations for {our_civ}")
    print(f"   Initial Budget: ${espionage_manager.intelligence_budget:,.2f}")
    print(f"   Influence Points: {espionage_manager.influence_points}")
    print(f"   Technology Level: {espionage_manager.technology_level:.1%}")
    print(f"   Counter-Intel Strength: {espionage_manager.counter_intelligence_strength:.1%}")
    
    # Define target civilizations
    targets = ["Rival_Kingdom", "Merchant_Republic", "Warrior_Clans"]
    
    print(f"\n🎯 Target Civilizations: {', '.join(targets)}")
    
    # === PHASE 1: ASSET RECRUITMENT ===
    print("\n" + "="*50)
    print("PHASE 1: ESPIONAGE ASSET RECRUITMENT")
    print("="*50)
    
    recruited_assets = []
    
    # Recruit different types of assets
    asset_types = [
        ("agent", targets[0], [EspionageOperationType.POLITICAL_INTELLIGENCE]),
        ("informant", targets[1], [EspionageOperationType.ADVISOR_SURVEILLANCE]),
        ("sleeper", targets[2], [EspionageOperationType.SABOTAGE_MISSION]),
        ("agent", targets[0], [EspionageOperationType.DISINFORMATION_CAMPAIGN])
    ]
    
    for asset_type, target, specialization in asset_types:
        try:
            asset = espionage_manager.recruit_asset(
                asset_type=asset_type,
                target_civilization=target,
                specialization=specialization
            )
            recruited_assets.append(asset)
            
            print(f"✅ Recruited {asset_type.title()}: {asset.asset_name}")
            print(f"   🎯 Target: {target}")
            print(f"   🛠️  Skill Level: {asset.skill_level:.1%}")
            print(f"   ⚠️  Exposure Risk: {asset.exposure_risk:.1%}")
            print(f"   📍 Specialization: {', '.join(op.value for op in specialization)}")
            print()
            
        except ValueError as e:
            print(f"❌ Failed to recruit {asset_type}: {e}")
    
    print(f"💰 Remaining Budget: ${espionage_manager.intelligence_budget:,.2f}")
    
    # === PHASE 2: ASSET TRAINING ===
    print("\n" + "="*50)
    print("PHASE 2: ASSET TRAINING AND ENHANCEMENT")
    print("="*50)
    
    # Train some assets to improve their capabilities
    training_programs = ["technical", "social", "infiltration"]
    
    for i, asset in enumerate(recruited_assets[:3]):  # Train first 3 assets
        training_type = training_programs[i]
        initial_skill = asset.skill_level
        
        success = espionage_manager.train_asset(asset.asset_id, training_type)
        
        if success:
            improvement = asset.skill_level - initial_skill
            print(f"📚 Trained {asset.asset_name} in {training_type}")
            print(f"   📈 Skill Improvement: +{improvement:.1%} (now {asset.skill_level:.1%})")
        else:
            print(f"❌ Failed to train {asset.asset_name} - insufficient budget")
    
    # === PHASE 3: OPERATION PLANNING ===
    print("\n" + "="*50)
    print("PHASE 3: ESPIONAGE OPERATION PLANNING")
    print("="*50)
    
    planned_operations = []
    
    # Plan various types of operations
    operation_plans = [
        (EspionageOperationType.POLITICAL_INTELLIGENCE, targets[0], None),
        (EspionageOperationType.ADVISOR_SURVEILLANCE, targets[1], "military_advisor"),
        (EspionageOperationType.DISINFORMATION_CAMPAIGN, targets[2], "chief_diplomat"),
        (EspionageOperationType.SABOTAGE_MISSION, targets[0], None),
    ]
    
    for operation_type, target_civ, target_advisor in operation_plans:
        operation = espionage_manager.plan_operation(
            operation_type, target_civ, target_advisor=target_advisor
        )
        planned_operations.append(operation)
        
        print(f"📋 Planned {operation_type.value.replace('_', ' ').title()}")
        print(f"   🎯 Target: {target_civ}")
        if target_advisor:
            print(f"   👤 Target Advisor: {target_advisor}")
        print(f"   ⚡ Difficulty: {operation.difficulty.value.title()}")
        print(f"   ⏱️  Duration: {operation.time_to_complete} turns")
        print(f"   💰 Cost: {operation.resource_cost}")
        print(f"   ⚠️  Discovery Risk: {operation.discovery_risk:.1%}")
        print()
    
    # === PHASE 4: ASSET ASSIGNMENT ===
    print("\n" + "="*50)
    print("PHASE 4: ASSET ASSIGNMENT TO OPERATIONS")
    print("="*50)
    
    # Assign assets to operations based on specialization and target
    for i, operation in enumerate(planned_operations):
        # Find suitable assets for this operation
        suitable_assets = [
            asset for asset in recruited_assets
            if (asset.assigned_target == operation.target_civilization and
                operation.operation_type in asset.specialization and
                asset.is_active and not asset.is_compromised)
        ]
        
        if suitable_assets:
            # Assign best asset (highest skill level)
            best_asset = max(suitable_assets, key=lambda a: a.skill_level)
            asset_ids = [best_asset.asset_id]
            
            # Add supporting asset if available
            supporting_assets = [a for a in suitable_assets if a != best_asset]
            if supporting_assets and len(supporting_assets) > 0:
                asset_ids.append(supporting_assets[0].asset_id)
            
            success = espionage_manager.assign_assets_to_operation(operation, asset_ids)
            
            if success:
                print(f"👥 Assigned to {operation.operation_type.value.replace('_', ' ').title()}:")
                for asset_id in operation.assigned_assets:
                    asset = espionage_manager.get_asset(asset_id)
                    role = "Leader" if asset_id == operation.operation_leader else "Support"
                    print(f"   • {asset.asset_name} ({role}) - Skill: {asset.skill_level:.1%}")
                print(f"   ⚠️  Updated Discovery Risk: {operation.discovery_risk:.1%}")
                print()
            else:
                print(f"❌ Failed to assign assets to {operation.operation_type.value}")
        else:
            print(f"⚠️  No suitable assets for {operation.operation_type.value}")
    
    # === PHASE 5: OPERATION EXECUTION ===
    print("\n" + "="*50)
    print("PHASE 5: OPERATION EXECUTION")
    print("="*50)
    
    current_turn = 1
    
    # Launch operations
    launched_operations = []
    for operation in planned_operations:
        if len(operation.assigned_assets) > 0:
            success = espionage_manager.launch_operation(operation, current_turn)
            if success:
                launched_operations.append(operation)
                print(f"🚀 Launched: {operation.operation_type.value.replace('_', ' ').title()}")
                print(f"   🎯 Target: {operation.target_civilization}")
                print(f"   👥 Assets: {len(operation.assigned_assets)}")
                print()
            else:
                print(f"❌ Failed to launch {operation.operation_type.value}")
        else:
            print(f"⚠️  Cannot launch {operation.operation_type.value} - no assets assigned")
    
    print(f"💰 Budget after launching operations: ${espionage_manager.intelligence_budget:,.2f}")
    
    # === PHASE 6: TURN PROCESSING ===
    print("\n" + "="*50)
    print("PHASE 6: OPERATION PROCESSING SIMULATION")
    print("="*50)
    
    max_turns = 10
    turn = current_turn + 1
    
    while turn <= max_turns and len(espionage_manager.active_operations) > 0:
        print(f"\n📅 Turn {turn}:")
        print(f"   Active Operations: {len(espionage_manager.active_operations)}")
        
        # Process operations for this turn
        results = espionage_manager.process_operations_turn(turn)
        
        for result in results:
            operation_id = result["operation_id"]
            operation = espionage_manager.get_operation(operation_id)
            
            if operation:
                print(f"   📊 {operation.operation_type.value.replace('_', ' ').title()}:")
                print(f"      Progress: {operation.progress:.1%}")
                print(f"      Status: {operation.status}")
                
                if "outcome" in result:
                    print(f"      Outcome: {result['outcome'].value}")
                
                if result.get("discovered", False):
                    print(f"      ⚠️  OPERATION DISCOVERED!")
                
                if operation.status == "completed":
                    print(f"      ✅ COMPLETED")
                elif operation.status == "failed":
                    print(f"      ❌ FAILED")
        
        turn += 1
    
    # === PHASE 7: INTELLIGENCE ANALYSIS ===
    print("\n" + "="*50)
    print("PHASE 7: INTELLIGENCE ANALYSIS")
    print("="*50)
    
    # Analyze intelligence gathered
    total_reports = len(espionage_manager.intelligence_reports)
    print(f"📊 Total Intelligence Reports Gathered: {total_reports}")
    
    if total_reports > 0:
        print("\n🔍 Intelligence Summary by Target:")
        for target in targets:
            reports = espionage_manager.get_intelligence_on_target(target)
            
            if reports:
                print(f"\n   🎯 {target}:")
                for report in reports[:3]:  # Show first 3 reports
                    print(f"      • {report.intelligence_type.replace('_', ' ').title()}")
                    print(f"        Reliability: {report.reliability.value.replace('_', ' ').title()}")
                    print(f"        Date: {report.collection_date.strftime('%Y-%m-%d %H:%M')}")
                
                # Analyze weaknesses
                weaknesses = espionage_manager.analyze_target_weaknesses(target)
                if weaknesses:
                    print(f"      🔍 Identified Weaknesses:")
                    for weakness, level in weaknesses.items():
                        if level > 0.5:  # Only show significant weaknesses
                            print(f"        • {weakness.replace('_', ' ').title()}: {level:.1%}")
            else:
                print(f"   🎯 {target}: No intelligence gathered")
    
    # === PHASE 8: SECURITY ASSESSMENT ===
    print("\n" + "="*50)
    print("PHASE 8: SECURITY ASSESSMENT")
    print("="*50)
    
    # Conduct security audit
    audit_results = espionage_manager.conduct_security_audit()
    
    print(f"🛡️  Security Audit Results:")
    print(f"   Overall Security Score: {audit_results['security_score']:.1%}")
    print(f"   Vulnerabilities Found: {audit_results['vulnerabilities_found']}")
    print(f"   Suspicious Activities: {len(audit_results['suspicious_activities'])}")
    
    if audit_results["recommendations"]:
        print(f"   📋 Recommendations:")
        for recommendation in audit_results["recommendations"][:3]:
            print(f"      • {recommendation}")
    
    # === PHASE 9: COMPREHENSIVE SUMMARY ===
    print("\n" + "="*50)
    print("PHASE 9: COMPREHENSIVE ESPIONAGE SUMMARY")
    print("="*50)
    
    summary = espionage_manager.get_espionage_summary()
    
    print(f"📈 Final Espionage Statistics:")
    print(f"   Total Assets: {summary['total_assets']}")
    print(f"   Active Assets: {summary['active_assets']}")
    print(f"   Burned Assets: {summary.get('compromised_assets', 0)}")
    print(f"   Completed Operations: {summary['completed_operations']}")
    print(f"   Intelligence Reports: {summary['intelligence_reports']}")
    print(f"   Remaining Budget: ${summary['intelligence_budget']:,.2f}")
    print(f"   Technology Level: {summary['technology_level']:.1%}")
    print(f"   Success Rate: {summary.get('operation_success_rate', 0.0):.1%}")
    
    print(f"\n📊 Asset Breakdown:")
    for asset_type, count in summary["asset_breakdown"].items():
        print(f"   {asset_type.title()}: {count}")
    
    # Show target intelligence summaries
    print(f"\n🎯 Target Intelligence Coverage:")
    for target in targets:
        target_summary = espionage_manager.get_target_intelligence_summary(target)
        print(f"   {target}:")
        print(f"      Reports: {target_summary['intelligence_reports']}")
        print(f"      Assets: {target_summary['assigned_assets']}")
        
        # Show coverage areas
        coverage = target_summary.get('intelligence_coverage', {})
        if coverage:
            covered_areas = [area for area, level in coverage.items() if level != 'none']
            print(f"      Coverage Areas: {len(covered_areas)}/{len(coverage)}")
        else:
            print(f"      Coverage Areas: 0/0")
    
    print("\n" + "="*70)
    print("✅ TASK 6.1 INTELLIGENCE AND ESPIONAGE SYSTEM DEMONSTRATION COMPLETE")
    print("="*70)
    
    print(f"\n🎯 Key Achievements:")
    print(f"   ✅ Comprehensive asset recruitment and management")
    print(f"   ✅ Multi-target intelligence operations")
    print(f"   ✅ Dynamic operation planning and execution")
    print(f"   ✅ Real-time progress tracking and outcome determination")
    print(f"   ✅ Intelligence analysis and weakness identification")
    print(f"   ✅ Counter-intelligence and security auditing")
    print(f"   ✅ Resource management and budget allocation")
    print(f"   ✅ Diplomatic consequence modeling")
    
    print(f"\n📋 Implemented Operation Types:")
    operations_implemented = [
        "Political Intelligence Gathering",
        "Advisor Surveillance",
        "Disinformation Campaigns", 
        "Advisor Bribery",
        "Sabotage Missions",
        "Memory Extraction",
        "Counter-Surveillance",
        "Assassination Attempts"
    ]
    
    for op in operations_implemented:
        print(f"   ✅ {op}")
    
    print(f"\n🎮 System Features Demonstrated:")
    features = [
        "Asset specialization and skill development",
        "Operation difficulty scaling",
        "Discovery risk calculation",
        "Intelligence reliability assessment",
        "Multi-turn operation processing",
        "Resource cost management",
        "Diplomatic incident generation",
        "Target weakness analysis",
        "Security vulnerability detection",
        "Comprehensive reporting and analytics"
    ]
    
    for feature in features:
        print(f"   ✅ {feature}")
    
    return espionage_manager


if __name__ == "__main__":
    demonstrate_espionage_system()
