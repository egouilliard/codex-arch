#!/usr/bin/env python
"""
Comprehensive script to run all Codex-Arch analysis commands.

This script provides a single entry point to run all the necessary analysis commands:
1. Full analysis (dependencies, metrics, file tree)
2. Architecture graph generation
3. Dependency conversion and enhanced visualization

Usage:
    python run_all_analysis.py <repo_path> [options]
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('codex-arch')

def run_command(command, description=None):
    """Run a shell command and log the output."""
    if description:
        logger.info(f"Running: {description}")
    
    logger.debug(f"Command: {command}")
    
    try:
        # Run the command and capture output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Get return code
        return_code = process.poll()
        
        # Get any remaining stderr
        stderr = process.stderr.read()
        if stderr:
            logger.warning(f"Command stderr: {stderr}")
        
        if return_code != 0:
            logger.error(f"Command failed with return code {return_code}")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return False

def create_output_dir(output_dir):
    """Create the output directory if it doesn't exist."""
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Using output directory: {output_dir}")

def run_full_analysis(args):
    """Run the full codex-arch analysis pipeline."""
    repo_path = args.repo_path
    output_dir = args.output
    
    # Build the exclude_dirs parameter
    exclude_dirs = " ".join([f"--exclude-dirs {d}" for d in args.exclude_dirs])
    
    # Additional options
    options = ""
    if args.no_complexity:
        options += " --no-complexity"
    if args.no_metrics:
        options += " --skip-metrics"
    if args.no_file_tree:
        options += " --skip-file-tree"
    
    # Run the full analysis command
    command = f"codex-arch analyze {repo_path} --output {output_dir} {exclude_dirs} {options}"
    success = run_command(command, "Full analysis")
    
    if not success:
        logger.error("Full analysis failed, but continuing with remaining steps...")
    
    return success

def run_dependency_conversion(args):
    """Convert the dependency format for better visualization."""
    output_dir = args.output
    
    # Define input and output file paths
    input_file = os.path.join(output_dir, "python_dependencies.json")
    output_file = os.path.join(output_dir, "complete_dependencies.json")
    
    # Check if the input file exists
    if not os.path.exists(input_file):
        logger.error(f"Dependency file not found: {input_file}")
        return False
    
    # Run the conversion script
    command = f"python convert_deps.py {input_file} {output_file}"
    return run_command(command, "Converting dependency format")

def run_architecture_visualization(args):
    """Generate architecture visualizations."""
    output_dir = args.output
    
    # Define input and output file paths
    dep_file = os.path.join(output_dir, "python_dependencies.json")
    arch_output = os.path.join(output_dir, "architecture_graph")
    
    # Generate basic architecture graph
    command = f"python generate_arch_graph.py {dep_file} {arch_output}"
    success = run_command(command, "Generating architecture graph")
    
    # If conversion was done, also generate an enhanced graph
    if args.convert_deps:
        converted_file = os.path.join(output_dir, "complete_dependencies.json")
        enhanced_output = os.path.join(output_dir, "enhanced_architecture_graph")
        
        if os.path.exists(converted_file):
            command = f"python generate_arch_graph.py {converted_file} {enhanced_output}"
            enhanced_success = run_command(command, "Generating enhanced architecture graph")
            success = success and enhanced_success
    
    return success

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run all Codex-Arch analysis commands in sequence",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the repository to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output",
        help="Output directory for all results"
    )
    
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "node_modules", "__pycache__"],
        help="Directories to exclude from analysis"
    )
    
    parser.add_argument(
        "--convert-deps",
        action="store_true",
        help="Convert dependency format for enhanced visualization"
    )
    
    parser.add_argument(
        "--no-complexity",
        action="store_true",
        help="Skip complexity analysis for faster processing"
    )
    
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Skip metrics collection"
    )
    
    parser.add_argument(
        "--no-file-tree",
        action="store_true",
        help="Skip file tree generation"
    )
    
    parser.add_argument(
        "--no-visualization",
        action="store_true",
        help="Skip architecture visualization"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def main():
    """Main function to run all analysis steps."""
    # Parse arguments
    args = parse_args()
    
    # Set up logging based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Record the start time
    start_time = time.time()
    
    logger.info(f"Starting comprehensive analysis of {args.repo_path}")
    
    # Create output directory
    create_output_dir(args.output)
    
    # Run the full analysis
    full_analysis_success = run_full_analysis(args)
    
    # Convert dependency format if requested
    if args.convert_deps:
        conversion_success = run_dependency_conversion(args)
    else:
        conversion_success = True
    
    # Generate architecture visualizations
    if not args.no_visualization:
        visualization_success = run_architecture_visualization(args)
    else:
        visualization_success = True
    
    # Calculate execution time
    execution_time = time.time() - start_time
    minutes, seconds = divmod(execution_time, 60)
    
    # Report overall success/failure
    all_success = full_analysis_success and conversion_success and visualization_success
    
    if all_success:
        logger.info(f"All analysis tasks completed successfully in {int(minutes)} minutes and {int(seconds)} seconds")
    else:
        logger.warning(f"Some analysis tasks failed. Check the logs for details.")
    
    # List the generated files
    logger.info(f"Generated files in {args.output}:")
    for file_path in Path(args.output).glob("*"):
        logger.info(f"  - {file_path.name}")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main()) 