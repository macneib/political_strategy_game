# 🏛️ Political Strategy Game: The Inner Game of Empires

> *A 4X strategy game where your advisors have memory, personality, and hidden agendas - and the power to overthrow you.*

## 🚀 **Join Us - We're Building Something Revolutionary!**

This isn't your typical strategy game. We're creating a **living political ecosystem** where every advisor remembers every decision, forms relationships, holds grudges, and can plot against you. Think *Game of Thrones* meets *Civilization* with AI-powered political intrigue.

**🎯 Want to help code the future of strategy games? [Jump in and contribute!](#-ready-to-contribute)**

---

## 🌟 What Makes This Different?

### Traditional 4X Games:
- Build cities, research tech, raise armies
- Advisors are just stat bonuses
- Politics is a tech tree
- Internal threats are minimal

### **Our Vision:**
- **🧠 Advisors have memory and personality** - They remember every slight, every favor, every broken promise
- **🤝 Dynamic relationship networks** - Trust webs and influence chains that shift constantly  
- **🕵️ Information warfare** - Control what your advisors know, plant false memories
- **💥 Real coup threats** - Your military advisor might stage a revolt if you ignore them too often
- **🤖 Emergent AI personalities** - LLM integration creates advisors with unique voices and agendas

### The Result?
A strategy game where **the most dangerous enemies aren't at your borders - they're sitting at your council table.**

## 🏗️ Project Status

**Current Phase**: Foundation & Core Systems (Phase 1)

### ✅ Completed (Task 1.1)
- [x] Python project structure with proper packages
- [x] Core data classes (Advisor, Leader, Civilization) with type hints
- [x] Personality system with trait compatibility
- [x] Memory system with decay and manipulation mechanics
- [x] Political event system with consequences
- [x] Relationship management between advisors
- [x] Basic coup detection and execution mechanics
- [x] Configuration system for game parameters
- [x] Logging framework for debugging and analysis
- [x] Unit tests for data validation and operations
- [x] Demo script showcasing core functionality

### 🚧 Next Steps (Tasks 1.2-1.3)
- [ ] JSON-based memory persistence 
- [ ] Memory decay algorithms
- [ ] Advanced personality interactions
- [ ] Relationship decay over time

## 🚀 Quick Start

### Prerequisites
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Quick setup and run
bash quickstart.sh

# Or manual setup:
uv venv
uv pip install -e ".[dev]"
```

### Run the Demo
```bash
# Basic demo simulation
uv run python demo.py

# Run tests
uv run python tests/test_core_structures.py
```

### Example Output
```
🏛️ Political Strategy Game - Demo Simulation
==================================================
Created civilization: Demo Empire
Leader: Ruler of Demo Empire (collaborative)
Advisors: 5

📅 Turn 1
------------------------------
🕵️ Conspiracy detected among advisors!
```

## 🏛️ Core Components

### Advisor System
Each advisor has:
- **Personality Traits**: ambition, loyalty, charisma, pragmatism, etc.
- **Relationships**: trust and influence with other advisors
- **Memory**: historical events with emotional impact and decay
- **Goals**: personal agenda that may conflict with civilization objectives

### Leadership Dynamics
Leaders have different styles that affect advisor interactions:
- **Authoritarian**: Makes decisions with minimal input, prefers loyal advisors
- **Collaborative**: Seeks consensus, values advisor recommendations
- **Delegative**: Gives advisors autonomy, prefers competent advisors

### Political Events
Events drive the narrative and create consequences:
- **Decisions**: Leader choices affect advisor loyalty and relationships
- **Conspiracies**: Advisors plot together based on shared grievances
- **Coups**: Overthrow attempts based on faction strength and motivation
- **Appointments**: Adding/removing advisors changes political dynamics

### Memory System
Advisors maintain historical knowledge with:
- **Decay**: Memories fade over time unless reinforced
- **Reliability**: Information accuracy degrades through transfer
- **Manipulation**: Leaders can filter or falsify information
- **Emotional Weight**: Important events are remembered longer

## 📊 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Game Engine   │    │  Political Core  │    │  LLM Interface  │
│   (Unity/Godot) │◄──►│     Engine       │◄──►│   (Future)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Memory System   │
                       │  (JSON/SQLite)   │
                       └──────────────────┘
```

## 🎮 Game Features

### Current Features
- ✅ Turn-based political simulation
- ✅ Advisor personality system with compatibility scoring
- ✅ Political relationship dynamics
- ✅ Conspiracy detection and coup mechanics
- ✅ Event-driven narrative system
- ✅ Memory management with decay

### Planned Features (Next Phases)
- 🔄 LLM-driven advisor personalities (OpenAI/Anthropic integration)
- 🔄 Advanced memory persistence and compression
- 🔄 Information warfare and propaganda systems
- 🔄 Technology tree affecting political mechanics
- 🔄 Player espionage and psychological operations
- 🔄 Visual game engine integration (Unity/Godot)

## 🧪 Testing

### Run All Tests
```bash
# Basic functionality tests
uv run python tests/test_core_structures.py

# With pytest (when available)
uv run pytest tests/
```

### Manual Testing
```bash
# Interactive political simulation
uv run python -c "
from demo import PoliticalStrategyGame
game = PoliticalStrategyGame()
civ_id = game.create_sample_civilization('Test Empire')
game.display_political_summary(civ_id)
results = game.simulate_turn(civ_id)
print(results)
"
```

## 🔧 Configuration

Game parameters can be customized in `config/game_config.py`:

```python
POLITICAL_CONFIG = {
    "max_advisors_per_civilization": 10,
    "conspiracy_threshold": 0.3,
    "coup_success_base_chance": 0.4,
    "memory_decay_rate": 0.02,
}
```

### Package Management with uv

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management:

```bash
# Install dependencies by group
uv pip install -e ".[dev]"      # Development tools
uv pip install -e ".[llm]"      # LLM integration (OpenAI, Anthropic)
uv pip install -e ".[game-engine]"  # Game engine integration

# Run commands in the virtual environment
uv run python demo.py           # Run demo
uv run pytest tests/            # Run tests
uv run black src/               # Format code

# Add new dependencies
uv add pydantic                 # Add to main dependencies
uv add --dev pytest-cov        # Add to dev dependencies
```

## 📁 Project Structure

```
political_strategy_game/
├── src/
│   ├── core/                 # Core game logic
│   │   ├── advisor.py       # Advisor personalities and behavior
│   │   ├── leader.py        # Leader decision-making
│   │   ├── civilization.py # Complete civilization management
│   │   ├── memory.py        # Memory system with decay
│   │   └── political_event.py # Event system
│   └── utils/               # Utilities
│       └── logging.py       # Logging framework
├── tests/                   # Unit tests
├── config/                  # Configuration files
├── data/                    # Game data and saves
├── demo.py                  # Demonstration script
└── requirements.txt         # Dependencies
```

## 🎯 Development Roadmap

### Phase 1: Foundation (CURRENT)
- ✅ Core data structures and relationships
- 🔄 Memory persistence and decay
- 🔄 Advanced personality interactions

### Phase 2: Political Engine  
- Rule-based advisor decision making
- Event processing pipeline
- Leadership and civilization management

### Phase 3: Advanced Politics
- Conspiracy and coup systems
- Information warfare mechanics
- Technology integration

### Phase 4: LLM Integration
- OpenAI/Anthropic advisor personalities
- Dynamic conversation generation
- Emergent storytelling

### Phase 5: Game Integration
- Unity/Godot visual frontend
- Real-time political visualization
- Player interaction systems

## 🚀 **Ready to Contribute?**

We're looking for developers who want to build the future of strategy games! Here's how you can jump in:

### 🎯 **Quick Start for Contributors**
```bash
# Get the code running in 2 minutes
git clone https://github.com/your-org/political-strategy-game
cd political_strategy_game
bash quickstart.sh
uv run python demo.py  # See the political simulation in action
```

### 🔥 **Hot Contribution Areas**

#### 🧠 **Psychology & AI Systems** *(Python, Pydantic)*
- **Current**: 8-trait personality system with compatibility scoring
- **Your Mission**: Add psychological realism, implement personality disorders, create trait interactions
- **Impact**: Make advisors feel genuinely human (or inhuman)

#### 🕵️ **Political Intrigue Engine** *(Logic, Algorithms)*  
- **Current**: Basic conspiracy detection
- **Your Mission**: Advanced plotting mechanics, secret communication channels, conspiracy cascades
- **Impact**: Turn every council meeting into a potential powder keg

#### 🤖 **LLM Integration** *(OpenAI/Anthropic APIs)*
- **Current**: Rule-based advisor responses
- **Your Mission**: Integrate AI APIs, prompt engineering, emergent personality consistency
- **Impact**: Create advisors that feel truly alive and unpredictable

#### 🎮 **Game Balance & Mechanics** *(Design, Testing)*
- **Current**: Basic political events
- **Your Mission**: Balance coup probabilities, design fair information warfare, create meaningful player agency
- **Impact**: Ensure the game is challenging but not impossible

#### 📊 **Data & Visualization** *(JSON, SQLite, future React/Unity)*
- **Current**: Text-based output
- **Your Mission**: Interactive relationship graphs, political tension heatmaps, conspiracy visualization
- **Impact**: Make the invisible politics visible and beautiful

### 🌟 **What We're Looking For**

- **Python Developers**: Core engine contributors
- **Game Designers**: Political mechanics and balance  
- **AI/ML Engineers**: LLM integration specialists
- **Writers**: Political events and narrative design
- **Historians**: Realistic political scenarios
- **Anyone** who thinks politics in games should be more than just a tech tree!

### 💡 **Contribution Philosophy**
- **🎯 Experiment First**: Try crazy ideas, fail fast, iterate quickly
- **🤝 Collaborate Openly**: Share your wild ideas, build on others' work  
- **🧪 Test Everything**: Political systems are complex - verify your assumptions
- **🎮 Player Experience Focus**: Cool tech is great, but does it make the game more fun?

### 📋 **Getting Started**
1. **Check out** `/tasks.md` for detailed work items
2. **Pick** a small feature that interests you
3. **Fork** the repo and start coding  
4. **Submit** a PR and get feedback
5. **Join** our Discord for real-time collaboration

**🎪 Ready to help overthrow some digital governments? Let's build this together!**

## 📄 **License - Completely Free & Open**

**MIT Licensed** - This project is completely free and open source! 

- ✅ **Use it however you want** - Commercial, personal, educational, anything
- ✅ **Your contributions remain yours** - We're not claiming ownership of your ideas
- ✅ **Fork and build your own version** - Take this engine and make something amazing
- ✅ **No restrictions** - The most permissive license possible

We chose MIT specifically because we want this to be a **community-driven project** where everyone feels safe contributing. Your ideas, your code, your creativity - all welcome and protected.

**🎯 Our goal**: Build something revolutionary together, not claim ownership of your brilliance.

## 🎨 Design Philosophy

This game explores themes of:
- **Leadership under pressure** - Making decisions with incomplete information
- **Truth vs control** - The tension between transparency and authority  
- **Memory vs manipulation** - How information shapes political reality
- **Emergent narrative** - Stories that arise from AI personality interactions

The goal is creating a game where the most interesting dynamics happen *within* each civilization, not just between them.
