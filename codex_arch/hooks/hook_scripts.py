"""
Git Hook Scripts

This module provides functionality to create, install, and manage Git hooks
that trigger incremental code analysis when changes are detected.
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any

from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.change_detection.incremental import IncrementalAnalyzer
from codex_arch.hooks.config import load_hook_config, HookConfig
from codex_arch.hooks.throttling import ThrottleManager
from codex_arch.hooks.notification import NotificationManager

logger = logging.getLogger(__name__)

# Path to Git hooks directory in a Git repository
GIT_HOOKS_DIR = ".git/hooks"

def find_git_root() -> Optional[Path]:
    """
    Find the root directory of the Git repository.
    
    Returns:
        Path to the git repository root, or None if not in a git repository.
    """
    try:
        git_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            universal_newlines=True
        ).strip()
        return Path(git_root)
    except subprocess.CalledProcessError:
        logger.warning("Not in a git repository")
        return None
    except Exception as e:
        logger.error(f"Error finding git root: {str(e)}")
        return None

def install_hooks(force: bool = False) -> bool:
    """
    Install Git hooks into the current repository.
    
    Args:
        force: If True, overwrite existing hooks. Defaults to False.
        
    Returns:
        True if hooks were installed successfully, False otherwise.
    """
    git_root = find_git_root()
    if not git_root:
        logger.error("Cannot install hooks: not in a Git repository")
        return False
    
    # Create the .codex-arch directory if it doesn't exist
    codex_dir = git_root / ".codex-arch"
    codex_dir.mkdir(exist_ok=True)
    
    # Get the path to the installed package hooks
    package_hooks_dir = Path(__file__).parent.parent.parent / "hooks"
    
    # Get the path to the Git hooks directory
    git_hooks_dir = git_root / GIT_HOOKS_DIR
    
    if not git_hooks_dir.exists():
        logger.error(f"Git hooks directory not found: {git_hooks_dir}")
        return False
    
    # Install each hook
    hooks = ["post-commit", "post-merge", "pre-push"]
    installed_hooks = []
    
    for hook in hooks:
        source = package_hooks_dir / hook
        target = git_hooks_dir / hook
        
        # Check if hook already exists
        if target.exists() and not force:
            logger.warning(f"Hook already exists: {target}. Use --force to overwrite.")
            continue
        
        # Copy the hook and make it executable
        try:
            shutil.copy2(source, target)
            os.chmod(target, 0o755)  # Make executable
            installed_hooks.append(hook)
        except Exception as e:
            logger.error(f"Error installing {hook}: {str(e)}")
            continue
    
    # Create default configuration
    config = HookConfig()
    config_path = codex_dir / "hooks.json"
    with open(config_path, "w") as f:
        f.write(config.to_json(indent=2))
    
    if installed_hooks:
        logger.info(f"Installed hooks: {', '.join(installed_hooks)}")
        return True
    else:
        logger.warning("No hooks were installed")
        return False

def uninstall_hooks() -> bool:
    """
    Uninstall Git hooks from the current repository.
    
    Returns:
        True if hooks were uninstalled successfully, False otherwise.
    """
    git_root = find_git_root()
    if not git_root:
        logger.error("Cannot uninstall hooks: not in a Git repository")
        return False
    
    # Get the path to the Git hooks directory
    git_hooks_dir = git_root / GIT_HOOKS_DIR
    
    if not git_hooks_dir.exists():
        logger.error(f"Git hooks directory not found: {git_hooks_dir}")
        return False
    
    # Uninstall each hook
    hooks = ["post-commit", "post-merge", "pre-push"]
    uninstalled_hooks = []
    
    for hook in hooks:
        target = git_hooks_dir / hook
        
        # Check if it's our hook (simple check for codex-arch string)
        if target.exists():
            try:
                with open(target, "r") as f:
                    content = f.read()
                
                if "Codex-Arch" in content:
                    target.unlink()
                    uninstalled_hooks.append(hook)
            except Exception as e:
                logger.error(f"Error uninstalling {hook}: {str(e)}")
                continue
    
    if uninstalled_hooks:
        logger.info(f"Uninstalled hooks: {', '.join(uninstalled_hooks)}")
        return True
    else:
        logger.warning("No hooks were uninstalled")
        return False

def post_commit_hook() -> int:
    """
    Implementation of the post-commit hook.
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    try:
        git_root = find_git_root()
        if not git_root:
            return 1
        
        # Load configuration
        config = load_hook_config()
        
        # Check if hook is enabled
        if not config.post_commit_enabled:
            logger.info("Post-commit hook is disabled in configuration")
            return 0
        
        # Check throttling
        throttle_manager = ThrottleManager(throttle_interval=config.throttle_interval)
        if throttle_manager.should_throttle("post_commit"):
            logger.info("Throttling post-commit hook execution")
            return 0
        
        # Mark the hook as executed to update throttling timestamp
        throttle_manager.record_execution("post_commit")
        
        # Create notification manager
        notification = NotificationManager(
            enabled=config.notification_enabled,
            level=config.notification_level
        )
        
        # Notify that hook has been triggered
        notification.notify_hook_execution("post-commit", "Analyzing code changes after commit...")
        
        # Perform incremental analysis
        incremental = IncrementalAnalyzer(repo_path=str(git_root))
        
        # Only proceed if we should use incremental analysis
        if incremental.should_use_incremental():
            # Get changes
            detector = GitChangeDetector(str(git_root))
            changes = detector.get_changes("HEAD~1", "HEAD")
            
            # Bail if no changes
            if not any(changes.values()):
                logger.info("No changes detected in commit")
                return 0
            
            # Perform analysis
            analysis_result = incremental.perform_incremental_dependency_analysis()
            
            # Notify about results
            if analysis_result:
                notification.notify_analysis_results(
                    analysis_result,
                    level="info"
                )
        
        return 0
    except Exception as e:
        logger.error(f"Error in post-commit hook: {str(e)}")
        return 1

def post_merge_hook() -> int:
    """
    Implementation of the post-merge hook.
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    try:
        git_root = find_git_root()
        if not git_root:
            return 1
        
        # Load configuration
        config = load_hook_config()
        
        # Check if hook is enabled
        if not config.post_merge_enabled:
            logger.info("Post-merge hook is disabled in configuration")
            return 0
        
        # Check throttling
        throttle_manager = ThrottleManager(throttle_interval=config.throttle_interval)
        if throttle_manager.should_throttle("post_merge"):
            logger.info("Throttling post-merge hook execution")
            return 0
        
        # Mark the hook as executed to update throttling timestamp
        throttle_manager.record_execution("post_merge")
        
        # Create notification manager
        notification = NotificationManager(
            enabled=config.notification_enabled,
            level=config.notification_level
        )
        
        # Notify that hook has been triggered
        notification.notify_hook_execution("post-merge", "Analyzing code changes after merge...")
        
        # Perform incremental analysis
        incremental = IncrementalAnalyzer(repo_path=str(git_root))
        
        # For merges, it's more reliable to use incremental analysis
        # regardless of cache state, as we want to ensure all merged
        # changes are properly analyzed
        detector = GitChangeDetector(str(git_root))
        
        # Try to get merge base and HEAD
        merge_base = detector.get_merge_base()
        if merge_base:
            analysis_result = incremental.perform_incremental_dependency_analysis(
                from_commit=merge_base,
                to_commit="HEAD"
            )
            
            # Notify about results
            notification.notify_analysis_results(
                analysis_result,
                level="info"
            )
        
        return 0
    except Exception as e:
        logger.error(f"Error in post-merge hook: {str(e)}")
        return 1

def pre_push_hook() -> int:
    """
    Implementation of the pre-push hook.
    
    Returns:
        Exit code (0 for success, non-zero for error).
    """
    try:
        git_root = find_git_root()
        if not git_root:
            return 1
        
        # Load configuration
        config = load_hook_config()
        
        # Check if hook is enabled
        if not config.pre_push_enabled:
            logger.info("Pre-push hook is disabled in configuration")
            return 0
        
        # Create notification manager
        notification = NotificationManager(
            enabled=config.notification_enabled,
            level=config.notification_level
        )
        
        # Perform final analysis before push
        detector = GitChangeDetector(str(git_root))
        
        # Get remote changes
        remote_changes = detector.get_unpushed_changes()
        if not remote_changes:
            logger.info("No unpushed changes detected")
            return 0
        
        # Notify user
        notification.notify_hook_execution(
            "pre-push", 
            f"Checking {len(remote_changes)} unpushed commits before push..."
        )
        
        # Run a quick analysis to check for major issues
        incremental = IncrementalAnalyzer(repo_path=str(git_root))
        
        # Use incremental analysis to check only changed files
        result = incremental.perform_incremental_metrics_analysis(
            from_commit=remote_changes[-1],
            to_commit="HEAD"
        )
        
        # Check for any critical issues that might prevent push
        # This is just a placeholder - you would implement your own checks
        issues = check_for_critical_issues(result)
        
        if issues:
            # Notify user about critical issues
            results_with_issues = {
                "findings_count": len(issues),
                "issues": issues,
                "severity": "high"
            }
            notification.notify_analysis_results(
                results_with_issues,
                level="error"
            )
            
            # Log issues
            for issue in issues:
                logger.warning(f"Critical issue: {issue}")
            
            # Return non-zero to prevent push
            return 1
        
        # All good
        notification.notify_analysis_results(
            {"findings_count": 0},
            level="info"
        )
        
        return 0
    except Exception as e:
        logger.error(f"Error in pre-push hook: {str(e)}")
        return 1

def check_for_critical_issues(analysis_result: Dict[str, Any]) -> List[str]:
    """
    Check for critical issues that might prevent push.
    
    Args:
        analysis_result: Analysis result dictionary.
        
    Returns:
        List of critical issues found (empty if none).
    """
    # This is a placeholder function - you would implement your own checks
    issues = []
    
    # Example check: detect large file additions
    if 'file_metrics' in analysis_result:
        for file_path, metrics in analysis_result.get('file_metrics', {}).items():
            if metrics.get('loc', 0) > 1000:
                issues.append(f"File {file_path} is very large ({metrics.get('loc')} lines)")
    
    return issues

def main():
    """
    Main entry point when this module is executed directly.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m codex_arch.hooks.hook_scripts <hook_type>")
        return 1
        
    hook_type = sys.argv[1]
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(".git/hooks/codex_arch_hooks.log"),
            logging.StreamHandler()
        ]
    )
    
    if hook_type == "post-commit":
        return post_commit_hook()
    elif hook_type == "post-merge":
        return post_merge_hook()
    elif hook_type == "pre-push":
        return pre_push_hook()
    else:
        print(f"Unknown hook type: {hook_type}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 