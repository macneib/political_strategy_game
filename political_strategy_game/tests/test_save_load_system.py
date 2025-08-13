"""
Comprehensive Test Suite for Save/Load System - Task 7.2

This test module validates all aspects of the save/load and persistence system:
- SaveGameManager functionality
- Compression and decompression
- Version migration and compatibility
- Integrity validation and error handling
- Backup and recovery operations
- Encryption and security features
- Performance and stress testing
"""

import pytest
import tempfile
import shutil
import json
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import hashlib
import os

from src.persistence.save_game_manager import (
    SaveGameManager, SaveGameData, SaveGameMetadata, SaveFileFormat, 
    SaveFileVersion, CompressionManager, VersionManager, 
    IntegrityValidator, BackupManager
)
from src.persistence.encryption import (
    SaveFileEncryption, EncryptionConfig, EncryptionMethod, 
    KeyDerivationMethod, EncryptedSaveManager
)
from src.persistence.save_file_debugger import SaveFileDebugger, AnalysisLevel

# Mock data structures for testing
@pytest.fixture
def mock_game_state():
    """Create a mock game state for testing."""
    class MockTurnState:
        def __init__(self):
            self.turn_number = 42
            self.civilization_id = "test_civ"
            self.phase = "planning"
        
        def to_dict(self):
            return {
                'turn_number': self.turn_number,
                'civilization_id': self.civilization_id,
                'phase': self.phase
            }
    
    class MockCivilization:
        def __init__(self, civ_id: str):
            self.civilization_id = civ_id
        
        def to_dict(self):
            return {'civilization_id': self.civilization_id}
    
    class MockGameState:
        def __init__(self):
            self.turn_state = MockTurnState()
            self.civilizations = [MockCivilization("test_civ")]
            self.advisors = []
            self.global_events = []
            self.metadata = {"test_key": "test_value"}
        
        def to_dict(self):
            return {
                'turn_state': self.turn_state.to_dict(),
                'civilizations': [civ.to_dict() for civ in self.civilizations],
                'advisors': self.advisors,
                'global_events': self.global_events,
                'metadata': self.metadata
            }
    
    return MockGameState()


@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager for testing."""
    class MockMemoryBank:
        def __init__(self, civilization_id: str):
            self.civilization_id = civilization_id
            self.advisor_memories = {}
            self.shared_memories = []
        
        def model_dump(self):
            return {
                'civilization_id': self.civilization_id,
                'advisor_memories': self.advisor_memories,
                'shared_memories': self.shared_memories
            }
    
    class MockMemoryManager:
        def __init__(self):
            self._memory_banks = {}
        
        def get_memory_bank(self, civ_id: str):
            if civ_id not in self._memory_banks:
                self._memory_banks[civ_id] = MockMemoryBank(civ_id)
            return self._memory_banks[civ_id]
    
    return MockMemoryManager()


@pytest.fixture
def mock_civilizations():
    """Create mock civilizations for testing."""
    class MockCivilization:
        def __init__(self, name: str, civ_id: str):
            self.name = name
            self.civilization_id = civ_id
        
        def model_dump(self):
            return {
                'name': self.name,
                'civilization_id': self.civilization_id,
                'leader': 'Test Leader',
                'advisors': [],
                'test_data': 'mock_value'
            }
    
    return {
        "test_civ": MockCivilization("Test Civilization", "test_civ")
    }


@pytest.fixture
def sample_save_data(mock_game_state, mock_memory_manager):
    """Create sample save data for testing."""
    # This fixture is deprecated - using direct method calls instead
    pass


@pytest.fixture
def temp_save_dir():
    """Create a temporary directory for save files."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestSaveGameManager:
    """Test the main SaveGameManager functionality."""
    
    def test_initialization(self, temp_save_dir):
        """Test SaveGameManager initialization."""
        manager = SaveGameManager(temp_save_dir)
        
        assert manager.save_dir == temp_save_dir
        assert temp_save_dir.exists()
        assert manager.compression_manager is not None
        assert manager.version_manager is not None
        assert manager.integrity_validator is not None
        assert manager.backup_manager is not None
    
    def test_save_game_json(self, temp_save_dir, mock_game_state, mock_memory_manager, mock_civilizations):
        """Test saving game in JSON format."""
        manager = SaveGameManager(temp_save_dir)
        
        save_path = manager.save_game(
            game_name="test_save",
            game_state=mock_game_state,
            memory_manager=mock_memory_manager,
            civilizations=mock_civilizations,
            save_format=SaveFileFormat.JSON
        )
        
        assert save_path.exists()
        assert '.json' in str(save_path)
        
        # Verify the file was created in the correct directory
        assert save_path.parent == temp_save_dir
    
    def test_save_game_json_compressed(self, temp_save_dir, mock_game_state, mock_memory_manager, mock_civilizations):
        """Test saving game in compressed JSON format."""
        manager = SaveGameManager(temp_save_dir)
        
        save_path = manager.save_game(
            game_name="test_save_compressed",
            game_state=mock_game_state,
            memory_manager=mock_memory_manager,
            civilizations=mock_civilizations,
            save_format=SaveFileFormat.JSON_COMPRESSED
        )
        
        assert save_path.exists()
        assert '.json.gz' in str(save_path)
    
    def test_save_game_binary(self, temp_save_dir, mock_game_state, mock_memory_manager, mock_civilizations):
        """Test saving game in binary format."""
        manager = SaveGameManager(temp_save_dir)
        
        save_path = manager.save_game(
            game_name="test_save_binary",
            game_state=mock_game_state,
            memory_manager=mock_memory_manager,
            civilizations=mock_civilizations,
            save_format=SaveFileFormat.BINARY
        )
        
        assert save_path.exists()
        assert '.binary' in str(save_path)
    
    def test_load_game(self, temp_save_dir, mock_game_state, mock_memory_manager, mock_civilizations):
        """Test loading saved game."""
        manager = SaveGameManager(temp_save_dir)
        
        # Save first
        save_path = manager.save_game(
            game_name="test_load",
            game_state=mock_game_state,
            memory_manager=mock_memory_manager,
            civilizations=mock_civilizations,
            save_format=SaveFileFormat.JSON
        )
        
        # Load
        loaded_data = manager.load_game(save_path)
        
        assert loaded_data.metadata.game_name == "test_load"
        assert loaded_data.game_state.turn_state.turn_number == 42
    
    def test_load_nonexistent_file(self, temp_save_dir):
        """Test loading non-existent file raises appropriate error."""
        manager = SaveGameManager(temp_save_dir)
        
        with pytest.raises(FileNotFoundError):
            manager.load_game(temp_save_dir / "nonexistent.json")
    
    def test_list_save_files(self, temp_save_dir, mock_game_state, mock_memory_manager, mock_civilizations):
        """Test listing save files."""
        manager = SaveGameManager(temp_save_dir)
        
        # Create multiple save files
        manager.save_game("save1", mock_game_state, mock_memory_manager, mock_civilizations, SaveFileFormat.JSON)
        manager.save_game("save2", mock_game_state, mock_memory_manager, mock_civilizations, SaveFileFormat.JSON_COMPRESSED)
        manager.save_game("save3", mock_game_state, mock_memory_manager, mock_civilizations, SaveFileFormat.BINARY)
        
        save_files = manager.list_save_games()
        
        assert len(save_files) == 3
        save_names = [info.game_name for info in save_files]
        assert "save1" in save_names
        assert "save2" in save_names
        assert "save3" in save_names
    
    def test_delete_save_file(self, temp_save_dir, mock_game_state, mock_memory_manager, mock_civilizations):
        """Test deleting save files."""
        manager = SaveGameManager(temp_save_dir)
        
        save_path = manager.save_game("test_delete", mock_game_state, mock_memory_manager, mock_civilizations, SaveFileFormat.JSON)
        assert save_path.exists()
        
        success = manager.delete_save_game(save_path)
        assert success
        assert not save_path.exists()


class TestCompressionManager:
    """Test compression functionality."""
    
    def test_compress_decompress_data(self):
        """Test basic compression and decompression."""
        manager = CompressionManager()
        original_data = b"A" * 1000  # Use highly compressible data
        
        compressed = manager.compress_data(original_data)
        decompressed = manager.decompress_data(compressed)
        
        assert decompressed == original_data
        assert len(compressed) < len(original_data)  # Should be smaller
    
    def test_compression_levels(self):
        """Test different compression levels."""
        manager = CompressionManager()
        test_data = b"A" * 1000  # Repeating data compresses well
        
        compressed_fast = manager.compress_data(test_data, level=1)
        compressed_best = manager.compress_data(test_data, level=9)
        
        assert len(compressed_best) <= len(compressed_fast)
        
        # Both should decompress to original
        assert manager.decompress_data(compressed_fast) == test_data
        assert manager.decompress_data(compressed_best) == test_data
    
    def test_compression_ratio_calculation(self):
        """Test compression ratio calculation."""
        manager = CompressionManager()
        
        # Test with highly compressible data
        compressible_data = b"A" * 1000
        compressed = manager.compress_data(compressible_data)
        ratio = manager.calculate_compression_ratio(len(compressible_data), len(compressed))
        assert ratio > 0.9  # Should compress well
        
        # Test with less compressible data (might not compress or even expand)
        random_data = os.urandom(1000)
        compressed_random = manager.compress_data(random_data)
        ratio_random = manager.calculate_compression_ratio(len(random_data), len(compressed_random))
        # Random data might not compress, so just check the calculation is valid
        assert isinstance(ratio_random, float)
        
        # Test edge case: empty data
        ratio_empty = manager.calculate_compression_ratio(0, 0)
        assert ratio_empty == 0.0


class TestVersionManager:
    """Test version migration functionality."""
    
    def test_version_detection(self):
        """Test version detection from save data."""
        manager = VersionManager()
        
        # Test current version
        current_data = {"version": SaveFileVersion.CURRENT.value}
        assert manager.detect_version(current_data) == SaveFileVersion.CURRENT
        
        # Test legacy version
        legacy_data = {"version": SaveFileVersion.LEGACY_V1_0.value}
        assert manager.detect_version(legacy_data) == SaveFileVersion.LEGACY_V1_0
    
    def test_needs_migration(self):
        """Test migration necessity detection."""
        manager = VersionManager()
        
        assert not manager.needs_migration(SaveFileVersion.CURRENT)
        assert manager.needs_migration(SaveFileVersion.LEGACY_V1_0)
        assert manager.needs_migration(SaveFileVersion.LEGACY_V1_1)
    
    def test_migration_v1_0_to_v1_1(self):
        """Test migration from V1.0 to V1.1."""
        manager = VersionManager()
        
        v1_0_data = {
            "version": "1.0",
            "game_state": {"turn": 42},
            "civilizations": []
        }
        
        migrated = manager.migrate_from_v1_0_to_v1_1(v1_0_data)
        
        assert migrated["version"] == "1.1"
        assert "metadata" in migrated
        assert migrated["metadata"]["migrated_from"] == "1.0"
    
    def test_migration_v1_1_to_v2_0(self):
        """Test migration from V1.1 to V2.0."""
        manager = VersionManager()
        
        v1_1_data = {
            "version": "1.1",
            "metadata": {"migrated_from": "1.0"},
            "game_state": {"turn": 42},
            "civilizations": []
        }
        
        migrated = manager.migrate_from_v1_1_to_v2_0(v1_1_data)
        
        assert migrated["version"] == "2.0"
        assert "memory_banks" in migrated
        assert "custom_data" in migrated
    
    def test_full_migration_chain(self):
        """Test complete migration from V1.0 to current."""
        manager = VersionManager()
        
        v1_0_data = {
            "version": "1.0",
            "game_state": {"turn": 42},
            "civilizations": []
        }
        
        migrated = manager.migrate_save_data(v1_0_data)
        
        assert migrated["version"] == SaveFileVersion.CURRENT.value
        assert "metadata" in migrated
        assert "memory_banks" in migrated
        assert "custom_data" in migrated


class TestIntegrityValidator:
    """Test save file integrity validation."""
    
    def test_calculate_checksum(self, sample_save_data):
        """Test checksum calculation."""
        validator = IntegrityValidator()
        
        checksum = validator.calculate_checksum(sample_save_data)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex string
    
    def test_verify_checksum_valid(self, sample_save_data):
        """Test checksum verification with valid data."""
        validator = IntegrityValidator()
        
        # Calculate and set checksum
        checksum = validator.calculate_checksum(sample_save_data)
        sample_save_data.metadata.checksum = checksum
        
        # Verify
        is_valid = validator.verify_checksum(sample_save_data)
        assert is_valid
    
    def test_verify_checksum_invalid(self, sample_save_data):
        """Test checksum verification with invalid data."""
        validator = IntegrityValidator()
        
        # Set incorrect checksum
        sample_save_data.metadata.checksum = "invalid_checksum"
        
        # Verify
        is_valid = validator.verify_checksum(sample_save_data)
        assert not is_valid
    
    def test_validate_save_file_structure(self, sample_save_data):
        """Test save file structure validation."""
        validator = IntegrityValidator()
        
        errors = validator.validate_save_file_structure(sample_save_data)
        assert len(errors) == 0  # Should be valid
    
    def test_validate_save_file_structure_invalid(self):
        """Test save file structure validation with invalid data."""
        validator = IntegrityValidator()
        
        # Create invalid save data
        invalid_data = SaveGameData(
            metadata=None,  # Invalid - should not be None
            game_state=None,  # Invalid - should not be None
            memory_banks={},
            civilizations={},
            custom_data={}
        )
        
        errors = validator.validate_save_file_structure(invalid_data)
        assert len(errors) > 0


class TestBackupManager:
    """Test backup and recovery functionality."""
    
    def test_create_backup(self, temp_save_dir, sample_save_data):
        """Test backup creation."""
        # Create main save directory and backup directory
        backup_dir = temp_save_dir / "backups"
        manager = BackupManager(backup_dir)
        
        # Create a save file to backup
        save_path = temp_save_dir / "test_save.json"
        with open(save_path, 'w') as f:
            json.dump(sample_save_data.to_dict(), f)
        
        # Create backup
        backup_path = manager.create_backup(save_path)
        
        assert backup_path.exists()
        assert backup_path.parent == backup_dir
        assert "test_save" in backup_path.name
        assert "backup" in backup_path.name
    
    def test_restore_backup(self, temp_save_dir, sample_save_data):
        """Test backup restoration."""
        backup_dir = temp_save_dir / "backups"
        manager = BackupManager(backup_dir)
        
        # Create original save file
        save_path = temp_save_dir / "test_save.json"
        with open(save_path, 'w') as f:
            json.dump(sample_save_data.to_dict(), f)
        
        # Create backup
        backup_path = manager.create_backup(save_path)
        
        # Delete original
        save_path.unlink()
        assert not save_path.exists()
        
        # Restore
        restored_path = manager.restore_backup(backup_path, save_path)
        
        assert restored_path.exists()
        assert restored_path == save_path
    
    def test_cleanup_old_backups(self, temp_save_dir):
        """Test automatic cleanup of old backups."""
        backup_dir = temp_save_dir / "backups"
        manager = BackupManager(backup_dir, max_backups=2)
        
        # Create test files
        test_files = []
        for i in range(4):
            test_file = temp_save_dir / f"test_{i}.json"
            with open(test_file, 'w') as f:
                json.dump({"test": i}, f)
            test_files.append(test_file)
        
        # Create backups (should trigger cleanup)
        for test_file in test_files:
            manager.create_backup(test_file)
        
        # Check that only max_backups remain
        backups = list(backup_dir.glob("*.backup"))
        assert len(backups) <= manager.max_backups


class TestSaveFileEncryption:
    """Test save file encryption functionality."""
    
    def test_password_encryption_decryption(self):
        """Test password-based encryption and decryption."""
        encryption = SaveFileEncryption()
        test_data = b"This is test save data"
        password = "test_password"
        
        config = EncryptionConfig(
            method=EncryptionMethod.PASSWORD_AES256,
            key_derivation=KeyDerivationMethod.PBKDF2
        )
        
        # Encrypt
        encrypted_data, metadata = encryption.encrypt_save_data(
            test_data, config, password=password
        )
        
        # Decrypt
        decrypted_data = encryption.decrypt_save_data(
            encrypted_data, metadata, password=password
        )
        
        assert decrypted_data == test_data
    
    def test_key_encryption_decryption(self):
        """Test key-based encryption and decryption."""
        encryption = SaveFileEncryption()
        test_data = b"This is test save data"
        key = encryption.generate_random_key()
        
        config = EncryptionConfig(method=EncryptionMethod.KEY_AES256)
        
        # Encrypt
        encrypted_data, metadata = encryption.encrypt_save_data(
            test_data, config, key=key
        )
        
        # Decrypt
        decrypted_data = encryption.decrypt_save_data(
            encrypted_data, metadata, key=key
        )
        
        assert decrypted_data == test_data
    
    def test_wrong_password_fails(self):
        """Test that wrong password fails decryption."""
        encryption = SaveFileEncryption()
        test_data = b"This is test save data"
        
        config = EncryptionConfig(
            method=EncryptionMethod.PASSWORD_AES256,
            key_derivation=KeyDerivationMethod.PBKDF2
        )
        
        # Encrypt with one password
        encrypted_data, metadata = encryption.encrypt_save_data(
            test_data, config, password="correct_password"
        )
        
        # Try to decrypt with wrong password
        with pytest.raises(ValueError):
            encryption.decrypt_save_data(
                encrypted_data, metadata, password="wrong_password"
            )
    
    def test_rsa_keypair_generation(self):
        """Test RSA keypair generation."""
        encryption = SaveFileEncryption()
        
        private_key, public_key = encryption.generate_rsa_keypair()
        
        assert isinstance(private_key, bytes)
        assert isinstance(public_key, bytes)
        assert b"BEGIN PRIVATE KEY" in private_key
        assert b"BEGIN PUBLIC KEY" in public_key


class TestSaveFileDebugger:
    """Test save file debugging tools."""
    
    def test_analyze_save_file(self, temp_save_dir, sample_save_data):
        """Test save file analysis."""
        # Create a save file
        manager = SaveGameManager(temp_save_dir)
        save_path = manager.save_game(sample_save_data, "debug_test", SaveFileFormat.JSON)
        
        # Analyze it
        debugger = SaveFileDebugger()
        analysis = debugger.analyze_save_file(save_path, AnalysisLevel.DETAILED)
        
        assert analysis.file_path == save_path
        assert analysis.file_size > 0
        assert analysis.format == SaveFileFormat.JSON
        assert analysis.version == SaveFileVersion.CURRENT
        assert analysis.metadata.save_id == "debug_test"
    
    def test_compare_save_files(self, temp_save_dir, sample_save_data):
        """Test save file comparison."""
        manager = SaveGameManager(temp_save_dir)
        debugger = SaveFileDebugger()
        
        # Create two similar save files
        save_path_1 = manager.save_game(sample_save_data, "compare_1", SaveFileFormat.JSON)
        
        # Modify the data slightly
        sample_save_data.metadata.game_turn = 43
        save_path_2 = manager.save_game(sample_save_data, "compare_2", SaveFileFormat.JSON)
        
        # Compare
        comparison = debugger.compare_save_files(save_path_1, save_path_2)
        
        assert comparison.file_a == save_path_1
        assert comparison.file_b == save_path_2
        assert len(comparison.differences) > 0
        assert comparison.similarity_score < 1.0  # Should be different
    
    def test_extract_save_data(self, temp_save_dir, sample_save_data):
        """Test save data extraction."""
        manager = SaveGameManager(temp_save_dir)
        debugger = SaveFileDebugger()
        
        # Create save file
        save_path = manager.save_game(sample_save_data, "extract_test", SaveFileFormat.JSON)
        
        # Extract
        extract_dir = temp_save_dir / "extracted"
        success = debugger.extract_save_data(save_path, extract_dir)
        
        assert success
        assert extract_dir.exists()
        assert (extract_dir / "metadata.json").exists()
        assert (extract_dir / "game_state.json").exists()


class TestPerformanceAndStress:
    """Test performance and stress scenarios."""
    
    def test_large_save_file_performance(self, temp_save_dir):
        """Test performance with large save files."""
        manager = SaveGameManager(temp_save_dir)
        
        # Create large save data
        large_civilizations = {}
        for i in range(100):
            large_civilizations[f"civ_{i}"] = {
                "name": f"Civilization {i}",
                "data": "x" * 1000  # 1KB per civilization
            }
        
        large_save_data = SaveGameData(
            metadata=SaveGameMetadata(
                save_id="large_test",
                game_name="Large Test Game",
                timestamp=datetime.now(),
                version=SaveFileVersion.CURRENT,
                format=SaveFileFormat.JSON_COMPRESSED,
                compression_level=6,
                game_turn=1000,
                civilization_count=100,
                advisor_count=0,
                memory_count=0,
                file_size=0,
                checksum=""
            ),
            game_state=Mock(),  # Use mock for performance
            memory_banks={},
            civilizations=large_civilizations,
            custom_data={}
        )
        
        # Measure save time
        start_time = datetime.now()
        save_path = manager.save_game(large_save_data, "large_test", SaveFileFormat.JSON_COMPRESSED)
        save_time = (datetime.now() - start_time).total_seconds()
        
        # Measure load time
        start_time = datetime.now()
        loaded_data = manager.load_game(save_path)
        load_time = (datetime.now() - start_time).total_seconds()
        
        # Performance assertions (adjust thresholds as needed)
        assert save_time < 5.0  # Should save within 5 seconds
        assert load_time < 5.0  # Should load within 5 seconds
        assert len(loaded_data.civilizations) == 100
    
    def test_concurrent_save_operations(self, temp_save_dir, sample_save_data):
        """Test concurrent save operations."""
        import threading
        import time
        
        manager = SaveGameManager(temp_save_dir)
        results = []
        
        def save_worker(worker_id):
            try:
                save_path = manager.save_game(
                    sample_save_data, 
                    f"concurrent_{worker_id}", 
                    SaveFileFormat.JSON
                )
                results.append((worker_id, save_path.exists()))
            except Exception as e:
                results.append((worker_id, False))
        
        # Start multiple save operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=save_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Check results
        assert len(results) == 5
        assert all(success for _, success in results)
    
    def test_memory_usage_monitoring(self, temp_save_dir, sample_save_data):
        """Test memory usage during save/load operations."""
        import psutil
        import gc
        
        manager = SaveGameManager(temp_save_dir)
        process = psutil.Process()
        
        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss
        
        # Perform save operation
        save_path = manager.save_game(sample_save_data, "memory_test", SaveFileFormat.JSON)
        save_memory = process.memory_info().rss
        
        # Perform load operation
        loaded_data = manager.load_game(save_path)
        load_memory = process.memory_info().rss
        
        # Clean up
        del loaded_data
        gc.collect()
        final_memory = process.memory_info().rss
        
        # Memory should not leak significantly
        memory_increase = final_memory - baseline_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Allow for some reasonable memory increase (adjust as needed)
        assert memory_increase_mb < 50  # Less than 50MB increase


class TestIntegrationScenarios:
    """Test complete integration scenarios."""
    
    def test_complete_save_load_cycle(self, temp_save_dir, sample_save_data):
        """Test complete save/load cycle with all features."""
        manager = SaveGameManager(temp_save_dir)
        
        # Save with compression
        save_path = manager.save_game(
            sample_save_data, 
            "integration_test", 
            SaveFileFormat.JSON_COMPRESSED
        )
        
        # Verify backup was created
        backups = list(manager.backup_manager.backup_directory.glob("*.backup"))
        assert len(backups) >= 1
        
        # Load and verify
        loaded_data = manager.load_game(save_path)
        
        assert loaded_data.metadata.save_id == sample_save_data.metadata.save_id
        assert loaded_data.game_state.turn_state.turn_number == 42
        
        # Verify integrity
        errors = manager.integrity_validator.validate_save_file(loaded_data)
        assert len(errors) == 0
    
    def test_encryption_integration(self, temp_save_dir, sample_save_data):
        """Test integration with encryption system."""
        # Create encrypted save manager
        encrypted_manager = EncryptedSaveManager(temp_save_dir)
        
        # Create encryption config
        config = EncryptionConfig(
            method=EncryptionMethod.PASSWORD_AES256,
            key_derivation=KeyDerivationMethod.PBKDF2
        )
        
        # Convert save data to bytes
        save_bytes = json.dumps(sample_save_data.to_dict(), default=str).encode()
        
        # Save encrypted
        save_path = encrypted_manager.save_encrypted(
            save_bytes, "encrypted_test", config, password="test_password"
        )
        
        # Load encrypted
        decrypted_bytes = encrypted_manager.load_encrypted(
            save_path, password="test_password"
        )
        
        # Verify data integrity
        loaded_dict = json.loads(decrypted_bytes.decode())
        assert loaded_dict['metadata']['save_id'] == 'encrypted_test'
    
    def test_version_migration_integration(self, temp_save_dir):
        """Test integration with version migration."""
        manager = SaveGameManager(temp_save_dir)
        
        # Create legacy save file manually
        legacy_data = {
            "version": "1.0",
            "game_state": {"turn": 42},
            "civilizations": [{"name": "Test Civ"}]
        }
        
        legacy_path = temp_save_dir / "legacy_save.json"
        with open(legacy_path, 'w') as f:
            json.dump(legacy_data, f)
        
        # Load should trigger migration
        loaded_data = manager.load_game(legacy_path)
        
        # Verify migration occurred
        assert loaded_data.metadata.version == SaveFileVersion.CURRENT
        assert "memory_banks" in loaded_data.to_dict()
        assert "custom_data" in loaded_data.to_dict()


if __name__ == "__main__":
    # Run specific test categories
    pytest.main([
        __file__ + "::TestSaveGameManager",
        "-v"
    ])
