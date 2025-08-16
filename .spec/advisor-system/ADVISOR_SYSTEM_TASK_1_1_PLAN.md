# Advisor System Task 1.1: Citizen Data Structure - Implementation Plan

## Task Overview

**Task 1.1: Citizen Data Structure**
- **Effort**: 3 days
- **Priority**: High
- **Dependencies**: None
- **Location**: New implementation in `/src/core/citizen.py`

## Current Status Analysis

### ✅ **Available Foundation**
- **Core Architecture**: Complete GameState coordination and era progression
- **Memory Systems**: Advanced memory management for citizen history tracking
- **Technology System**: Era-appropriate technology and skill definitions
- **Resource System**: Population tracking as ResourceType.POPULATION
- **Save System**: Advanced persistence system for citizen data

### 🔍 **Gap Analysis**
- **No existing Citizen class**: Need to create from scratch
- **No population tracking**: Currently only high-level population resource counts
- **No skill systems**: Need to create skill tracking and development
- **No achievement systems**: Need achievement categorization and tracking

---

## Acceptance Criteria Analysis

### ✅ **1. Citizen class with extensible skill and trait dictionaries**

**Requirements**:
- Flexible skill system supporting era-specific skills
- Trait system for personality and aptitude characteristics
- Extensible design for future skill/trait additions
- Efficient storage for large population tracking

**Implementation Strategy**:
```python
class Citizen:
    # Core identity
    id: str
    name: str
    birth_turn: int
    era_born: TechnologyEra
    
    # Skills (era-appropriate)
    skills: Dict[str, float]  # skill_name -> proficiency (0.0-1.0)
    
    # Traits (personality & aptitude)
    traits: Dict[str, float]  # trait_name -> strength (-1.0 to 1.0)
    
    # Advisor potential
    advisor_potential: float
    potential_roles: Set[AdvisorRole]
```

### ✅ **2. Achievement tracking system with categorization**

**Requirements**:
- Achievement categories (Military, Economic, Diplomatic, Cultural, Technological)
- Achievement impact on advisor potential
- Historical achievement tracking
- Era-appropriate achievement types

**Implementation Strategy**:
```python
class Achievement:
    id: str
    category: AchievementCategory
    title: str
    description: str
    impact_on_advisor_potential: float
    era_granted: TechnologyEra
    turn_granted: int

class AchievementCategory(Enum):
    MILITARY = "military"
    ECONOMIC = "economic" 
    DIPLOMATIC = "diplomatic"
    CULTURAL = "cultural"
    TECHNOLOGICAL = "technological"
    LEADERSHIP = "leadership"
```

### ✅ **3. Social relationship and network connection modeling**

**Requirements**:
- Social network connections between citizens
- Relationship strength tracking
- Family/clan relationships
- Professional/guild relationships
- Political alliance tracking

**Implementation Strategy**:
```python
class SocialRelationship:
    citizen_a: str  # citizen ID
    citizen_b: str  # citizen ID
    relationship_type: RelationshipType
    strength: float  # 0.0-1.0
    established_turn: int

class RelationshipType(Enum):
    FAMILY = "family"
    PROFESSIONAL = "professional"
    POLITICAL = "political"
    MENTOR_STUDENT = "mentor_student"
    RIVAL = "rival"
```

### ✅ **4. Advisor potential calculation algorithms**

**Requirements**:
- Multi-factor advisor potential scoring
- Era-specific skill weighting
- Achievement impact calculation
- Social network influence assessment
- Dynamic recalculation over time

**Implementation Strategy**:
```python
def calculate_advisor_potential(citizen: Citizen, era: TechnologyEra) -> float:
    # Era-specific skill weighting
    skill_score = calculate_era_weighted_skills(citizen.skills, era)
    
    # Achievement impact
    achievement_score = sum(achievement.impact_on_advisor_potential 
                          for achievement in citizen.achievements)
    
    # Social network influence
    network_score = calculate_social_influence(citizen.id, relationships)
    
    # Trait suitability for leadership
    trait_score = calculate_leadership_traits(citizen.traits)
    
    return weighted_average([skill_score, achievement_score, network_score, trait_score])
```

### ✅ **5. Era-appropriate citizen generation**

**Requirements**:
- Era-specific skill distributions
- Historical accuracy in citizen characteristics
- Era-appropriate name generation
- Technology-influenced citizen capabilities
- Cultural context for citizen generation

**Implementation Strategy**:
```python
def generate_era_appropriate_citizen(era: TechnologyEra, turn: int) -> Citizen:
    # Era-specific skill probabilities
    skills = generate_era_skills(era)
    
    # Era-appropriate traits
    traits = generate_era_traits(era)
    
    # Era-appropriate name
    name = generate_era_name(era)
    
    return Citizen(name=name, skills=skills, traits=traits, era_born=era)
```

---

## Integration Points

### 🔗 **Core Architecture Integration**
- **GameState**: Citizens tied to civilization and era progression
- **Turn Management**: Citizen skill development and aging during turn advancement
- **Era Progression**: Era transitions affect citizen skill valuations and opportunities

### 🔗 **Existing System Integration**
- **AdvisorWithMemory**: Citizens can be promoted to advisors with full memory integration
- **ResourceManager**: Population resource tracking enhanced with citizen detail
- **TechnologyTree**: Technology unlocks affect citizen skill development opportunities
- **SaveGameManager**: Citizen data persisted with civilization state

---

## Implementation Plan

### **Day 1: Core Citizen Data Structure**
1. **Create `src/core/citizen.py`**
   - Citizen class with Pydantic validation
   - Basic skill and trait dictionaries
   - Integration with TechnologyEra enum
   - Unique ID generation and name system

2. **Era-specific skill definitions**
   - Ancient era: combat, crafting, leadership, agriculture
   - Classical era: add engineering, philosophy, administration
   - Medieval era: add scholarship, trade, diplomacy
   - Progressive skill additions through eras

### **Day 2: Achievement and Relationship Systems**
1. **Achievement system implementation**
   - Achievement class with categorization
   - Achievement impact on advisor potential
   - Era-appropriate achievement types
   - Achievement granting mechanisms

2. **Social relationship modeling**
   - SocialRelationship class
   - Relationship type definitions
   - Network connection algorithms
   - Relationship strength calculations

### **Day 3: Advisor Potential and Generation**
1. **Advisor potential calculation**
   - Multi-factor scoring algorithm
   - Era-specific skill weighting
   - Social network influence assessment
   - Dynamic recalculation system

2. **Era-appropriate citizen generation**
   - Era-specific generation parameters
   - Historical accuracy in characteristics
   - Integration with existing civilization creation
   - Batch citizen generation for population initialization

3. **Testing and validation**
   - Unit tests for all citizen functionality
   - Integration tests with existing systems
   - Performance testing for large populations
   - Era progression impact validation

---

## Expected Outcomes

### **Immediate Benefits**
- **Foundation for Advisor Emergence**: Citizens provide authentic pool for advisor selection
- **Population Depth**: Rich population simulation enhances immersion
- **Era Authenticity**: Era-appropriate citizen characteristics and skills
- **Strategic Depth**: Population development affects advisor quality

### **Integration with Existing Systems**
- **AdvisorWithMemory**: Citizens promoted to advisors retain full history
- **Memory System**: Citizen achievements and relationships create advisor memories
- **Era Progression**: Citizen development drives era transition readiness
- **Resource Management**: Detailed population tracking enhances strategic decisions

### **Foundation for Future Tasks**
- **Task 1.2**: Population skill distribution algorithms
- **Task 1.3**: Agent pool management (top 1-5% tracking)
- **Task 1.4**: Advisor candidate selection algorithms
- **Future Systems**: Population evolution, crisis impact on citizens

---

## Technical Considerations

### **Performance Optimization**
- **Efficient Data Structures**: Use appropriate data structures for large populations
- **Lazy Loading**: Load citizen details only when needed
- **Caching**: Cache advisor potential calculations
- **Database Design**: Consider future database integration for massive populations

### **Extensibility**
- **Skill System**: Easily add new skills for future eras or mods
- **Trait System**: Extensible trait framework for diverse characteristics
- **Achievement System**: Pluggable achievement definitions
- **Relationship System**: Support for new relationship types

### **Integration Strategy**
- **Pydantic Models**: Full validation and serialization support
- **SaveGame Integration**: Seamless persistence with existing save system
- **Memory Integration**: Citizen history feeds into advisor memory systems
- **Era Integration**: Dynamic citizen characteristics based on era progression

**Status**: Ready to begin implementation - all dependencies satisfied and integration points clear!
