---
applyTo: '**'
---

# User Memory

## User Preferences
- Programming languages: Python (primary), modern tooling with uv package management
- Code style preferences: Clean, modular, well-documented code with comprehensive testing
- Development environment: Linux, VS Code, collaborative development focus
- Communication style: Technical and thorough, focused on implementation details

## Project Context
- Current project type: Political strategy game with advisor personality system
- Tech stack: Python 3.11+, Pydantic v2, uv package management, pytest
- Architecture patterns: Modular design, memory systems with decay mechanics, JSON persistence
- Key requirements: Realistic political simulation, collaborative development, open source (MIT license)

## Coding Patterns
- Comprehensive unit testing for all components
- JSON-based persistence with proper serialization handling
- Pydantic models for data validation and structure
- Modular design with clear separation of concerns
- Factory patterns for test data generation

## Current Implementation Status

### Task 1.1: Project Setup [COMPLETE]
- ✅ uv package management integration
- ✅ Fixed TOML parsing and build backend issues  
- ✅ Pydantic v2 migration completed
- ✅ Working demo (demo.py runs successfully)
- ✅ MIT license for collaboration
- ✅ Comprehensive README for contributor recruitment

### Task 1.2: Basic Memory System [COMPLETE]
- ✅ Memory class with decay algorithms and persistence
- ✅ AdvisorMemory for individual advisor memory collections
- ✅ MemoryBank for civilization-wide memory management
- ✅ MemoryManager with JSON persistence and disk I/O
- ✅ MemoryFactory for realistic test data generation
- ✅ Comprehensive unit tests (23 tests, all passing)
- ✅ Fixed JSON serialization for set types
- ✅ Memory transfer capabilities between advisors
- ✅ Memory compression when capacity limits exceeded

### Task 1.3: Enhanced Personality System [COMPLETE]
- ✅ Extended AdvisorWithMemory class integrating memory system
- ✅ Memory-informed decision making with tag overlap analysis
- ✅ Secret sharing and relationship dynamics affected by memories
- ✅ Threat assessment from conspiracy and intelligence memories
- ✅ AdvisorCouncil for managing multiple advisors with shared memory
- ✅ Coup risk detection with conspiracy network analysis
- ✅ Council dynamics simulation with turn-based progression
- ✅ Comprehensive unit tests (14 tests, all passing)
- ✅ Full integration with memory persistence and decay
- ✅ Realistic personality-driven behavior patterns

### Task 2.1: Political Event System [COMPLETE]
- ✅ Complete political event system with EventManager orchestration
- ✅ Event lifecycle management with template-based generation
- ✅ Comprehensive EventLibrary with 8 diverse political scenarios
- ✅ Memory integration for event consequences and historical tracking
- ✅ Advisor integration for dynamic recommendations and responses
- ✅ Full testing suite with 18 event-specific tests (62 total tests passing)
- ✅ Interactive demonstration system showing 5-turn political simulation
- ✅ Turn-based event processing with consequence calculation
- ✅ Repository cleanup with comprehensive .gitignore

### Task 2.2: Civilization Management System [COMPLETE]
- ✅ Modernized civilization.py to use new event/memory/advisor systems
- ✅ Import migration from legacy political_event to events.py system
- ✅ AdvisorWithMemory integration for enhanced advisor capabilities
- ✅ MemoryManager integration with proper advisor registration
- ✅ EventManager integration for dynamic political event handling
- ✅ Comprehensive test suite creation (17 tests covering all integration points)
- ✅ Bug resolution and validation fixes (Pydantic v2 requirements, method signatures)
- ✅ Directory creation fixes for temporary memory storage
- ✅ All tests passing - full system integration validated

### Task 3.1: Resource Management Systems [COMPLETE]
- ✅ Complete resource management system with Economic, Military, and Technology states
- ✅ ResourceManager class for turn-based resource processing
- ✅ ResourceEvent system for resource-driven political consequences
- ✅ Full integration with civilization system for turn-based resource updates
- ✅ Advisor memory integration for resource decisions and events
- ✅ Technology research system with civilization benefits
- ✅ Economic stability and trade route establishment capabilities
- ✅ Military budget allocation and effectiveness systems
- ✅ Comprehensive test suite (23 tests covering all resource functionality)
- ✅ Complete demonstration script showing integrated resource management
- ✅ All 102 tests passing (79 existing + 23 new resource tests)

### Task 3.2: Inter-Civilization Systems [COMPLETE]
- ✅ Complete diplomatic framework with DiplomacyManager orchestration
- ✅ CivilizationRelations for bilateral relationship management (trust, trade dependency, cultural affinity)
- ✅ Embassy system with ambassador assignments and diplomatic missions
- ✅ Treaty system with multiple types (trade agreements, defense pacts, non-aggression)
- ✅ Trade route establishment with economic impact and disruption mechanics
- ✅ Military conflict system with war declaration, progression, and resolution
- ✅ Intelligence operations with spy networks and counter-intelligence
- ✅ Global stability tracking based on cooperation vs. conflict
- ✅ Full integration with civilization system (13 new diplomatic methods)
- ✅ Memory integration for all diplomatic actions and consequences
- ✅ Resource system integration for trade benefits and conflict costs
- ✅ Comprehensive test suite (30 tests covering all diplomatic functionality)
- ✅ Complete demonstration script showing 4-civilization diplomatic scenario
- ✅ All 132 tests passing (102 existing + 30 new diplomacy tests)

## Technical Achievements
- Robust memory decay with exponential algorithms
- Comprehensive test coverage including integration tests (132 tests total)
- Proper JSON serialization handling for complex data types
- Memory transfer and sharing mechanisms
- Realistic test data generation with scenario-based templates
- Full persistence layer with automatic civilization-advisor mapping
- Advanced advisor personality system with memory-informed decision making
- Coup detection and political risk assessment
- Council management with relationship dynamics and conspiracy tracking
- Complete political event system with template-driven scenarios
- Fully integrated civilization management system with modernized event/memory/advisor integration
- Complete resource management system with economic, military, and technology mechanics
- Resource-driven political consequences and advisor memory integration
- Comprehensive inter-civilization diplomacy system with relations, treaties, trade, conflicts, intelligence
- Multi-civilization coordination with global stability tracking
- Sophisticated diplomatic mechanics integrated with memory and resource systems
- Repository hygiene with proper gitignore and cache file management

## Notes
- All major technical blockers resolved
- Project ready for collaborative development
- Event system successfully integrated with memory and advisor systems
- Civilization system fully modernized and integrated with all enhanced systems
- Resource management system fully implemented and integrated with all existing systems
- Inter-civilization diplomacy system fully implemented with comprehensive diplomatic mechanics
- Repository properly cleaned up with cache files ignored
- **Branch consolidation completed**: All feature branches merged into main
- All 132 tests passing - complete system integration validated with full diplomatic capabilities
- Ready to proceed to next development phase: likely advanced political scenarios, LLM integration, or player interaction systems
