"""
Command-line interface for the context bundle assembler module.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from tqdm import tqdm

from codex_arch.bundler.context_bundle_assembler import ContextBundleAssembler, BundleConfig

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a context bundle of all analysis artifacts",
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
        help="Output directory for results (default: './output')"
    )
    
    parser.add_argument(
        "--bundle-dir",
        type=str,
        default="repo_meta",
        help="Directory name for the bundle within the output directory (default: repo_meta)"
    )
    
    parser.add_argument(
        "--no-file-tree",
        action="store_true",
        help="Don't include file tree artifacts in the bundle"
    )
    
    parser.add_argument(
        "--no-dependencies",
        action="store_true",
        help="Don't include dependency artifacts in the bundle"
    )
    
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Don't include metrics artifacts in the bundle"
    )
    
    parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Don't include visualization artifacts in the bundle"
    )
    
    parser.add_argument(
        "--no-summaries",
        action="store_true",
        help="Don't include summary artifacts in the bundle"
    )
    
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't clean up temporary files after bundling"
    )
    
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress the bundle into a single file"
    )
    
    parser.add_argument(
        "--compression-format",
        choices=["zip", "tar", "tar.gz"],
        default="zip",
        help="Format for compression if --compress is used (default: zip)"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Run the context bundle assembler CLI."""
    parsed_args = parse_args(args)
    
    try:
        # Get absolute path to the repository
        repo_path = Path(parsed_args.path).resolve()
        if not repo_path.exists():
            print(f"Error: Repository path not found: {repo_path}")
            return 1
        
        # Prepare output directory
        output_dir = parsed_args.output or os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # Display progress info
        print(f"Creating context bundle for repository: {repo_path}")
        print(f"Bundle will be created in: {output_dir}")
        
        # Create bundle configuration
        config = BundleConfig(
            bundle_dir=parsed_args.bundle_dir,
            include_file_tree=not parsed_args.no_file_tree,
            include_dependencies=not parsed_args.no_dependencies,
            include_metrics=not parsed_args.no_metrics,
            include_visualizations=not parsed_args.no_visualizations,
            include_summaries=not parsed_args.no_summaries,
            cleanup_temp_files=not parsed_args.no_cleanup,
            compress_bundle=parsed_args.compress,
            compression_format=parsed_args.compression_format
        )
        
        # Create the bundle assembler
        bundler = ContextBundleAssembler(
            repo_path=str(repo_path),
            output_dir=output_dir,
            config=config
        )
        
        # Run the bundling process with progress reporting
        print("Collecting and bundling artifacts...")
        with tqdm(total=100, desc="Bundling") as pbar:
            # Collect artifacts (30%)
            print("Collecting artifacts...")
            artifacts = bundler.collect_artifacts()
            pbar.update(30)
            
            # Generate manifest (20%)
            print("Generating bundle manifest...")
            manifest_path = bundler.generate_manifest()
            pbar.update(20)
            
            # Generate prompt template (20%)
            print("Generating prompt template...")
            prompt_path = bundler.generate_prompt_template()
            pbar.update(20)
            
            # Compress or finalize bundle (30%)
            if config.compress_bundle:
                print(f"Compressing bundle to {config.compression_format} format...")
                archive_path = bundler.compress_bundle()
                pbar.update(30)
            else:
                print("Finalizing bundle...")
                bundler.finalize_bundle()
                pbar.update(30)
        
        # Print summary
        bundle_path = os.path.join(output_dir, config.bundle_dir)
        print(f"\nBundle creation complete!")
        print(f"Bundle path: {bundle_path}")
        
        if config.compress_bundle:
            print(f"Compressed archive: {bundler.compress_bundle()}")
        
        # Print artifact counts
        file_tree_count = len(artifacts.get('file_tree', []))
        dependencies_count = len(artifacts.get('dependencies', []))
        metrics_count = len(artifacts.get('metrics', []))
        vis_count = len(artifacts.get('visualizations', []))
        summary_count = len(artifacts.get('summaries', []))
        
        print("\nArtifacts included:")
        print(f"  - File tree artifacts: {file_tree_count}")
        print(f"  - Dependency artifacts: {dependencies_count}")
        print(f"  - Metrics artifacts: {metrics_count}")
        print(f"  - Visualization artifacts: {vis_count}")
        print(f"  - Summary artifacts: {summary_count}")
        
        if manifest_path:
            print(f"  - Manifest: {os.path.basename(manifest_path)}")
        
        if prompt_path:
            print(f"  - Prompt template: {os.path.basename(prompt_path)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 