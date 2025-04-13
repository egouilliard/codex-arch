"""
Metrics Module.

This module provides functionality to calculate various code metrics such as file counts,
lines of code, and complexity measures for a codebase.
"""

from .metrics_collector import MetricsCollector
from .language_analyzer import (
    analyze_language_distribution,
    get_language_for_extension,
    get_language_family,
    LANGUAGE_MAP,
    LANGUAGE_FAMILIES
)
from .complexity_analyzer import ComplexityAnalyzer

__all__ = [
    'MetricsCollector',
    'analyze_language_distribution',
    'get_language_for_extension',
    'get_language_family',
    'LANGUAGE_MAP',
    'LANGUAGE_FAMILIES',
    'ComplexityAnalyzer'
] 