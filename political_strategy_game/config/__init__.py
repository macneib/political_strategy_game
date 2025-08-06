"""
Configuration management for the political strategy game.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .game_config import *


@dataclass
class GameConfig:
    """Main configuration class for the game."""
    
    political: Dict[str, Any]
    leader: Dict[str, Any]
    event: Dict[str, Any]
    memory: Dict[str, Any]
    llm: Dict[str, Any]
    performance: Dict[str, Any]
    paths: Dict[str, str]
    logging: Dict[str, Any]
    
    @classmethod
    def load_default(cls) -> 'GameConfig':
        """Load default configuration."""
        return cls(
            political=POLITICAL_CONFIG,
            leader=LEADER_CONFIG,
            event=EVENT_CONFIG,
            memory=MEMORY_CONFIG,
            llm=LLM_CONFIG,
            performance=PERFORMANCE_CONFIG,
            paths=PATHS,
            logging=LOGGING_CONFIG
        )
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'GameConfig':
        """Load configuration from a JSON file."""
        if not config_path.exists():
            return cls.load_default()
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Merge with defaults
            default_config = cls.load_default()
            
            return cls(
                political=config_data.get('political', default_config.political),
                leader=config_data.get('leader', default_config.leader),
                event=config_data.get('event', default_config.event),
                memory=config_data.get('memory', default_config.memory),
                llm=config_data.get('llm', default_config.llm),
                performance=config_data.get('performance', default_config.performance),
                paths=config_data.get('paths', default_config.paths),
                logging=config_data.get('logging', default_config.logging)
            )
        except Exception as e:
            print(f"Error loading config file: {e}")
            return cls.load_default()
    
    def save_to_file(self, config_path: Path) -> bool:
        """Save configuration to a JSON file."""
        try:
            config_data = {
                'political': self.political,
                'leader': self.leader,
                'event': self.event,
                'memory': self.memory,
                'llm': self.llm,
                'performance': self.performance,
                'paths': self.paths,
                'logging': self.logging
            }
            
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving config file: {e}")
            return False
    
    def get_data_path(self, subdir: str = "") -> Path:
        """Get path to data directory or subdirectory."""
        base_path = Path(self.paths['data_dir'])
        if subdir:
            return base_path / subdir
        return base_path
    
    def ensure_directories(self) -> None:
        """Create all necessary directories."""
        for path_key, path_value in self.paths.items():
            Path(path_value).mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Manages game configuration and environment variables."""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("config/game_config.json")
        self.config = GameConfig.load_from_file(self.config_file)
        
        # Load environment variables
        self._load_env_variables()
        
        # Ensure directories exist
        self.config.ensure_directories()
    
    def _load_env_variables(self) -> None:
        """Load configuration from environment variables."""
        # LLM API keys
        if os.getenv('OPENAI_API_KEY'):
            self.config.llm['openai_api_key'] = os.getenv('OPENAI_API_KEY')
        
        if os.getenv('ANTHROPIC_API_KEY'):
            self.config.llm['anthropic_api_key'] = os.getenv('ANTHROPIC_API_KEY')
        
        # Override config values from environment
        if os.getenv('LLM_PROVIDER'):
            self.config.llm['provider'] = os.getenv('LLM_PROVIDER')
        
        if os.getenv('LLM_MODEL'):
            self.config.llm['model'] = os.getenv('LLM_MODEL')
        
        if os.getenv('LOG_LEVEL'):
            self.config.logging['level'] = os.getenv('LOG_LEVEL')
    
    def get_config(self) -> GameConfig:
        """Get the current configuration."""
        return self.config
    
    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update a configuration value."""
        if hasattr(self.config, section):
            section_dict = getattr(self.config, section)
            if isinstance(section_dict, dict):
                section_dict[key] = value
    
    def save_config(self) -> bool:
        """Save current configuration to file."""
        return self.config.save_to_file(self.config_file)
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self.config = GameConfig.load_from_file(self.config_file)
        self._load_env_variables()


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> GameConfig:
    """Get the global game configuration."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_config()


def init_config(config_file: Optional[Path] = None) -> ConfigManager:
    """Initialize the global configuration manager."""
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager
