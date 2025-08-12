"""
Political Technology Tree System

Implements a comprehensive technology tree with political technologies,
advisor lobbying mechanics, and research prerequisite systems.
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field
import uuid
from dataclasses import dataclass


class TechnologyCategory(str, Enum):
    """Categories of political technologies."""
    GOVERNANCE = "governance"
    INFORMATION_CONTROL = "information_control"
    ADMINISTRATIVE = "administrative"
    SOCIAL_ENGINEERING = "social_engineering"
    INTELLIGENCE = "intelligence"


class TechnologyEra(str, Enum):
    """Historical eras for technology progression."""
    ANCIENT = "ancient"
    CLASSICAL = "classical"
    MEDIEVAL = "medieval"
    RENAISSANCE = "renaissance"
    INDUSTRIAL = "industrial"
    MODERN = "modern"
    CONTEMPORARY = "contemporary"
    FUTURE = "future"


class AdvisorCapability(str, Enum):
    """New capabilities unlocked for advisors by technologies."""
    PROPAGANDA_CREATION = "propaganda_creation"
    MASS_SURVEILLANCE = "mass_surveillance"
    BUREAUCRATIC_EFFICIENCY = "bureaucratic_efficiency"
    DIPLOMATIC_IMMUNITY = "diplomatic_immunity"
    ECONOMIC_MANIPULATION = "economic_manipulation"
    MILITARY_INTELLIGENCE = "military_intelligence"
    COUNTER_ESPIONAGE = "counter_espionage"
    MEDIA_CONTROL = "media_control"
    EDUCATION_OVERSIGHT = "education_oversight"
    HEALTHCARE_ADMINISTRATION = "healthcare_administration"


@dataclass
class PoliticalTechnology:
    """Definition of a political technology in the tree."""
    
    tech_id: str
    name: str
    description: str
    category: TechnologyCategory
    era: TechnologyEra
    
    # Research requirements
    prerequisites: List[str]  # Required tech_ids
    alternative_prerequisites: List[List[str]]  # OR-gate prerequisites
    research_cost: float
    
    # Effects and unlocks
    political_effects: Dict[str, Any]
    advisor_unlocks: List[AdvisorCapability]
    espionage_enhancements: Dict[str, float]
    resource_modifiers: Dict[str, float]
    
    # Civilization requirements
    required_civic_level: float = 0.0
    required_population: int = 0
    required_buildings: List[str] = None
    
    # Metadata
    historical_description: str = ""
    unlock_year: int = 0
    
    def __post_init__(self):
        if self.required_buildings is None:
            self.required_buildings = []


class TechnologyNode(BaseModel):
    """A node in the technology tree representing research progress."""
    
    technology: PoliticalTechnology
    unlocked: bool = Field(default=False)
    researched: bool = Field(default=False)
    research_progress: float = Field(default=0.0, ge=0.0)
    
    # Advisor influence on this technology
    advisor_support: Dict[str, float] = Field(default_factory=dict)  # advisor_id -> support_level
    lobbying_pressure: float = Field(default=0.0, ge=0.0)
    
    # Discovery and availability
    available_for_research: bool = Field(default=False)
    discovery_turn: Optional[int] = Field(default=None)


class TechnologyTree(BaseModel):
    """Complete technology tree management system."""
    
    civilization_id: str
    current_turn: int = Field(default=1)
    
    # Technology nodes and progression
    nodes: Dict[str, TechnologyNode] = Field(default_factory=dict)
    research_queue: List[str] = Field(default_factory=list)
    completed_technologies: Set[str] = Field(default_factory=set)
    
    # Research resources
    accumulated_research_points: float = Field(default=0.0)
    research_points_per_turn: float = Field(default=10.0)
    current_research: Optional[str] = Field(default=None)
    
    # Advisor lobbying system
    advisor_technology_preferences: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    research_priority_modifiers: Dict[str, float] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_technology_tree()
    
    def _initialize_technology_tree(self) -> None:
        """Initialize the technology tree with political technologies."""
        technologies = self._get_political_technologies()
        
        for tech in technologies:
            node = TechnologyNode(
                technology=tech,
                unlocked=self._is_initially_unlocked(tech),
                available_for_research=self._is_initially_available(tech)
            )
            self.nodes[tech.tech_id] = node
        
        # Update availability based on prerequisites
        self._update_technology_availability()
    
    def _get_political_technologies(self) -> List[PoliticalTechnology]:
        """Define all political technologies in the tree."""
        technologies = []
        
        # GOVERNANCE CATEGORY
        technologies.extend([
            PoliticalTechnology(
                tech_id="tribal_council",
                name="Tribal Council",
                description="Basic collective decision-making structure",
                category=TechnologyCategory.GOVERNANCE,
                era=TechnologyEra.ANCIENT,
                prerequisites=[],
                alternative_prerequisites=[],
                research_cost=25.0,
                political_effects={"stability_bonus": 0.1, "advisor_loyalty_bonus": 0.05},
                advisor_unlocks=[],
                espionage_enhancements={},
                resource_modifiers={"political_influence": 0.1}
            ),
            PoliticalTechnology(
                tech_id="monarchy",
                name="Monarchy",
                description="Centralized rule under a single leader",
                category=TechnologyCategory.GOVERNANCE,
                era=TechnologyEra.ANCIENT,
                prerequisites=["tribal_council"],
                alternative_prerequisites=[],
                research_cost=50.0,
                political_effects={"authority_bonus": 0.2, "succession_stability": 0.1},
                advisor_unlocks=[AdvisorCapability.DIPLOMATIC_IMMUNITY],
                espionage_enhancements={},
                resource_modifiers={"military_effectiveness": 0.1}
            ),
            PoliticalTechnology(
                tech_id="republic",
                name="Republic",
                description="Representative government with elected officials",
                category=TechnologyCategory.GOVERNANCE,
                era=TechnologyEra.CLASSICAL,
                prerequisites=["tribal_council"],
                alternative_prerequisites=[["law_codes", "written_language"]],
                research_cost=75.0,
                political_effects={"popular_support": 0.15, "corruption_resistance": 0.1},
                advisor_unlocks=[AdvisorCapability.BUREAUCRATIC_EFFICIENCY],
                espionage_enhancements={},
                resource_modifiers={"economic_growth": 0.1, "innovation_rate": 0.05}
            ),
            PoliticalTechnology(
                tech_id="democracy",
                name="Democracy",
                description="Government by the people with universal participation",
                category=TechnologyCategory.GOVERNANCE,
                era=TechnologyEra.MODERN,
                prerequisites=["republic", "mass_education"],
                alternative_prerequisites=[],
                research_cost=200.0,
                political_effects={"legitimacy_bonus": 0.3, "popular_mandate": 0.2},
                advisor_unlocks=[AdvisorCapability.MEDIA_CONTROL],
                espionage_enhancements={"counter_intelligence": 0.2},
                resource_modifiers={"economic_growth": 0.2, "innovation_rate": 0.15}
            ),
            PoliticalTechnology(
                tech_id="federation",
                name="Federation",
                description="Union of semi-autonomous regions under central authority",
                category=TechnologyCategory.GOVERNANCE,
                era=TechnologyEra.MODERN,
                prerequisites=["republic", "administrative_provinces"],
                alternative_prerequisites=[],
                research_cost=180.0,
                political_effects={"regional_stability": 0.25, "diversity_management": 0.2},
                advisor_unlocks=[AdvisorCapability.BUREAUCRATIC_EFFICIENCY],
                espionage_enhancements={},
                resource_modifiers={"trade_efficiency": 0.15, "cultural_unity": 0.1}
            ),
        ])
        
        # INFORMATION CONTROL CATEGORY
        technologies.extend([
            PoliticalTechnology(
                tech_id="written_language",
                name="Written Language",
                description="System of recording and transmitting information",
                category=TechnologyCategory.INFORMATION_CONTROL,
                era=TechnologyEra.ANCIENT,
                prerequisites=[],
                alternative_prerequisites=[],
                research_cost=30.0,
                political_effects={"knowledge_preservation": 0.1, "administrative_efficiency": 0.05},
                advisor_unlocks=[],
                espionage_enhancements={"intelligence_gathering": 0.1},
                resource_modifiers={"research_rate": 0.1}
            ),
            PoliticalTechnology(
                tech_id="state_propaganda",
                name="State Propaganda",
                description="Organized dissemination of political messaging",
                category=TechnologyCategory.INFORMATION_CONTROL,
                era=TechnologyEra.CLASSICAL,
                prerequisites=["written_language"],
                alternative_prerequisites=[],
                research_cost=60.0,
                political_effects={"opinion_control": 0.15, "loyalty_reinforcement": 0.1},
                advisor_unlocks=[AdvisorCapability.PROPAGANDA_CREATION],
                espionage_enhancements={"disinformation": 0.2},
                resource_modifiers={"social_cohesion": 0.1}
            ),
            PoliticalTechnology(
                tech_id="printing_press",
                name="Printing Press",
                description="Mass production of written materials",
                category=TechnologyCategory.INFORMATION_CONTROL,
                era=TechnologyEra.RENAISSANCE,
                prerequisites=["written_language"],
                alternative_prerequisites=[],
                research_cost=100.0,
                political_effects={"information_spread": 0.2, "literacy_improvement": 0.15},
                advisor_unlocks=[AdvisorCapability.MEDIA_CONTROL],
                espionage_enhancements={"propaganda_effectiveness": 0.25},
                resource_modifiers={"education_rate": 0.2, "cultural_development": 0.1}
            ),
            PoliticalTechnology(
                tech_id="mass_media",
                name="Mass Media",
                description="Radio, television, and widespread information distribution",
                category=TechnologyCategory.INFORMATION_CONTROL,
                era=TechnologyEra.MODERN,
                prerequisites=["printing_press", "telecommunications"],
                alternative_prerequisites=[],
                research_cost=150.0,
                political_effects={"public_opinion_influence": 0.3, "narrative_control": 0.25},
                advisor_unlocks=[AdvisorCapability.MEDIA_CONTROL, AdvisorCapability.PROPAGANDA_CREATION],
                espionage_enhancements={"disinformation": 0.3, "propaganda_effectiveness": 0.2},
                resource_modifiers={"cultural_influence": 0.2}
            ),
            PoliticalTechnology(
                tech_id="digital_surveillance",
                name="Digital Surveillance",
                description="Electronic monitoring and data collection systems",
                category=TechnologyCategory.INFORMATION_CONTROL,
                era=TechnologyEra.CONTEMPORARY,
                prerequisites=["mass_media", "computer_networks"],
                alternative_prerequisites=[],
                research_cost=250.0,
                political_effects={"social_monitoring": 0.4, "dissent_detection": 0.3},
                advisor_unlocks=[AdvisorCapability.MASS_SURVEILLANCE],
                espionage_enhancements={"intelligence_gathering": 0.4, "counter_intelligence": 0.3},
                resource_modifiers={"security_effectiveness": 0.3}
            ),
        ])
        
        # ADMINISTRATIVE CATEGORY
        technologies.extend([
            PoliticalTechnology(
                tech_id="law_codes",
                name="Law Codes",
                description="Formal written legal systems and procedures",
                category=TechnologyCategory.ADMINISTRATIVE,
                era=TechnologyEra.ANCIENT,
                prerequisites=["written_language"],
                alternative_prerequisites=[],
                research_cost=40.0,
                political_effects={"legal_stability": 0.15, "justice_consistency": 0.1},
                advisor_unlocks=[],
                espionage_enhancements={},
                resource_modifiers={"social_order": 0.1, "trade_security": 0.05}
            ),
            PoliticalTechnology(
                tech_id="bureaucracy",
                name="Bureaucracy",
                description="Professional administrative class and procedures",
                category=TechnologyCategory.ADMINISTRATIVE,
                era=TechnologyEra.CLASSICAL,
                prerequisites=["law_codes"],
                alternative_prerequisites=[],
                research_cost=80.0,
                political_effects={"administrative_efficiency": 0.2, "policy_implementation": 0.15},
                advisor_unlocks=[AdvisorCapability.BUREAUCRATIC_EFFICIENCY],
                espionage_enhancements={},
                resource_modifiers={"tax_collection": 0.15, "public_works": 0.1}
            ),
            PoliticalTechnology(
                tech_id="census_system",
                name="Census System",
                description="Systematic population and resource accounting",
                category=TechnologyCategory.ADMINISTRATIVE,
                era=TechnologyEra.CLASSICAL,
                prerequisites=["bureaucracy"],
                alternative_prerequisites=[],
                research_cost=70.0,
                political_effects={"resource_tracking": 0.2, "taxation_efficiency": 0.15},
                advisor_unlocks=[],
                espionage_enhancements={"population_monitoring": 0.2},
                resource_modifiers={"economic_planning": 0.15, "military_recruitment": 0.1}
            ),
            PoliticalTechnology(
                tech_id="administrative_provinces",
                name="Administrative Provinces",
                description="Regional governmental subdivisions",
                category=TechnologyCategory.ADMINISTRATIVE,
                era=TechnologyEra.MEDIEVAL,
                prerequisites=["bureaucracy", "census_system"],
                alternative_prerequisites=[],
                research_cost=120.0,
                political_effects={"territorial_control": 0.25, "local_governance": 0.2},
                advisor_unlocks=[AdvisorCapability.BUREAUCRATIC_EFFICIENCY],
                espionage_enhancements={},
                resource_modifiers={"administrative_reach": 0.2, "regional_stability": 0.15}
            ),
        ])
        
        # SOCIAL ENGINEERING CATEGORY
        technologies.extend([
            PoliticalTechnology(
                tech_id="public_education",
                name="Public Education",
                description="State-sponsored education systems",
                category=TechnologyCategory.SOCIAL_ENGINEERING,
                era=TechnologyEra.RENAISSANCE,
                prerequisites=["printing_press", "bureaucracy"],
                alternative_prerequisites=[],
                research_cost=130.0,
                political_effects={"citizen_competency": 0.2, "social_mobility": 0.15},
                advisor_unlocks=[AdvisorCapability.EDUCATION_OVERSIGHT],
                espionage_enhancements={},
                resource_modifiers={"innovation_rate": 0.2, "economic_productivity": 0.15}
            ),
            PoliticalTechnology(
                tech_id="mass_education",
                name="Mass Education",
                description="Universal literacy and standardized curriculum",
                category=TechnologyCategory.SOCIAL_ENGINEERING,
                era=TechnologyEra.INDUSTRIAL,
                prerequisites=["public_education"],
                alternative_prerequisites=[],
                research_cost=180.0,
                political_effects={"national_unity": 0.25, "skilled_workforce": 0.2},
                advisor_unlocks=[AdvisorCapability.EDUCATION_OVERSIGHT],
                espionage_enhancements={},
                resource_modifiers={"industrial_capacity": 0.2, "technological_advancement": 0.15}
            ),
            PoliticalTechnology(
                tech_id="public_healthcare",
                name="Public Healthcare",
                description="State-provided medical services",
                category=TechnologyCategory.SOCIAL_ENGINEERING,
                era=TechnologyEra.MODERN,
                prerequisites=["bureaucracy"],
                alternative_prerequisites=[["mass_education", "medical_knowledge"]],
                research_cost=160.0,
                political_effects={"population_health": 0.25, "social_welfare": 0.2},
                advisor_unlocks=[AdvisorCapability.HEALTHCARE_ADMINISTRATION],
                espionage_enhancements={},
                resource_modifiers={"population_growth": 0.15, "economic_productivity": 0.1}
            ),
            PoliticalTechnology(
                tech_id="social_security",
                name="Social Security",
                description="State welfare and pension systems",
                category=TechnologyCategory.SOCIAL_ENGINEERING,
                era=TechnologyEra.MODERN,
                prerequisites=["public_healthcare", "mass_education"],
                alternative_prerequisites=[],
                research_cost=220.0,
                political_effects={"social_stability": 0.3, "elderly_support": 0.25},
                advisor_unlocks=[AdvisorCapability.BUREAUCRATIC_EFFICIENCY],
                espionage_enhancements={},
                resource_modifiers={"social_cohesion": 0.2, "political_legitimacy": 0.15}
            ),
        ])
        
        # INTELLIGENCE CATEGORY (Building on Task 6.1)
        technologies.extend([
            PoliticalTechnology(
                tech_id="courier_networks",
                name="Courier Networks",
                description="Organized information relay systems",
                category=TechnologyCategory.INTELLIGENCE,
                era=TechnologyEra.ANCIENT,
                prerequisites=[],
                alternative_prerequisites=[],
                research_cost=35.0,
                political_effects={"communication_speed": 0.1},
                advisor_unlocks=[],
                espionage_enhancements={"intelligence_gathering": 0.15, "operation_coordination": 0.1},
                resource_modifiers={"administrative_efficiency": 0.05}
            ),
            PoliticalTechnology(
                tech_id="secret_police",
                name="Secret Police",
                description="Covert law enforcement and surveillance apparatus",
                category=TechnologyCategory.INTELLIGENCE,
                era=TechnologyEra.MEDIEVAL,
                prerequisites=["courier_networks", "law_codes"],
                alternative_prerequisites=[],
                research_cost=90.0,
                political_effects={"internal_security": 0.2, "dissent_suppression": 0.15},
                advisor_unlocks=[AdvisorCapability.COUNTER_ESPIONAGE],
                espionage_enhancements={"counter_intelligence": 0.25, "domestic_surveillance": 0.3},
                resource_modifiers={"regime_stability": 0.15}
            ),
            PoliticalTechnology(
                tech_id="cryptography",
                name="Cryptography",
                description="Secret codes and message encryption",
                category=TechnologyCategory.INTELLIGENCE,
                era=TechnologyEra.RENAISSANCE,
                prerequisites=["written_language"],
                alternative_prerequisites=[],
                research_cost=110.0,
                political_effects={"communication_security": 0.2},
                advisor_unlocks=[],
                espionage_enhancements={"operation_security": 0.3, "counter_intelligence": 0.2},
                resource_modifiers={"diplomatic_security": 0.2}
            ),
            PoliticalTechnology(
                tech_id="intelligence_agencies",
                name="Intelligence Agencies",
                description="Professional espionage organizations",
                category=TechnologyCategory.INTELLIGENCE,
                era=TechnologyEra.MODERN,
                prerequisites=["secret_police", "cryptography"],
                alternative_prerequisites=[],
                research_cost=200.0,
                political_effects={"foreign_intelligence": 0.3, "covert_operations": 0.25},
                advisor_unlocks=[AdvisorCapability.MILITARY_INTELLIGENCE, AdvisorCapability.COUNTER_ESPIONAGE],
                espionage_enhancements={"all_operations": 0.3, "asset_training": 0.2},
                resource_modifiers={"national_security": 0.2}
            ),
            PoliticalTechnology(
                tech_id="signals_intelligence",
                name="Signals Intelligence",
                description="Electronic communication interception",
                category=TechnologyCategory.INTELLIGENCE,
                era=TechnologyEra.CONTEMPORARY,
                prerequisites=["intelligence_agencies", "telecommunications"],
                alternative_prerequisites=[],
                research_cost=280.0,
                political_effects={"electronic_surveillance": 0.4},
                advisor_unlocks=[AdvisorCapability.MASS_SURVEILLANCE],
                espionage_enhancements={"intelligence_gathering": 0.4, "counter_intelligence": 0.3},
                resource_modifiers={"information_warfare": 0.3}
            ),
        ])
        
        return technologies
    
    def _is_initially_unlocked(self, tech: PoliticalTechnology) -> bool:
        """Check if a technology should be unlocked from the start."""
        # Ancient era technologies with no prerequisites are initially unlocked
        return tech.era == TechnologyEra.ANCIENT and not tech.prerequisites
    
    def _is_initially_available(self, tech: PoliticalTechnology) -> bool:
        """Check if a technology should be available for research from the start."""
        # Available if unlocked and all prerequisites are met
        return self._is_initially_unlocked(tech)
    
    def _update_technology_availability(self) -> None:
        """Update which technologies are available for research."""
        for tech_id, node in self.nodes.items():
            if node.researched:
                continue
            
            tech = node.technology
            can_research = True
            
            # Check prerequisites
            for prereq_id in tech.prerequisites:
                if prereq_id not in self.completed_technologies:
                    can_research = False
                    break
            
            # Check alternative prerequisites (OR-gates)
            if not can_research and tech.alternative_prerequisites:
                for alt_prereqs in tech.alternative_prerequisites:
                    if all(prereq in self.completed_technologies for prereq in alt_prereqs):
                        can_research = True
                        break
            
            node.available_for_research = can_research
            if can_research:
                node.unlocked = True
    
    def can_research_technology(self, tech_id: str) -> bool:
        """Check if a technology can be researched."""
        if tech_id not in self.nodes:
            return False
        
        node = self.nodes[tech_id]
        return (node.available_for_research and 
                not node.researched and 
                tech_id not in self.research_queue)
    
    def add_to_research_queue(self, tech_id: str, priority_position: Optional[int] = None) -> bool:
        """Add a technology to the research queue."""
        if not self.can_research_technology(tech_id):
            return False
        
        if priority_position is None:
            self.research_queue.append(tech_id)
        else:
            self.research_queue.insert(min(priority_position, len(self.research_queue)), tech_id)
        
        return True
    
    def start_research(self, tech_id: str) -> bool:
        """Start researching a specific technology."""
        if not self.can_research_technology(tech_id):
            return False
        
        # Stop current research if any
        if self.current_research:
            # Move current research back to queue
            self.research_queue.insert(0, self.current_research)
        
        self.current_research = tech_id
        if tech_id in self.research_queue:
            self.research_queue.remove(tech_id)
        
        return True
    
    def research_technology(self, tech_id: str) -> bool:
        """Directly complete research of a technology (for testing/admin purposes)."""
        if tech_id not in self.nodes:
            return False
        
        node = self.nodes[tech_id]
        if node.researched:
            return False  # Already researched
        
        # Mark as researched
        node.researched = True
        node.research_progress = node.technology.research_cost
        self.completed_technologies.add(tech_id)
        
        # Update availability of dependent technologies
        self._unlock_dependent_technologies(tech_id)
        
        return True
    
    def process_research_turn(self, additional_research_points: float = 0.0) -> Dict[str, Any]:
        """Process one turn of research progress."""
        results = {
            "research_progress": 0.0,
            "completed_technologies": [],
            "new_unlocks": [],
            "advisor_influence_applied": {}
        }
        
        if not self.current_research:
            self._start_next_research()
        
        if not self.current_research:
            return results
        
        # Calculate research points for this turn
        base_research = self.research_points_per_turn
        advisor_influence = self._calculate_advisor_research_influence(self.current_research)
        total_research = base_research + additional_research_points + advisor_influence
        
        results["research_progress"] = total_research
        results["advisor_influence_applied"][self.current_research] = advisor_influence
        
        # Apply research progress
        self.accumulated_research_points += total_research
        current_node = self.nodes[self.current_research]
        current_node.research_progress += total_research
        
        # Check if research is complete
        tech = current_node.technology
        if self.accumulated_research_points >= tech.research_cost:
            # Complete the research
            self.accumulated_research_points -= tech.research_cost
            current_node.researched = True
            current_node.research_progress = tech.research_cost
            self.completed_technologies.add(self.current_research)
            
            results["completed_technologies"].append(self.current_research)
            
            # Update availability of new technologies
            newly_unlocked = self._unlock_dependent_technologies(self.current_research)
            results["new_unlocks"] = newly_unlocked
            
            # Start next research
            self.current_research = None
            self._start_next_research()
        
        self.current_turn += 1
        return results
    
    def _start_next_research(self) -> None:
        """Start the next technology in the research queue."""
        while self.research_queue:
            next_tech = self.research_queue.pop(0)
            if self.can_research_technology(next_tech):
                self.current_research = next_tech
                break
    
    def _unlock_dependent_technologies(self, completed_tech_id: str) -> List[str]:
        """Unlock technologies that depend on the completed technology."""
        newly_unlocked = []
        
        for tech_id, node in self.nodes.items():
            if node.unlocked or node.researched:
                continue
            
            tech = node.technology
            
            # Check if this tech depends on the completed one
            depends_on_completed = (
                completed_tech_id in tech.prerequisites or
                any(completed_tech_id in alt_prereqs for alt_prereqs in tech.alternative_prerequisites)
            )
            
            if depends_on_completed:
                # Re-check if all prerequisites are now met
                self._update_technology_availability()
                if node.available_for_research:
                    newly_unlocked.append(tech_id)
        
        return newly_unlocked
    
    def _calculate_advisor_research_influence(self, tech_id: str) -> float:
        """Calculate how advisor lobbying affects research speed."""
        if tech_id not in self.nodes:
            return 0.0
        
        node = self.nodes[tech_id]
        total_influence = 0.0
        
        # Sum up advisor support for this technology
        for advisor_id, support_level in node.advisor_support.items():
            # Get advisor influence modifier
            influence_modifier = self.research_priority_modifiers.get(advisor_id, 1.0)
            total_influence += support_level * influence_modifier
        
        # Apply lobbying pressure bonus
        lobbying_bonus = node.lobbying_pressure * 0.1  # 10% per lobbying pressure point
        
        return total_influence + lobbying_bonus
    
    def get_available_technologies(self) -> List[str]:
        """Get list of technologies available for research."""
        return [
            tech_id for tech_id, node in self.nodes.items()
            if node.available_for_research and not node.researched
        ]
    
    def get_research_priorities_by_advisor_influence(self) -> List[Tuple[str, float]]:
        """Get technologies sorted by advisor influence and lobbying."""
        available_techs = self.get_available_technologies()
        
        tech_scores = []
        for tech_id in available_techs:
            influence_score = self._calculate_advisor_research_influence(tech_id)
            tech_scores.append((tech_id, influence_score))
        
        # Sort by influence score (highest first)
        tech_scores.sort(key=lambda x: x[1], reverse=True)
        return tech_scores
    
    def apply_technology_effects(self, tech_id: str) -> Dict[str, Any]:
        """Apply the effects of a completed technology."""
        if tech_id not in self.nodes or not self.nodes[tech_id].researched:
            return {}
        
        tech = self.nodes[tech_id].technology
        return {
            "political_effects": tech.political_effects.copy(),
            "advisor_unlocks": tech.advisor_unlocks.copy(),
            "espionage_enhancements": tech.espionage_enhancements.copy(),
            "resource_modifiers": tech.resource_modifiers.copy()
        }
    
    def get_technology_tree_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the technology tree state."""
        completed_by_category = {}
        available_by_category = {}
        
        for category in TechnologyCategory:
            completed_by_category[category.value] = []
            available_by_category[category.value] = []
        
        for tech_id, node in self.nodes.items():
            category = node.technology.category.value
            if node.researched:
                completed_by_category[category].append(tech_id)
            elif node.available_for_research:
                available_by_category[category].append(tech_id)
        
        return {
            "civilization_id": self.civilization_id,
            "current_turn": self.current_turn,
            "current_research": self.current_research,
            "accumulated_research": self.accumulated_research_points,
            "research_per_turn": self.research_points_per_turn,
            "total_completed": len(self.completed_technologies),
            "completed_by_category": completed_by_category,
            "available_by_category": available_by_category,
            "research_queue": self.research_queue.copy(),
            "technologies_by_era": self._get_technologies_by_era()
        }
    
    def _get_technologies_by_era(self) -> Dict[str, List[str]]:
        """Get technologies organized by historical era."""
        by_era = {}
        for era in TechnologyEra:
            by_era[era.value] = []
        
        for tech_id, node in self.nodes.items():
            era = node.technology.era.value
            status = "researched" if node.researched else ("available" if node.available_for_research else "locked")
            by_era[era].append(f"{tech_id} ({status})")
        
        return by_era
