#!/usr/bin/env python3
"""
Tests for Git Hook Throttling and Notification Mechanisms.

This module tests the throttling and notification mechanisms for Git hooks
to ensure they properly limit execution frequency and notify users of results.
"""

import os
import json
import time
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Directly import only the classes we need to test
from codex_arch.hooks.throttling import ThrottleManager
from codex_arch.hooks.notification import NotificationManager


class TestThrottling(unittest.TestCase):
    """Test the throttling mechanism for Git hooks."""

    def setUp(self):
        """Set up a temporary throttle file for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.throttle_file = os.path.join(self.temp_dir.name, "throttle.json")
        self.throttle_manager = ThrottleManager(
            throttle_file=self.throttle_file,
            throttle_interval=5  # Short interval for testing (5 seconds)
        )

    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()

    def test_should_throttle_initial(self):
        """Test that initial execution is not throttled."""
        # First execution should not be throttled
        self.assertFalse(self.throttle_manager.should_throttle("test_hook"))

    def test_throttle_after_execution(self):
        """Test that hook is throttled after recent execution."""
        # Record an execution
        self.throttle_manager.record_execution("test_hook")
        
        # Second execution should be throttled (within throttle interval)
        self.assertTrue(self.throttle_manager.should_throttle("test_hook"))

    def test_throttle_expiration(self):
        """Test that throttling expires after the interval."""
        # Record an execution
        self.throttle_manager.record_execution("test_hook")
        
        # Wait for throttle period to expire (6 seconds > 5 second throttle)
        time.sleep(6)
        
        # Should not be throttled anymore
        self.assertFalse(self.throttle_manager.should_throttle("test_hook"))

    def test_multiple_hooks(self):
        """Test that different hooks are throttled independently."""
        # Record an execution for first hook
        self.throttle_manager.record_execution("hook1")
        
        # Second hook should not be throttled
        self.assertFalse(self.throttle_manager.should_throttle("hook2"))
        
        # First hook should be throttled
        self.assertTrue(self.throttle_manager.should_throttle("hook1"))

    def test_reset_throttle(self):
        """Test that resetting the throttle works."""
        # Record executions
        self.throttle_manager.record_execution("hook1")
        self.throttle_manager.record_execution("hook2")
        
        # Reset one hook's throttle
        self.throttle_manager.reset_throttle("hook1")
        
        # hook1 should not be throttled anymore, but hook2 should be
        self.assertFalse(self.throttle_manager.should_throttle("hook1"))
        self.assertTrue(self.throttle_manager.should_throttle("hook2"))
        
        # Reset all hooks
        self.throttle_manager.reset_throttle()
        
        # No hooks should be throttled now
        self.assertFalse(self.throttle_manager.should_throttle("hook1"))
        self.assertFalse(self.throttle_manager.should_throttle("hook2"))


class TestNotification(unittest.TestCase):
    """Test the notification mechanism for Git hooks."""

    def setUp(self):
        """Set up the notification manager."""
        self.notification_manager = NotificationManager(enabled=True)

    @patch('subprocess.run')
    def test_send_notification(self, mock_run):
        """Test sending a notification."""
        # Configure the mock
        mock_run.return_value = MagicMock()
        
        # Test sending a notification
        with patch.object(self.notification_manager, '_get_platform_command', 
                         return_value=["echo", "notification"]):
            result = self.notification_manager.send_notification(
                "Test Title", "Test Message"
            )
            
            # Verify notification was sent
            self.assertTrue(result)
            mock_run.assert_called_once()

    def test_notification_levels(self):
        """Test notification level filtering."""
        # Set notification level to warning
        self.notification_manager.set_level("warning")
        
        # Info notifications should not be sent
        with patch.object(self.notification_manager, '_get_platform_command',
                         return_value=["echo", "notification"]):
            with patch('subprocess.run') as mock_run:
                # Info notification should be filtered out
                result = self.notification_manager.send_notification(
                    "Test Title", "Test Message", level="info"
                )
                self.assertFalse(result)
                mock_run.assert_not_called()
                
                # Warning notification should be sent
                result = self.notification_manager.send_notification(
                    "Test Title", "Test Message", level="warning"
                )
                self.assertTrue(result)
                mock_run.assert_called_once()

    def test_disable_notifications(self):
        """Test disabling notifications."""
        # Disable notifications
        self.notification_manager.set_enabled(False)
        
        # No notifications should be sent when disabled
        with patch.object(self.notification_manager, '_get_platform_command',
                         return_value=["echo", "notification"]):
            with patch('subprocess.run') as mock_run:
                result = self.notification_manager.send_notification(
                    "Test Title", "Test Message"
                )
                self.assertFalse(result)
                mock_run.assert_not_called()

    @patch('subprocess.run')
    def test_hook_execution_notification(self, mock_run):
        """Test notification for hook execution."""
        # Configure the mock
        mock_run.return_value = MagicMock()
        
        # Test notifying about hook execution
        with patch.object(self.notification_manager, '_get_platform_command',
                         return_value=["echo", "notification"]):
            result = self.notification_manager.notify_hook_execution("post-commit")
            
            # Verify notification was sent
            self.assertTrue(result)
            mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_analysis_results_notification(self, mock_run):
        """Test notification for analysis results."""
        # Configure the mock
        mock_run.return_value = MagicMock()
        
        # Test notifying about analysis results
        with patch.object(self.notification_manager, '_get_platform_command',
                         return_value=["echo", "notification"]):
            result = self.notification_manager.notify_analysis_results(
                {"findings_count": 5}
            )
            
            # Verify notification was sent
            self.assertTrue(result)
            mock_run.assert_called_once()


if __name__ == '__main__':
    unittest.main() 