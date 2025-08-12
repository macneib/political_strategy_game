# Conventional Commits for Political Strategy Game

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification for semantic versioning and automated releases.

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Types

### Major Version (Breaking Changes)
- `feat!:` - Breaking feature changes
- `fix!:` - Breaking bug fixes
- `BREAKING CHANGE:` in footer

### Minor Version (Features)
- `feat:` - New features and system implementations
- `feat(core):` - Core political engine features
- `feat(llm):` - LLM integration features
- `feat(ui):` - User interface and visualization features
- `feat(api):` - API and integration features

### Patch Version (Bug Fixes)
- `fix:` - Bug fixes and error corrections
- `fix(tests):` - Test fixes
- `fix(docs):` - Documentation fixes

### Other Types (No Version Bump)
- `docs:` - Documentation only changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring without feature changes
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `ci:` - CI/CD pipeline changes
- `perf:` - Performance improvements

## Scopes

Common scopes for this project:
- `core` - Core political engine systems
- `advisor` - Advisor personality and behavior systems
- `memory` - Memory and persistence systems
- `espionage` - Intelligence and espionage operations
- `tech` - Technology tree systems
- `politics` - Advanced political mechanics
- `ui` - User interface and visualization
- `api` - API and game engine integration
- `llm` - LLM integration and AI features
- `demo` - Demo scripts and examples
- `test` - Testing infrastructure
- `ci` - CI/CD pipeline

## Examples

### Features (Minor Version Bump)
```
feat(core): add conspiracy detection system

Implements comprehensive conspiracy detection with:
- Dynamic threat assessment
- Evidence gathering mechanics
- Interactive investigation workflow
```

```
feat(espionage): implement covert operations system

Add complete espionage capabilities including:
- Asset recruitment and training
- Multi-turn operation execution
- Counter-intelligence measures

Closes #123
```

### Bug Fixes (Patch Version Bump)
```
fix(memory): resolve memory decay calculation error

Memory decay was applying exponentially instead of linearly.
Fixed calculation to properly handle time-based degradation.
```

### Breaking Changes (Major Version Bump)
```
feat(api)!: redesign game engine bridge interface

BREAKING CHANGE: The game engine API has been completely redesigned.
Previous WebSocket message format is no longer supported.
Migration guide available in docs/migration.md
```

## Versioning Strategy

### Pre-1.0.0 (Current Development)
- **0.x.x** - Major system implementations and core feature development
- Focus on completing core political engine capabilities
- Breaking changes allowed as we refine the architecture

### 1.0.0 Release Criteria
- ✅ Complete core political engine (DONE)
- ✅ Advanced political mechanics (DONE)
- ✅ Interactive systems (DONE)
- ✅ Visualization framework (DONE)
- 🔄 LLM integration with OpenAI/Anthropic APIs
- 🔄 Production-ready game engine integration
- 🔄 Comprehensive documentation for external developers

### Post-1.0.0
- **Major (x.0.0)** - Architectural changes, new game systems
- **Minor (x.y.0)** - New features, enhanced capabilities
- **Patch (x.y.z)** - Bug fixes, performance improvements

## Release Automation

This project uses semantic-release for automated versioning:

1. **Commit Analysis** - Analyzes commit messages since last release
2. **Version Calculation** - Determines next version based on conventional commits
3. **Changelog Generation** - Automatically generates CHANGELOG.md
4. **Release Creation** - Creates GitHub release with notes
5. **Asset Upload** - Includes documentation and demo files

## Development Workflow

1. Create feature branch: `feat/add-conspiracy-system`
2. Make commits following conventional format
3. Create pull request to `main`
4. After merge, semantic-release automatically creates release
5. Version is bumped in `pyproject.toml`
6. GitHub release created with generated notes

## Current Status

**Development Phase**: Pre-1.0.0 (Advanced Implementation)
**Progress**: ~75% toward 1.0.0 release
**Quality**: Production-ready core systems with 391 passing tests
**Next Milestone**: LLM integration and game engine implementation
