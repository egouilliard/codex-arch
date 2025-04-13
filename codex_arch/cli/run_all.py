"""
Command-line interface for running all analysis steps together.
"""

import os
import sys
import time
import logging
import click
from pathlib import Path

from codex_arch.cli.cli import cli
from codex_arch.analyzer import run_analysis
from codex_arch.extractors.python.extractor import extract_dependencies

logger = logging.getLogger(__name__)

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output directory for all results')
@click.option('--exclude-dirs', '-d', multiple=True, help='Directories to exclude')
@click.option('--exclude-patterns', '-e', multiple=True, help='Regex patterns to exclude')
@click.option('--include-hidden', is_flag=True, help='Include hidden files and directories')
@click.option('--no-complexity', is_flag=True, help='Skip complexity analysis')
@click.option('--no-metrics', is_flag=True, help='Skip metrics collection')
@click.option('--no-file-tree', is_flag=True, help='Skip file tree generation')
@click.option('--no-visualization', is_flag=True, help='Skip architecture visualization')
@click.option('--convert-deps', is_flag=True, help='Convert dependencies for enhanced visualization')
def run_all(path, output, exclude_dirs, exclude_patterns, include_hidden, 
            no_complexity, no_metrics, no_file_tree, no_visualization, convert_deps):
    """
    Run all analysis commands in sequence.
    
    This command executes the full analysis pipeline, including dependency extraction,
    metrics collection, file tree generation, and architecture visualization. It combines
    the functionality of multiple commands in a single workflow.
    """
    start_time = time.time()
    click.echo(f"Starting comprehensive analysis of: {path}")
    
    # Default output directory if not specified
    output = output or 'output'
    os.makedirs(output, exist_ok=True)
    
    # Run the full analysis
    run_full_analysis(
        path=path,
        output_dir=output,
        exclude_dirs=list(exclude_dirs) if exclude_dirs else None,
        exclude_patterns=list(exclude_patterns) if exclude_patterns else None,
        include_hidden=include_hidden,
        analyze_complexity=not no_complexity,
        analyze_metrics=not no_metrics,
        analyze_file_tree=not no_file_tree,
    )
    
    # Convert dependency format if requested
    if convert_deps and os.path.exists(os.path.join(output, "python_dependencies.json")):
        convert_dependency_format(
            input_file=os.path.join(output, "python_dependencies.json"),
            output_file=os.path.join(output, "complete_dependencies.json")
        )
    
    # Generate architecture visualizations
    if not no_visualization:
        generate_architecture_graph(
            dependency_file=os.path.join(output, "python_dependencies.json"),
            output_file=os.path.join(output, "architecture_graph")
        )
        
        # If conversion was done, also generate enhanced graph
        if convert_deps and os.path.exists(os.path.join(output, "complete_dependencies.json")):
            generate_architecture_graph(
                dependency_file=os.path.join(output, "complete_dependencies.json"),
                output_file=os.path.join(output, "enhanced_architecture_graph")
            )
    
    # Calculate execution time
    execution_time = time.time() - start_time
    minutes, seconds = divmod(execution_time, 60)
    
    click.echo(f"Analysis completed in {int(minutes)} minutes and {int(seconds)} seconds")
    click.echo(f"Results saved to: {output}")

def run_full_analysis(path, output_dir, exclude_dirs=None, exclude_patterns=None, 
                      include_hidden=False, analyze_complexity=True, 
                      analyze_metrics=True, analyze_file_tree=True):
    """Run the full analysis using the analyzer module."""
    click.echo("Running full analysis...")
    
    results = run_analysis(
        paths=path,
        output_dir=output_dir,
        exclude_dirs=exclude_dirs or ["venv", ".git", "node_modules", "__pycache__"],
        exclude_patterns=exclude_patterns,
        include_hidden=include_hidden,
        analyze_complexity=analyze_complexity,
        analyze_dependencies=True,  # Always analyze dependencies
        analyze_metrics=analyze_metrics,
        analyze_file_tree=analyze_file_tree,
    )
    
    click.echo(f"Analysis complete: {results.get('file_count', 0)} files analyzed")

def convert_dependency_format(input_file, output_file):
    """Convert the dependency format using convert_deps.py."""
    click.echo("Converting dependency format for enhanced visualization...")
    
    try:
        # Use subprocess to run the external script
        import subprocess
        result = subprocess.run(
            ["python", "convert_deps.py", input_file, output_file],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo("Dependency conversion complete")
        return True
    except Exception as e:
        click.echo(f"Error converting dependencies: {str(e)}")
        return False

def generate_architecture_graph(dependency_file, output_file):
    """Generate architecture graph using generate_arch_graph.py."""
    click.echo(f"Generating architecture graph from: {dependency_file}")
    
    try:
        # Use subprocess to run the external script
        import subprocess
        result = subprocess.run(
            ["python", "generate_arch_graph.py", dependency_file, output_file],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(f"Architecture graph generated at: {output_file}.svg and {output_file}.png")
        return True
    except Exception as e:
        click.echo(f"Error generating architecture graph: {str(e)}")
        return False 