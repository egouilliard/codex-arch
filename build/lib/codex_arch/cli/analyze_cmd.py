"""
Command-line interface for the full analysis pipeline.
"""

import argparse
import os
import sys
import logging
import importlib
from typing import List, Optional
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run full analysis pipeline (filetree, dependencies, metrics, visualization, summary)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="Path to the repository to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory for all results (default: './output')"
    )
    
    parser.add_argument(
        "--skip-file-tree",
        action="store_true",
        help="Skip file tree analysis"
    )
    
    parser.add_argument(
        "--skip-dependencies",
        action="store_true",
        help="Skip dependency analysis"
    )
    
    parser.add_argument(
        "--skip-metrics",
        action="store_true",
        help="Skip metrics collection"
    )
    
    parser.add_argument(
        "--skip-visualization",
        action="store_true",
        help="Skip visualization generation"
    )
    
    parser.add_argument(
        "--skip-summary",
        action="store_true",
        help="Skip summary generation"
    )
    
    parser.add_argument(
        "--bundle",
        action="store_true",
        help="Create a context bundle with all artifacts"
    )
    
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="+",
        default=["venv", ".git", "__pycache__", "node_modules"],
        help="Directories to exclude from all analyses"
    )
    
    return parser.parse_args(args)


def run_command(command_module, command_args):
    """Run a command module with the given arguments."""
    return command_module.main(command_args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the full analysis pipeline."""
    parsed_args = parse_args(args)
    
    try:
        # Prepare repository path and output directory
        repo_path = Path(parsed_args.path).resolve()
        output_dir = Path(parsed_args.output)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Track overall success
        success = True
        results = {}
        
        print(f"Starting full analysis of repository: {repo_path}")
        print(f"Output directory: {output_dir}")
        
        # Import command modules dynamically
        from codex_arch.cli import file_tree_cmd
        from codex_arch.cli import dependency_cmd
        from codex_arch.cli import metrics_cmd
        from codex_arch.cli import visualization_cmd
        from codex_arch.cli import summary_cmd
        from codex_arch.cli import bundle_cmd
        
        # Set up the pipeline steps
        pipeline = []
        dependencies_file = str(output_dir / "python_dependencies.json")
        metrics_file = str(output_dir / "metrics.json")
        
        # 1. File Tree Analysis
        if not parsed_args.skip_file_tree:
            pipeline.append({
                'name': 'File Tree Analysis',
                'module': file_tree_cmd,
                'args': [
                    str(repo_path),
                    "--output", str(output_dir / "file_tree.json"),
                    "--format", "json",
                    "--exclude-dirs"
                ] + parsed_args.exclude_dirs
            })
        
        # 2. Dependency Analysis
        if not parsed_args.skip_dependencies:
            pipeline.append({
                'name': 'Dependency Analysis',
                'module': dependency_cmd,
                'args': [
                    str(repo_path),
                    "--output", str(output_dir),
                    "--file", "python_dependencies.json",
                    "--exclude-patterns"
                ] + [f"**/{d}/**" for d in parsed_args.exclude_dirs]
            })
        
        # 3. Metrics Collection
        if not parsed_args.skip_metrics:
            pipeline.append({
                'name': 'Metrics Collection',
                'module': metrics_cmd,
                'args': [
                    str(repo_path),
                    "--output", metrics_file,
                    "--exclude-dirs"
                ] + parsed_args.exclude_dirs
            })
        
        # 4. Visualization Generation
        if not parsed_args.skip_visualization and not parsed_args.skip_dependencies:
            pipeline.append({
                'name': 'Visualization Generation',
                'module': visualization_cmd,
                'args': [
                    dependencies_file,
                    "--output", str(output_dir / "dependency_graph.svg"),
                    "--format", "svg",
                    "--group-modules"
                ]
            })
        
        # 5. Summary Generation
        if not parsed_args.skip_summary:
            pipeline.append({
                'name': 'Summary Generation',
                'module': summary_cmd,
                'args': [
                    str(repo_path),
                    "--output", str(output_dir / "summary.md"),
                    "--exclude-dirs"
                ] + parsed_args.exclude_dirs
            })
        
        # 6. Bundle Creation (if requested)
        if parsed_args.bundle:
            pipeline.append({
                'name': 'Bundle Creation',
                'module': bundle_cmd,
                'args': [
                    str(repo_path),
                    "--output", str(output_dir),
                    "--compress"
                ]
            })
        
        # Run the pipeline with progress tracking
        total_steps = len(pipeline)
        
        with tqdm(total=total_steps, desc="Analysis Pipeline") as pbar:
            for i, step in enumerate(pipeline, 1):
                step_name = step['name']
                pbar.set_description(f"[{i}/{total_steps}] {step_name}")
                
                print(f"\n--- Running {step_name} ---")
                
                try:
                    # Run the command
                    result = run_command(step['module'], step['args'])
                    results[step_name] = result
                    
                    if result != 0:
                        print(f"Warning: {step_name} completed with non-zero exit code: {result}")
                        success = False
                    else:
                        print(f"{step_name} completed successfully.")
                        
                except Exception as e:
                    print(f"Error in {step_name}: {str(e)}")
                    logger.error(f"Error in {step_name}: {str(e)}", exc_info=True)
                    results[step_name] = 1
                    success = False
                
                pbar.update(1)
        
        # Print summary
        print("\n--- Analysis Pipeline Complete ---")
        print("Steps executed:")
        
        for step_name, result in results.items():
            status = "Success" if result == 0 else "Failed"
            print(f"  - {step_name}: {status}")
        
        if success:
            print("\nAnalysis completed successfully!")
        else:
            print("\nAnalysis completed with errors. Check the logs for details.")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 