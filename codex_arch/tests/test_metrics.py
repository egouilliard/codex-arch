#!/usr/bin/env python3
"""
Test script for the Metrics Collector module.
"""

import os
import json
import argparse
from codex_arch.metrics import MetricsCollector

def main():
    """Run the metrics collector test."""
    parser = argparse.ArgumentParser(description='Test the metrics collector module')
    parser.add_argument('--path', '-p', type=str, default='.',
                       help='Path to analyze (default: current directory)')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Output file for metrics JSON (default: prints to stdout)')
    parser.add_argument('--exclude-dirs', '-d', type=str, default='venv,node_modules,__pycache__,.git',
                       help='Comma-separated list of directories to exclude')
    parser.add_argument('--exclude-patterns', '-e', type=str, default=None,
                       help='Comma-separated list of regex patterns to exclude')
    parser.add_argument('--no-hidden', action='store_true',
                       help='Exclude hidden files and directories')
    parser.add_argument('--json-only', action='store_true',
                       help='Only output JSON metrics without summary')
    parser.add_argument('--no-complexity', action='store_true',
                       help='Skip complexity analysis')
    parser.add_argument('--summary-only', action='store_true',
                       help='Only output the summary, not the full JSON')
    args = parser.parse_args()
    
    # Parse exclude dirs
    exclude_dirs = args.exclude_dirs.split(',') if args.exclude_dirs else []
    
    # Parse exclude patterns
    exclude_patterns = args.exclude_patterns.split(',') if args.exclude_patterns else []
    
    # Create metrics collector
    collector = MetricsCollector(
        root_path=args.path,
        exclude_dirs=exclude_dirs,
        exclude_patterns=exclude_patterns,
        include_hidden=not args.no_hidden,
        analyze_complexity=not args.no_complexity
    )
    
    # Collect metrics
    if not args.json_only:
        print(f"Collecting metrics for {args.path}...")
    metrics = collector.collect_metrics()
    
    # Output metrics
    if args.output:
        if not args.json_only:
            print(f"Writing metrics to {args.output}")
        collector.to_json(args.output)
    elif not args.summary_only:
        if args.json_only:
            # Print raw JSON for piping to other tools
            json_output = collector.to_json()
            print(json_output)
            return
        else:
            # Print JSON with title
            json_output = collector.to_json()
            print(json_output)
    
    if not args.json_only:
        print_summary(metrics, not args.no_complexity)

def print_summary(metrics, with_complexity=True):
    """Print a human-readable summary of the metrics."""
    print("\nMetrics Summary:")
    print(f"Total Files: {metrics['file_counts']['total']}")
    print(f"Total Lines: {metrics['line_counts']['total']}")
    print(f"Average Lines per File: {metrics['line_counts']['average_per_file']}")
    print(f"Total Size: {_format_size(metrics['size_metrics']['total_bytes'])}")
    
    # Print language distribution
    if 'language_analysis' in metrics:
        lang_analysis = metrics['language_analysis']
        
        # Top languages by line count
        print("\nTop Languages:")
        for lang in lang_analysis['top_languages']:
            print(f"{lang['name']}: {lang['percentage']}% ({_format_number(lang['lines'])} lines)")
        
        # Language families
        print("\nLanguage Families:")
        families = sorted(
            [(family, pct) for family, pct in lang_analysis['by_family']['lines'].items()],
            key=lambda x: x[1],
            reverse=True
        )
        for family, percentage in families:
            print(f"{family}: {percentage}%")
    
    # Print complexity metrics if available
    if with_complexity and 'complexity_metrics' in metrics:
        complexity = metrics['complexity_metrics']
        
        print("\nComplexity Analysis:")
        print(f"Files Analyzed: {complexity['files_analyzed']}")
        print(f"Files Skipped: {complexity['files_skipped']}")
        print(f"Average Complexity: {complexity['average_complexity']}")
        print(f"Comment Ratio: {complexity['comment_metrics']['overall_comment_ratio']}%")
        
        # Print most complex files
        if complexity['most_complex_files']:
            print("\nMost Complex Files:")
            for i, file_info in enumerate(complexity['most_complex_files'][:5], 1):
                print(f"{i}. {file_info['path']} - Complexity: {file_info['complexity']} - Lines: {file_info['lines']}")
        
        # Print language complexity
        if complexity['complexity_by_language']:
            print("\nComplexity by Language:")
            for lang, lang_metrics in complexity['complexity_by_language'].items():
                print(f"{lang}: Avg Complexity: {lang_metrics['average_complexity']} - Files: {lang_metrics['file_count']}")

def _format_size(size_bytes):
    """Format size in bytes to a human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024 or unit == 'TB':
            if unit == 'B':
                return f"{size_bytes} {unit}"
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def _format_number(num):
    """Format number with thousands separator."""
    return f"{num:,}"

if __name__ == "__main__":
    main() 