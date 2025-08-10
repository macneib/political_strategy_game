---
applyTo: '**'
---

# User Memory

## User Preferences
- Programming languages: Python (primary), TypeScript/JavaScript
- Code style preferences: Clean, readable, well-documented code with comprehensive error handling
- Development environment: VS Code on Linux, prefers local development over remote APIs
- Communication style: Prefers autonomous implementation with detailed explanations

## Project Context
- Current project type: Political strategy game simulation with turn-based gameplay
- Tech stack: Python, pytest, local vLLM for AI models, CLI interface
- Architecture patterns: Object-oriented design, event-driven systems, modular components
- Key requirements: Local AI inference, interactive gameplay, comprehensive testing

## Coding Patterns
- Comprehensive test coverage (current: 162 passing tests)
- Modular class-based architecture with clear separation of concerns
- Detailed docstrings and inline comments
- Robust error handling and validation
- Incremental development with frequent testing

## Context7 Research History
- vLLM integration: Researched quickstart guide, supported models, installation via pip
- Small model options: Qwen2 0.5B/1.5B, Phi-3 Mini, Llama 3.2 1B/3B identified as suitable
- OpenAI API compatibility: vLLM server provides drop-in replacement for OpenAI endpoints
- Local deployment: Can run models locally without API keys or internet dependency

## Conversation History
- Task 3.3 (Advanced Political Mechanics): Completed successfully with all tests passing
- Task 4.1 (Interactive Game Interface): Current focus, implementing LLM-enhanced advisors
- User preference: Local vLLM instead of remote APIs due to access limitations
- Game playability: Currently has sophisticated backend but needs interactive player interface
- Development approach: Begin with LLM abstraction layer, then build game interface

## Notes
- Game currently has automated demos but no player input system
- 14-step implementation plan created for Task 4.1
- Focus on LLM-powered advisor personalities with memory and context
- Architecture designed to support both local vLLM and future remote API integration
- Small models sufficient for advisor personality use case
