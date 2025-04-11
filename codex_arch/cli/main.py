"""
Main CLI entry point for Codex-Arch.
"""

import argparse
import logging
import sys
from typing import List, Optional

from codex_arch import __version__
from codex_arch.cli import file_tree_cmd


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
    """Run the Codex-Arch CLI."""
    parsed_args = parse_args(args)
    
    # Set up logging
    setup_logging(parsed_args)
    
    if parsed_args.command is None:
        print("No command specified. Use -h for help.")
        return 1
    
    try:
        # Dispatch to the appropriate command
        if parsed_args.command == "filetree":
            # Pass all arguments except the command itself to the file tree command
            filetree_args = sys.argv[2:] if args is None else args[1:]
            return file_tree_cmd.main(filetree_args)
        elif parsed_args.command == "dependencies":
            # Import here to avoid circular imports
            from codex_arch.cli import dependency_cmd
            dependency_args = sys.argv[2:] if args is None else args[1:]
            return dependency_cmd.main(dependency_args)
        elif parsed_args.command == "metrics":
            # Import here to avoid circular imports
            from codex_arch.cli import metrics_cmd
            metrics_args = sys.argv[2:] if args is None else args[1:]
            return metrics_cmd.main(metrics_args)
        elif parsed_args.command == "visualize":
            # Import here to avoid circular imports
            from codex_arch.cli import visualization_cmd
            viz_args = sys.argv[2:] if args is None else args[1:]
            return visualization_cmd.main(viz_args)
        elif parsed_args.command == "summary":
            # Import here to avoid circular imports
            from codex_arch.cli import summary_cmd
            summary_args = sys.argv[2:] if args is None else args[1:]
            return summary_cmd.main(summary_args)
        elif parsed_args.command == "bundle":
            # Import here to avoid circular imports
            from codex_arch.cli import bundle_cmd
            bundle_args = sys.argv[2:] if args is None else args[1:]
            return bundle_cmd.main(bundle_args)
        elif parsed_args.command == "analyze":
            # Import here to avoid circular imports
            from codex_arch.cli import analyze_cmd
            analyze_args = sys.argv[2:] if args is None else args[1:]
            return analyze_cmd.main(analyze_args)
        
        print(f"Unknown command: {parsed_args.command}")
        return 1
    
    except Exception as e:
        logging.error(f"Error executing command {parsed_args.command}: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 