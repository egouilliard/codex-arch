#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Git hooks functionality
"""

import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from codex_arch.hooks.hook_scripts import (
    find_git_root,
    install_hooks,
    uninstall_hooks,
    post_commit_hook,
    post_merge_hook,
    pre_push_hook
)
from codex_arch.hooks.config import HookConfig, load_hook_config, save_hook_config
from codex_arch.hooks.throttling import ThrottleManager
from codex_arch.hooks.notification import NotificationManager


class TestHookScripts(unittest.TestCase):
    """Test cases for Git hook scripts"""
    
    def setUp(self):
        """Set up temporary directory structure for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.git_dir = os.path.join(self.temp_dir, '.git')
        self.hooks_dir = os.path.join(self.git_dir, 'hooks')
        self.config_dir = os.path.join(self.temp_dir, '.codex-arch')
        
        # Create directory structure
        os.makedirs(self.hooks_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Change to temp directory for tests
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files after tests"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)
    
    @patch('codex_arch.hooks.hook_scripts.find_git_root')
    def test_install_hooks(self, mock_find_git_root):
        """Test installation of Git hooks"""
        mock_find_git_root.return_value = Path(self.temp_dir)
        
        # Run the install function
        install_hooks()
        
        # Check that hook files were created
        hooks = ['post-commit', 'post-merge', 'pre-push']
        for hook in hooks:
            hook_path = os.path.join(self.hooks_dir, hook)
            self.assertTrue(os.path.exists(hook_path))
            self.assertTrue(os.access(hook_path, os.X_OK))
    
    @patch('codex_arch.hooks.hook_scripts.find_git_root')
    def test_uninstall_hooks(self, mock_find_git_root):
        """Test uninstallation of Git hooks"""
        mock_find_git_root.return_value = Path(self.temp_dir)
        
        # Create dummy hook files
        hooks = ['post-commit', 'post-merge', 'pre-push']
        for hook in hooks:
            hook_path = os.path.join(self.hooks_dir, hook)
            with open(hook_path, 'w') as f:
                f.write('#!/bin/sh\n# Codex-Arch hook')
            os.chmod(hook_path, 0o755)
        
        # Run the uninstall function
        uninstall_hooks()
        
        # Check that hook files were removed
        for hook in hooks:
            hook_path = os.path.join(self.hooks_dir, hook)
            self.assertFalse(os.path.exists(hook_path))
    
    def test_hook_config(self):
        """Test hook configuration loading and saving"""
        config_path = os.path.join(self.config_dir, 'hooks.json')
        
        # Create a custom config
        config = HookConfig(
            post_commit_enabled=True,
            post_merge_enabled=False,
            pre_push_enabled=True,
            throttle_interval=600,
            notification_enabled=True,
            notification_level="warning"
        )
        
        # Save the config
        save_hook_config(config, config_path)
        
        # Load the config and verify
        loaded_config = load_hook_config(config_path)
        self.assertEqual(loaded_config.post_commit_enabled, True)
        self.assertEqual(loaded_config.post_merge_enabled, False)
        self.assertEqual(loaded_config.throttle_interval, 600)
        self.assertEqual(loaded_config.notification_level, "warning")
    
    @patch('codex_arch.hooks.throttling.ThrottleManager.should_run')
    @patch('codex_arch.hooks.hook_scripts.IncrementalAnalyzer')
    def test_post_commit_hook(self, mock_analyzer, mock_should_run):
        """Test post-commit hook functionality"""
        mock_should_run.return_value = True
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Run the hook
        result = post_commit_hook()
        
        # Verify the hook called the analyzer
        self.assertTrue(result)
        mock_analyzer_instance.analyze_changes.assert_called_once()
    
    @patch('codex_arch.hooks.throttling.ThrottleManager.should_run')
    @patch('codex_arch.hooks.hook_scripts.IncrementalAnalyzer')
    def test_throttling(self, mock_analyzer, mock_should_run):
        """Test throttling mechanism"""
        # Set up the throttle manager to reject the run
        mock_should_run.return_value = False
        
        # Run the hook
        result = post_commit_hook()
        
        # Verify the hook was throttled
        self.assertTrue(result)  # Should still return True for Git
        mock_analyzer.assert_not_called()  # But should not run analysis
    
    @patch('codex_arch.hooks.notification.NotificationManager.notify')
    @patch('codex_arch.hooks.hook_scripts.IncrementalAnalyzer')
    def test_notifications(self, mock_analyzer, mock_notify):
        """Test notification mechanism"""
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Run the hook with notifications enabled
        with patch('codex_arch.hooks.hook_scripts.load_hook_config') as mock_config:
            config = HookConfig(notification_enabled=True)
            mock_config.return_value = config
            
            post_commit_hook()
            
            # Verify notification was sent
            mock_notify.assert_called()


class TestThrottleManager(unittest.TestCase):
    """Test cases for the throttling mechanism"""
    
    def setUp(self):
        """Set up temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.throttle_file = os.path.join(self.temp_dir, 'throttle.json')
    
    def tearDown(self):
        """Clean up temporary files after tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_throttle_manager_new(self):
        """Test ThrottleManager with a new throttle file"""
        manager = ThrottleManager(throttle_file=self.throttle_file)
        
        # First run should always be allowed
        self.assertTrue(manager.should_run('post-commit'))
        
        # Run again immediately - should be throttled
        self.assertFalse(manager.should_run('post-commit'))
    
    def test_throttle_manager_expiry(self):
        """Test ThrottleManager throttle expiration"""
        # Create a throttle file with an expired timestamp
        with open(self.throttle_file, 'w') as f:
            json.dump({
                'post-commit': '2000-01-01T00:00:00'
            }, f)
        
        manager = ThrottleManager(throttle_file=self.throttle_file)
        
        # Run should be allowed since timestamp is old
        self.assertTrue(manager.should_run('post-commit'))


class TestNotificationManager(unittest.TestCase):
    """Test cases for the notification mechanism"""
    
    @patch('codex_arch.hooks.notification.NotificationManager._send_notification')
    def test_notifications(self, mock_send):
        """Test notification sending logic"""
        manager = NotificationManager(enabled=True, level="info")
        
        # Info level notification
        manager.notify("Test info message", level="info")
        mock_send.assert_called_once()
        mock_send.reset_mock()
        
        # Warning level notification
        manager.notify("Test warning message", level="warning")
        mock_send.assert_called_once()
        mock_send.reset_mock()
        
        # Disabled notifications
        manager = NotificationManager(enabled=False)
        manager.notify("Test disabled message")
        mock_send.assert_not_called()
        
        # Level filtering
        manager = NotificationManager(enabled=True, level="warning")
        manager.notify("Test info filtered", level="info")
        mock_send.assert_not_called()


if __name__ == '__main__':
    unittest.main() 