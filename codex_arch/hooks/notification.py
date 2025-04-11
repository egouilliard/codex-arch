"""
Notification Mechanism for Git Hooks

This module provides functionality to send notifications when Git hooks are triggered
and when analysis results are available.
"""

import os
import logging
import platform
import subprocess
from typing import Optional, List, Dict, Any, Union

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages notifications for Git hook events and analysis results.
    """
    
    def __init__(self, enabled: bool = True, level: str = "info"):
        """
        Initialize the notification manager.
        
        Args:
            enabled: Whether notifications are enabled.
            level: Minimum level of notifications to display ("info", "warning", "error").
        """
        self.enabled = enabled
        self.level = level.lower()
        self._level_map = {
            "info": 0,
            "warning": 1,
            "error": 2
        }
    
    def _can_send(self, level: str) -> bool:
        """
        Check if a notification of the given level can be sent.
        
        Args:
            level: Notification level ("info", "warning", "error").
            
        Returns:
            bool: True if the notification can be sent, False otherwise.
        """
        if not self.enabled:
            return False
            
        level_value = self._level_map.get(level.lower(), 0)
        min_level_value = self._level_map.get(self.level, 0)
        
        return level_value >= min_level_value
    
    def _get_platform_command(self, title: str, message: str) -> Optional[List[str]]:
        """
        Get the platform-specific command to show a notification.
        
        Args:
            title: Notification title.
            message: Notification message.
            
        Returns:
            Optional[List[str]]: Command arguments, or None if not supported.
        """
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return [
                "osascript", "-e", 
                f'display notification "{message}" with title "{title}"'
            ]
        elif system == "Linux":
            # Try to detect available notification systems
            if self._command_exists("notify-send"):
                return ["notify-send", title, message]
            elif self._command_exists("zenity"):
                return ["zenity", "--notification", "--text", f"{title}: {message}"]
        elif system == "Windows":
            # PowerShell notification
            script = f"""
            [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipTitle = '{title}'
            $notification.BalloonTipText = '{message}'
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            """
            return ["powershell", "-Command", script]
            
        return None
    
    def _command_exists(self, command: str) -> bool:
        """
        Check if a command exists in the system PATH.
        
        Args:
            command: Command name.
            
        Returns:
            bool: True if the command exists, False otherwise.
        """
        return any(
            os.path.exists(os.path.join(path, command))
            for path in os.environ.get("PATH", "").split(os.pathsep)
        )
    
    def send_notification(self, title: str, message: str, level: str = "info") -> bool:
        """
        Send a notification with the given title and message.
        
        Args:
            title: Notification title.
            message: Notification message.
            level: Notification level ("info", "warning", "error").
            
        Returns:
            bool: True if the notification was sent, False otherwise.
        """
        if not self._can_send(level):
            return False
            
        command = self._get_platform_command(title, message)
        if command is None:
            logger.debug("Notifications not supported on this platform")
            return False
            
        try:
            subprocess.run(command, check=False, capture_output=True)
            logger.debug(f"Sent notification: {title} - {message}")
            return True
        except Exception as e:
            logger.debug(f"Failed to send notification: {e}")
            return False
    
    def notify_hook_execution(self, hook_name: str, message: Optional[str] = None) -> bool:
        """
        Send a notification about a hook execution.
        
        Args:
            hook_name: Name of the hook (e.g., 'post-commit').
            message: Optional additional message.
            
        Returns:
            bool: True if the notification was sent, False otherwise.
        """
        title = f"Codex-Arch {hook_name} Hook"
        content = message or f"The {hook_name} hook was triggered"
        return self.send_notification(title, content)
    
    def notify_analysis_results(self, results: Dict[str, Any], level: str = "info") -> bool:
        """
        Send a notification about analysis results.
        
        Args:
            results: Analysis results.
            level: Notification level based on the severity of findings.
            
        Returns:
            bool: True if the notification was sent, False otherwise.
        """
        title = "Codex-Arch Analysis Results"
        
        # Create a summary of the results
        findings_count = results.get("findings_count", 0)
        
        if findings_count == 0:
            message = "No issues found in the analyzed code."
        else:
            message = f"Found {findings_count} issues in the analyzed code."
            
        return self.send_notification(title, message, level)
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable notifications.
        
        Args:
            enabled: Whether notifications should be enabled.
        """
        self.enabled = enabled
        logger.info(f"Notifications {'enabled' if enabled else 'disabled'}")
    
    def set_level(self, level: str) -> None:
        """
        Set the minimum notification level.
        
        Args:
            level: Minimum level of notifications to display ("info", "warning", "error").
        """
        if level.lower() in self._level_map:
            self.level = level.lower()
            logger.info(f"Notification level set to {level}")
        else:
            logger.warning(f"Invalid notification level: {level}") 