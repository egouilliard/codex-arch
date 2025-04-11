"""
Main CLI entry point for Codex-Arch.
"""

import argparse
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
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the Codex-Arch CLI."""
    parsed_args = parse_args(args)
    
    if parsed_args.command is None:
        print("No command specified. Use -h for help.")
        return 1
    
    # Dispatch to the appropriate command
    if parsed_args.command == "filetree":
        # Pass all arguments except the command itself to the file tree command
        filetree_args = sys.argv[2:] if args is None else args[1:]
        return file_tree_cmd.main(filetree_args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 