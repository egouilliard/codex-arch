"""
Command module for generating architecture graphs.
"""

import argparse
import sys
from codex_arch.visualization.graph_generator import generate_graph

def main(args=None):
    """Main entry point for the command."""
    parser = argparse.ArgumentParser(
        description="Generate architecture graph from dependency data"
    )
    
    parser.add_argument(
        "input_file",
        help="Input dependency file (e.g., complete_dependencies.json)"
    )
    
    parser.add_argument(
        "output_file",
        help="Output file path for the graph (without extension)"
    )
    
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    try:
        generate_graph(parsed_args.input_file, parsed_args.output_file)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 