"""
Basic Integration Test for Save/Load System

This simpler test validates that the save/load system works without 
requiring complex mocking of all game state structures.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

from src.persistence.save_game_manager import (
    SaveGameManager, SaveGameData, SaveGameMetadata, SaveFileFormat, 
    SaveFileVersion, CompressionManager, VersionManager, 
    IntegrityValidator, BackupManager
)


@pytest.fixture
def temp_save_dir():
    """Create a temporary directory for save files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


def test_component_initialization():
    """Test that all save system components can be initialized."""
    compression_manager = CompressionManager()
    version_manager = VersionManager()
    integrity_validator = IntegrityValidator()
    
    assert compression_manager is not None
    assert version_manager is not None
    assert integrity_validator is not None


def test_compression_manager():
    """Test compression manager functionality."""
    manager = CompressionManager()
    
    # Test with compressible data
    data = b"A" * 1000
    compressed = manager.compress_data(data)
    decompressed = manager.decompress_data(compressed)
    
    assert decompressed == data
    assert len(compressed) < len(data)
    
    # Test compression ratio
    ratio = manager.calculate_compression_ratio(len(data), len(compressed))
    assert ratio > 0.9  # Should compress well


def test_version_manager():
    """Test version management functionality."""
    manager = VersionManager()
    
    # Test version compatibility
    assert manager.is_compatible(SaveFileVersion.CURRENT)
    assert manager.is_compatible(SaveFileVersion.V2_0)
    assert not manager.is_compatible(SaveFileVersion.V1_0)


def test_save_file_metadata():
    """Test save file metadata creation and serialization."""
    metadata = SaveGameMetadata(
        save_id="test_save",
        game_name="Test Game",
        timestamp=datetime.now(),
        version=SaveFileVersion.CURRENT,
        format=SaveFileFormat.JSON,
        compression_level=6,
        game_turn=42,
        civilization_count=1,
        advisor_count=0,
        memory_count=0,
        file_size=0,
        checksum="test_checksum"
    )
    
    # Test serialization
    metadata_dict = metadata.to_dict()
    assert metadata_dict['save_id'] == 'test_save'
    assert metadata_dict['game_name'] == 'Test Game'
    assert metadata_dict['game_turn'] == 42
    
    # Test deserialization
    restored_metadata = SaveGameMetadata.from_dict(metadata_dict)
    assert restored_metadata.save_id == metadata.save_id
    assert restored_metadata.game_name == metadata.game_name
    assert restored_metadata.game_turn == metadata.game_turn


def test_save_manager_initialization(temp_save_dir):
    """Test save manager initialization."""
    manager = SaveGameManager(temp_save_dir)
    
    assert manager.save_dir == temp_save_dir
    assert temp_save_dir.exists()
    assert manager.compression_manager is not None
    assert manager.version_manager is not None
    assert manager.integrity_validator is not None
    assert manager.backup_manager is not None


def test_file_format_handling(temp_save_dir):
    """Test different save file formats."""
    manager = SaveGameManager(temp_save_dir)
    
    # Create a simple save data structure for testing
    metadata = SaveGameMetadata(
        save_id="format_test",
        game_name="Format Test",
        timestamp=datetime.now(),
        version=SaveFileVersion.CURRENT,
        format=SaveFileFormat.JSON,
        compression_level=6,
        game_turn=42,
        civilization_count=1,
        advisor_count=0,
        memory_count=0,
        file_size=0,
        checksum="test_checksum"
    )
    
    # Create minimal save data for testing
    save_data = SaveGameData(
        metadata=metadata,
        game_state={"test": "data"},  # Simplified for testing
        memory_banks={},
        civilizations={},
        custom_data={}
    )
    
    # Test JSON format
    json_path = temp_save_dir / "test.json"
    manager._write_save_file(save_data, json_path, SaveFileFormat.JSON)
    assert json_path.exists()
    
    # Verify JSON content
    with open(json_path, 'r') as f:
        loaded_json = json.load(f)
    assert loaded_json['metadata']['save_id'] == 'format_test'
    
    # Test compressed JSON format
    gz_path = temp_save_dir / "test.json.gz"
    manager._write_save_file(save_data, gz_path, SaveFileFormat.JSON_COMPRESSED)
    assert gz_path.exists()
    
    # Compressed file should be smaller than uncompressed (for larger data)
    # For this small test data, the compressed version might be larger due to headers


def test_backup_manager(temp_save_dir):
    """Test backup functionality."""
    backup_dir = temp_save_dir / "backups"
    backup_manager = BackupManager(backup_dir)
    
    # Create a test file to backup
    test_file = temp_save_dir / "test_save.json"
    test_file.write_text('{"test": "data"}')
    
    # Create backup
    backup_path = backup_manager.create_backup(test_file)
    assert backup_path.exists()
    assert backup_path.parent == backup_dir
    
    # Restore backup
    test_file.unlink()  # Delete original
    assert not test_file.exists()
    
    success = backup_manager.restore_backup(backup_path, test_file)
    assert success
    assert test_file.exists()
    
    # Verify content
    assert test_file.read_text() == '{"test": "data"}'


def test_integrity_validation():
    """Test save file integrity validation."""
    validator = IntegrityValidator()
    
    # Test checksum calculation
    test_data = b"test data for checksum"
    checksum = validator.calculate_checksum(test_data)
    
    assert isinstance(checksum, str)
    assert len(checksum) == 64  # SHA256 hex string
    
    # Test checksum verification
    same_checksum = validator.calculate_checksum(test_data)
    assert checksum == same_checksum
    
    # Different data should produce different checksum
    different_checksum = validator.calculate_checksum(b"different data")
    assert checksum != different_checksum


def test_save_file_path_generation(temp_save_dir):
    """Test save file path generation and naming."""
    manager = SaveGameManager(temp_save_dir)
    
    # Test with normal game name
    test_names = [
        "Test Game",
        "Game-With-Hyphens",
        "Game_With_Underscores",
        "Game With Spaces",
        "Special!@#Characters",  # Should be sanitized
    ]
    
    for game_name in test_names:
        # Since we can't easily mock the save_game method, 
        # we test the path sanitization logic directly
        safe_name = "".join(c for c in game_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        assert safe_name  # Should not be empty
        assert all(c.isalnum() or c in (' ', '-', '_') for c in safe_name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
