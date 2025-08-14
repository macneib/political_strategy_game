# Requirements Specification: Political Advisor System

## Overview
Create a sophisticated LLM-powered advisor system where AI personalities emerge naturally from population performance curves, providing authentic leadership that reflects civilization development while maintaining computational efficiency through selective detailed modeling.

**Strategic Vision**: Revolutionary advisor emergence system that solves three fundamental strategy game problems: immortal leaders breaking immersion, computational limits of simulating entire populations, and random advisor selection feeling disconnected from society.

## Population-Driven Advisor Emergence

### The Population Performance Curve Approach

**Population Modeling Structure**:
- **Agents (Top 1-5%)**: Detailed individuals with full personality profiles, accomplishments, and skill development
- **Abstracted Masses (95-99%)**: Statistical aggregations representing the general population with key demographic trends
- **Performance Distribution**: Bell curve or Pareto distribution ranking citizens in era-appropriate skill domains

### Advisor Selection Mechanics

**Natural Emergence Process**:
1. **Skill Domain Ranking**: Citizens ranked by relevant abilities (military prowess, scientific knowledge, diplomatic skill)
2. **Era-Weighted Selection**: Skills valued differently across eras (hunting in Ancient vs. data analysis in Information Era)
3. **Top Slice Candidates**: Advisors selected from top 0.5-1% of population in relevant domains
4. **Dynamic Candidate Pool**: Available advisor quality changes based on population development and era progression

## User Stories

### Story 1: Natural Advisor Emergence
**As a** strategy game player
**I want** my advisors to emerge naturally from my civilization's population
**So that** I feel connected to the development of my society and leadership reflects my civilization's capabilities

**Acceptance Criteria**:
WHEN my civilization develops in specific skill areas
THE SYSTEM SHALL produce advisor candidates with expertise reflecting population development

WHEN I examine advisor backgrounds
THE SYSTEM SHALL show their emergence from specific population segments with authentic achievement histories

WHEN key advisors die or retire
THE SYSTEM SHALL select replacements from the current population's top performers in relevant skills

WHEN my civilization's culture shifts over time
THE SYSTEM SHALL produce advisors whose personalities and values reflect those cultural changes

### Story 2: Era-Specific Advisor Evolution
**As a** strategy game player
**I want** my advisors to represent the knowledge and capabilities appropriate to my civilization's era
**So that** I experience authentic historical progression and era-appropriate strategic thinking

**Acceptance Criteria**:
WHEN playing in the Ancient Era
THE SYSTEM SHALL produce advisors focused on hunting, tribal warfare, oral traditions, and survival skills

WHEN advancing to Classical Era
THE SYSTEM SHALL transition to advisors skilled in formation tactics, agriculture, philosophy, and formal governance

WHEN reaching Medieval Era
THE SYSTEM SHALL provide advisors expert in feudal politics, religious influence, trade guilds, and court intrigue

WHEN entering Renaissance Era
THE SYSTEM SHALL generate advisors knowledgeable in cultural movements, exploration, banking, and scientific method

### Story 3: Advisor Lifecycle Management
**As a** strategy game player
**I want** advisors to have realistic lifespans and career progression
**So that** I experience the natural turnover of leadership and must plan for succession

**Acceptance Criteria**:
WHEN advisors age naturally over decades of game time
THE SYSTEM SHALL show declining effectiveness and eventual retirement or death

WHEN advisors face high-stress situations or dangerous assignments
THE SYSTEM SHALL apply appropriate risks of burnout, scandal, or violent death

WHEN advisor positions become vacant
THE SYSTEM SHALL automatically scan the population for qualified candidates and present selection options

WHEN long-serving advisors retire or die
THE SYSTEM SHALL preserve their influence on civilization culture and provide narrative closure

### Story 4: LLM Personality Integration
**As a** strategy game player
**I want** to interact with advisors that have distinct personalities reflecting their backgrounds
**So that** I experience meaningful political relationships and authentic strategic discussions

**Acceptance Criteria**:
WHEN new advisors are promoted from the population
THE SYSTEM SHALL generate LLM personalities based on their statistical background and achievements

WHEN I consult with advisors on strategic decisions
THE SYSTEM SHALL provide advice consistent with their era, expertise, and personality profile

WHEN advisors disagree with each other or my decisions
THE SYSTEM SHALL reflect authentic personality conflicts based on their backgrounds and values

WHEN advisors develop relationships over time
THE SYSTEM SHALL show evolving dynamics based on shared experiences and policy outcomes

## Era-Specific Skill Weighting Examples

| Era | Military Advisors | Economic Advisors | Cultural Advisors | Scientific Advisors |
|-----|------------------|-------------------|-------------------|-------------------|
| **Ancient** | Hunting, tribal warfare, survival | Resource gathering, trade basics | Storytelling, tribal customs | Tool making, natural observation |
| **Classical** | Formation tactics, siege warfare | Agriculture, currency systems | Philosophy, arts, education | Mathematics, engineering, astronomy |
| **Medieval** | Cavalry, fortification, logistics | Guild management, feudal economics | Religious influence, artistic patronage | Alchemy, mechanical innovation |
| **Renaissance** | Naval warfare, gunpowder tactics | Banking, international trade | Cultural movements, printing | Scientific method, exploration |
| **Industrial** | Mass warfare, industrial logistics | Factory management, labor relations | Mass media, social movements | Engineering, chemical sciences |
| **Information** | Cyber warfare, intelligence networks | Global economics, data analysis | Social media, cultural trends | Computer science, biotechnology |

## Non-Functional Requirements

### Computational Efficiency Requirements
WHEN managing advisor LLM instances
THE SYSTEM SHALL limit active instances to 5-8 advisors simultaneously to maintain performance

WHEN selecting advisors from population
THE SYSTEM SHALL use efficient algorithms to rank population performance without processing individual citizens

WHEN promoting citizens to advisor status
THE SYSTEM SHALL generate detailed personality profiles on-demand rather than maintaining them for entire population

### Personality Authenticity Requirements
WHEN generating advisor personalities
THE SYSTEM SHALL create backgrounds consistent with era-appropriate knowledge and cultural values

WHEN advisors provide strategic advice
THE SYSTEM SHALL maintain consistency with their generated personality and expertise area

### Narrative Integration Requirements
WHEN advisors emerge, retire, or die
THE SYSTEM SHALL provide meaningful narrative context that enhances the civilization's story

WHEN advisor backgrounds are examined
THE SYSTEM SHALL show believable achievement histories that justify their promotion to leadership

## Technical Architecture

### Population Database
```python
class PopulationManager:
    def __init__(self):
        self.agents = {}  # Top 1-5% with detailed profiles
        self.demographics = {}  # Aggregated population statistics
        self.skill_distributions = {}  # Era-weighted skill curves
        
    def select_advisor_candidates(self, skill_domain, era):
        """Rank population by relevant skills and return top performers"""
        candidates = []
        for citizen_id, citizen in self.agents.items():
            skill_score = self._calculate_era_weighted_skill(citizen, skill_domain, era)
            candidates.append((citizen_id, skill_score))
        
        # Return top 0.5-1% as potential advisors
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_percentile = max(1, len(candidates) // 200)
        return candidates[:top_percentile]
        
    def promote_to_advisor(self, citizen_id):
        """Convert detailed agent to LLM advisor instance"""
        citizen = self.agents[citizen_id]
        personality_prompt = self._generate_personality_prompt(citizen)
        return AdvisorPersonality(citizen_id, personality_prompt, citizen.achievements)
```

### Advisor Instance Management
```python
class AdvisorManager:
    def __init__(self):
        self.active_advisors = {}  # Current LLM instances
        self.advisor_history = {}  # Previous advisors for narrative
        self.max_active_advisors = 8  # Performance limit
        
    def handle_advisor_vacancy(self, role, skill_requirements):
        """Handle advisor death, retirement, or dismissal"""
        candidates = self.population_manager.select_advisor_candidates(
            skill_requirements['domain'], 
            self.game_state.current_era
        )
        
        # Present top 3-5 candidates to player for selection
        return self._present_candidate_selection(candidates, role)
        
    def process_advisor_aging(self):
        """Handle natural aging and career progression"""
        for advisor_id, advisor in self.active_advisors.items():
            if self._check_retirement_conditions(advisor):
                self._process_advisor_retirement(advisor_id)
            elif self._check_death_conditions(advisor):
                self._process_advisor_death(advisor_id)
```

### LLM Personality Generation
```python
class PersonalityGenerator:
    def __init__(self):
        self.era_templates = {}  # Era-specific personality frameworks
        self.achievement_patterns = {}  # Achievement-to-personality mappings
        
    def generate_advisor_personality(self, citizen, era):
        """Create LLM personality prompt from citizen background"""
        base_template = self.era_templates[era]
        
        personality_prompt = f"""
        You are {citizen.name}, a {citizen.age}-year-old advisor in the {era} era.
        
        Background: {self._generate_background_story(citizen)}
        
        Expertise: {citizen.primary_skills}
        Achievements: {citizen.major_achievements}
        
        Personality Traits: {self._derive_personality_traits(citizen)}
        
        Communication Style: {self._determine_communication_style(citizen, era)}
        
        Values and Beliefs: {self._generate_era_appropriate_values(citizen, era)}
        """
        
        return personality_prompt
```

## Implementation Strategy

### Phase 1: Basic Population Tracking
- Simple skill distributions across population
- Basic advisor selection from top performers
- Fundamental lifecycle events (aging, death, replacement)
- LLM personality generation from citizen profiles

### Phase 2: Advanced Population Simulation
- Complex skill development over time
- Cultural and technological influences on skill distributions
- Advanced advisor personality generation with deeper backgrounds
- Advisor relationship dynamics and faction formation

### Phase 3: Full Emergence System
- Population social networks affecting advisor selection
- Cultural movements influencing skill valuations
- Dynamic faction formation within population
- Multi-generational advisor legacy systems

## Quality Standards

### Advisor Quality
- ✅ Personalities reflect authentic era-appropriate knowledge and values
- ✅ Advisory recommendations consistent with background and expertise
- ✅ Natural emergence from population development patterns
- ✅ Meaningful lifecycle progression and succession planning

### Performance Quality
- ✅ Efficient population ranking algorithms under 100ms
- ✅ Limited active LLM instances (5-8) for performance management
- ✅ On-demand personality generation without population-wide processing
- ✅ Scalable architecture supporting large civilizations

### Narrative Quality
- ✅ Compelling advisor background stories that justify their rise to leadership
- ✅ Authentic personality conflicts and political dynamics
- ✅ Meaningful consequences from advisor decisions and relationships
- ✅ Rich historical narratives connecting advisor generations
