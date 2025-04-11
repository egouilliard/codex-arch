"""
Command-line interface for the Python dependency extractor module.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional
from tqdm import tqdm

from codex_arch.extractors.python.extractor import PythonDependencyExtractor, extract_dependencies

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract and analyze dependencies from Python code",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="Path to the Python project to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output directory for results (default: './output')"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        default="python_dependencies.json",
        help="Output filename (default: python_dependencies.json)"
    )
    
    parser.add_argument(
        "--include-patterns",
        type=str,
        nargs="+",
        default=["**/*.py"],
        help="Glob patterns for files to include (default: ['**/*.py'])"
    )
    
    parser.add_argument(
        "--exclude-patterns",
        type=str,
        nargs="+",
        default=["**/venv/**", "**/.git/**", "**/__pycache__/**"],
        help="Glob patterns for files to exclude (default: ['**/venv/**', '**/.git/**', '**/__pycache__/**'])"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the Python dependency extractor CLI."""
    parsed_args = parse_args(args)
    
    try:
        # Get absolute path to the Python project
        root_dir = os.path.abspath(parsed_args.path)
        output_dir = parsed_args.output or os.path.join(os.getcwd(), 'output')
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Show progress information
        print(f"Analyzing Python dependencies in: {root_dir}")
        print(f"Output will be saved to: {output_dir}")
        
        # Create extractor with progress tracking
        print("Finding Python files...")
        extractor = PythonDependencyExtractor(root_dir, output_dir)
        python_files = extractor.find_python_files(
            include_patterns=parsed_args.include_patterns,
            exclude_patterns=parsed_args.exclude_patterns
        )
        
        print(f"Found {len(python_files)} Python files to analyze")
        
        # Process files with progress bar
        print("Analyzing imports and dependencies...")
        for file_path in tqdm(python_files, desc="Processing", unit="file"):
            try:
                extractor.process_file(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Export results
        print("Generating dependency graph...")
        output_file = parsed_args.file
        json_path = extractor.export(output_file)
        
        print(f"Successfully generated dependency graph at: {json_path}")
        print(f"Found {len(extractor.dependency_graph.nodes)} modules with {extractor.dependency_graph.edge_count()} dependencies")
        
        errors = extractor.exporter.errors
        if errors:
            print(f"Encountered {len(errors)} errors during analysis")
            for i, error in enumerate(errors[:3], 1):  # Show first 3 errors
                print(f"  {i}. {error['file_path']}: {error['message']}")
            if len(errors) > 3:
                print(f"  ... and {len(errors) - 3} more errors")
                
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 