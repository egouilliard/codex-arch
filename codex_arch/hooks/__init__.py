"""
Git Hook Integration Module

This module provides integration with Git hooks to automatically trigger
code analysis on repository changes.
"""

from codex_arch.hooks.hook_scripts import (
    install_hooks,
    uninstall_hooks,
    post_commit_hook,
    post_merge_hook,
    pre_push_hook
)

from codex_arch.hooks.config import (
    HookConfig,
    load_hook_config
)

from codex_arch.hooks.throttling import (
    ThrottleManager
)

from codex_arch.hooks.notification import (
    NotificationManager
)

__all__ = [
    'install_hooks',
    'uninstall_hooks',
    'post_commit_hook',
    'post_merge_hook',
    'pre_push_hook',
    'HookConfig',
    'load_hook_config',
    'ThrottleManager',
    'NotificationManager'
] 