"""
Main CLI entry point for Codex-Arch.
"""

import argparse
import logging
import sys
import warnings
from typing import List, Optional
import click
from pathlib import Path

from codex_arch import __version__
from codex_arch.cli import file_tree_cmd
from codex_arch.analyzer import run_analysis
from codex_arch.indexer import index_repository
from codex_arch.storage import get_storage
from codex_arch.query import query_architecture
from codex_arch.report import generate_report
from codex_arch.change_detection import detect_changes, summarize_changes
from codex_arch.hooks import install_hooks, uninstall_hooks
from codex_arch.cli.commands.dependency_query import query
from codex_arch.visualization.converter import convert_command
from codex_arch.visualization.graph_generator import visualize

# Show deprecation warning
def show_deprecation_warning(command_name):
    warnings.warn(
        f"\nWARNING: Using '{command_name}' with this command style is deprecated.\n"
        f"Please use the new CLI format: python -m codex_arch.cli.cli {command_name} [OPTIONS]\n"
        f"Run 'python -m codex_arch.cli.cli --help' for more information.",
        DeprecationWarning, stacklevel=2
    )

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Codex-Arch: A tool for analyzing and visualizing code architecture",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Codex-Arch {__version__}"
    )
    
    # Logging and verbosity controls
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log to the specified file instead of stdout"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands",
        help="Command to run"
    )
    
    # File tree command
    file_tree_parser = subparsers.add_parser(
        "filetree",
        help="Extract and generate file trees from directories",
        description="Generate a hierarchical representation of a directory structure"
    )
    
    file_tree_parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to analyze"
    )
    
    file_tree_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    file_tree_parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown", "md"],
        default="json",
        help="Output format (json, markdown/md)"
    )
    
    file_tree_parser.add_argument(
        "-d", "--max-depth",
        type=int,
        help="Maximum depth to traverse"
    )
    
    file_tree_parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        help="Directories to exclude (e.g., .git node_modules)"
    )
    
    file_tree_parser.add_argument(
        "--exclude-patterns",
        type=str,
        nargs="+",
        help="Regex patterns to exclude files and directories"
    )
    
    file_tree_parser.add_argument(
        "--exclude-extensions",
        type=str,
        nargs="+",
        help="File extensions to exclude (e.g., .pyc .log)"
    )
    
    file_tree_parser.add_argument(
        "--include-extensions",
        type=str,
        nargs="+",
        help="Only include these file extensions"
    )
    
    file_tree_parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories"
    )
    
    file_tree_parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links"
    )
    
    # JSON-specific options
    file_tree_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for JSON output"
    )
    
    file_tree_parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from JSON output"
    )
    
    # Markdown-specific options
    file_tree_parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Don't use emoji icons in Markdown output"
    )
    
    file_tree_parser.add_argument(
        "--no-size",
        action="store_true",
        help="Don't include file size in Markdown output"
    )
    
    file_tree_parser.add_argument(
        "--no-header",
        action="store_true",
        help="Don't include header in Markdown output"
    )
    
    file_tree_parser.add_argument(
        "--relative-paths",
        action="store_true",
        help="Use paths relative to the root path"
    )
    
    # Python Dependencies command
    dependencies_parser = subparsers.add_parser(
        "dependencies",
        help="Extract and analyze dependencies from Python code",
        description="Extract and analyze dependencies between Python modules"
    )
    
    dependencies_parser.add_argument(
        "path",
        type=str,
        help="Path to the Python project to analyze"
    )
    
    dependencies_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory for results (default: './output')"
    )
    
    dependencies_parser.add_argument(
        "-f", "--file",
        type=str,
        default="python_dependencies.json",
        help="Output filename (default: python_dependencies.json)"
    )
    
    dependencies_parser.add_argument(
        "--include-patterns",
        type=str,
        nargs="+",
        default=["**/*.py"],
        help="Glob patterns for files to include (default: ['**/*.py'])"
    )
    
    dependencies_parser.add_argument(
        "--exclude-patterns",
        type=str,
        nargs="+",
        default=["**/venv/**", "**/.git/**", "**/__pycache__/**"],
        help="Glob patterns for files to exclude (default: ['**/venv/**', '**/.git/**', '**/__pycache__/**'])"
    )
    
    # Metrics command
    metrics_parser = subparsers.add_parser(
        "metrics",
        help="Collect code metrics from a codebase",
        description="Collect metrics like file count, line count, and complexity"
    )
    
    metrics_parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to analyze"
    )
    
    metrics_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: './output/metrics.json')"
    )
    
    metrics_parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude (default: venv, .git, __pycache__, node_modules)"
    )
    
    metrics_parser.add_argument(
        "--exclude-patterns",
        type=str,
        nargs="+",
        help="Regex patterns to exclude files and directories"
    )
    
    metrics_parser.add_argument(
        "--exclude-extensions",
        type=str,
        nargs="+",
        default=[".pyc", ".pyo", ".pyd", ".egg", ".egg-info"],
        help="File extensions to exclude"
    )
    
    metrics_parser.add_argument(
        "--include-extensions",
        type=str,
        nargs="+",
        help="Only include these file extensions"
    )
    
    metrics_parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories"
    )
    
    metrics_parser.add_argument(
        "--max-file-size",
        type=int,
        default=10 * 1024 * 1024,  # 10MB
        help="Maximum file size in bytes to process (default: 10MB)"
    )
    
    metrics_parser.add_argument(
        "--no-complexity",
        action="store_true",
        help="Skip complexity analysis"
    )
    
    metrics_parser.add_argument(
        "--complexity-max-file-size",
        type=int,
        default=1024 * 1024,  # 1MB
        help="Maximum file size in bytes for complexity analysis (default: 1MB)"
    )
    
    metrics_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for JSON output"
    )
    
    metrics_parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from JSON output"
    )
    
    # Visualization command
    viz_parser = subparsers.add_parser(
        "visualize",
        help="Generate graph visualizations from dependency data",
        description="Create DOT, SVG, or PNG visualizations of code dependencies"
    )
    
    viz_parser.add_argument(
        "input",
        type=str,
        help="Input dependency JSON file to visualize"
    )
    
    viz_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: based on input filename)"
    )
    
    viz_parser.add_argument(
        "-f", "--format",
        choices=["dot", "svg", "png"],
        default="svg",
        help="Output format (default: svg)"
    )
    
    viz_parser.add_argument(
        "--theme",
        choices=["light", "dark", "colorful"],
        default="colorful",
        help="Visualization color theme (default: colorful)"
    )
    
    viz_parser.add_argument(
        "--group-modules",
        action="store_true",
        help="Group nodes by module/package"
    )
    
    viz_parser.add_argument(
        "--max-nodes",
        type=int,
        help="Maximum number of nodes to display (limits to most connected nodes)"
    )
    
    viz_parser.add_argument(
        "--layout",
        choices=["dot", "neato", "fdp", "sfdp", "twopi", "circo"],
        default="dot",
        help="GraphViz layout engine to use (default: dot)"
    )
    
    viz_parser.add_argument(
        "--include-external",
        action="store_true",
        help="Include external dependencies in visualization"
    )
    
    # Summary command
    summary_parser = subparsers.add_parser(
        "summary",
        help="Generate a summary report of the codebase",
        description="Create a markdown summary report of the codebase architecture"
    )
    
    summary_parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to analyze"
    )
    
    summary_parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output/summary.md",
        help="Output file path (default: ./output/summary.md)"
    )
    
    summary_parser.add_argument(
        "--template",
        type=str,
        choices=["standard", "detailed", "minimal"],
        default="standard",
        help="Summary template to use (default: standard)"
    )
    
    summary_parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude (default: venv, .git, __pycache__, node_modules)"
    )
    
    summary_parser.add_argument(
        "--include-metrics",
        action="store_true",
        default=True,
        help="Include metrics in the summary (default: True)"
    )
    
    summary_parser.add_argument(
        "--include-dependencies",
        action="store_true",
        default=True,
        help="Include dependency analysis in the summary (default: True)"
    )
    
    summary_parser.add_argument(
        "--include-visualizations",
        action="store_true",
        default=True,
        help="Include visualizations in the summary (default: True)"
    )
    
    summary_parser.add_argument(
        "--no-smart-summarization",
        action="store_true",
        help="Disable smart summarization of code structures"
    )
    
    # Bundle command
    bundle_parser = subparsers.add_parser(
        "bundle",
        help="Create a context bundle of all analysis artifacts",
        description="Package all analysis artifacts into a structured bundle for LLM consumption"
    )
    
    bundle_parser.add_argument(
        "path",
        type=str,
        help="Path to the repository to analyze"
    )
    
    bundle_parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory for results (default: './output')"
    )
    
    bundle_parser.add_argument(
        "--bundle-dir",
        type=str,
        default="repo_meta",
        help="Directory name for the bundle within the output directory (default: repo_meta)"
    )
    
    bundle_parser.add_argument(
        "--no-file-tree",
        action="store_true",
        help="Don't include file tree artifacts in the bundle"
    )
    
    bundle_parser.add_argument(
        "--no-dependencies",
        action="store_true",
        help="Don't include dependency artifacts in the bundle"
    )
    
    bundle_parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Don't include metrics artifacts in the bundle"
    )
    
    bundle_parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Don't include visualization artifacts in the bundle"
    )
    
    bundle_parser.add_argument(
        "--no-summaries",
        action="store_true",
        help="Don't include summary artifacts in the bundle"
    )
    
    bundle_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't clean up temporary files after bundling"
    )
    
    bundle_parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress the bundle into a single file"
    )
    
    bundle_parser.add_argument(
        "--compression-format",
        choices=["zip", "tar", "tar.gz"],
        default="zip",
        help="Format for compression if --compress is used (default: zip)"
    )
    
    # API server command
    api_parser = subparsers.add_parser(
        "api",
        help="Start the REST API service",
        description="Launch a server providing REST API access to Codex-Arch functionality"
    )
    
    api_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    api_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind the server to (default: 5000)"
    )
    
    api_parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the server in debug mode"
    )
    
    api_parser.add_argument(
        "--env",
        choices=["dev", "test", "prod"],
        default="dev",
        help="Environment to run the server in (default: dev)"
    )
    
    api_parser.add_argument(
        "--output-dir",
        type=str,
        help="Base directory for analysis output files (default: './output')"
    )
    
    api_parser.add_argument(
        "--cors-origins",
        type=str,
        help="CORS allowed origins (comma-separated, default: '*')"
    )
    
    # Analyze command (run everything)
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run full analysis pipeline (filetree, dependencies, metrics, visualization, summary)",
        description="Perform complete code architecture analysis and generate all artifacts"
    )
    
    analyze_parser.add_argument(
        "path",
        type=str,
        help="Path to the repository to analyze"
    )
    
    analyze_parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory for all results (default: './output')"
    )
    
    analyze_parser.add_argument(
        "--skip-file-tree",
        action="store_true",
        help="Skip file tree analysis"
    )
    
    analyze_parser.add_argument(
        "--skip-dependencies",
        action="store_true",
        help="Skip dependency analysis"
    )
    
    analyze_parser.add_argument(
        "--skip-metrics",
        action="store_true",
        help="Skip metrics collection"
    )
    
    analyze_parser.add_argument(
        "--skip-visualization",
        action="store_true",
        help="Skip visualization generation"
    )
    
    analyze_parser.add_argument(
        "--skip-summary",
        action="store_true",
        help="Skip summary generation"
    )
    
    analyze_parser.add_argument(
        "--bundle",
        action="store_true",
        help="Create a context bundle with all artifacts"
    )
    
    analyze_parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude from all analyses"
    )
    
    # Query Dependencies command
    query_deps_parser = subparsers.add_parser(
        "query-deps",
        help="Query dependencies for a specific file",
        description="Show files that depend on a given file and files that the given file depends on"
    )
    
    query_deps_parser.add_argument(
        "file_path",
        type=str,
        help="Path to the file to query dependencies for"
    )
    
    query_deps_parser.add_argument(
        "-d", "--dependency-file",
        type=str,
        default="output/complete_dependencies.json",
        help="Path to the dependency JSON file"
    )
    
    query_deps_parser.add_argument(
        "--direction",
        choices=["in", "out", "both"],
        default="both",
        help="Direction of dependencies to show: in=reverse deps, out=direct deps, both=all"
    )
    
    # Convert Dependencies command
    convert_deps_parser = subparsers.add_parser(
        "convert-deps",
        help="Convert dependency data to visualization format",
        description="Convert raw dependency data to a format suitable for visualization"
    )
    
    convert_deps_parser.add_argument(
        "input_file",
        type=str,
        help="Input dependency file (e.g., python_dependencies.json)"
    )
    
    convert_deps_parser.add_argument(
        "output_file",
        type=str,
        help="Output file for converted dependencies"
    )
    
    # Generate Graph command
    graph_parser = subparsers.add_parser(
        "graph",
        help="Generate architecture graph from dependency data",
        description="Create a visual graph representation of dependencies"
    )
    
    graph_parser.add_argument(
        "input_file",
        type=str,
        help="Input dependency file (e.g., complete_dependencies.json)"
    )
    
    graph_parser.add_argument(
        "output_file",
        type=str,
        help="Output file path for the graph (without extension)"
    )
    
    return parser.parse_args(args)


def setup_logging(args: argparse.Namespace) -> None:
    """Set up logging based on command line arguments."""
    log_level = getattr(logging, args.log_level)
    
    if args.verbose and log_level > logging.DEBUG:
        log_level = logging.DEBUG
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if args.log_file:
        logging.basicConfig(
            filename=args.log_file,
            level=log_level,
            format=log_format
        )
    else:
        logging.basicConfig(
            level=log_level,
            format=log_format
        )


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI."""
    try:
        # Parse command line arguments
        parsed_args = parse_args(args)
        
        # Configure logging
        setup_logging(parsed_args)
        
        if parsed_args.command is None:
            print("No command specified. Use -h for help.")
            return 1
            
        # Execute the requested command
        if parsed_args.command == "filetree":
            # Show deprecation warning
            show_deprecation_warning("filetree")
            # Pass all arguments except the command itself to the file tree command
            filetree_args = sys.argv[2:] if args is None else args[1:]
            return file_tree_cmd.main(filetree_args)
        elif parsed_args.command == "dependencies":
            # Show deprecation warning
            show_deprecation_warning("dependencies")
            # Import here to avoid circular imports
            from codex_arch.cli import dependency_cmd
            dependency_args = sys.argv[2:] if args is None else args[1:]
            return dependency_cmd.main(dependency_args)
        elif parsed_args.command == "metrics":
            # Show deprecation warning
            show_deprecation_warning("metrics")
            # Import here to avoid circular imports
            from codex_arch.cli import metrics_cmd
            metrics_args = sys.argv[2:] if args is None else args[1:]
            return metrics_cmd.main(metrics_args)
        elif parsed_args.command == "visualize":
            # Show deprecation warning
            show_deprecation_warning("visualize")
            # Import here to avoid circular imports
            from codex_arch.cli import visualization_cmd
            viz_args = sys.argv[2:] if args is None else args[1:]
            return visualization_cmd.main(viz_args)
        elif parsed_args.command == "summary":
            # Show deprecation warning
            show_deprecation_warning("summary")
            # Import here to avoid circular imports
            from codex_arch.cli import summary_cmd
            summary_args = sys.argv[2:] if args is None else args[1:]
            return summary_cmd.main(summary_args)
        elif parsed_args.command == "bundle":
            # Show deprecation warning
            show_deprecation_warning("bundle")
            # Import here to avoid circular imports
            from codex_arch.cli import bundle_cmd
            bundle_args = sys.argv[2:] if args is None else args[1:]
            return bundle_cmd.main(bundle_args)
        elif parsed_args.command == "api":
            # Show deprecation warning
            show_deprecation_warning("api")
            # Import here to avoid circular imports
            from codex_arch.cli import api_cmd
            api_args = sys.argv[2:] if args is None else args[1:]
            return api_cmd.main(api_args)
        elif parsed_args.command == "analyze":
            # Show deprecation warning
            show_deprecation_warning("analyze")
            # Import here to avoid circular imports
            from codex_arch.cli import analyze_cmd
            analyze_args = sys.argv[2:] if args is None else args[1:]
            return analyze_cmd.main(analyze_args)
        elif parsed_args.command == "query-deps":
            # Show deprecation warning
            show_deprecation_warning("query-deps")
            # Import here to avoid circular imports
            from codex_arch.cli import query_deps_cmd
            query_deps_args = sys.argv[2:] if args is None else args[1:]
            return query_deps_cmd.main(query_deps_args)
        elif parsed_args.command == "convert-deps":
            # Show deprecation warning
            show_deprecation_warning("convert-deps")
            # Import here to avoid circular imports
            from codex_arch.cli import convert_deps_cmd
            convert_deps_args = sys.argv[2:] if args is None else args[1:]
            return convert_deps_cmd.main(convert_deps_args)
        elif parsed_args.command == "graph":
            # Show deprecation warning
            show_deprecation_warning("graph")
            # Import here to avoid circular imports
            from codex_arch.cli import graph_cmd
            graph_args = sys.argv[2:] if args is None else args[1:]
            return graph_cmd.main(graph_args)
        
        print(f"Unknown command: {parsed_args.command}")
        return 1
    
    except Exception as e:
        logging.error(f"Error executing command {parsed_args.command}: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


# Git hooks commands
@click.group()
def hooks():
    """Manage Git hooks integration."""
    pass

@hooks.command('install')
@click.option('--force', is_flag=True, help='Force override existing hooks')
def install_git_hooks(force):
    """Install Git hooks into the current repository."""
    install_hooks(force=force)
    click.echo("Git hooks installed successfully.")

@hooks.command('uninstall')
def uninstall_git_hooks():
    """Remove Git hooks from the current repository."""
    uninstall_hooks()
    click.echo("Git hooks uninstalled successfully.")


def create_cli() -> click.Group:
    """Create the Click CLI group with all commands."""
    from codex_arch.cli import file_tree_cmd
    
    # Create base CLI
    cli = click.Group(name="codex-arch")
    
    # Add all commands
    cli.add_command(file_tree_cmd.filetree)
    cli.add_command(hooks)
    cli.add_command(query, name='query-deps')
    cli.add_command(convert_command, name='convert-deps')
    cli.add_command(visualize, name='graph')
    return cli


@click.group()
@click.version_option(version=__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), 
              default='INFO', help='Set logging level')
def cli():
    """
    Codex-Arch: A tool for analyzing and visualizing code architecture.
    
    Run a command with --help to see command-specific options.
    """
    pass

# Create a pipelines command group
@cli.group('pipeline')
def pipeline():
    """Run complete analysis pipelines with a single command."""
    pass

@pipeline.command('analyze')
@click.argument('path')
@click.option('--output', '-o', default='output', help='Output directory for results')
def complete_analysis(path, output):
    """
    Run a complete analysis pipeline on a codebase.
    
    This will:
    1. Extract dependencies with 'codex-arch dependencies'
    2. Convert dependencies to visualization format
    3. Generate architecture graph visualization
    4. Collect metrics
    
    Equivalent to running these commands sequentially:
    - codex-arch dependencies PATH --output OUTPUT
    - codex-arch convert OUTPUT/python_dependencies.json OUTPUT/complete_dependencies.json
    - codex-arch visualize OUTPUT/complete_dependencies.json OUTPUT/complete_arch_graph
    """
    import os
    import subprocess
    from pathlib import Path
    
    # Create output directory if needed
    os.makedirs(output, exist_ok=True)
    
    # Step 1: Extract dependencies
    print("Step 1: Extracting dependencies...")
    subprocess.run(['codex-arch', 'dependencies', path, '--output', output])
    
    # Step 2: Convert dependencies
    print("\nStep 2: Converting dependencies to visualization format...")
    deps_file = os.path.join(output, 'python_dependencies.json')
    complete_deps_file = os.path.join(output, 'complete_dependencies.json')
    
    from codex_arch.visualization.converter import convert_dependencies
    convert_dependencies(deps_file, complete_deps_file)
    
    # Step 3: Generate architecture visualization
    print("\nStep 3: Generating architecture visualization...")
    arch_graph_path = os.path.join(output, 'complete_arch_graph')
    
    from codex_arch.visualization.graph_generator import generate_graph
    generate_graph(complete_deps_file, arch_graph_path)
    
    # Step 4: Generate module-level visualization
    print("\nStep 4: Generating module-level visualization...")
    module_graph_path = os.path.join(output, 'architecture_graph')
    generate_graph(deps_file, module_graph_path)
    
    print("\nAnalysis complete! Results are available in the output directory.")
    print(f"- Dependencies: {deps_file}")
    print(f"- Complete dependencies: {complete_deps_file}")
    print(f"- Architecture graph: {module_graph_path}.png and {module_graph_path}.svg")
    print(f"- Complete architecture graph: {arch_graph_path}.png and {arch_graph_path}.svg")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 