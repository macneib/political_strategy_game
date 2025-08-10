"""
Game Module for Interactive Political Strategy Game

This module provides the interactive game interface and integration with
the existing political strategy game engine.
"""

from .interactive import InteractiveGameCLI, GameSession

__all__ = [
    "InteractiveGameCLI",
    "GameSession"
]
