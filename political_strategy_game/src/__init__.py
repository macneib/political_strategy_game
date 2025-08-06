"""
Political Strategy Game - Core Package

A turn-based 4X strategy game with AI-driven internal political dynamics.
Each civilization features advisors with personalities, memories, and agendas.
"""

__version__ = "0.1.0"
__author__ = "Political Strategy Game Team"

from .core.advisor import Advisor
from .core.leader import Leader
from .core.civilization import Civilization
from .core.memory import Memory, MemoryManager
from .core.political_event import PoliticalEvent

__all__ = [
    "Advisor",
    "Leader", 
    "Civilization",
    "Memory",
    "MemoryManager",
    "PoliticalEvent",
]
