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

# Intelligence and Espionage Parameters (Task 6.1)
ESPIONAGE_CONFIG = {
    "base_intelligence_budget": 1000.0,
    "base_influence_points": 100.0,
    "base_technology_level": 0.5,
    "base_counter_intelligence_strength": 0.5,
    "asset_recruitment_costs": {
        "agent": 150.0,
        "informant": 75.0,
        "sleeper": 200.0,
        "corrupted_advisor": 300.0,
        "double_agent": 400.0
    },
    "operation_base_costs": {
        "political_intelligence": {"budget": 50.0, "influence": 10.0},
        "advisor_surveillance": {"budget": 75.0, "influence": 15.0},
        "disinformation_campaign": {"budget": 100.0, "influence": 25.0},
        "advisor_bribery": {"budget": 200.0, "influence": 20.0},
        "sabotage_mission": {"budget": 150.0, "influence": 30.0},
        "assassination_attempt": {"budget": 500.0, "influence": 100.0},
        "memory_extraction": {"budget": 300.0, "influence": 50.0},
        "counter_surveillance": {"budget": 100.0, "influence": 15.0}
    },
    "operation_difficulty_modifiers": {
        "trivial": 0.5,
        "easy": 0.7,
        "moderate": 1.0,
        "hard": 1.5,
        "extreme": 2.0
    },
    "discovery_risk_base": {
        "political_intelligence": 0.1,
        "advisor_surveillance": 0.15,
        "disinformation_campaign": 0.2,
        "advisor_bribery": 0.25,
        "sabotage_mission": 0.3,
        "assassination_attempt": 0.5,
        "memory_extraction": 0.4,
        "counter_surveillance": 0.05
    },
    "intelligence_reliability_thresholds": {
        "low_confidence": 0.3,
        "moderate_confidence": 0.6,
        "high_confidence": 0.8,
        "certain": 0.95
    },
    "diplomatic_incident_severity": {
        "political_intelligence": -0.1,
        "advisor_surveillance": -0.2,
        "disinformation_campaign": -0.4,
        "advisor_bribery": -0.4,
        "sabotage_mission": -0.6,
        "assassination_attempt": -0.8,
        "memory_extraction": -0.6,
        "counter_surveillance": 0.0
    },
    "asset_skill_improvement_rates": {
        "technical": 0.1,
        "social": 0.08,
        "infiltration": 0.12,
        "analysis": 0.06,
        "operational": 0.09
    },
    "training_costs": {
        "technical": 100.0,
        "social": 80.0,
        "infiltration": 120.0,
        "analysis": 60.0,
        "operational": 90.0
    },
    "max_active_operations_per_target": 3,
    "intelligence_report_expiry_turns": 10,
    "asset_exposure_risk_increase_per_operation": 0.05,
    "counter_intelligence_detection_threshold": 0.7,
    "security_audit_frequency": 5  # turns
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
