"""
Command-line interface for the metrics collector module.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional
from pathlib import Path
from tqdm import tqdm

from codex_arch.metrics.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Collect code metrics from a codebase",
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
        help="Output file path (default: './output/metrics.json')"
    )
    
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude (default: venv, .git, __pycache__, node_modules)"
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
        default=[".pyc", ".pyo", ".pyd", ".egg", ".egg-info"],
        help="File extensions to exclude"
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
        "--max-file-size",
        type=int,
        default=10 * 1024 * 1024,  # 10MB
        help="Maximum file size in bytes to process (default: 10MB)"
    )
    
    parser.add_argument(
        "--no-complexity",
        action="store_true",
        help="Skip complexity analysis"
    )
    
    parser.add_argument(
        "--complexity-max-file-size",
        type=int,
        default=1024 * 1024,  # 1MB
        help="Maximum file size in bytes for complexity analysis (default: 1MB)"
    )
    
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
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the metrics collector CLI."""
    parsed_args = parse_args(args)
    
    try:
        # Get absolute path to the directory
        root_path = Path(parsed_args.path).resolve()
        
        # Prepare output path
        if parsed_args.output:
            output_path = Path(parsed_args.output)
        else:
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / 'metrics.json'
        
        # Make sure the output directory exists
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Display progress info
        print(f"Collecting metrics for: {root_path}")
        print(f"Output will be saved to: {output_path}")
        
        # Create collector
        collector = MetricsCollector(
            root_path=root_path,
            exclude_dirs=parsed_args.exclude_dirs,
            exclude_patterns=parsed_args.exclude_patterns,
            exclude_extensions=parsed_args.exclude_extensions,
            include_extensions=parsed_args.include_extensions,
            include_hidden=parsed_args.include_hidden,
            max_file_size=parsed_args.max_file_size,
            analyze_complexity=not parsed_args.no_complexity,
            complexity_max_file_size=parsed_args.complexity_max_file_size
        )
        
        # Collect metrics with feedback
        print("Analyzing files...")
        with tqdm(total=100, desc="Collecting metrics") as pbar:
            # Estimate progress - file counting (20%)
            pbar.update(20)
            
            # Collect all metrics
            metrics = collector.collect_metrics()
            
            # Update progress - metrics collected
            pbar.update(60)
            
            # Export to JSON
            collector.to_json(
                output_file=str(output_path),
                indent=parsed_args.indent,
                include_metadata=not parsed_args.no_metadata
            )
            
            # Finalize progress
            pbar.update(20)
        
        # Print summary stats
        print("\nMetrics collection complete!")
        print(f"Files analyzed: {metrics['file_counts']['total']}")
        print(f"Total lines of code: {metrics['line_counts']['total']}")
        
        if not parsed_args.no_complexity and 'complexity_metrics' in metrics:
            print(f"Files analyzed for complexity: {metrics['complexity_metrics']['files_analyzed']}")
            print(f"Average complexity: {metrics['complexity_metrics']['average_complexity']}")
        
        print(f"Results saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 