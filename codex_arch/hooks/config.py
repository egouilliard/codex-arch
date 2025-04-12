"""
Hook Configuration System

This module provides functionality to manage configuration for Git hooks,
including enabling/disabling hooks and setting throttling parameters.
"""

import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = ".codex-arch/hooks.json"


@dataclass
class HookConfig:
    """Configuration for Git hooks"""
    
    # Hook enablement flags
    post_commit_enabled: bool = True
    post_merge_enabled: bool = True
    pre_push_enabled: bool = True
    
    # Throttling parameters (in seconds)
    throttle_interval: int = 300  # 5 minutes
    
    # Notification settings
    notification_enabled: bool = True
    notification_level: str = "info"  # "info", "warning", "error"
    
    # Analysis settings
    max_files_to_analyze: int = 10
    include_file_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"])
    exclude_file_patterns: List[str] = field(default_factory=lambda: ["**/node_modules/**", "**/venv/**", "**/.git/**"])
    
    # Additional hook-specific settings
    post_commit_settings: Dict[str, Any] = field(default_factory=dict)
    post_merge_settings: Dict[str, Any] = field(default_factory=dict)
    pre_push_settings: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Convert the configuration to a JSON string"""
        return json.dumps(asdict(self), indent=4)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'HookConfig':
        """Create a configuration object from a JSON string"""
        try:
            data = json.loads(json_str)
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to parse configuration: {e}")
            return cls()  # Return default configuration on error


def find_git_root() -> Optional[Path]:
    """
    Find the root directory of the Git repository.
    
    Returns:
        Path to the Git repository root, or None if not in a Git repository.
    """
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, ImportError):
        logger.error("Not in a Git repository or Git is not installed")
        return None


def create_default_config(config_path: Optional[str] = None) -> HookConfig:
    """
    Create a default hook configuration.
    
    Args:
        config_path: Optional path to save the configuration.
        
    Returns:
        HookConfig: Default configuration object.
    """
    config = HookConfig()
    
    if config_path:
        save_hook_config(config, config_path)
    
    return config


def load_hook_config(config_path: Optional[str] = None) -> HookConfig:
    """
    Load the hook configuration from a file.
    
    Args:
        config_path: Path to the configuration file. If None, will try to find it
                     in the Git repository root.
    
    Returns:
        The loaded configuration, or default configuration if loading fails.
    """
    # If no config path is provided, try to find it in the repository root
    if config_path is None:
        git_root = find_git_root()
        if git_root:
            config_path = git_root / DEFAULT_CONFIG_PATH
        else:
            logger.warning("Not in a Git repository, using default configuration")
            return HookConfig()
    else:
        config_path = Path(config_path)
    
    # Check if the configuration file exists
    if not config_path.exists():
        logger.warning(f"Configuration file not found at {config_path}, using default configuration")
        return HookConfig()
    
    # Load the configuration
    try:
        with open(config_path, 'r') as f:
            config_data = f.read()
        
        return HookConfig.from_json(config_data)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return HookConfig()


def save_hook_config(config: HookConfig, config_path: Optional[str] = None) -> bool:
    """
    Save the hook configuration to a file.
    
    Args:
        config: The configuration to save.
        config_path: Path to the configuration file. If None, will try to save it
                     in the Git repository root.
    
    Returns:
        True if the configuration was saved successfully, False otherwise.
    """
    # If no config path is provided, try to find it in the repository root
    if config_path is None:
        git_root = find_git_root()
        if git_root:
            config_dir = git_root / ".codex-arch"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "hooks.json"
        else:
            logger.error("Not in a Git repository, cannot save configuration")
            return False
    else:
        config_path = Path(config_path)
        config_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Save the configuration
    try:
        with open(config_path, 'w') as f:
            f.write(config.to_json())
        
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        return False


def update_hook_config(
    updates: Dict[str, Any],
    config_path: Optional[str] = None
) -> HookConfig:
    """
    Update hook configuration with new values.
    
    Args:
        updates: Dictionary of configuration values to update.
        config_path: Optional path to the configuration file.
        
    Returns:
        HookConfig: Updated configuration object.
    """
    config = load_hook_config(config_path)
    
    # Update the configuration with new values
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown configuration key: {key}")
    
    # Save the updated configuration
    save_hook_config(config, config_path)
    
    return config 