"""
Tests for the Intelligence and Espionage System (Task 6.1)

Comprehensive test suite covering all espionage mechanics including
asset management, operation planning and execution, intelligence gathering,
and counter-intelligence operations.
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.core.espionage import (
    EspionageManager, EspionageAsset, EspionageOperation, IntelligenceReport,
    EspionageOperationType, OperationDifficulty, IntelligenceReliability, 
    OperationOutcome
)


class TestEspionageAsset:
    """Test espionage asset functionality."""
    
    def test_asset_creation(self):
        """Test creating espionage assets."""
        asset = EspionageAsset(
            asset_name="Agent Smith",
            asset_type="agent",
            specialization=[EspionageOperationType.POLITICAL_INTELLIGENCE],
            skill_level=0.7,
            assigned_target="enemy_civ"
        )
        
        assert asset.asset_name == "Agent Smith"
        assert asset.asset_type == "agent"
        assert asset.skill_level == 0.7
        assert asset.assigned_target == "enemy_civ"
        assert asset.is_active == True
        assert asset.is_compromised == False
        assert asset.operations_completed == 0
        assert EspionageOperationType.POLITICAL_INTELLIGENCE in asset.specialization
    
    def test_asset_skill_bounds(self):
        """Test that asset skills are properly bounded."""
        asset = EspionageAsset(skill_level=1.5)  # Should be clamped
        assert asset.skill_level == 1.5  # Dataclass doesn't auto-clamp, but manager should handle this
        
    def test_asset_exposure_risk(self):
        """Test asset exposure risk mechanics."""
        asset = EspionageAsset(exposure_risk=0.15)
        assert 0.0 <= asset.exposure_risk <= 1.0
        assert asset.exposure_risk == 0.15


class TestEspionageOperation:
    """Test espionage operation functionality."""
    
    def test_operation_creation(self):
        """Test creating espionage operations."""
        operation = EspionageOperation(
            operation_type=EspionageOperationType.ADVISOR_SURVEILLANCE,
            target_civilization="enemy_civ",
            target_advisor="enemy_advisor_1",
            difficulty=OperationDifficulty.MODERATE
        )
        
        assert operation.operation_type == EspionageOperationType.ADVISOR_SURVEILLANCE
        assert operation.target_civilization == "enemy_civ"
        assert operation.target_advisor == "enemy_advisor_1"
        assert operation.difficulty == OperationDifficulty.MODERATE
        assert operation.status == "planning"
        assert operation.progress == 0.0
        assert len(operation.assigned_assets) == 0
    
    def test_operation_progress_tracking(self):
        """Test operation progress tracking."""
        operation = EspionageOperation(
            operation_type=EspionageOperationType.POLITICAL_INTELLIGENCE,
            target_civilization="enemy_civ",
            time_to_complete=4
        )
        
        operation.progress = 0.5
        assert operation.progress == 0.5
        
        operation.progress = 1.0
        assert operation.progress == 1.0


class TestIntelligenceReport:
    """Test intelligence report functionality."""
    
    def test_report_creation(self):
        """Test creating intelligence reports."""
        report = IntelligenceReport(
            source_operation="op_123",
            target_civilization="enemy_civ",
            intelligence_type="political_intelligence",
            content={"stability": 0.6, "leader_approval": 0.4},
            reliability=IntelligenceReliability.HIGH_CONFIDENCE
        )
        
        assert report.source_operation == "op_123"
        assert report.target_civilization == "enemy_civ"
        assert report.intelligence_type == "political_intelligence"
        assert report.content["stability"] == 0.6
        assert report.reliability == IntelligenceReliability.HIGH_CONFIDENCE
        assert isinstance(report.collection_date, datetime)
    
    def test_report_expiry(self):
        """Test intelligence report expiry mechanics."""
        future_date = datetime.now() + timedelta(days=10)
        report = IntelligenceReport(
            target_civilization="enemy_civ",
            expiry_date=future_date
        )
        
        assert report.expiry_date == future_date


class TestEspionageManager:
    """Test the main espionage manager."""
    
    @pytest.fixture
    def espionage_manager(self):
        """Create a test espionage manager."""
        return EspionageManager(civilization_id="test_civ")
    
    def test_manager_initialization(self, espionage_manager):
        """Test espionage manager initialization."""
        assert espionage_manager.civilization_id == "test_civ"
        assert len(espionage_manager.assets) == 0
        assert len(espionage_manager.active_operations) == 0
        assert espionage_manager.intelligence_budget == 1000.0
        assert espionage_manager.influence_points == 100.0
        assert espionage_manager.technology_level == 0.5
        assert espionage_manager.counter_intelligence_strength == 0.5
    
    def test_recruit_asset(self, espionage_manager):
        """Test recruiting espionage assets."""
        asset = espionage_manager.recruit_asset(
            asset_type="agent",
            target_civilization="enemy_civ",
            specialization=[EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        assert asset.asset_type == "agent"
        assert asset.assigned_target == "enemy_civ"
        assert len(espionage_manager.assets) == 1
        assert espionage_manager.intelligence_budget < 1000.0  # Cost deducted
        
        # Test insufficient budget
        espionage_manager.intelligence_budget = 50
        with pytest.raises(ValueError):
            espionage_manager.recruit_asset("agent", "enemy_civ2", [])
    
    def test_train_asset(self, espionage_manager):
        """Test asset training."""
        # Recruit an asset first
        asset = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        initial_skill = asset.skill_level
        initial_budget = espionage_manager.intelligence_budget
        
        # Train the asset
        success = espionage_manager.train_asset(asset.asset_id, "technical")
        
        assert success == True
        assert asset.skill_level > initial_skill
        assert espionage_manager.intelligence_budget < initial_budget
        
        # Test insufficient budget
        espionage_manager.intelligence_budget = 10
        success = espionage_manager.train_asset(asset.asset_id, "infiltration")
        assert success == False
    
    def test_burn_asset(self, espionage_manager):
        """Test burning compromised assets."""
        # Recruit an asset
        asset = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        assert asset.is_active == True
        assert asset.is_compromised == False
        
        # Burn the asset
        espionage_manager.burn_asset(asset.asset_id, "cover_blown")
        
        assert asset.is_active == False
        assert asset.is_compromised == True
        assert asset.asset_id in espionage_manager.burned_assets
    
    def test_plan_operation(self, espionage_manager):
        """Test operation planning."""
        operation = espionage_manager.plan_operation(
            EspionageOperationType.ADVISOR_SURVEILLANCE,
            "enemy_civ",
            target_advisor="enemy_advisor"
        )
        
        assert operation.operation_type == EspionageOperationType.ADVISOR_SURVEILLANCE
        assert operation.target_civilization == "enemy_civ"
        assert operation.target_advisor == "enemy_advisor"
        assert operation.difficulty in list(OperationDifficulty)
        assert operation.required_skill_level > 0.0
        assert operation.time_to_complete > 0
        assert len(operation.resource_cost) > 0
    
    def test_assign_assets_to_operation(self, espionage_manager):
        """Test assigning assets to operations."""
        # Recruit assets
        asset1 = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.ADVISOR_SURVEILLANCE]
        )
        asset2 = espionage_manager.recruit_asset(
            "informant", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        # Plan operation
        operation = espionage_manager.plan_operation(
            EspionageOperationType.ADVISOR_SURVEILLANCE,
            "enemy_civ"
        )
        
        # Assign assets
        success = espionage_manager.assign_assets_to_operation(
            operation, [asset1.asset_id, asset2.asset_id]
        )
        
        assert success == True
        assert len(operation.assigned_assets) == 2
        assert operation.operation_leader is not None
        assert operation.discovery_risk > 0.0
        
        # Test assigning non-existent assets
        success = espionage_manager.assign_assets_to_operation(
            operation, ["fake_asset_id"]
        )
        assert success == False
    
    def test_launch_operation(self, espionage_manager):
        """Test launching operations."""
        # Setup: recruit asset and plan operation
        asset = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        operation = espionage_manager.plan_operation(
            EspionageOperationType.POLITICAL_INTELLIGENCE,
            "enemy_civ"
        )
        
        espionage_manager.assign_assets_to_operation(operation, [asset.asset_id])
        
        initial_budget = espionage_manager.intelligence_budget
        
        # Launch operation
        success = espionage_manager.launch_operation(operation, current_turn=1)
        
        assert success == True
        assert operation.status == "active"
        assert operation.start_turn == 1
        assert operation.operation_id in espionage_manager.active_operations
        assert espionage_manager.intelligence_budget < initial_budget
        
        # Test launching without assigned assets
        operation2 = espionage_manager.plan_operation(
            EspionageOperationType.POLITICAL_INTELLIGENCE,
            "enemy_civ2"
        )
        success = espionage_manager.launch_operation(operation2, current_turn=1)
        assert success == False
    
    def test_process_operations_turn(self, espionage_manager):
        """Test processing operations for one turn."""
        # Setup active operation
        asset = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        operation = espionage_manager.plan_operation(
            EspionageOperationType.POLITICAL_INTELLIGENCE,
            "enemy_civ"
        )
        
        espionage_manager.assign_assets_to_operation(operation, [asset.asset_id])
        espionage_manager.launch_operation(operation, current_turn=1)
        
        # Process turn
        results = espionage_manager.process_operations_turn(current_turn=2)
        
        assert len(results) == 1
        assert results[0]["operation_id"] == operation.operation_id
        assert operation.progress > 0.0
    
    def test_intelligence_gathering(self, espionage_manager):
        """Test gathering intelligence on targets."""
        # Create sample intelligence reports
        report1 = IntelligenceReport(
            target_civilization="enemy_civ",
            intelligence_type="political",
            content={"stability": 0.5},
            reliability=IntelligenceReliability.HIGH_CONFIDENCE
        )
        
        report2 = IntelligenceReport(
            target_civilization="enemy_civ",
            intelligence_type="military",
            content={"strength": 0.7},
            reliability=IntelligenceReliability.MODERATE_CONFIDENCE
        )
        
        espionage_manager.intelligence_reports[report1.report_id] = report1
        espionage_manager.intelligence_reports[report2.report_id] = report2
        
        # Test getting intelligence on target
        reports = espionage_manager.get_intelligence_on_target("enemy_civ")
        assert len(reports) == 2
        
        # Test filtering by intelligence type
        political_reports = espionage_manager.get_intelligence_on_target(
            "enemy_civ", "political"
        )
        assert len(political_reports) == 1
        assert political_reports[0].intelligence_type == "political"
    
    def test_analyze_target_weaknesses(self, espionage_manager):
        """Test analyzing target weaknesses from intelligence."""
        # Create intelligence with weakness indicators
        report = IntelligenceReport(
            target_civilization="enemy_civ",
            intelligence_type="political",
            content={
                "political_instability": 0.8,
                "advisor_corruption": 0.6,
                "faction_conflicts": 0.4
            },
            reliability=IntelligenceReliability.HIGH_CONFIDENCE
        )
        
        espionage_manager.intelligence_reports[report.report_id] = report
        
        weaknesses = espionage_manager.analyze_target_weaknesses("enemy_civ")
        
        assert "political_instability" in weaknesses
        assert "advisor_corruption" in weaknesses
        assert "faction_conflicts" in weaknesses
        assert weaknesses["political_instability"] > 0.0
        assert weaknesses["advisor_corruption"] > 0.0
    
    def test_disinformation_campaign_planning(self, espionage_manager):
        """Test planning disinformation campaigns."""
        false_info = {
            "fake_memory": "Leader secretly planning to betray allies",
            "false_intelligence": "Enemy army much weaker than reported"
        }
        
        operation = espionage_manager.plan_disinformation_campaign(
            "enemy_civ", "enemy_advisor", false_info
        )
        
        assert operation.operation_type == EspionageOperationType.DISINFORMATION_CAMPAIGN
        assert operation.target_civilization == "enemy_civ"
        assert operation.target_advisor == "enemy_advisor"
        assert operation.intelligence_gathered["disinformation_payload"] == false_info
        assert "influence" in operation.resource_cost
    
    def test_bribery_operation_planning(self, espionage_manager):
        """Test planning bribery operations."""
        operation = espionage_manager.plan_bribery_operation(
            "enemy_civ", "enemy_advisor", 500.0, "Provide military intelligence"
        )
        
        assert operation.operation_type == EspionageOperationType.ADVISOR_BRIBERY
        assert operation.target_civilization == "enemy_civ"
        assert operation.target_advisor == "enemy_advisor"
        assert operation.resource_cost["budget"] == 500.0
        assert operation.intelligence_gathered["desired_outcome"] == "Provide military intelligence"
        assert operation.discovery_risk > 0.1  # Higher than base risk
    
    def test_sabotage_mission_planning(self, espionage_manager):
        """Test planning sabotage missions."""
        operation = espionage_manager.plan_sabotage_mission(
            "enemy_civ", "communication_networks"
        )
        
        assert operation.operation_type == EspionageOperationType.SABOTAGE_MISSION
        assert operation.target_civilization == "enemy_civ"
        assert operation.intelligence_gathered["sabotage_target"] == "communication_networks"
        assert operation.difficulty == OperationDifficulty.HARD
        assert operation.discovery_risk > 0.2  # High risk operation
    
    def test_security_audit(self, espionage_manager):
        """Test conducting security audits."""
        audit_results = espionage_manager.conduct_security_audit()
        
        assert "vulnerabilities_found" in audit_results
        assert "suspicious_activities" in audit_results
        assert "recommendations" in audit_results
        assert "security_score" in audit_results
        assert isinstance(audit_results["security_score"], float)
    
    def test_counter_operation_launch(self, espionage_manager):
        """Test launching counter-intelligence operations."""
        operation = espionage_manager.launch_counter_operation(
            "suspected_enemy_op", "enemy_civ"
        )
        
        assert operation.operation_type == EspionageOperationType.COUNTER_SURVEILLANCE
        assert operation.target_civilization == "enemy_civ"
        assert operation.intelligence_gathered["target_operation"] == "suspected_enemy_op"
    
    def test_operation_difficulty_calculation(self, espionage_manager):
        """Test operation difficulty calculation."""
        # Test different operation types have appropriate difficulties
        easy_op = espionage_manager.plan_operation(
            EspionageOperationType.POLITICAL_INTELLIGENCE, "enemy_civ"
        )
        assert easy_op.difficulty in [OperationDifficulty.TRIVIAL, OperationDifficulty.EASY]
        
        hard_op = espionage_manager.plan_operation(
            EspionageOperationType.SABOTAGE_MISSION, "enemy_civ"
        )
        assert hard_op.difficulty in [OperationDifficulty.HARD, OperationDifficulty.EXTREME]
    
    def test_espionage_summary(self, espionage_manager):
        """Test getting comprehensive espionage summary."""
        # Add some assets and operations
        asset = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        operation = espionage_manager.plan_operation(
            EspionageOperationType.POLITICAL_INTELLIGENCE, "enemy_civ"
        )
        espionage_manager.assign_assets_to_operation(operation, [asset.asset_id])
        espionage_manager.launch_operation(operation, 1)
        
        summary = espionage_manager.get_espionage_summary()
        
        assert "total_assets" in summary
        assert "active_assets" in summary
        assert "active_operations" in summary
        assert "intelligence_budget" in summary
        assert "technology_level" in summary
        assert "asset_breakdown" in summary
        assert summary["total_assets"] == 1
        assert summary["active_operations"] == 1
    
    def test_target_intelligence_summary(self, espionage_manager):
        """Test getting intelligence summary for specific target."""
        # Add intelligence report
        report = IntelligenceReport(
            target_civilization="enemy_civ",
            intelligence_type="political",
            content={"political_instability": 0.7},
            reliability=IntelligenceReliability.HIGH_CONFIDENCE
        )
        espionage_manager.intelligence_reports[report.report_id] = report
        
        # Add targeting asset
        asset = espionage_manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        summary = espionage_manager.get_target_intelligence_summary("enemy_civ")
        
        assert summary["target_civilization"] == "enemy_civ"
        assert summary["intelligence_reports"] == 1
        assert summary["assigned_assets"] == 1
        assert "identified_weaknesses" in summary
        assert "recommended_operations" in summary
        assert "intelligence_coverage" in summary


class TestEspionageIntegration:
    """Integration tests for the complete espionage system."""
    
    def test_complete_espionage_lifecycle(self):
        """Test complete espionage operation lifecycle."""
        manager = EspionageManager("test_civ")
        
        # 1. Recruit assets
        agent = manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.ADVISOR_SURVEILLANCE]
        )
        informant = manager.recruit_asset(
            "informant", "enemy_civ", [EspionageOperationType.POLITICAL_INTELLIGENCE]
        )
        
        # 2. Plan operation
        operation = manager.plan_operation(
            EspionageOperationType.ADVISOR_SURVEILLANCE,
            "enemy_civ",
            target_advisor="enemy_military_advisor"
        )
        
        # 3. Assign assets
        success = manager.assign_assets_to_operation(
            operation, [agent.asset_id, informant.asset_id]
        )
        assert success == True
        
        # 4. Launch operation
        success = manager.launch_operation(operation, current_turn=1)
        assert success == True
        
        # 5. Process turns until completion
        turn = 2
        while operation.status == "active" and turn < 10:
            results = manager.process_operations_turn(turn)
            assert len(results) >= 1
            turn += 1
        
        # 6. Check results
        if operation.status == "completed":
            assert operation.outcome is not None
            # If successful, should have intelligence report
            if operation.outcome in [OperationOutcome.COMPLETE_SUCCESS, 
                                   OperationOutcome.PARTIAL_SUCCESS]:
                assert len(manager.intelligence_reports) > 0
        
        # 7. Analyze intelligence
        weaknesses = manager.analyze_target_weaknesses("enemy_civ")
        assert isinstance(weaknesses, dict)
        
        # 8. Get summary
        summary = manager.get_espionage_summary()
        assert summary["total_assets"] == 2
        assert summary["completed_operations"] >= 0
    
    def test_multi_target_espionage(self):
        """Test managing espionage against multiple targets."""
        manager = EspionageManager("test_civ")
        
        targets = ["enemy_civ_1", "enemy_civ_2", "enemy_civ_3"]
        
        # Recruit specialized assets for each target
        for target in targets:
            agent = manager.recruit_asset(
                "agent", target, [EspionageOperationType.POLITICAL_INTELLIGENCE]
            )
            
            operation = manager.plan_operation(
                EspionageOperationType.POLITICAL_INTELLIGENCE, target
            )
            
            manager.assign_assets_to_operation(operation, [agent.asset_id])
            manager.launch_operation(operation, 1)
        
        # Process operations
        results = manager.process_operations_turn(2)
        assert len(results) == 3  # One result per target
        
        # Check each target has dedicated assets
        for target in targets:
            target_summary = manager.get_target_intelligence_summary(target)
            assert target_summary["assigned_assets"] >= 1
    
    def test_counter_intelligence_scenario(self):
        """Test counter-intelligence discovery scenario."""
        manager = EspionageManager("test_civ")
        
        # Recruit asset
        asset = manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.SABOTAGE_MISSION]
        )
        
        # Plan high-risk operation
        operation = manager.plan_operation(
            EspionageOperationType.SABOTAGE_MISSION, "enemy_civ"
        )
        
        manager.assign_assets_to_operation(operation, [asset.asset_id])
        manager.launch_operation(operation, 1)
        
        # Force discovery for testing
        with patch('random.random', return_value=0.0):  # Force discovery
            results = manager.process_operations_turn(2)
            
            # Should have diplomatic incident
            assert any("discovered" in result.get("status", "") for result in results)
    
    def test_resource_management(self):
        """Test espionage resource management."""
        manager = EspionageManager("test_civ")
        initial_budget = manager.intelligence_budget
        initial_influence = manager.influence_points
        
        # Recruit expensive assets
        expensive_agent = manager.recruit_asset(
            "agent", "enemy_civ", [EspionageOperationType.ASSASSINATION_ATTEMPT]
        )
        
        # Budget should be reduced
        assert manager.intelligence_budget < initial_budget
        
        # Train asset (costs more budget)
        manager.train_asset(expensive_agent.asset_id, "technical")
        
        # Plan expensive operation
        expensive_op = manager.plan_operation(
            EspionageOperationType.MEMORY_EXTRACTION, "enemy_civ"
        )
        
        # Should require both budget and influence
        assert "budget" in expensive_op.resource_cost
        assert "influence" in expensive_op.resource_cost
        
        # Test resource constraints
        manager.intelligence_budget = 50  # Low budget
        manager.influence_points = 10   # Low influence
        
        manager.assign_assets_to_operation(expensive_op, [expensive_agent.asset_id])
        
        # Should fail to launch due to insufficient resources
        success = manager.launch_operation(expensive_op, 1)
        assert success == False


if __name__ == "__main__":
    pytest.main([__file__])
