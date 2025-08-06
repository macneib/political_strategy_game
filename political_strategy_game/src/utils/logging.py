"""
Logging utilities for the political strategy game.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from ..config import get_config


class GameLogger:
    """Centralized logging for the political strategy game."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup the logger with handlers and formatters."""
        config = get_config()
        log_config = config.logging
        
        # Set log level
        level = getattr(logging, log_config['level'].upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(log_config['format'])
        
        # Console handler
        if log_config['console_logging']:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_config['file_logging']:
            log_dir = Path(config.paths['logs_dir'])
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / f"{self.name.replace('.', '_')}.log"
            
            # Rotating file handler
            max_bytes = log_config['max_log_size_mb'] * 1024 * 1024
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=log_config['backup_count']
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Avoid duplicate logs
        self.logger.propagate = False
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def log_political_event(self, event_data: dict) -> None:
        """Log a political event with structured data."""
        event_type = event_data.get('type', 'unknown')
        civilization = event_data.get('civilization_id', 'unknown')
        turn = event_data.get('turn', 0)
        
        self.info(
            f"Political Event [{event_type}] in {civilization} at turn {turn}: "
            f"{event_data.get('description', 'No description')}"
        )
    
    def log_advisor_action(self, advisor_id: str, action: str, 
                          context: Optional[dict] = None) -> None:
        """Log an advisor action."""
        context_str = f" - Context: {context}" if context else ""
        self.info(f"Advisor {advisor_id} performed action: {action}{context_str}")
    
    def log_leader_decision(self, leader_id: str, decision: str, 
                           advisor_input: Optional[dict] = None) -> None:
        """Log a leader decision."""
        input_str = f" (based on advisor input: {advisor_input})" if advisor_input else ""
        self.info(f"Leader {leader_id} made decision: {decision}{input_str}")
    
    def log_coup_attempt(self, civilization_id: str, conspirators: list, 
                        success: bool, turn: int) -> None:
        """Log a coup attempt."""
        outcome = "succeeded" if success else "failed"
        conspirator_list = ", ".join(conspirators)
        self.warning(
            f"COUP ATTEMPT in {civilization_id} at turn {turn}: "
            f"Conspirators [{conspirator_list}] - {outcome}"
        )
    
    def log_performance_metric(self, operation: str, duration: float, 
                              success: bool = True) -> None:
        """Log performance metrics."""
        status = "SUCCESS" if success else "FAILED"
        self.debug(f"Performance [{operation}]: {duration:.3f}s - {status}")


# Logger instances for different components
def get_logger(name: str) -> GameLogger:
    """Get a logger instance for a component."""
    return GameLogger(name)


# Pre-configured loggers for main components
political_logger = get_logger("political.engine")
memory_logger = get_logger("memory.system")  
advisor_logger = get_logger("advisor.system")
leader_logger = get_logger("leader.system")
llm_logger = get_logger("llm.integration")
event_logger = get_logger("event.system")
performance_logger = get_logger("performance")
game_logger = get_logger("game.main")
