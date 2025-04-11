"""
Change Detection Module

This module provides functionality to detect changes in the repository and enables
incremental updates to analysis artifacts.
"""

from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.change_detection.caching import CacheManager
from codex_arch.change_detection.incremental import IncrementalAnalyzer
from codex_arch.change_detection.summary import ChangeSummaryGenerator

__all__ = [
    'GitChangeDetector',
    'CacheManager',
    'IncrementalAnalyzer',
    'ChangeSummaryGenerator',
] 