#!/usr/bin/env python
import json
import os
import re
import sys
from pathlib import Path
import click
from graphviz import Digraph

def generate_graph(input_file, output_file):
    """Generate architecture graph visualization from dependency data."""
    print(f"Reading dependency data from: {input_file}")

    # Load the dependency data
    with open(input_file, "r") as f:
        data = json.load(f)

    # Extract nodes and edges from the correct location in the JSON
    graph_data = data.get("graph", {})
    if graph_data:
        print("Found graph data within the JSON")
        # Extract nodes and edges
        nodes = graph_data.get("nodes", {})
        edges = graph_data.get("edges", [])
        
        print(f"Number of nodes in graph: {len(nodes)}")
        print(f"Number of edges in graph: {len(edges)}")
    else:
        # Fall back to looking at the top-level keys
        nodes = data.get("nodes", {})
        edges = data.get("edges", {})
        
        print(f"Using top-level nodes and edges")
        print(f"Number of nodes: {len(nodes)}")
        print(f"Number of edges: {len(edges) if isinstance(edges, list) else sum(len(targets) for targets in edges.values()) if isinstance(edges, dict) else 0}")

    # Create a directed graph
    dot = Digraph(comment='Codex-Arch Architecture')
    dot.attr(rankdir='LR', size='12,8', ratio='fill', fontname='Arial')
    dot.attr('node', shape='box', style='filled', fillcolor='#f5f5f5', fontname='Arial')
    dot.attr('edge', fontname='Arial')

    # Focus on codex_arch modules
    MODULE_PATTERN = r'^(.+?)/'  # Match up to the first slash
    SUBMODULE_PATTERN = r'^(.+?/.+?)/'  # Match up to the second slash

    # Track modules and submodules
    modules = set()
    submodules = set()
    module_files = {}

    # Process nodes differently based on the format
    node_items = []
    if isinstance(nodes, dict):
        # Handle dictionary format
        for node_id, node_data in nodes.items():
            if isinstance(node_data, dict):
                node_items.append((node_id, node_data))
            else:
                node_items.append((node_id, {"id": node_id}))
    elif isinstance(nodes, list):
        # Handle list format
        for node in nodes:
            node_id = node.get("id", "")
            node_items.append((node_id, node))

    # First pass: identify all modules and submodules
    for node_id, node_data in node_items:
        # Get file path, trying different possible keys
        file_path = ""
        for key in ["file_path", "path", "name", "label", "id"]:
            if isinstance(node_data, dict) and key in node_data and node_data[key]:
                file_path = node_data[key]
                break
        
        if not file_path and node_id:
            file_path = node_id
        
        # Skip external dependencies or empty paths
        if not file_path or file_path.startswith(("__", "external")):
            continue
            
        # Try to extract module name (first directory level)
        module_match = re.match(MODULE_PATTERN, file_path)
        if module_match:
            module = module_match.group(1)
            modules.add(module)
            
            # Track files per module
            if module not in module_files:
                module_files[module] = set()
            module_files[module].add(file_path)
        else:
            # If no slash, use the filename as the module
            module = os.path.basename(file_path)
            if "." in module:  # If it has an extension, remove it
                module = os.path.splitext(module)[0]
            modules.add(module)
            if module not in module_files:
                module_files[module] = set()
            module_files[module].add(file_path)
            
        # Also track submodules
        submodule_match = re.match(SUBMODULE_PATTERN, file_path)
        if submodule_match:
            submodule = submodule_match.group(1)
            submodules.add(submodule)

    # Debug information about detected modules
    print(f"Detected modules: {modules}")
    print(f"Detected submodules: {submodules}")

    # Process edges differently based on the format
    edge_items = []
    if isinstance(edges, dict):
        # Handle dictionary format (source -> targets)
        for source_id, targets in edges.items():
            if isinstance(targets, list):
                edge_items.append((source_id, targets))
    elif isinstance(edges, list):
        # Handle list format of edge objects
        edge_dict = {}
        
        # Determine the edge format by inspecting the first item
        if edges and isinstance(edges[0], list):
            # Format is [source, target] or similar
            print("Edge format appears to be list of lists")
            for edge in edges:
                if len(edge) >= 2:
                    source = edge[0]
                    target = edge[1]
                    if source not in edge_dict:
                        edge_dict[source] = []
                    edge_dict[source].append(target)
        else:
            # Format might be list of dicts with source/target keys
            print("Edge format appears to be list of objects")
            try:
                for edge in edges:
                    if isinstance(edge, dict):
                        source = edge.get("source", "")
                        target = edge.get("target", "")
                        if source and target:
                            if source not in edge_dict:
                                edge_dict[source] = []
                            edge_dict[source].append(target)
            except Exception as e:
                print(f"Error processing edges: {e}")
                # Print a sample of the edges for debugging
                print(f"Edge sample: {edges[:2]}")
        
        for source, targets in edge_dict.items():
            edge_items.append((source, targets))

    print(f"Processed {len(edge_items)} different source nodes with edges")

    # Add nodes for each module with a unique color
    colors = [
        "#e1f5fe", "#b3e5fc", "#81d4fa", "#4fc3f7", "#29b6f6", 
        "#03a9f4", "#039be5", "#0288d1", "#0277bd", "#01579b",
        "#e0f2f1", "#b2dfdb", "#80cbc4", "#4db6ac", "#26a69a",
        "#009688", "#00897b", "#00796b", "#00695c", "#004d40"
    ]
    
    # Add a module cluster for each module
    for i, module in enumerate(sorted(modules)):
        color = colors[i % len(colors)]
        
        # Add module node
        dot.node(module, module, fillcolor=color, style='filled,bold', shape='tab')
        
        # Add files within this module, if any
        files = module_files.get(module, set())
        if files:
            # Only show up to 10 files per module to prevent cluttering
            for j, file_path in enumerate(sorted(files)[:10]):
                file_name = os.path.basename(file_path)
                dot.node(file_path, file_name, fillcolor=color, style='filled')
                dot.edge(module, file_path, style='dashed', arrowhead='none')
            
            # If there are more files, add a count node
            if len(files) > 10:
                dot.node(f"{module}_more", f"+ {len(files) - 10} more files", 
                        shape='plaintext', fontcolor='#666666')
                dot.edge(module, f"{module}_more", style='dashed', arrowhead='none')

    # Add dependency edges between modules
    module_deps = {}
    for source, targets in edge_items:
        # Extract source module
        source_module = None
        source_match = re.match(MODULE_PATTERN, source)
        if source_match:
            source_module = source_match.group(1)
        else:
            source_name = os.path.basename(source)
            if "." in source_name:
                source_module = os.path.splitext(source_name)[0]
            else:
                source_module = source_name
        
        # Skip if source module not found
        if not source_module or source_module not in modules:
            continue
        
        # Process each target
        for target in targets:
            # Extract target module
            target_module = None
            target_match = re.match(MODULE_PATTERN, target)
            if target_match:
                target_module = target_match.group(1)
            else:
                target_name = os.path.basename(target)
                if "." in target_name:
                    target_module = os.path.splitext(target_name)[0]
                else:
                    target_module = target_name
            
            # Skip if target module not found or it's a self-reference
            if not target_module or target_module not in modules or target_module == source_module:
                continue
            
            # Add to module dependencies
            if source_module not in module_deps:
                module_deps[source_module] = set()
            
            module_deps[source_module].add(target_module)
    
    # Draw edges between modules
    for source_module, target_modules in module_deps.items():
        for target_module in target_modules:
            dot.edge(source_module, target_module, color='#666666', penwidth='2.0')

    # Save the graph to file
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Render to both PNG and SVG
        dot.render(output_file, format='png', cleanup=True)
        dot.render(output_file, format='svg', cleanup=True)
        
        print(f"Graph visualization saved to: {output_file}.png and {output_file}.svg")
        return True
    except Exception as e:
        print(f"Error saving graph: {e}")
        return False

@click.command()
@click.argument('input_file')
@click.argument('output_file')
def visualize(input_file, output_file):
    """
    Generate architecture visualization from dependency data.
    
    Creates architectural diagrams from dependency data,
    showing relationships between modules and files.
    """
    try:
        generate_graph(input_file, output_file)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    visualize() 