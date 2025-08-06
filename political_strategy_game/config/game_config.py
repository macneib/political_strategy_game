# Game Configuration Settings

# Political Simulation Parameters
POLITICAL_CONFIG = {
    "max_advisors_per_civilization": 10,
    "base_advisor_loyalty": 0.5,
    "base_advisor_influence": 0.5,
    "conspiracy_threshold": 0.3,
    "coup_success_base_chance": 0.4,
    "memory_decay_rate": 0.02,
    "relationship_decay_rate": 0.01,
    "max_memories_per_advisor": 1000,
}

# Leader Behavior Parameters  
LEADER_CONFIG = {
    "base_legitimacy": 0.7,
    "base_popularity": 0.5,
    "paranoia_increase_rate": 0.01,
    "popularity_decay_rate": 0.005,
    "trust_change_multiplier": 1.0,
}

# Event System Parameters
EVENT_CONFIG = {
    "max_events_per_turn": 5,
    "event_probability_modifiers": {
        "stable": 0.1,
        "tense": 0.3,
        "unstable": 0.6,
        "crisis": 0.9,
        "collapse": 1.0
    }
}

# Memory System Parameters
MEMORY_CONFIG = {
    "compression_threshold": 1000,
    "min_reliability_threshold": 0.01,
    "access_reinforcement": 0.01,
    "emotional_weight_multiplier": 1.5,
}

# LLM Integration Parameters
LLM_CONFIG = {
    "provider": "openai",  # "openai", "anthropic", "local"
    "model": "gpt-4",
    "max_tokens": 500,
    "temperature": 0.7,
    "timeout_seconds": 10,
    "max_retries": 3,
    "fallback_to_rules": True,
}

# Performance Parameters
PERFORMANCE_CONFIG = {
    "max_turn_processing_time": 30,  # seconds
    "max_llm_response_time": 5,      # seconds
    "memory_operation_timeout": 0.1,  # seconds
    "concurrent_civilization_limit": 8,
}

# File Paths
PATHS = {
    "data_dir": "data/",
    "saves_dir": "data/saves/",
    "logs_dir": "logs/",
    "config_dir": "config/",
    "memory_dir": "data/memories/",
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_logging": True,
    "console_logging": True,
    "max_log_size_mb": 100,
    "backup_count": 5,
}
