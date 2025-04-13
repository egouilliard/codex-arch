"""
Command module for converting dependency data.
"""

import argparse
import sys
from codex_arch.visualization.converter import convert_dependencies

def main(args=None):
    """Main entry point for the command."""
    parser = argparse.ArgumentParser(
        description="Convert dependency data to visualization format"
    )
    
    parser.add_argument(
        "input_file",
        help="Input dependency file (e.g., python_dependencies.json)"
    )
    
    parser.add_argument(
        "output_file",
        help="Output file for converted dependencies"
    )
    
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    try:
        convert_dependencies(parsed_args.input_file, parsed_args.output_file)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 