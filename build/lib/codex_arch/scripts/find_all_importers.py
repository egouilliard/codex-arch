#!/usr/bin/env python3
import json
import sys
import argparse
import os
from pathlib import Path
import re

def find_all_importers(deps_file, target_pattern):
    """Find all files that import any version of the target file pattern."""
    print(f"Finding all importers matching pattern '{target_pattern}' in {deps_file}...")
    
    # Load dependencies
    with open(deps_file, 'r') as f:
        data = json.load(f)
    
    # Extract nodes and edges
    nodes = data.get('nodes', {})
    edges = data.get('edges', {})
    
    # Compile regex pattern
    pattern = re.compile(target_pattern)
    
    # Find target nodes
    target_nodes = {}
    for node_id, node_data in nodes.items():
        path = node_data.get('path', '')
        if pattern.search(path):
            target_nodes[node_id] = path
            
    if not target_nodes:
        print(f"No files matching pattern '{target_pattern}' found in the dependency graph.")
        return
        
    print(f"Found {len(target_nodes)} target files matching the pattern:")
    for node_id, path in target_nodes.items():
        print(f"- {node_id} ({path})")
    
    # Find all importers for each target node
    all_importers = {}
    
    for target_id, target_path in target_nodes.items():
        importers = []
        for source, targets in edges.items():
            if target_id in targets:
                source_path = nodes.get(source, {}).get('path', source)
                importers.append((source, source_path))
        
        all_importers[target_id] = importers
    
    # Print results
    print("\n=== IMPORTERS BY FILE ===")
    
    total_importers = set()
    for target_id, importers in all_importers.items():
        target_path = target_nodes[target_id]
        print(f"\n{target_id} ({target_path}):")
        
        if importers:
            for idx, (importer_id, importer_path) in enumerate(importers, 1):
                print(f"  {idx}. {importer_id} ({importer_path})")
                total_importers.add(importer_id)
        else:
            print("  No files import this file")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total unique files that import any version: {len(total_importers)}")
    if total_importers:
        print("Unique importers:")
        for idx, importer_id in enumerate(sorted(total_importers), 1):
            importer_path = nodes.get(importer_id, {}).get('path', importer_id)
            print(f"  {idx}. {importer_id} ({importer_path})")

def parse_args():
    parser = argparse.ArgumentParser(description="Find files that import any file matching a pattern")
    parser.add_argument("deps_file", help="Path to the dependency JSON file")
    parser.add_argument("target_pattern", help="Regex pattern to match against file paths")
    parser.add_argument("--output-dir", "-o", help="Output directory to save results (optional)")
    return parser.parse_args()

def generate_example_command(output_dir=None):
    """Generate an example command based on the output directory if provided"""
    if output_dir:
        return f"python scripts/find_all_importers.py {output_dir}/complete_dependencies.json 'models.*\\.py'"
    else:
        return "python scripts/find_all_importers.py <path/to/output>/complete_dependencies.json 'models.*\\.py'"

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python find_all_importers.py <dependencies_file> <target_pattern> [--output-dir <dir>]")
        print("Example: " + generate_example_command())
        sys.exit(1)
    
    args = parse_args()
    
    # If output directory is provided and deps_file is a relative path,
    # construct the full path to the dependencies file
    if args.output_dir and not os.path.isabs(args.deps_file):
        # If deps_file doesn't already include the output_dir
        if not args.deps_file.startswith(args.output_dir):
            args.deps_file = os.path.join(args.output_dir, args.deps_file)
    
    find_all_importers(args.deps_file, args.target_pattern) 