"""
Command Line Interface for Codex-Arch.

This module provides a Click-based CLI for interacting with Codex-Arch functionality.
"""

import os
import sys
import logging
import click
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

from codex_arch import __version__
from codex_arch.analyzer import run_analysis
from codex_arch.indexer import index_repository
from codex_arch.storage import get_storage
from codex_arch.query import query_architecture
from codex_arch.report import generate_report
from codex_arch.change_detection import detect_changes, summarize_changes
from codex_arch.hooks import install_hooks, uninstall_hooks

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), 
              default='INFO', help='Set logging level')
@click.option('--log-file', type=click.Path(), help='Log to a file instead of stdout')
def cli(verbose, log_level, log_file):
    """
    Codex-Arch: A tool for analyzing and visualizing code architecture.
    
    Run a command with --help to see command-specific options.
    """
    # Configure logging
    log_format = '%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)'
    
    if verbose:
        log_level = 'DEBUG'
    
    if log_file:
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            filename=log_file,
            filemode='a'
        )
    else:
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
        )

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory for analysis results')
@click.option('--exclude-dirs', '-d', multiple=True, help='Directories to exclude')
@click.option('--exclude-patterns', '-e', multiple=True, help='Regex patterns to exclude')
@click.option('--include-hidden', is_flag=True, help='Include hidden files and directories')
@click.option('--no-complexity', is_flag=True, help='Skip complexity analysis')
@click.option('--no-dependencies', is_flag=True, help='Skip dependency analysis')
@click.option('--no-metrics', is_flag=True, help='Skip metrics collection')
def analyze(path, output, exclude_dirs, exclude_patterns, include_hidden, 
           no_complexity, no_dependencies, no_metrics):
    """
    Analyze code structure and dependencies.
    
    Performs a comprehensive analysis of code, including structure,
    dependencies, complexity, and metrics.
    """
    click.echo(f"Analyzing code in: {path}")
    
    results = run_analysis(
        paths=path,
        output_dir=output,
        exclude_dirs=list(exclude_dirs) if exclude_dirs else None,
        exclude_patterns=list(exclude_patterns) if exclude_patterns else None,
        include_hidden=include_hidden,
        analyze_complexity=not no_complexity,
        analyze_dependencies=not no_dependencies,
        analyze_metrics=not no_metrics,
    )
    
    click.echo(f"Analysis complete: {results['file_count']} files analyzed")
    
    if output:
        click.echo(f"Results saved to: {output}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory for index')
@click.option('--exclude-dirs', '-d', multiple=True, help='Directories to exclude')
@click.option('--exclude-patterns', '-e', multiple=True, help='Regex patterns to exclude')
@click.option('--include-hidden', is_flag=True, help='Include hidden files and directories')
def index(path, output, exclude_dirs, exclude_patterns, include_hidden):
    """
    Index a code repository for faster searching and analysis.
    
    Creates an index of files, symbols, and their relationships.
    """
    click.echo(f"Indexing repository: {path}")
    
    results = index_repository(
        repo_path=path,
        output_dir=output,
        exclude_dirs=list(exclude_dirs) if exclude_dirs else None,
        exclude_patterns=list(exclude_patterns) if exclude_patterns else None,
        include_hidden=include_hidden,
    )
    
    click.echo(f"Indexing complete: {results['indexed_files']} files indexed")
    
    if output:
        click.echo(f"Index saved to: {output}")

@cli.command()
@click.argument('query')
@click.option('--repo-path', '-p', type=click.Path(exists=True), help='Path to repository')
@click.option('--type', '-t', type=click.Choice(['general', 'file', 'symbol', 'dependency']), 
              default='general', help='Type of query')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.option('--max-results', '-m', type=int, default=100, help='Maximum number of results')
@click.option('--include-code', is_flag=True, help='Include code snippets in results')
def query(query, repo_path, type, output, max_results, include_code):
    """
    Query code architecture data.
    
    Search for files, symbols, or dependencies matching a query.
    """
    click.echo(f"Querying with: {query}")
    
    results = query_architecture(
        query=query,
        repo_path=repo_path,
        query_type=type,
        output_file=output,
        max_results=max_results,
        include_code=include_code,
    )
    
    click.echo(f"Query complete: {results['total_matches']} matches found")
    
    if output:
        click.echo(f"Results saved to: {output}")
    else:
        # Display summary of results
        if type == 'file':
            for i, match in enumerate(results['matches'][:5], 1):
                click.echo(f"{i}. {match.get('path', 'Unknown')}")
        elif type == 'symbol':
            for i, match in enumerate(results['matches'][:5], 1):
                click.echo(f"{i}. {match.get('name', 'Unknown')} ({match.get('type', 'Unknown')})")
        elif type == 'dependency':
            for i, match in enumerate(results['matches'][:5], 1):
                click.echo(f"{i}. {match.get('source', 'Unknown')} -> {', '.join(match.get('targets', []))}")
        else:  # general
            click.echo(f"Files: {len(results['matches'].get('files', []))} matches")
            click.echo(f"Symbols: {len(results['matches'].get('symbols', []))} matches")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory for report')
@click.option('--type', '-t', type=click.Choice(['full', 'summary', 'metrics', 'dependencies', 'complexity']), 
              default='full', help='Type of report')
@click.option('--format', '-f', type=click.Choice(['html', 'markdown', 'json']), 
              default='html', help='Output format')
@click.option('--no-metrics', is_flag=True, help='Exclude metrics from report')
@click.option('--no-dependencies', is_flag=True, help='Exclude dependencies from report')
@click.option('--no-complexity', is_flag=True, help='Exclude complexity analysis from report')
def report(path, output, type, format, no_metrics, no_dependencies, no_complexity):
    """
    Generate a report about code architecture.
    
    Creates a human-readable report about code structure, metrics,
    dependencies, and complexity.
    """
    click.echo(f"Generating {type} report for: {path}")
    
    report_metadata = generate_report(
        repo_path=path,
        output_dir=output,
        report_type=type,
        include_metrics=not no_metrics,
        include_dependencies=not no_dependencies,
        include_complexity=not no_complexity,
        format=format,
    )
    
    if "error" in report_metadata:
        click.echo(f"Error: {report_metadata['error']}")
        return
    
    click.echo(f"Report generated: {report_metadata['output_path']}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--from-commit', help='Base commit for comparison')
@click.option('--to-commit', default='HEAD', help='Target commit for comparison')
@click.option('--output', '-o', type=click.Path(), help='Output file for changes')
def changes(path, from_commit, to_commit, output):
    """
    Detect changes between Git commits.
    
    Identifies files that have been added, modified, or deleted
    between two Git commits.
    """
    click.echo(f"Detecting changes in {path} from {from_commit or 'last analyzed commit'} to {to_commit}")
    
    changes = detect_changes(
        repo_path=path,
        from_commit=from_commit,
        to_commit=to_commit,
    )
    
    for change_type, files in changes.items():
        click.echo(f"{change_type.capitalize()}: {len(files)} files")
        for file in files[:5]:  # Show first 5 files
            click.echo(f"  - {file}")
        if len(files) > 5:
            click.echo(f"  - ...and {len(files) - 5} more")
    
    if output:
        import json
        with open(output, 'w') as f:
            json.dump(changes, f, indent=2)
        click.echo(f"Changes saved to: {output}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--from-commit', help='Base commit for comparison')
@click.option('--to-commit', default='HEAD', help='Target commit for comparison')
@click.option('--output', '-o', type=click.Path(), help='Output file for summary')
def summarize(path, from_commit, to_commit, output):
    """
    Summarize changes between Git commits.
    
    Provides a high-level summary of code changes, including metrics
    about added, modified, and deleted files.
    """
    click.echo(f"Summarizing changes in {path} from {from_commit or 'last analyzed commit'} to {to_commit}")
    
    summary = summarize_changes(
        repo_path=path,
        from_commit=from_commit,
        to_commit=to_commit,
    )
    
    click.echo(f"Summary of changes:")
    click.echo(f"Total files changed: {summary['total_files_changed']}")
    click.echo(f"Total lines added: {summary['lines_added']}")
    click.echo(f"Total lines removed: {summary['lines_removed']}")
    
    if output:
        import json
        with open(output, 'w') as f:
            json.dump(summary, f, indent=2)
        click.echo(f"Summary saved to: {output}")

@cli.group()
def hooks():
    """
    Manage Git hooks for automatic analysis.
    
    Install or uninstall Git hooks that automatically run analysis
    on code changes.
    """
    pass

@hooks.command('install')
@click.option('--force', is_flag=True, help='Force override existing hooks')
def install_git_hooks(force):
    """Install Git hooks for automatic analysis."""
    click.echo("Installing Git hooks...")
    
    result = install_hooks(force=force)
    
    if result.get('success'):
        click.echo("Git hooks installed successfully.")
        for hook, path in result.get('installed_hooks', {}).items():
            click.echo(f"  - {hook}: {path}")
    else:
        click.echo(f"Error installing Git hooks: {result.get('error')}")

@hooks.command('uninstall')
def uninstall_git_hooks():
    """Uninstall Git hooks."""
    click.echo("Uninstalling Git hooks...")
    
    result = uninstall_hooks()
    
    if result.get('success'):
        click.echo("Git hooks uninstalled successfully.")
    else:
        click.echo(f"Error uninstalling Git hooks: {result.get('error')}")

if __name__ == '__main__':
    cli() 