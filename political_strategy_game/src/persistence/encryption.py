"""
Encryption System for Save Files - Task 7.2

This module provides secure encryption and decryption for save files:
- AES-256 encryption with multiple key derivation methods
- Support for password-based and key-based encryption
- Secure key management and rotation
- Encrypted save file integrity verification
- Backward compatibility with unencrypted saves
"""

import os
import hashlib
import hmac
import secrets
from typing import Dict, Optional, Tuple, Union, Any, List
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import json
import logging
from datetime import datetime

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class EncryptionMethod(str, Enum):
    """Supported encryption methods."""
    NONE = "none"
    PASSWORD_AES256 = "password_aes256"
    KEY_AES256 = "key_aes256"
    RSA_AES_HYBRID = "rsa_aes_hybrid"


class KeyDerivationMethod(str, Enum):
    """Key derivation methods for password-based encryption."""
    PBKDF2 = "pbkdf2"
    SCRYPT = "scrypt"


@dataclass
class EncryptionConfig:
    """Configuration for encryption operations."""
    method: EncryptionMethod
    key_derivation: Optional[KeyDerivationMethod] = None
    iterations: int = 100000  # For PBKDF2
    scrypt_n: int = 2**14     # For Scrypt
    scrypt_r: int = 8         # For Scrypt
    scrypt_p: int = 1         # For Scrypt
    salt_size: int = 32
    iv_size: int = 16
    key_size: int = 32        # 256 bits
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'method': self.method.value,
            'key_derivation': self.key_derivation.value if self.key_derivation else None,
            'iterations': self.iterations,
            'scrypt_n': self.scrypt_n,
            'scrypt_r': self.scrypt_r,
            'scrypt_p': self.scrypt_p,
            'salt_size': self.salt_size,
            'iv_size': self.iv_size,
            'key_size': self.key_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptionConfig':
        """Create from dictionary."""
        return cls(
            method=EncryptionMethod(data['method']),
            key_derivation=KeyDerivationMethod(data['key_derivation']) if data.get('key_derivation') else None,
            iterations=data.get('iterations', 100000),
            scrypt_n=data.get('scrypt_n', 2**14),
            scrypt_r=data.get('scrypt_r', 8),
            scrypt_p=data.get('scrypt_p', 1),
            salt_size=data.get('salt_size', 32),
            iv_size=data.get('iv_size', 16),
            key_size=data.get('key_size', 32)
        )


@dataclass
class EncryptedSaveMetadata:
    """Metadata for encrypted save files."""
    encryption_config: EncryptionConfig
    salt: bytes
    iv: bytes
    hmac_digest: bytes
    timestamp: datetime
    key_hint: Optional[str] = None  # Optional hint for password
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'encryption_config': self.encryption_config.to_dict(),
            'salt': self.salt.hex(),
            'iv': self.iv.hex(),
            'hmac_digest': self.hmac_digest.hex(),
            'timestamp': self.timestamp.isoformat(),
            'key_hint': self.key_hint
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncryptedSaveMetadata':
        """Create from dictionary."""
        return cls(
            encryption_config=EncryptionConfig.from_dict(data['encryption_config']),
            salt=bytes.fromhex(data['salt']),
            iv=bytes.fromhex(data['iv']),
            hmac_digest=bytes.fromhex(data['hmac_digest']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            key_hint=data.get('key_hint')
        )


class SaveFileEncryption:
    """Handles encryption and decryption of save files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Cryptography library not available. Encryption disabled.")
    
    def encrypt_save_data(self, data: bytes, 
                         encryption_config: EncryptionConfig,
                         password: Optional[str] = None,
                         key: Optional[bytes] = None,
                         public_key: Optional[bytes] = None) -> Tuple[bytes, EncryptedSaveMetadata]:
        """
        Encrypt save file data.
        
        Args:
            data: Raw save file data to encrypt
            encryption_config: Encryption configuration
            password: Password for password-based encryption
            key: Key for key-based encryption
            public_key: Public key for RSA hybrid encryption
            
        Returns:
            Tuple of (encrypted_data, encryption_metadata)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        if encryption_config.method == EncryptionMethod.NONE:
            # No encryption - return data as-is with dummy metadata
            return data, EncryptedSaveMetadata(
                encryption_config=encryption_config,
                salt=b'',
                iv=b'',
                hmac_digest=b'',
                timestamp=datetime.now()
            )
        
        # Generate salt and IV
        salt = os.urandom(encryption_config.salt_size)
        iv = os.urandom(encryption_config.iv_size)
        
        # Derive encryption key
        if encryption_config.method == EncryptionMethod.PASSWORD_AES256:
            if not password:
                raise ValueError("Password required for password-based encryption")
            encryption_key = self._derive_key_from_password(password, salt, encryption_config)
        
        elif encryption_config.method == EncryptionMethod.KEY_AES256:
            if not key or len(key) != encryption_config.key_size:
                raise ValueError(f"Key of {encryption_config.key_size} bytes required")
            encryption_key = key
        
        elif encryption_config.method == EncryptionMethod.RSA_AES_HYBRID:
            if not public_key:
                raise ValueError("Public key required for RSA hybrid encryption")
            # Generate random AES key
            encryption_key = os.urandom(encryption_config.key_size)
            # This will be encrypted with RSA (implemented below)
        
        else:
            raise ValueError(f"Unsupported encryption method: {encryption_config.method}")
        
        # Encrypt data with AES
        encrypted_data = self._encrypt_aes(data, encryption_key, iv)
        
        # Handle RSA hybrid encryption
        if encryption_config.method == EncryptionMethod.RSA_AES_HYBRID:
            encrypted_data = self._encrypt_key_with_rsa(encryption_key, public_key) + encrypted_data
        
        # Generate HMAC for integrity
        hmac_key = hashlib.sha256(encryption_key + salt).digest()
        hmac_digest = hmac.new(hmac_key, encrypted_data, hashlib.sha256).digest()
        
        metadata = EncryptedSaveMetadata(
            encryption_config=encryption_config,
            salt=salt,
            iv=iv,
            hmac_digest=hmac_digest,
            timestamp=datetime.now()
        )
        
        self.logger.info(f"Encrypted save data using {encryption_config.method.value}")
        return encrypted_data, metadata
    
    def decrypt_save_data(self, encrypted_data: bytes,
                         metadata: EncryptedSaveMetadata,
                         password: Optional[str] = None,
                         key: Optional[bytes] = None,
                         private_key: Optional[bytes] = None) -> bytes:
        """
        Decrypt save file data.
        
        Args:
            encrypted_data: Encrypted save file data
            metadata: Encryption metadata
            password: Password for password-based decryption
            key: Key for key-based decryption
            private_key: Private key for RSA hybrid decryption
            
        Returns:
            Decrypted save file data
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        config = metadata.encryption_config
        
        if config.method == EncryptionMethod.NONE:
            return encrypted_data
        
        # Derive decryption key
        if config.method == EncryptionMethod.PASSWORD_AES256:
            if not password:
                raise ValueError("Password required for decryption")
            decryption_key = self._derive_key_from_password(password, metadata.salt, config)
        
        elif config.method == EncryptionMethod.KEY_AES256:
            if not key or len(key) != config.key_size:
                raise ValueError(f"Key of {config.key_size} bytes required")
            decryption_key = key
        
        elif config.method == EncryptionMethod.RSA_AES_HYBRID:
            if not private_key:
                raise ValueError("Private key required for RSA hybrid decryption")
            # Extract encrypted AES key and decrypt it
            rsa_key_size = 256  # 2048-bit RSA key
            encrypted_aes_key = encrypted_data[:rsa_key_size]
            encrypted_data = encrypted_data[rsa_key_size:]
            decryption_key = self._decrypt_key_with_rsa(encrypted_aes_key, private_key)
        
        else:
            raise ValueError(f"Unsupported encryption method: {config.method}")
        
        # Verify HMAC integrity
        hmac_key = hashlib.sha256(decryption_key + metadata.salt).digest()
        expected_hmac = hmac.new(hmac_key, encrypted_data, hashlib.sha256).digest()
        
        if not hmac.compare_digest(expected_hmac, metadata.hmac_digest):
            raise ValueError("HMAC verification failed - data may be corrupted or tampered with")
        
        # Decrypt data
        decrypted_data = self._decrypt_aes(encrypted_data, decryption_key, metadata.iv)
        
        self.logger.info(f"Successfully decrypted save data using {config.method.value}")
        return decrypted_data
    
    def _derive_key_from_password(self, password: str, salt: bytes, 
                                 config: EncryptionConfig) -> bytes:
        """Derive encryption key from password using specified method."""
        password_bytes = password.encode('utf-8')
        
        if config.key_derivation == KeyDerivationMethod.PBKDF2:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=config.key_size,
                salt=salt,
                iterations=config.iterations,
                backend=default_backend()
            )
            return kdf.derive(password_bytes)
        
        elif config.key_derivation == KeyDerivationMethod.SCRYPT:
            kdf = Scrypt(
                algorithm=hashes.SHA256(),
                length=config.key_size,
                salt=salt,
                n=config.scrypt_n,
                r=config.scrypt_r,
                p=config.scrypt_p,
                backend=default_backend()
            )
            return kdf.derive(password_bytes)
        
        else:
            raise ValueError(f"Unsupported key derivation method: {config.key_derivation}")
    
    def _encrypt_aes(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        """Encrypt data using AES-256-CBC."""
        # Add PKCS7 padding
        block_size = 16
        padding_length = block_size - (len(data) % block_size)
        padded_data = data + bytes([padding_length] * padding_length)
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data
    
    def _decrypt_aes(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """Decrypt data using AES-256-CBC."""
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = padded_data[-1]
        if padding_length > 16 or padding_length == 0:
            raise ValueError("Invalid padding")
        
        for i in range(padding_length):
            if padded_data[-(i+1)] != padding_length:
                raise ValueError("Invalid padding")
        
        return padded_data[:-padding_length]
    
    def _encrypt_key_with_rsa(self, aes_key: bytes, public_key_bytes: bytes) -> bytes:
        """Encrypt AES key with RSA public key."""
        public_key = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())
        
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_key
    
    def _decrypt_key_with_rsa(self, encrypted_key: bytes, private_key_bytes: bytes) -> bytes:
        """Decrypt AES key with RSA private key."""
        private_key = serialization.load_pem_private_key(
            private_key_bytes, 
            password=None, 
            backend=default_backend()
        )
        
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return aes_key
    
    def generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA keypair for hybrid encryption.
        
        Args:
            key_size: RSA key size in bits
            
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    def generate_random_key(self, key_size: int = 32) -> bytes:
        """Generate a random encryption key."""
        return os.urandom(key_size)
    
    def is_encrypted_save(self, file_path: Path) -> bool:
        """Check if a save file is encrypted."""
        try:
            with open(file_path, 'rb') as f:
                # Try to read as JSON to check for encryption metadata
                data = f.read()
                
            # Check if it starts with encryption metadata marker
            if data.startswith(b'{"encryption_metadata":'):
                return True
            
            # Try to parse as JSON and look for encryption metadata
            try:
                json_data = json.loads(data.decode('utf-8'))
                return 'encryption_metadata' in json_data
            except:
                # If it's not valid JSON, it might be encrypted binary
                return True
                
        except Exception:
            return False
    
    def extract_encryption_metadata(self, file_path: Path) -> Optional[EncryptedSaveMetadata]:
        """Extract encryption metadata from encrypted save file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Try to parse as JSON first
            try:
                json_data = json.loads(data.decode('utf-8'))
                if 'encryption_metadata' in json_data:
                    return EncryptedSaveMetadata.from_dict(json_data['encryption_metadata'])
            except:
                pass
            
            # For binary format, metadata would be at the beginning
            # This is a simplified implementation
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract encryption metadata: {e}")
            return None
    
    # Convenience methods for backward compatibility
    def encrypt_data_password(self, data: bytes, password: str) -> bytes:
        """Encrypt data with password - simplified interface."""
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Cryptography not available, returning unencrypted data")
            return data
            
        config = EncryptionConfig(
            method=EncryptionMethod.PASSWORD_AES256,
            key_derivation=KeyDerivationMethod.PBKDF2
        )
        
        encrypted_data, metadata = self.encrypt_save_data(data, config, password=password)
        
        # Pack metadata and encrypted data together for simple interface
        import json
        metadata_json = json.dumps(metadata.to_dict()).encode('utf-8')
        metadata_length = len(metadata_json)
        
        # Format: [4 bytes length][metadata][encrypted_data]
        packed_data = (
            metadata_length.to_bytes(4, 'big') +
            metadata_json +
            encrypted_data
        )
        
        return packed_data
    
    def decrypt_data_password(self, packed_data: bytes, password: str) -> bytes:
        """Decrypt data with password - simplified interface."""
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Cryptography not available, returning data as-is")
            return packed_data
            
        try:
            # Unpack metadata and encrypted data
            metadata_length = int.from_bytes(packed_data[:4], 'big')
            metadata_json = packed_data[4:4+metadata_length]
            encrypted_data = packed_data[4+metadata_length:]
            
            # Parse metadata
            import json
            metadata_dict = json.loads(metadata_json.decode('utf-8'))
            metadata = EncryptedSaveMetadata.from_dict(metadata_dict)
            
            return self.decrypt_save_data(encrypted_data, metadata, password=password)
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt with simple interface: {e}")
            # Fallback: try to return original data
            return packed_data


class EncryptedSaveManager:
    """High-level manager for encrypted save operations."""
    
    def __init__(self, save_dir: Path):
        self.save_dir = Path(save_dir)
        self.encryption = SaveFileEncryption()
        self.logger = logging.getLogger(__name__)
        
        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)
    
    def save_encrypted(self, save_data: bytes, save_name: str,
                      encryption_config: EncryptionConfig,
                      password: Optional[str] = None,
                      key: Optional[bytes] = None) -> Path:
        """
        Save data with encryption.
        
        Args:
            save_data: Save file data to encrypt
            save_name: Name for the save file
            encryption_config: Encryption configuration
            password: Password for password-based encryption
            key: Key for key-based encryption
            
        Returns:
            Path to the encrypted save file
        """
        save_path = self.save_dir / f"{save_name}.encrypted"
        
        # Encrypt the data
        encrypted_data, metadata = self.encryption.encrypt_save_data(
            save_data, encryption_config, password=password, key=key
        )
        
        # Create save file structure
        save_file_data = {
            'encryption_metadata': metadata.to_dict(),
            'encrypted_data': encrypted_data.hex()
        }
        
        # Write to file
        with open(save_path, 'w') as f:
            json.dump(save_file_data, f, indent=2)
        
        self.logger.info(f"Encrypted save file written: {save_path}")
        return save_path
    
    def load_encrypted(self, save_path: Path,
                      password: Optional[str] = None,
                      key: Optional[bytes] = None,
                      private_key: Optional[bytes] = None) -> bytes:
        """
        Load and decrypt save file.
        
        Args:
            save_path: Path to encrypted save file
            password: Password for decryption
            key: Key for decryption
            private_key: Private key for RSA decryption
            
        Returns:
            Decrypted save file data
        """
        with open(save_path, 'r') as f:
            save_file_data = json.load(f)
        
        # Extract metadata and encrypted data
        metadata = EncryptedSaveMetadata.from_dict(save_file_data['encryption_metadata'])
        encrypted_data = bytes.fromhex(save_file_data['encrypted_data'])
        
        # Decrypt the data
        decrypted_data = self.encryption.decrypt_save_data(
            encrypted_data, metadata, 
            password=password, key=key, private_key=private_key
        )
        
        self.logger.info(f"Decrypted save file loaded: {save_path}")
        return decrypted_data
    
    def change_encryption(self, save_path: Path, new_config: EncryptionConfig,
                         old_password: Optional[str] = None,
                         new_password: Optional[str] = None,
                         old_key: Optional[bytes] = None,
                         new_key: Optional[bytes] = None) -> Path:
        """
        Change encryption method/password for existing save file.
        
        Args:
            save_path: Path to existing encrypted save file
            new_config: New encryption configuration
            old_password: Current password (if applicable)
            new_password: New password (if applicable)
            old_key: Current key (if applicable)
            new_key: New key (if applicable)
            
        Returns:
            Path to re-encrypted save file
        """
        # Decrypt with old credentials
        decrypted_data = self.load_encrypted(
            save_path, password=old_password, key=old_key
        )
        
        # Re-encrypt with new configuration
        save_name = save_path.stem.replace('.encrypted', '') + '_reencrypted'
        new_save_path = self.save_encrypted(
            decrypted_data, save_name, new_config,
            password=new_password, key=new_key
        )
        
        self.logger.info(f"Re-encrypted save file: {save_path} -> {new_save_path}")
        return new_save_path
    
    def verify_password(self, save_path: Path, password: str) -> bool:
        """Verify if a password is correct for an encrypted save file."""
        try:
            self.load_encrypted(save_path, password=password)
            return True
        except Exception:
            return False
    
    def list_encrypted_saves(self) -> List[Tuple[Path, EncryptedSaveMetadata]]:
        """List all encrypted save files with their metadata."""
        encrypted_saves = []
        
        for save_file in self.save_dir.glob("*.encrypted"):
            try:
                metadata = self.encryption.extract_encryption_metadata(save_file)
                if metadata:
                    encrypted_saves.append((save_file, metadata))
            except Exception as e:
                self.logger.warning(f"Failed to read metadata from {save_file}: {e}")
        
        return encrypted_saves


# Utility functions for common encryption operations
def create_password_config(password_hint: Optional[str] = None) -> EncryptionConfig:
    """Create a standard password-based encryption configuration."""
    config = EncryptionConfig(
        method=EncryptionMethod.PASSWORD_AES256,
        key_derivation=KeyDerivationMethod.PBKDF2,
        iterations=100000
    )
    return config


def create_key_config() -> EncryptionConfig:
    """Create a standard key-based encryption configuration."""
    return EncryptionConfig(
        method=EncryptionMethod.KEY_AES256
    )


def create_hybrid_config() -> EncryptionConfig:
    """Create a standard RSA+AES hybrid encryption configuration."""
    return EncryptionConfig(
        method=EncryptionMethod.RSA_AES_HYBRID
    )


def generate_encryption_key() -> bytes:
    """Generate a random 256-bit encryption key."""
    encryption = SaveFileEncryption()
    return encryption.generate_random_key()


def generate_keypair() -> Tuple[bytes, bytes]:
    """Generate RSA keypair for hybrid encryption."""
    encryption = SaveFileEncryption()
    return encryption.generate_rsa_keypair()


# Example usage and testing
if __name__ == "__main__":
    # Example of encrypting and decrypting save data
    sample_data = b"This is sample save file data"
    
    # Password-based encryption
    config = create_password_config()
    encryption = SaveFileEncryption()
    
    encrypted_data, metadata = encryption.encrypt_save_data(
        sample_data, config, password="test_password"
    )
    
    decrypted_data = encryption.decrypt_save_data(
        encrypted_data, metadata, password="test_password"
    )
    
    print(f"Original: {sample_data}")
    print(f"Decrypted: {decrypted_data}")
    print(f"Match: {sample_data == decrypted_data}")
