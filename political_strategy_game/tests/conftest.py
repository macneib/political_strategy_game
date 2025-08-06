"""
Test configuration for pytest.
"""

import pytest
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture
def sample_advisor_data():
    """Sample data for creating test advisors."""
    return {
        "name": "Test Advisor",
        "role": "military",
        "civilization_id": "test_civ_001"
    }

@pytest.fixture  
def sample_leader_data():
    """Sample data for creating test leaders."""
    return {
        "name": "Test Leader",
        "civilization_id": "test_civ_001",
        "leadership_style": "collaborative"
    }

@pytest.fixture
def sample_civilization_data():
    """Sample data for creating test civilizations."""
    return {
        "name": "Test Civilization"
    }
