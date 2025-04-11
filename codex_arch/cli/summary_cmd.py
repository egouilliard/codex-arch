"""
Command-line interface for the summary builder module.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from tqdm import tqdm

from codex_arch.summary.summary_builder import SummaryBuilder, SummaryConfig
from codex_arch.summary.data_collector import DataCollector

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a summary report of the codebase",
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
        default="./output/summary.md",
        help="Output file path (default: ./output/summary.md)"
    )
    
    parser.add_argument(
        "--template",
        type=str,
        choices=["standard", "detailed", "minimal"],
        default="standard",
        help="Summary template to use (default: standard)"
    )
    
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude (default: venv, .git, __pycache__, node_modules)"
    )
    
    parser.add_argument(
        "--include-metrics",
        action="store_true",
        default=True,
        help="Include metrics in the summary (default: True)"
    )
    
    parser.add_argument(
        "--include-dependencies",
        action="store_true",
        default=True,
        help="Include dependency analysis in the summary (default: True)"
    )
    
    parser.add_argument(
        "--include-visualizations",
        action="store_true",
        default=True,
        help="Include visualizations in the summary (default: True)"
    )
    
    parser.add_argument(
        "--no-smart-summarization",
        action="store_true",
        help="Disable smart summarization of code structures"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the summary builder CLI."""
    parsed_args = parse_args(args)
    
    try:
        # Get absolute path to the directory
        root_path = Path(parsed_args.path).resolve()
        if not root_path.exists():
            print(f"Error: Path not found: {root_path}")
            return 1
        
        # Prepare output path
        output_path = Path(parsed_args.output)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Display progress info
        print(f"Generating summary for: {root_path}")
        print(f"Output will be saved to: {output_path}")
        
        # Create summary configuration
        config = SummaryConfig(
            template=parsed_args.template,
            include_metrics=parsed_args.include_metrics,
            include_dependencies=parsed_args.include_dependencies,
            include_visualizations=parsed_args.include_visualizations,
            use_smart_summarization=not parsed_args.no_smart_summarization,
            exclude_dirs=parsed_args.exclude_dirs
        )
        
        # Collect data and build summary with progress reporting
        print("Building summary...")
        with tqdm(total=100, desc="Summarizing") as pbar:
            # Data collection (40%)
            print("Collecting project data...")
            data_collector = DataCollector(root_path)
            data = data_collector.collect_data()
            pbar.update(40)
            
            # Build summary (40%)
            print("Building summary document...")
            summary_builder = SummaryBuilder(config)
            summary = summary_builder.build_summary(data)
            pbar.update(40)
            
            # Write to file (20%)
            print("Writing to file...")
            with open(output_path, 'w') as f:
                f.write(summary)
            pbar.update(20)
        
        print(f"\nSummary generated successfully: {output_path}")
        
        # Print some stats from the data
        print(f"Repository: {data.get('repo_name', 'Unknown')}")
        print(f"File count: {data.get('file_count', 'Unknown')}")
        
        if 'language_distribution' in data:
            top_languages = sorted(
                data['language_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            if top_languages:
                print("Top languages:")
                for lang, percentage in top_languages:
                    print(f"  - {lang}: {percentage:.1f}%")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 