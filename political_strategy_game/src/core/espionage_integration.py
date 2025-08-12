"""
Espionage Integration Module for Political Strategy Game

Integrates the espionage system with existing game components including
diplomacy, information warfare, advisors, and the main game engine.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from src.core.espionage import EspionageManager, EspionageOperationType, OperationOutcome
from src.core.diplomacy import DiplomaticRelationship


class EspionageGameIntegration:
    """
    Integrates espionage operations with the main game systems.
    
    Handles diplomatic consequences, advisor interactions, and
    information warfare coordination.
    """
    
    def __init__(self, game_engine, espionage_manager: EspionageManager):
        """Initialize espionage integration."""
        self.game_engine = game_engine
        self.espionage_manager = espionage_manager
        self.logger = logging.getLogger(__name__)
        
        # Track diplomatic incidents caused by espionage
        self.diplomatic_incidents = []
        
        # Cache for efficiency
        self._cached_intelligence = {}
        self._cache_expires = {}
    
    def process_espionage_turn(self, current_turn: int) -> Dict[str, Any]:
        """
        Process all espionage activities for the current turn.
        
        Args:
            current_turn: Current game turn number
            
        Returns:
            Dict containing espionage results and consequences
        """
        results = {
            "operations_completed": [],
            "intelligence_gathered": [],
            "diplomatic_incidents": [],
            "counter_intelligence_alerts": [],
            "asset_status_changes": []
        }
        
        # Process ongoing operations
        operation_results = self.espionage_manager.process_operations_turn(current_turn)
        
        for result in operation_results:
            operation_id = result["operation_id"]
            operation = self.espionage_manager.get_operation(operation_id)
            
            if not operation:
                continue
                
            # Handle successful operations
            if result.get("outcome") in [OperationOutcome.COMPLETE_SUCCESS, 
                                       OperationOutcome.PARTIAL_SUCCESS]:
                self._handle_successful_operation(operation, result, results)
            
            # Handle discovered operations
            if result.get("discovered", False):
                self._handle_discovered_operation(operation, result, results)
            
            # Handle failed operations
            if result.get("outcome") == OperationOutcome.CRITICAL_FAILURE:
                self._handle_failed_operation(operation, result, results)
        
        # Update diplomatic relationships
        self._update_diplomatic_consequences(results["diplomatic_incidents"])
        
        # Process counter-intelligence
        self._process_counter_intelligence(current_turn, results)
        
        return results
    
    def _handle_successful_operation(self, operation, result: Dict, results: Dict):
        """Handle successful espionage operations."""
        target_civ = operation.target_civilization
        
        if operation.operation_type == EspionageOperationType.POLITICAL_INTELLIGENCE:
            # Gather political intelligence
            intelligence = self._extract_political_intelligence(target_civ)
            results["intelligence_gathered"].append({
                "type": "political",
                "target": target_civ,
                "data": intelligence,
                "reliability": result.get("reliability", "moderate")
            })
            
        elif operation.operation_type == EspionageOperationType.ADVISOR_SURVEILLANCE:
            # Surveillance on specific advisor
            advisor_intel = self._extract_advisor_intelligence(
                target_civ, operation.target_advisor
            )
            results["intelligence_gathered"].append({
                "type": "advisor_surveillance",
                "target": target_civ,
                "advisor": operation.target_advisor,
                "data": advisor_intel,
                "reliability": result.get("reliability", "high")
            })
            
        elif operation.operation_type == EspionageOperationType.DISINFORMATION_CAMPAIGN:
            # Successfully planted disinformation
            self._apply_disinformation_effects(operation, result)
            
        elif operation.operation_type == EspionageOperationType.ADVISOR_BRIBERY:
            # Successful bribery - gain ongoing intelligence
            self._establish_bribed_advisor(operation, result)
            
        elif operation.operation_type == EspionageOperationType.SABOTAGE_MISSION:
            # Sabotage successful - apply damage
            self._apply_sabotage_effects(operation, result)
        
        results["operations_completed"].append({
            "operation_id": operation.operation_id,
            "type": operation.operation_type.value,
            "outcome": "success",
            "target": target_civ
        })
    
    def _handle_discovered_operation(self, operation, result: Dict, results: Dict):
        """Handle operations that were discovered by counter-intelligence."""
        target_civ = operation.target_civilization
        
        # Create diplomatic incident
        incident = {
            "type": "espionage_discovery",
            "perpetrator": self.espionage_manager.civilization_id,
            "victim": target_civ,
            "operation_type": operation.operation_type.value,
            "severity": self._calculate_incident_severity(operation),
            "turn": result.get("turn", 0),
            "evidence_strength": result.get("evidence_strength", 0.7)
        }
        
        results["diplomatic_incidents"].append(incident)
        self.diplomatic_incidents.append(incident)
        
        # Burn any compromised assets
        for asset_id in operation.assigned_assets:
            asset = self.espionage_manager.get_asset(asset_id)
            if asset and not asset.is_compromised:
                self.espionage_manager.burn_asset(asset_id, "operation_discovered")
                results["asset_status_changes"].append({
                    "asset_id": asset_id,
                    "status": "burned",
                    "reason": "operation_discovered"
                })
    
    def _handle_failed_operation(self, operation, result: Dict, results: Dict):
        """Handle critically failed operations."""
        # Mark involved assets as potentially compromised
        for asset_id in operation.assigned_assets:
            asset = self.espionage_manager.get_asset(asset_id)
            if asset:
                # Increase exposure risk
                asset.exposure_risk = min(1.0, asset.exposure_risk + 0.3)
                if asset.exposure_risk > 0.8:
                    self.espionage_manager.burn_asset(asset_id, "critical_failure")
                    results["asset_status_changes"].append({
                        "asset_id": asset_id,
                        "status": "burned",
                        "reason": "critical_failure"
                    })
    
    def _extract_political_intelligence(self, target_civilization: str) -> Dict[str, Any]:
        """Extract political intelligence from target civilization."""
        try:
            # Get civilization data from game engine
            target_civ_data = self.game_engine.get_civilization(target_civilization)
            if not target_civ_data:
                return {"error": "Target civilization not found"}
            
            intelligence = {
                "political_stability": getattr(target_civ_data, 'political_stability', 0.5),
                "leader_approval": getattr(target_civ_data, 'leader_approval', 0.5),
                "economic_strength": getattr(target_civ_data, 'economic_strength', 0.5),
                "military_readiness": getattr(target_civ_data, 'military_readiness', 0.5),
                "technology_level": getattr(target_civ_data, 'technology_level', 0.5),
                "recent_decisions": getattr(target_civ_data, 'recent_decisions', []),
                "active_policies": getattr(target_civ_data, 'active_policies', []),
                "resource_levels": getattr(target_civ_data, 'resources', {})
            }
            
            # Add faction analysis if available
            if hasattr(target_civ_data, 'factions'):
                intelligence["faction_analysis"] = {
                    faction.name: {
                        "influence": faction.influence_points,
                        "loyalty": faction.loyalty_to_leader,
                        "agenda": faction.current_agenda
                    }
                    for faction in target_civ_data.factions
                }
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"Failed to extract political intelligence: {e}")
            return {"error": "Intelligence gathering failed"}
    
    def _extract_advisor_intelligence(self, target_civilization: str, 
                                    advisor_id: str) -> Dict[str, Any]:
        """Extract intelligence on specific advisor."""
        try:
            # Get advisor data from game engine
            advisor_data = self.game_engine.get_advisor(target_civilization, advisor_id)
            if not advisor_data:
                return {"error": "Target advisor not found"}
            
            intelligence = {
                "advisor_id": advisor_id,
                "role": getattr(advisor_data, 'role', 'unknown'),
                "personality_traits": getattr(advisor_data, 'personality_traits', {}),
                "influence_level": getattr(advisor_data, 'influence_level', 0.5),
                "loyalty_to_leader": getattr(advisor_data, 'loyalty_to_leader', 0.5),
                "corruption_level": getattr(advisor_data, 'corruption_level', 0.0),
                "recent_advice": getattr(advisor_data, 'recent_advice', []),
                "personal_agenda": getattr(advisor_data, 'personal_agenda', "unknown"),
                "vulnerabilities": self._identify_advisor_vulnerabilities(advisor_data),
                "communication_patterns": getattr(advisor_data, 'communication_log', [])
            }
            
            # Add memory analysis if available
            if hasattr(advisor_data, 'memories'):
                intelligence["key_memories"] = [
                    {
                        "content": memory.content[:100] + "...",  # Truncated for security
                        "importance": memory.importance,
                        "category": memory.category
                    }
                    for memory in advisor_data.memories[-5:]  # Last 5 memories
                ]
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"Failed to extract advisor intelligence: {e}")
            return {"error": "Advisor intelligence gathering failed"}
    
    def _identify_advisor_vulnerabilities(self, advisor_data) -> List[str]:
        """Identify potential vulnerabilities in target advisor."""
        vulnerabilities = []
        
        # Check for corruption
        if getattr(advisor_data, 'corruption_level', 0.0) > 0.3:
            vulnerabilities.append("susceptible_to_bribery")
        
        # Check for low loyalty
        if getattr(advisor_data, 'loyalty_to_leader', 1.0) < 0.4:
            vulnerabilities.append("potential_defector")
        
        # Check personality traits
        traits = getattr(advisor_data, 'personality_traits', {})
        if traits.get('greed', 0.0) > 0.6:
            vulnerabilities.append("greedy")
        if traits.get('ambition', 0.0) > 0.8:
            vulnerabilities.append("overly_ambitious")
        if traits.get('paranoia', 0.0) > 0.7:
            vulnerabilities.append("paranoid")
        
        # Check for personal problems
        if hasattr(advisor_data, 'personal_issues'):
            vulnerabilities.extend(advisor_data.personal_issues)
        
        return vulnerabilities
    
    def _apply_disinformation_effects(self, operation, result: Dict):
        """Apply effects of successful disinformation campaign."""
        target_civ = operation.target_civilization
        target_advisor = operation.target_advisor
        false_info = operation.intelligence_gathered.get("disinformation_payload", {})
        
        try:
            # Get target advisor
            advisor = self.game_engine.get_advisor(target_civ, target_advisor)
            if advisor and hasattr(advisor, 'add_memory'):
                # Plant false memories/information
                for category, content in false_info.items():
                    fake_memory = {
                        "content": content,
                        "category": category,
                        "importance": 0.8,  # High importance for better integration
                        "source": "disinformation",  # Hidden tag for tracking
                        "planted": True
                    }
                    advisor.add_memory(fake_memory)
                    
                self.logger.info(f"Successfully planted disinformation in {target_advisor}")
        
        except Exception as e:
            self.logger.error(f"Failed to apply disinformation: {e}")
    
    def _establish_bribed_advisor(self, operation, result: Dict):
        """Establish ongoing intelligence from bribed advisor."""
        target_civ = operation.target_civilization
        target_advisor = operation.target_advisor
        
        # Create ongoing intelligence asset
        bribed_asset = self.espionage_manager.recruit_asset(
            asset_type="corrupted_advisor",
            target_civilization=target_civ,
            specialization=[EspionageOperationType.POLITICAL_INTELLIGENCE,
                          EspionageOperationType.ADVISOR_SURVEILLANCE],
            skill_level=0.8,  # High skill due to inside access
            asset_name=f"Corrupted_{target_advisor}"
        )
        
        # Mark as special asset with ongoing intelligence
        bribed_asset.special_capabilities = ["ongoing_intelligence", "decision_preview"]
        bribed_asset.intelligence_frequency = 1  # Reports every turn
        
        self.logger.info(f"Established bribed advisor asset: {target_advisor}")
    
    def _apply_sabotage_effects(self, operation, result: Dict):
        """Apply effects of successful sabotage mission."""
        target_civ = operation.target_civilization
        sabotage_target = operation.intelligence_gathered.get("sabotage_target")
        
        try:
            target_civ_data = self.game_engine.get_civilization(target_civ)
            if not target_civ_data:
                return
            
            if sabotage_target == "communication_networks":
                # Reduce information sharing between advisors
                if hasattr(target_civ_data, 'communication_efficiency'):
                    target_civ_data.communication_efficiency *= 0.7
                    
            elif sabotage_target == "resource_infrastructure":
                # Reduce resource generation
                if hasattr(target_civ_data, 'resources'):
                    for resource, amount in target_civ_data.resources.items():
                        target_civ_data.resources[resource] = amount * 0.85
                        
            elif sabotage_target == "military_coordination":
                # Reduce military effectiveness
                if hasattr(target_civ_data, 'military_readiness'):
                    target_civ_data.military_readiness *= 0.8
            
            self.logger.info(f"Applied sabotage effects to {target_civ}: {sabotage_target}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply sabotage effects: {e}")
    
    def _calculate_incident_severity(self, operation) -> str:
        """Calculate diplomatic incident severity based on operation type."""
        severity_map = {
            EspionageOperationType.POLITICAL_INTELLIGENCE: "minor",
            EspionageOperationType.ADVISOR_SURVEILLANCE: "moderate",
            EspionageOperationType.DISINFORMATION_CAMPAIGN: "serious",
            EspionageOperationType.ADVISOR_BRIBERY: "serious",
            EspionageOperationType.SABOTAGE_MISSION: "severe",
            EspionageOperationType.ASSASSINATION_ATTEMPT: "extreme",
            EspionageOperationType.MEMORY_EXTRACTION: "severe"
        }
        return severity_map.get(operation.operation_type, "moderate")
    
    def _update_diplomatic_consequences(self, incidents: List[Dict]):
        """Update diplomatic relationships based on espionage incidents."""
        for incident in incidents:
            perpetrator = incident["perpetrator"]
            victim = incident["victim"]
            severity = incident["severity"]
            
            try:
                # Get diplomatic relationship
                relationship = self.game_engine.get_diplomatic_relationship(
                    perpetrator, victim
                )
                
                if relationship:
                    # Apply trust penalties based on severity
                    trust_penalty = {
                        "minor": -0.1,
                        "moderate": -0.2,
                        "serious": -0.4,
                        "severe": -0.6,
                        "extreme": -0.8
                    }.get(severity, -0.2)
                    
                    relationship.trust_level += trust_penalty
                    relationship.trust_level = max(0.0, relationship.trust_level)
                    
                    # Add incident to diplomatic history
                    if hasattr(relationship, 'add_incident'):
                        relationship.add_incident(incident)
                        
                    self.logger.info(f"Applied diplomatic penalty: {perpetrator} -> {victim} ({trust_penalty})")
            
            except Exception as e:
                self.logger.error(f"Failed to update diplomatic consequences: {e}")
    
    def _process_counter_intelligence(self, current_turn: int, results: Dict):
        """Process counter-intelligence activities."""
        # Conduct periodic security audits
        if current_turn % 5 == 0:  # Every 5 turns
            audit_results = self.espionage_manager.conduct_security_audit()
            
            if audit_results["security_score"] < 0.5:
                results["counter_intelligence_alerts"].append({
                    "type": "security_vulnerability",
                    "severity": "high",
                    "recommendations": audit_results["recommendations"]
                })
        
        # Check for suspicious activities against us
        suspicious_activities = self._detect_enemy_espionage()
        for activity in suspicious_activities:
            results["counter_intelligence_alerts"].append(activity)
            
            # Launch counter-operation if confidence is high
            if activity.get("confidence", 0.0) > 0.7:
                counter_op = self.espionage_manager.launch_counter_operation(
                    activity["suspected_operation"], activity["source_civilization"]
                )
                results["operations_completed"].append({
                    "operation_id": counter_op.operation_id,
                    "type": "counter_surveillance",
                    "target": activity["source_civilization"]
                })
    
    def _detect_enemy_espionage(self) -> List[Dict]:
        """Detect potential enemy espionage activities."""
        suspicious_activities = []
        
        try:
            # Check for unusual advisor behavior patterns
            our_civ = self.game_engine.get_civilization(
                self.espionage_manager.civilization_id
            )
            
            if hasattr(our_civ, 'advisors'):
                for advisor in our_civ.advisors:
                    # Check for suspicious memory patterns
                    if hasattr(advisor, 'memories'):
                        suspicious_memories = [
                            m for m in advisor.memories 
                            if getattr(m, 'source', '') == 'disinformation' or
                               getattr(m, 'planted', False)
                        ]
                        
                        if suspicious_memories:
                            suspicious_activities.append({
                                "type": "memory_manipulation",
                                "target_advisor": advisor.advisor_id,
                                "confidence": 0.8,
                                "evidence": f"Found {len(suspicious_memories)} suspicious memories"
                            })
            
            # Check for resource anomalies (potential sabotage)
            if hasattr(our_civ, 'resources'):
                for resource, amount in our_civ.resources.items():
                    expected_amount = getattr(our_civ, f'expected_{resource}', amount)
                    if amount < expected_amount * 0.9:  # 10% or more reduction
                        suspicious_activities.append({
                            "type": "resource_sabotage",
                            "affected_resource": resource,
                            "confidence": 0.6,
                            "evidence": f"{resource} below expected levels"
                        })
        
        except Exception as e:
            self.logger.error(f"Failed to detect enemy espionage: {e}")
        
        return suspicious_activities
    
    def get_intelligence_briefing(self, target_civilization: str = None) -> Dict[str, Any]:
        """Get comprehensive intelligence briefing."""
        briefing = {
            "summary": self.espionage_manager.get_espionage_summary(),
            "recent_operations": [],
            "active_threats": [],
            "recommendations": []
        }
        
        # Get recent completed operations
        for op_id, operation in self.espionage_manager.completed_operations.items():
            if operation.completion_turn and operation.completion_turn >= self.game_engine.current_turn - 3:
                briefing["recent_operations"].append({
                    "operation_type": operation.operation_type.value,
                    "target": operation.target_civilization,
                    "outcome": operation.outcome.value if operation.outcome else "unknown",
                    "intelligence_value": len(operation.intelligence_gathered)
                })
        
        # Get target-specific intelligence if requested
        if target_civilization:
            target_summary = self.espionage_manager.get_target_intelligence_summary(
                target_civilization
            )
            briefing["target_analysis"] = target_summary
        
        # Add strategic recommendations
        briefing["recommendations"] = self._generate_strategic_recommendations()
        
        return briefing
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic espionage recommendations."""
        recommendations = []
        
        # Check asset levels
        summary = self.espionage_manager.get_espionage_summary()
        if summary["active_assets"] < 3:
            recommendations.append("Consider recruiting more espionage assets")
        
        # Check budget allocation
        if self.espionage_manager.intelligence_budget < 200:
            recommendations.append("Increase intelligence budget allocation")
        
        # Check technology level
        if self.espionage_manager.technology_level < 0.6:
            recommendations.append("Invest in espionage technology upgrades")
        
        # Check counter-intelligence
        if self.espionage_manager.counter_intelligence_strength < 0.5:
            recommendations.append("Strengthen counter-intelligence capabilities")
        
        # Check for security vulnerabilities
        if len(self.diplomatic_incidents) > 3:
            recommendations.append("Review operational security - too many discoveries")
        
        return recommendations
