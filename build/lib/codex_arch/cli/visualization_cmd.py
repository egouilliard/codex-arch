"""
Command-line interface for the visualization module.
"""

import argparse
import os
import sys
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from tqdm import tqdm

from codex_arch.visualization.graph.dot_generator import DotGenerator

logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate graph visualizations from dependency data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input dependency JSON file to visualize"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: based on input filename)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["dot", "svg", "png"],
        default="svg",
        help="Output format (default: svg)"
    )
    
    parser.add_argument(
        "--theme",
        choices=["light", "dark", "colorful"],
        default="colorful",
        help="Visualization color theme (default: colorful)"
    )
    
    parser.add_argument(
        "--group-modules",
        action="store_true",
        help="Group nodes by module/package"
    )
    
    parser.add_argument(
        "--max-nodes",
        type=int,
        help="Maximum number of nodes to display (limits to most connected nodes)"
    )
    
    parser.add_argument(
        "--layout",
        choices=["dot", "neato", "fdp", "sfdp", "twopi", "circo"],
        default="dot",
        help="GraphViz layout engine to use (default: dot)"
    )
    
    parser.add_argument(
        "--include-external",
        action="store_true",
        help="Include external dependencies in visualization"
    )
    
    return parser.parse_args(args)


def load_dependency_data(file_path: str) -> Dict[str, Any]:
    """Load dependency data from JSON file."""
    with open(file_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {str(e)}")


def main(args: Optional[List[str]] = None) -> int:
    """Run the visualization CLI."""
    parsed_args = parse_args(args)
    
    try:
        # Validate and resolve input path
        input_path = Path(parsed_args.input).resolve()
        if not input_path.exists():
            print(f"Error: Input file not found: {input_path}")
            return 1
        
        # Prepare output path
        if parsed_args.output:
            output_path = Path(parsed_args.output)
        else:
            # Auto-generate output path based on input filename and format
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{input_path.stem}.{parsed_args.format}"
        
        # Make sure the output directory exists
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Display progress info
        print(f"Generating visualization from: {input_path}")
        print(f"Output will be saved to: {output_path}")
        
        # Load dependency data
        print("Loading dependency data...")
        dependency_data = load_dependency_data(str(input_path))
        
        # Prepare visualization settings
        settings = {
            'theme': parsed_args.theme,
            'group_modules': parsed_args.group_modules,
            'max_nodes': parsed_args.max_nodes,
            'layout_engine': parsed_args.layout,
            'include_external': parsed_args.include_external
        }
        
        # Create dot generator (fixed initialization)
        generator = DotGenerator(output_dir=str(output_path.parent))
        
        # Apply settings
        if settings['theme']:
            # Map 'colorful' to 'light' since DotGenerator only supports 'light' and 'dark'
            theme = settings['theme']
            if theme == 'colorful':
                theme = 'light'
            generator.set_theme(theme)
        
        # Generate visualization with progress reporting
        print("Generating graph visualization...")
        with tqdm(total=100, desc="Generating") as pbar:
            # Generate DOT (30%)
            dot_graph = generator.generate_from_dependency_graph(dependency_data)
            dot_content = generator.to_dot_string()
            pbar.update(30)
            
            # First save DOT file if requested
            if parsed_args.format == 'dot':
                with open(output_path, 'w') as f:
                    f.write(dot_content)
                pbar.update(70)
            else:
                # Render to the requested format (70%)
                actual_output_path = None
                if parsed_args.format == 'svg':
                    actual_output_path = generator.save_svg_file(str(output_path.stem))
                else:
                    actual_output_path = generator.save_rendered_file(str(output_path.stem), format=parsed_args.format)
                # Update output_path if the generator returned a different path
                if actual_output_path:
                    output_path = Path(actual_output_path)
                pbar.update(70)
        
        print(f"\nVisualization generated successfully: {output_path}")
        
        # Print some stats
        node_count = len(dependency_data.get('nodes', {}).keys())
        edge_count = sum(len(targets) if isinstance(targets, list) else len(targets.keys()) 
                        for targets in dependency_data.get('edges', {}).values())
        print(f"Graph contains {node_count} nodes and {edge_count} edges")
        
        if parsed_args.max_nodes and node_count > parsed_args.max_nodes:
            print(f"Limited visualization to {parsed_args.max_nodes} most connected nodes")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 