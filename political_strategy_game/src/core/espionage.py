"""
Intelligence and Espionage Systems

Task 6.1: Comprehensive espionage mechanics for gathering political intelligence
on enemy civilizations, conducting sabotage operations, and manipulating
enemy advisor relationships through bribery, blackmail, and disinformation.

This system enables player-driven intelligence gathering and manipulation
of enemy political systems.
"""

import uuid
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from .diplomacy import IntelligenceOperation, IntelligenceNetwork
from .memory import Memory, MemoryType


class EspionageOperationType(str, Enum):
    """Types of espionage operations available to players."""
    # Intelligence Gathering
    POLITICAL_INTELLIGENCE = "political_intelligence"
    ADVISOR_SURVEILLANCE = "advisor_surveillance"
    FACTION_MONITORING = "faction_monitoring"
    DECISION_INTERCEPT = "decision_intercept"
    MEMORY_EXTRACTION = "memory_extraction"
    
    # Active Operations
    DISINFORMATION_CAMPAIGN = "disinformation_campaign"
    ADVISOR_BRIBERY = "advisor_bribery"
    BLACKMAIL_OPERATION = "blackmail_operation"
    SABOTAGE_MISSION = "sabotage_mission"
    ASSASSINATION_ATTEMPT = "assassination_attempt"
    
    # Counter-Intelligence
    DOUBLE_AGENT_RECRUITMENT = "double_agent_recruitment"
    SECURITY_AUDIT = "security_audit"
    COUNTER_SURVEILLANCE = "counter_surveillance"


class OperationDifficulty(str, Enum):
    """Difficulty levels for espionage operations."""
    TRIVIAL = "trivial"        # 90%+ success rate
    EASY = "easy"              # 70-90% success rate
    MODERATE = "moderate"      # 50-70% success rate
    HARD = "hard"              # 30-50% success rate
    EXTREME = "extreme"        # 10-30% success rate
    IMPOSSIBLE = "impossible"  # <10% success rate


class IntelligenceReliability(str, Enum):
    """Reliability levels for gathered intelligence."""
    CONFIRMED = "confirmed"           # 95%+ accuracy
    HIGH_CONFIDENCE = "high_confidence"  # 80-95% accuracy
    MODERATE_CONFIDENCE = "moderate_confidence"  # 60-80% accuracy
    LOW_CONFIDENCE = "low_confidence"    # 40-60% accuracy
    UNRELIABLE = "unreliable"         # 20-40% accuracy
    DISINFORMATION = "disinformation"  # Deliberately false


class OperationOutcome(str, Enum):
    """Possible outcomes for espionage operations."""
    COMPLETE_SUCCESS = "complete_success"
    PARTIAL_SUCCESS = "partial_success"
    MINIMAL_SUCCESS = "minimal_success"
    FAILURE = "failure"
    CATASTROPHIC_FAILURE = "catastrophic_failure"
    OPERATION_COMPROMISED = "operation_compromised"


@dataclass
class EspionageAsset:
    """Individual espionage asset (agent, informant, etc.)."""
    asset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_name: str = ""
    asset_type: str = "agent"  # agent, informant, double_agent, sleeper
    
    # Capabilities
    skill_level: float = 0.5  # 0.0 to 1.0
    specialization: List[EspionageOperationType] = field(default_factory=list)
    infiltration_level: float = 0.0  # How deep in target organization
    
    # Status
    is_active: bool = True
    is_compromised: bool = False
    cover_identity: str = ""
    assigned_target: Optional[str] = None
    
    # Experience and reliability
    operations_completed: int = 0
    success_rate: float = 0.5
    last_contact: datetime = field(default_factory=datetime.now)
    
    # Security
    exposure_risk: float = 0.1  # Risk of being discovered
    loyalty: float = 0.8  # Risk of defection or double-crossing


@dataclass
class EspionageOperation:
    """Individual espionage operation."""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: EspionageOperationType = EspionageOperationType.POLITICAL_INTELLIGENCE
    
    # Targeting
    target_civilization: str = ""
    target_advisor: Optional[str] = None  # For advisor-specific operations
    target_faction: Optional[str] = None  # For faction-specific operations
    
    # Operation parameters
    difficulty: OperationDifficulty = OperationDifficulty.MODERATE
    required_skill_level: float = 0.5
    time_to_complete: int = 3  # Turns
    resource_cost: Dict[str, float] = field(default_factory=dict)
    
    # Assignment
    assigned_assets: List[str] = field(default_factory=list)  # Asset IDs
    operation_leader: Optional[str] = None  # Lead asset
    
    # Status
    status: str = "planning"  # planning, active, completed, failed, compromised
    start_turn: Optional[int] = None
    completion_turn: Optional[int] = None
    progress: float = 0.0  # 0.0 to 1.0
    
    # Results
    outcome: Optional[OperationOutcome] = None
    intelligence_gathered: Dict[str, Any] = field(default_factory=dict)
    reliability: IntelligenceReliability = IntelligenceReliability.MODERATE_CONFIDENCE
    side_effects: List[str] = field(default_factory=list)  # Unintended consequences
    
    # Security
    discovery_risk: float = 0.2
    discovered_by: List[str] = field(default_factory=list)  # Who discovered it
    diplomatic_consequences: Dict[str, float] = field(default_factory=dict)


@dataclass 
class IntelligenceReport:
    """Report containing gathered intelligence."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_operation: str = ""
    target_civilization: str = ""
    
    # Content
    intelligence_type: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    reliability: IntelligenceReliability = IntelligenceReliability.MODERATE_CONFIDENCE
    
    # Metadata
    collection_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    classification_level: str = "secret"
    
    # Verification
    confirmed_by: List[str] = field(default_factory=list)  # Other sources
    contradicted_by: List[str] = field(default_factory=list)  # Conflicting sources


class EspionageManager:
    """Manages all espionage and intelligence operations."""
    
    def __init__(self, civilization_id: str):
        self.civilization_id = civilization_id
        self.assets: Dict[str, EspionageAsset] = {}
        self.active_operations: Dict[str, EspionageOperation] = {}
        self.completed_operations: Dict[str, EspionageOperation] = {}
        self.intelligence_reports: Dict[str, IntelligenceReport] = {}
        
        # Resources
        self.intelligence_budget: float = 1000.0
        self.influence_points: float = 100.0
        
        # Capabilities
        self.technology_level: float = 0.5  # Affects operation success rates
        self.counter_intelligence_strength: float = 0.5
        
        # Tracking
        self.diplomatic_incidents: List[Dict[str, Any]] = []
        self.burned_assets: List[str] = []  # Compromised asset IDs
        
        self.logger = logging.getLogger(__name__)
    
    # ===== Asset Management =====
    
    def recruit_asset(self, asset_type: str, target_civilization: str, 
                     specialization: List[EspionageOperationType]) -> EspionageAsset:
        """Recruit a new espionage asset."""
        asset = EspionageAsset(
            asset_name=f"{asset_type.title()}_{len(self.assets) + 1}",
            asset_type=asset_type,
            specialization=specialization,
            assigned_target=target_civilization,
            skill_level=random.uniform(0.3, 0.8),  # Random initial skill
            exposure_risk=random.uniform(0.05, 0.2)
        )
        
        # Cost increases with skill level
        recruitment_cost = 100 + (asset.skill_level * 200)
        if self.intelligence_budget >= recruitment_cost:
            self.intelligence_budget -= recruitment_cost
            self.assets[asset.asset_id] = asset
            self.logger.info(f"Recruited {asset.asset_name} targeting {target_civilization}")
            return asset
        else:
            raise ValueError(f"Insufficient budget for recruitment (need {recruitment_cost})")
    
    def train_asset(self, asset_id: str, training_type: str) -> bool:
        """Improve an asset's capabilities through training."""
        asset = self.assets.get(asset_id)
        if not asset or not asset.is_active:
            return False
        
        training_cost = 50 + (asset.skill_level * 100)
        if self.intelligence_budget < training_cost:
            return False
        
        self.intelligence_budget -= training_cost
        
        # Improve skill based on training type
        improvement = random.uniform(0.05, 0.15)
        if training_type == "infiltration":
            asset.infiltration_level = min(1.0, asset.infiltration_level + improvement)
        elif training_type == "technical":
            asset.skill_level = min(1.0, asset.skill_level + improvement)
        elif training_type == "counter_surveillance":
            asset.exposure_risk = max(0.01, asset.exposure_risk - improvement)
        
        self.logger.info(f"Trained {asset.asset_name} in {training_type}")
        return True
    
    def burn_asset(self, asset_id: str, reason: str = "compromised") -> None:
        """Remove a compromised or exposed asset."""
        asset = self.assets.get(asset_id)
        if asset:
            asset.is_active = False
            asset.is_compromised = True
            self.burned_assets.append(asset_id)
            
            # Remove from active operations
            for operation in self.active_operations.values():
                if asset_id in operation.assigned_assets:
                    operation.assigned_assets.remove(asset_id)
                    operation.discovery_risk += 0.2  # Increases risk for remaining assets
            
            self.logger.warning(f"Burned asset {asset.asset_name}: {reason}")
    
    # ===== Operation Planning =====
    
    def plan_operation(self, operation_type: EspionageOperationType, 
                      target_civilization: str, target_advisor: Optional[str] = None,
                      target_faction: Optional[str] = None) -> EspionageOperation:
        """Plan a new espionage operation."""
        operation = EspionageOperation(
            operation_type=operation_type,
            target_civilization=target_civilization,
            target_advisor=target_advisor,
            target_faction=target_faction
        )
        
        # Calculate operation difficulty and requirements
        operation.difficulty = self._calculate_operation_difficulty(operation)
        operation.required_skill_level = self._get_required_skill_level(operation)
        operation.time_to_complete = self._estimate_completion_time(operation)
        operation.resource_cost = self._calculate_resource_cost(operation)
        
        return operation
    
    def assign_assets_to_operation(self, operation: EspionageOperation, 
                                  asset_ids: List[str]) -> bool:
        """Assign assets to an operation."""
        # Validate assets
        available_assets = []
        for asset_id in asset_ids:
            asset = self.assets.get(asset_id)
            if asset and asset.is_active and not asset.is_compromised:
                available_assets.append(asset)
        
        if not available_assets:
            return False
        
        # Check if assets meet requirements
        max_skill = max(asset.skill_level for asset in available_assets)
        if max_skill < operation.required_skill_level * 0.8:  # Need at least 80% of required skill
            return False
        
        # Assign assets
        operation.assigned_assets = [asset.asset_id for asset in available_assets]
        operation.operation_leader = max(available_assets, key=lambda a: a.skill_level).asset_id
        
        # Calculate discovery risk
        operation.discovery_risk = self._calculate_discovery_risk(operation, available_assets)
        
        return True
    
    def launch_operation(self, operation: EspionageOperation, current_turn: int) -> bool:
        """Launch an operation that's been planned and has assets assigned."""
        if not operation.assigned_assets:
            return False
        
        # Check resource costs
        for resource, cost in operation.resource_cost.items():
            if resource == "budget" and self.intelligence_budget < cost:
                return False
            elif resource == "influence" and self.influence_points < cost:
                return False
        
        # Deduct resources
        for resource, cost in operation.resource_cost.items():
            if resource == "budget":
                self.intelligence_budget -= cost
            elif resource == "influence":
                self.influence_points -= cost
        
        # Launch operation
        operation.status = "active"
        operation.start_turn = current_turn
        self.active_operations[operation.operation_id] = operation
        
        self.logger.info(f"Launched {operation.operation_type.value} against {operation.target_civilization}")
        return True
    
    # ===== Operation Execution =====
    
    def process_operations_turn(self, current_turn: int) -> List[Dict[str, Any]]:
        """Process all active operations for one turn."""
        turn_results = []
        
        for operation in list(self.active_operations.values()):
            if operation.status == "active":
                result = self._process_single_operation(operation, current_turn)
                turn_results.append(result)
                
                # Check if operation completed
                if operation.progress >= 1.0:
                    self._complete_operation(operation, current_turn)
        
        return turn_results
    
    def _process_single_operation(self, operation: EspionageOperation, current_turn: int) -> Dict[str, Any]:
        """Process a single operation for one turn."""
        # Calculate progress
        progress_per_turn = 1.0 / operation.time_to_complete
        
        # Apply asset skill modifiers
        asset_modifier = 1.0
        for asset_id in operation.assigned_assets:
            asset = self.assets.get(asset_id)
            if asset and asset.is_active:
                asset_modifier *= (0.5 + asset.skill_level)
        
        progress_increase = progress_per_turn * asset_modifier
        operation.progress = min(1.0, operation.progress + progress_increase)
        
        # Check for discovery
        discovery_check = random.random()
        if discovery_check < operation.discovery_risk:
            return self._handle_operation_discovery(operation, current_turn)
        
        # Check for complications
        complication_chance = 0.1 + (operation.difficulty.value == "hard") * 0.1
        if random.random() < complication_chance:
            return self._handle_operation_complication(operation, current_turn)
        
        return {
            "operation_id": operation.operation_id,
            "type": operation.operation_type.value,
            "status": "progressing",
            "progress": operation.progress,
            "events": []
        }
    
    def _complete_operation(self, operation: EspionageOperation, current_turn: int) -> None:
        """Complete an operation and generate results."""
        operation.status = "completed"
        operation.completion_turn = current_turn
        
        # Determine outcome based on various factors
        outcome = self._determine_operation_outcome(operation)
        operation.outcome = outcome
        
        # Generate intelligence or execute operation effects
        if outcome in [OperationOutcome.COMPLETE_SUCCESS, OperationOutcome.PARTIAL_SUCCESS]:
            intelligence = self._generate_operation_intelligence(operation)
            if intelligence:
                self.intelligence_reports[intelligence.report_id] = intelligence
        
        # Update asset experience
        for asset_id in operation.assigned_assets:
            asset = self.assets.get(asset_id)
            if asset:
                asset.operations_completed += 1
                if outcome in [OperationOutcome.COMPLETE_SUCCESS, OperationOutcome.PARTIAL_SUCCESS]:
                    asset.success_rate = (asset.success_rate * asset.operations_completed + 1) / (asset.operations_completed + 1)
        
        # Move to completed operations
        self.completed_operations[operation.operation_id] = operation
        del self.active_operations[operation.operation_id]
        
        self.logger.info(f"Completed operation {operation.operation_type.value}: {outcome.value}")
    
    # ===== Intelligence Analysis =====
    
    def get_intelligence_on_target(self, target_civilization: str, 
                                  intelligence_type: Optional[str] = None) -> List[IntelligenceReport]:
        """Get all intelligence reports on a specific target."""
        reports = []
        for report in self.intelligence_reports.values():
            if report.target_civilization == target_civilization:
                if intelligence_type is None or report.intelligence_type == intelligence_type:
                    reports.append(report)
        
        # Sort by reliability and recency
        reports.sort(key=lambda r: (r.reliability.value, r.collection_date), reverse=True)
        return reports
    
    def analyze_target_weaknesses(self, target_civilization: str) -> Dict[str, float]:
        """Analyze gathered intelligence to identify target weaknesses."""
        reports = self.get_intelligence_on_target(target_civilization)
        
        weaknesses = {
            "political_instability": 0.0,
            "advisor_corruption": 0.0,
            "faction_conflicts": 0.0,
            "economic_vulnerability": 0.0,
            "military_weakness": 0.0,
            "succession_crisis": 0.0
        }
        
        for report in reports:
            # Weight by reliability
            reliability_weight = {
                IntelligenceReliability.CONFIRMED: 1.0,
                IntelligenceReliability.HIGH_CONFIDENCE: 0.8,
                IntelligenceReliability.MODERATE_CONFIDENCE: 0.6,
                IntelligenceReliability.LOW_CONFIDENCE: 0.4,
                IntelligenceReliability.UNRELIABLE: 0.2,
                IntelligenceReliability.DISINFORMATION: 0.0
            }.get(report.reliability, 0.5)
            
            # Extract weakness indicators from content
            content = report.content
            for weakness_type in weaknesses.keys():
                if weakness_type in content:
                    weaknesses[weakness_type] += content[weakness_type] * reliability_weight
        
        # Normalize to 0-1 range
        for key in weaknesses:
            weaknesses[key] = min(1.0, weaknesses[key])
        
        return weaknesses
    
    # ===== Sabotage and Manipulation =====
    
    def plan_disinformation_campaign(self, target_civilization: str, 
                                   target_advisor: str, false_information: Dict[str, Any]) -> EspionageOperation:
        """Plan a disinformation campaign to plant false memories or beliefs."""
        operation = self.plan_operation(
            EspionageOperationType.DISINFORMATION_CAMPAIGN,
            target_civilization,
            target_advisor=target_advisor
        )
        
        operation.intelligence_gathered["disinformation_payload"] = false_information
        operation.resource_cost["influence"] = 50  # Disinformation requires influence
        
        return operation
    
    def plan_bribery_operation(self, target_civilization: str, target_advisor: str, 
                             bribe_amount: float, desired_outcome: str) -> EspionageOperation:
        """Plan a bribery operation to influence an enemy advisor."""
        operation = self.plan_operation(
            EspionageOperationType.ADVISOR_BRIBERY,
            target_civilization,
            target_advisor=target_advisor
        )
        
        operation.resource_cost["budget"] = bribe_amount
        operation.intelligence_gathered["desired_outcome"] = desired_outcome
        operation.discovery_risk += 0.1  # Bribery increases discovery risk
        
        return operation
    
    def plan_sabotage_mission(self, target_civilization: str, sabotage_target: str) -> EspionageOperation:
        """Plan a sabotage mission against enemy infrastructure or capabilities."""
        operation = self.plan_operation(
            EspionageOperationType.SABOTAGE_MISSION,
            target_civilization
        )
        
        operation.intelligence_gathered["sabotage_target"] = sabotage_target
        operation.difficulty = OperationDifficulty.HARD  # Sabotage is inherently risky
        operation.discovery_risk += 0.2
        
        return operation
    
    # ===== Counter-Intelligence =====
    
    def conduct_security_audit(self) -> Dict[str, Any]:
        """Conduct internal security audit to detect enemy operations."""
        audit_results = {
            "vulnerabilities_found": [],
            "suspicious_activities": [],
            "recommendations": [],
            "security_score": 0.8  # Base security score
        }
        
        # Check for patterns indicating enemy espionage
        # This would integrate with the civilization's political system
        # to look for anomalies in advisor behavior, decision patterns, etc.
        
        return audit_results
    
    def launch_counter_operation(self, suspected_enemy_operation: str, 
                                target_civilization: str) -> EspionageOperation:
        """Launch a counter-intelligence operation."""
        operation = self.plan_operation(
            EspionageOperationType.COUNTER_SURVEILLANCE,
            target_civilization
        )
        
        operation.intelligence_gathered["target_operation"] = suspected_enemy_operation
        return operation
    
    # ===== Helper Methods =====
    
    def _calculate_operation_difficulty(self, operation: EspionageOperation) -> OperationDifficulty:
        """Calculate the difficulty of an operation based on type and target."""
        base_difficulty = {
            EspionageOperationType.POLITICAL_INTELLIGENCE: OperationDifficulty.EASY,
            EspionageOperationType.ADVISOR_SURVEILLANCE: OperationDifficulty.MODERATE,
            EspionageOperationType.FACTION_MONITORING: OperationDifficulty.MODERATE,
            EspionageOperationType.DECISION_INTERCEPT: OperationDifficulty.HARD,
            EspionageOperationType.MEMORY_EXTRACTION: OperationDifficulty.EXTREME,
            EspionageOperationType.DISINFORMATION_CAMPAIGN: OperationDifficulty.MODERATE,
            EspionageOperationType.ADVISOR_BRIBERY: OperationDifficulty.HARD,
            EspionageOperationType.BLACKMAIL_OPERATION: OperationDifficulty.HARD,
            EspionageOperationType.SABOTAGE_MISSION: OperationDifficulty.EXTREME,
            EspionageOperationType.ASSASSINATION_ATTEMPT: OperationDifficulty.IMPOSSIBLE,
        }.get(operation.operation_type, OperationDifficulty.MODERATE)
        
        return base_difficulty
    
    def _get_required_skill_level(self, operation: EspionageOperation) -> float:
        """Get the required skill level for an operation."""
        difficulty_skill_map = {
            OperationDifficulty.TRIVIAL: 0.1,
            OperationDifficulty.EASY: 0.3,
            OperationDifficulty.MODERATE: 0.5,
            OperationDifficulty.HARD: 0.7,
            OperationDifficulty.EXTREME: 0.9,
            OperationDifficulty.IMPOSSIBLE: 1.0
        }
        return difficulty_skill_map.get(operation.difficulty, 0.5)
    
    def _estimate_completion_time(self, operation: EspionageOperation) -> int:
        """Estimate how many turns an operation will take."""
        base_time = {
            EspionageOperationType.POLITICAL_INTELLIGENCE: 2,
            EspionageOperationType.ADVISOR_SURVEILLANCE: 3,
            EspionageOperationType.FACTION_MONITORING: 4,
            EspionageOperationType.DECISION_INTERCEPT: 2,
            EspionageOperationType.MEMORY_EXTRACTION: 5,
            EspionageOperationType.DISINFORMATION_CAMPAIGN: 4,
            EspionageOperationType.ADVISOR_BRIBERY: 3,
            EspionageOperationType.BLACKMAIL_OPERATION: 5,
            EspionageOperationType.SABOTAGE_MISSION: 6,
            EspionageOperationType.ASSASSINATION_ATTEMPT: 8,
        }.get(operation.operation_type, 3)
        
        # Modify by difficulty
        difficulty_modifier = {
            OperationDifficulty.TRIVIAL: 0.5,
            OperationDifficulty.EASY: 0.8,
            OperationDifficulty.MODERATE: 1.0,
            OperationDifficulty.HARD: 1.3,
            OperationDifficulty.EXTREME: 1.8,
            OperationDifficulty.IMPOSSIBLE: 2.5
        }.get(operation.difficulty, 1.0)
        
        return max(1, int(base_time * difficulty_modifier))
    
    def _calculate_resource_cost(self, operation: EspionageOperation) -> Dict[str, float]:
        """Calculate resource costs for an operation."""
        base_cost = {
            EspionageOperationType.POLITICAL_INTELLIGENCE: {"budget": 100},
            EspionageOperationType.ADVISOR_SURVEILLANCE: {"budget": 150},
            EspionageOperationType.FACTION_MONITORING: {"budget": 200},
            EspionageOperationType.DECISION_INTERCEPT: {"budget": 250, "influence": 20},
            EspionageOperationType.MEMORY_EXTRACTION: {"budget": 400, "influence": 50},
            EspionageOperationType.DISINFORMATION_CAMPAIGN: {"budget": 200, "influence": 40},
            EspionageOperationType.ADVISOR_BRIBERY: {"budget": 300, "influence": 30},
            EspionageOperationType.BLACKMAIL_OPERATION: {"budget": 250, "influence": 60},
            EspionageOperationType.SABOTAGE_MISSION: {"budget": 500, "influence": 80},
            EspionageOperationType.ASSASSINATION_ATTEMPT: {"budget": 800, "influence": 100},
        }.get(operation.operation_type, {"budget": 100})
        
        # Modify by difficulty
        difficulty_multiplier = {
            OperationDifficulty.TRIVIAL: 0.5,
            OperationDifficulty.EASY: 0.8,
            OperationDifficulty.MODERATE: 1.0,
            OperationDifficulty.HARD: 1.5,
            OperationDifficulty.EXTREME: 2.0,
            OperationDifficulty.IMPOSSIBLE: 3.0
        }.get(operation.difficulty, 1.0)
        
        return {resource: cost * difficulty_multiplier for resource, cost in base_cost.items()}
    
    def _calculate_discovery_risk(self, operation: EspionageOperation, 
                                 assets: List[EspionageAsset]) -> float:
        """Calculate the risk of an operation being discovered."""
        base_risk = {
            EspionageOperationType.POLITICAL_INTELLIGENCE: 0.1,
            EspionageOperationType.ADVISOR_SURVEILLANCE: 0.2,
            EspionageOperationType.FACTION_MONITORING: 0.15,
            EspionageOperationType.DECISION_INTERCEPT: 0.3,
            EspionageOperationType.MEMORY_EXTRACTION: 0.4,
            EspionageOperationType.DISINFORMATION_CAMPAIGN: 0.25,
            EspionageOperationType.ADVISOR_BRIBERY: 0.35,
            EspionageOperationType.BLACKMAIL_OPERATION: 0.3,
            EspionageOperationType.SABOTAGE_MISSION: 0.5,
            EspionageOperationType.ASSASSINATION_ATTEMPT: 0.7,
        }.get(operation.operation_type, 0.2)
        
        # Asset skill reduces risk
        avg_skill = sum(asset.skill_level for asset in assets) / len(assets)
        skill_reduction = avg_skill * 0.3
        
        # Asset exposure increases risk
        avg_exposure = sum(asset.exposure_risk for asset in assets) / len(assets)
        
        final_risk = base_risk - skill_reduction + avg_exposure
        return max(0.01, min(0.95, final_risk))
    
    def _handle_operation_discovery(self, operation: EspionageOperation, 
                                   current_turn: int) -> Dict[str, Any]:
        """Handle when an operation is discovered by the target."""
        operation.status = "compromised"
        operation.outcome = OperationOutcome.OPERATION_COMPROMISED
        
        # Burn some assets
        assets_to_burn = random.sample(operation.assigned_assets, 
                                     min(2, len(operation.assigned_assets)))
        for asset_id in assets_to_burn:
            self.burn_asset(asset_id, "operation_discovered")
        
        # Create diplomatic incident
        incident = {
            "type": "espionage_discovery",
            "operation": operation.operation_type.value,
            "target": operation.target_civilization,
            "turn": current_turn,
            "severity": "major" if operation.operation_type in [
                EspionageOperationType.SABOTAGE_MISSION,
                EspionageOperationType.ASSASSINATION_ATTEMPT
            ] else "moderate"
        }
        self.diplomatic_incidents.append(incident)
        
        return {
            "operation_id": operation.operation_id,
            "type": operation.operation_type.value,
            "status": "discovered",
            "events": [f"Operation discovered by {operation.target_civilization}"],
            "diplomatic_incident": incident
        }
    
    def _handle_operation_complication(self, operation: EspionageOperation, 
                                      current_turn: int) -> Dict[str, Any]:
        """Handle random complications during operations."""
        complications = [
            "Asset cover blown, requiring extraction",
            "Unexpected security measures encountered",
            "Target changed routine, delaying operation",
            "Communication intercepted, partial exposure",
            "Asset loyalty questioned, requiring reassurance"
        ]
        
        complication = random.choice(complications)
        operation.side_effects.append(complication)
        
        # Slow down operation
        operation.progress = max(0.0, operation.progress - 0.2)
        
        return {
            "operation_id": operation.operation_id,
            "type": operation.operation_type.value,
            "status": "complication",
            "events": [complication],
            "progress": operation.progress
        }
    
    def _determine_operation_outcome(self, operation: EspionageOperation) -> OperationOutcome:
        """Determine the final outcome of a completed operation."""
        # Base success rate by difficulty
        success_rates = {
            OperationDifficulty.TRIVIAL: 0.95,
            OperationDifficulty.EASY: 0.8,
            OperationDifficulty.MODERATE: 0.6,
            OperationDifficulty.HARD: 0.4,
            OperationDifficulty.EXTREME: 0.2,
            OperationDifficulty.IMPOSSIBLE: 0.05
        }
        
        base_success = success_rates.get(operation.difficulty, 0.5)
        
        # Modify by asset skill
        asset_skill_bonus = 0.0
        for asset_id in operation.assigned_assets:
            asset = self.assets.get(asset_id)
            if asset:
                asset_skill_bonus += (asset.skill_level - 0.5) * 0.1
        
        final_success_rate = min(0.95, base_success + asset_skill_bonus)
        
        roll = random.random()
        if roll < final_success_rate * 0.3:
            return OperationOutcome.COMPLETE_SUCCESS
        elif roll < final_success_rate * 0.7:
            return OperationOutcome.PARTIAL_SUCCESS
        elif roll < final_success_rate:
            return OperationOutcome.MINIMAL_SUCCESS
        elif roll < 0.9:
            return OperationOutcome.FAILURE
        else:
            return OperationOutcome.CATASTROPHIC_FAILURE
    
    def _generate_operation_intelligence(self, operation: EspionageOperation) -> Optional[IntelligenceReport]:
        """Generate intelligence report from a successful operation."""
        if operation.outcome not in [OperationOutcome.COMPLETE_SUCCESS, 
                                   OperationOutcome.PARTIAL_SUCCESS,
                                   OperationOutcome.MINIMAL_SUCCESS]:
            return None
        
        # Determine reliability based on outcome
        reliability_map = {
            OperationOutcome.COMPLETE_SUCCESS: IntelligenceReliability.HIGH_CONFIDENCE,
            OperationOutcome.PARTIAL_SUCCESS: IntelligenceReliability.MODERATE_CONFIDENCE,
            OperationOutcome.MINIMAL_SUCCESS: IntelligenceReliability.LOW_CONFIDENCE
        }
        
        # Generate content based on operation type
        content = self._generate_intelligence_content(operation)
        
        report = IntelligenceReport(
            source_operation=operation.operation_id,
            target_civilization=operation.target_civilization,
            intelligence_type=operation.operation_type.value,
            content=content,
            reliability=reliability_map[operation.outcome],
            expiry_date=datetime.now() + timedelta(days=30)  # Intelligence expires
        )
        
        return report
    
    def _generate_intelligence_content(self, operation: EspionageOperation) -> Dict[str, Any]:
        """Generate specific intelligence content based on operation type."""
        # This would integrate with the target civilization's actual political state
        # For now, generate plausible sample data
        
        content = {}
        
        if operation.operation_type == EspionageOperationType.POLITICAL_INTELLIGENCE:
            content = {
                "government_stability": random.uniform(0.3, 0.9),
                "leader_approval": random.uniform(0.2, 0.8),
                "recent_decisions": ["Policy change on taxation", "Military deployment approved"],
                "upcoming_events": ["Council meeting in 3 turns", "Trade negotiation planned"]
            }
        
        elif operation.operation_type == EspionageOperationType.ADVISOR_SURVEILLANCE:
            content = {
                "advisor_loyalty": random.uniform(0.3, 0.9),
                "recent_activities": ["Met with faction leaders", "Reviewed military reports"],
                "relationships": {"strong_allies": 2, "neutral": 3, "rivals": 1},
                "personal_vulnerabilities": ["Financial difficulties", "Family pressure"]
            }
        
        elif operation.operation_type == EspionageOperationType.FACTION_MONITORING:
            content = {
                "faction_strength": random.uniform(0.2, 0.8),
                "faction_goals": ["Increase military spending", "Reform taxation"],
                "faction_conflicts": ["Dispute with economic faction", "Competition for influence"],
                "key_members": ["General Marcus", "Admiral Chen", "Captain Rodriguez"]
            }
        
        elif operation.operation_type == EspionageOperationType.MEMORY_EXTRACTION:
            # This would extract specific memories from target advisors
            content = {
                "extracted_memories": [
                    {"content": "Private meeting with leader about succession", "reliability": 0.8},
                    {"content": "Concerns about neighboring civilizations", "reliability": 0.6}
                ],
                "memory_patterns": ["High stress about military matters", "Uncertainty about economic policy"]
            }
        
        return content
    
    # ===== Helper Methods =====
    
    def get_asset(self, asset_id: str) -> Optional[EspionageAsset]:
        """Get asset by ID."""
        return self.assets.get(asset_id)
    
    def get_operation(self, operation_id: str) -> Optional[EspionageOperation]:
        """Get operation by ID."""
        if operation_id in self.active_operations:
            return self.active_operations[operation_id]
        return self.completed_operations.get(operation_id)
    
    # ===== Reporting and Summary =====
    
    def get_espionage_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of espionage capabilities and operations."""
        active_assets = [asset for asset in self.assets.values() if asset.is_active]
        
        return {
            "total_assets": len(self.assets),
            "active_assets": len(active_assets),
            "compromised_assets": len(self.burned_assets),
            "active_operations": len(self.active_operations),
            "completed_operations": len(self.completed_operations),
            "intelligence_reports": len(self.intelligence_reports),
            "intelligence_budget": self.intelligence_budget,
            "influence_points": self.influence_points,
            "diplomatic_incidents": len(self.diplomatic_incidents),
            "technology_level": self.technology_level,
            "counter_intelligence_strength": self.counter_intelligence_strength,
            "asset_breakdown": {
                asset_type: len([a for a in active_assets if a.asset_type == asset_type])
                for asset_type in ["agent", "informant", "double_agent", "sleeper"]
            },
            "operation_success_rate": self._calculate_overall_success_rate()
        }
    
    def get_target_intelligence_summary(self, target_civilization: str) -> Dict[str, Any]:
        """Get summary of all intelligence on a specific target."""
        reports = self.get_intelligence_on_target(target_civilization)
        weaknesses = self.analyze_target_weaknesses(target_civilization)
        
        # Count assets targeting this civilization
        targeting_assets = [asset for asset in self.assets.values() 
                          if asset.assigned_target == target_civilization and asset.is_active]
        
        return {
            "target_civilization": target_civilization,
            "intelligence_reports": len(reports),
            "latest_report_date": max([r.collection_date for r in reports]) if reports else None,
            "assigned_assets": len(targeting_assets),
            "identified_weaknesses": weaknesses,
            "recommended_operations": self._recommend_operations(target_civilization, weaknesses),
            "intelligence_coverage": self._assess_intelligence_coverage(reports)
        }
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate of completed operations."""
        if not self.completed_operations:
            return 0.0
        
        successful_ops = sum(1 for op in self.completed_operations.values()
                           if op.outcome in [OperationOutcome.COMPLETE_SUCCESS,
                                           OperationOutcome.PARTIAL_SUCCESS,
                                           OperationOutcome.MINIMAL_SUCCESS])
        
        return successful_ops / len(self.completed_operations)
    
    def _recommend_operations(self, target_civilization: str, 
                            weaknesses: Dict[str, float]) -> List[str]:
        """Recommend operations based on identified target weaknesses."""
        recommendations = []
        
        if weaknesses.get("advisor_corruption", 0) > 0.6:
            recommendations.append("Advisor bribery operations have high success probability")
        
        if weaknesses.get("faction_conflicts", 0) > 0.7:
            recommendations.append("Disinformation campaign to exploit faction tensions")
        
        if weaknesses.get("political_instability", 0) > 0.8:
            recommendations.append("Sabotage mission to accelerate instability")
        
        if weaknesses.get("succession_crisis", 0) > 0.5:
            recommendations.append("Intelligence gathering on succession plans")
        
        return recommendations
    
    def _assess_intelligence_coverage(self, reports: List[IntelligenceReport]) -> Dict[str, str]:
        """Assess how well we understand the target based on available intelligence."""
        coverage = {
            "political_intelligence": "none",
            "advisor_surveillance": "none", 
            "faction_monitoring": "none",
            "military_intelligence": "none"
        }
        
        for report in reports:
            intelligence_type = report.intelligence_type
            if intelligence_type in coverage:
                if report.reliability in [IntelligenceReliability.CONFIRMED, 
                                        IntelligenceReliability.HIGH_CONFIDENCE]:
                    coverage[intelligence_type] = "excellent"
                elif coverage[intelligence_type] in ["none", "poor"]:
                    coverage[intelligence_type] = "moderate"
        
        return coverage
