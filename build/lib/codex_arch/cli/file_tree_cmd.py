"""
Command-line interface for the file tree extractor module.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from codex_arch.extractors.file_tree_extractor import FileTreeExtractor


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract and generate file trees from directories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown", "md"],
        default="json",
        help="Output format (json, markdown/md)"
    )
    
    parser.add_argument(
        "-d", "--max-depth",
        type=int,
        help="Maximum depth to traverse"
    )
    
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        help="Directories to exclude (e.g., .git node_modules)"
    )
    
    parser.add_argument(
        "--exclude-patterns",
        type=str,
        nargs="+",
        help="Regex patterns to exclude files and directories"
    )
    
    parser.add_argument(
        "--exclude-extensions",
        type=str,
        nargs="+",
        help="File extensions to exclude (e.g., .pyc .log)"
    )
    
    parser.add_argument(
        "--include-extensions",
        type=str,
        nargs="+",
        help="Only include these file extensions"
    )
    
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories"
    )
    
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links"
    )
    
    # JSON-specific options
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Indentation level for JSON output"
    )
    
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from JSON output"
    )
    
    # Markdown-specific options
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Don't use emoji icons in Markdown output"
    )
    
    parser.add_argument(
        "--no-size",
        action="store_true",
        help="Don't include file size in Markdown output"
    )
    
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Don't include header in Markdown output"
    )
    
    parser.add_argument(
        "--relative-paths",
        action="store_true",
        help="Use paths relative to the root path"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the file tree extractor CLI."""
    parsed_args = parse_args(args)
    
    try:
        # Create the extractor
        extractor = FileTreeExtractor(
            root_path=parsed_args.path,
            max_depth=parsed_args.max_depth,
            exclude_dirs=parsed_args.exclude_dirs,
            exclude_patterns=parsed_args.exclude_patterns,
            exclude_extensions=parsed_args.exclude_extensions,
            include_extensions=parsed_args.include_extensions,
            include_hidden=parsed_args.include_hidden,
            follow_symlinks=parsed_args.follow_symlinks
        )
        
        # Generate output based on format
        if parsed_args.format in ["markdown", "md"]:
            result = extractor.to_markdown(
                output_file=parsed_args.output if parsed_args.output else None,
                include_size=not parsed_args.no_size,
                include_header=not parsed_args.no_header,
                use_emoji=not parsed_args.no_emoji,
                relative_paths=parsed_args.relative_paths
            )
        else:  # json format
            result = extractor.generate_json(
                output_file=parsed_args.output if parsed_args.output else None,
                indent=parsed_args.indent,
                include_metadata=not parsed_args.no_metadata
            )
        
        # Print to stdout if not writing to file
        if result and not parsed_args.output:
            print(result)
            
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 