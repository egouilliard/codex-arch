#!/usr/bin/env python3
import json
import sys
import argparse
import os
from pathlib import Path

def find_importers(deps_file, target_file, exact_match=False):
    """Find all files that import the target file."""
    print(f"Finding all importers of {target_file} in {deps_file}...")
    
    # Get just the filename if a path was provided
    target_basename = Path(target_file).name
    print(f"Looking for files with {'exact path' if exact_match else 'name'}: {target_file if exact_match else target_basename}")
    
    # Load dependencies
    with open(deps_file, 'r') as f:
        data = json.load(f)
    
    # Extract nodes and edges
    nodes = data.get('nodes', {})
    edges = data.get('edges', {})
    
    # Find target node
    target_nodes = []
    for node_id, node_data in nodes.items():
        path = node_data.get('path', '')
        
        if exact_match:
            # Match the full path exactly
            if target_file == path:
                target_nodes.append(node_id)
                print(f"Found target file as node: {node_id} ({path})")
        else:
            # Match just the filename
            if target_basename in Path(path).name:
                target_nodes.append(node_id)
                print(f"Found target file as node: {node_id} ({path})")
    
    if not target_nodes:
        print(f"Target file '{target_file}' not found in the dependency graph.")
        return []
    
    # Find all importers
    importers = []
    for source, targets in edges.items():
        # Check if any of our target nodes are in the targets list
        for target_node in target_nodes:
            if target_node in targets:
                source_path = nodes.get(source, {}).get('path', source)
                importers.append((source, source_path))
                break
    
    # Print results
    if importers:
        print(f"\nFound {len(importers)} files that import {target_file if exact_match else target_basename}:")
        for idx, (importer_id, importer_path) in enumerate(importers, 1):
            print(f"{idx}. {importer_id} ({importer_path})")
    else:
        print(f"\nNo files found that import {target_file if exact_match else target_basename}")
    
    return importers

def parse_args():
    parser = argparse.ArgumentParser(description="Find files that import a target file")
    parser.add_argument("deps_file", help="Path to the dependency JSON file")
    parser.add_argument("target_file", help="Target file to find importers for")
    parser.add_argument("--exact", action="store_true", help="Match exact path instead of just filename")
    parser.add_argument("--output-dir", "-o", help="Output directory to save results (optional)")
    return parser.parse_args()

def generate_example_command(output_dir=None):
    """Generate an example command based on the output directory if provided"""
    if output_dir:
        return f"python scripts/find_imports.py {output_dir}/complete_dependencies.json pydantic_ai_coder.py"
    else:
        return "python scripts/find_imports.py <path/to/output>/complete_dependencies.json pydantic_ai_coder.py"

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python find_imports.py <dependencies_file> <target_file> [--exact] [--output-dir <dir>]")
        print("Example: " + generate_example_command())
        sys.exit(1)
        
    args = parse_args()
    
    # If output directory is provided and deps_file is a relative path,
    # construct the full path to the dependencies file
    if args.output_dir and not os.path.isabs(args.deps_file):
        # If deps_file doesn't already include the output_dir
        if not args.deps_file.startswith(args.output_dir):
            args.deps_file = os.path.join(args.output_dir, args.deps_file)
    
    find_importers(args.deps_file, args.target_file, args.exact) 