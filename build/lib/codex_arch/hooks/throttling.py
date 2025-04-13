"""
Throttling Mechanism for Git Hooks

This module provides functionality to throttle Git hook executions to prevent
excessive analysis runs when multiple changes occur in quick succession.
"""

import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union

logger = logging.getLogger(__name__)

DEFAULT_THROTTLE_FILE = ".codex-arch/throttle.json"


class ThrottleManager:
    """
    Manages throttling of hook executions to prevent excessive analysis runs.
    """
    
    def __init__(self, throttle_file: str = DEFAULT_THROTTLE_FILE, throttle_interval: int = 300):
        """
        Initialize the throttle manager.
        
        Args:
            throttle_file: Path to the file storing throttle timestamps.
            throttle_interval: Minimum interval between hook executions in seconds.
        """
        self.throttle_file = throttle_file
        self.throttle_interval = throttle_interval
        self.throttle_dir = os.path.dirname(throttle_file)
        
        # Create throttle directory if it doesn't exist
        if self.throttle_dir and not os.path.exists(self.throttle_dir):
            os.makedirs(self.throttle_dir)
    
    def _load_throttle_data(self) -> Dict[str, float]:
        """
        Load throttle timestamp data from file.
        
        Returns:
            Dict[str, float]: Dictionary of hook names to timestamp.
        """
        if not os.path.exists(self.throttle_file):
            return {}
            
        try:
            with open(self.throttle_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_throttle_data(self, data: Dict[str, float]) -> None:
        """
        Save throttle timestamp data to file.
        
        Args:
            data: Dictionary of hook names to timestamp.
        """
        with open(self.throttle_file, 'w') as f:
            json.dump(data, f)
    
    def should_throttle(self, hook_name: str) -> bool:
        """
        Check if a hook execution should be throttled.
        
        Args:
            hook_name: Name of the hook (e.g., 'post-commit').
            
        Returns:
            bool: True if the hook should be throttled, False otherwise.
        """
        throttle_data = self._load_throttle_data()
        
        # Get the timestamp of the last execution
        last_execution = throttle_data.get(hook_name, 0)
        current_time = time.time()
        
        # Check if enough time has passed since the last execution
        if current_time - last_execution < self.throttle_interval:
            time_since_last = int(current_time - last_execution)
            logger.info(
                f"Throttling {hook_name} hook: {time_since_last}s since last execution "
                f"(throttle interval: {self.throttle_interval}s)"
            )
            return True
            
        return False
    
    def record_execution(self, hook_name: str) -> None:
        """
        Record a hook execution.
        
        Args:
            hook_name: Name of the hook (e.g., 'post-commit').
        """
        throttle_data = self._load_throttle_data()
        
        # Update the timestamp
        throttle_data[hook_name] = time.time()
        
        # Save the updated data
        self._save_throttle_data(throttle_data)
        logger.debug(f"Recorded execution of {hook_name} hook")
    
    def get_next_allowed_time(self, hook_name: str) -> Optional[datetime]:
        """
        Get the next time a hook is allowed to execute.
        
        Args:
            hook_name: Name of the hook (e.g., 'post-commit').
            
        Returns:
            Optional[datetime]: The next allowed time, or None if execution is allowed now.
        """
        throttle_data = self._load_throttle_data()
        
        # Get the timestamp of the last execution
        last_execution = throttle_data.get(hook_name, 0)
        current_time = time.time()
        
        # Check if enough time has passed since the last execution
        if current_time - last_execution < self.throttle_interval:
            next_time = last_execution + self.throttle_interval
            return datetime.fromtimestamp(next_time)
            
        return None
    
    def reset_throttle(self, hook_name: Optional[str] = None) -> None:
        """
        Reset throttle timestamps.
        
        Args:
            hook_name: Optional name of the hook to reset. If None, reset all hooks.
        """
        if hook_name is None:
            # Reset all hooks
            if os.path.exists(self.throttle_file):
                os.remove(self.throttle_file)
            logger.info("Reset all throttle timestamps")
        else:
            # Reset only the specified hook
            throttle_data = self._load_throttle_data()
            if hook_name in throttle_data:
                del throttle_data[hook_name]
                self._save_throttle_data(throttle_data)
                logger.info(f"Reset throttle timestamp for {hook_name} hook")
    
    def update_throttle_interval(self, interval: int) -> None:
        """
        Update the throttle interval.
        
        Args:
            interval: New throttle interval in seconds.
        """
        self.throttle_interval = interval
        logger.info(f"Updated throttle interval to {interval}s") 