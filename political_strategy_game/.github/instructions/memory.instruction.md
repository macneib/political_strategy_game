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

### Task 2.1: Political Event System [NEXT]
- Status: Ready to implement basic political event generation and handling
- Dependencies: Memory and personality systems provide solid foundation

## Technical Achievements
- Robust memory decay with exponential algorithms
- Comprehensive test coverage including integration tests (37 tests total)
- Proper JSON serialization handling for complex data types
- Memory transfer and sharing mechanisms
- Realistic test data generation with scenario-based templates
- Full persistence layer with automatic civilization-advisor mapping
- Advanced advisor personality system with memory-informed decision making
- Coup detection and political risk assessment
- Council management with relationship dynamics and conspiracy tracking

## Notes
- All major technical blockers resolved
- Project ready for collaborative development
- Memory system provides solid foundation for personality interactions
- Need to assess Task 1.3 status and proceed to political event system
