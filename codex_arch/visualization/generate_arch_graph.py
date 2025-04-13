#!/usr/bin/env python
import json
import os
import re
import sys
from pathlib import Path
from graphviz import Digraph

def generate_graph(input_file=None, output_file=None):
    """Generate architecture graph from dependency data."""
    
    # Handle input parameters
    if input_file is None:
        input_file = "output/python_dependencies.json"
        
    if output_file is None:
        output_file = "output/architecture_graph"

    # Print debug information
    print(f"Reading dependency data from: {input_file}")

    # Load the dependency data
    with open(input_file, "r") as f:
        data = json.load(f)

    # Debug information about the data structure
    print(f"Data keys: {list(data.keys())}")

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
        print(f"Number of edges: {len(edges)}")

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
            node_items.append((node_id, node_data))
    elif isinstance(nodes, list):
        # Handle list format
        for node in nodes:
            node_id = node.get("id", "")
            node_items.append((node_id, node))

    # First pass: identify all modules and submodules
    for node_id, node_data in node_items:
        # Get file path, trying different possible keys
        file_path = ""
        for key in ["file_path", "path", "name", "label"]:
            if key in node_data and node_data[key]:
                file_path = node_data[key]
                break
        
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

    # Generate the graph based on module dependencies
    module_dependencies = {}
    
    # Extract module-level dependencies from file-level dependencies
    for source_id, targets in edge_items:
        # Skip if source not found
        source_module = None
        module_match = re.match(MODULE_PATTERN, source_id)
        if module_match:
            source_module = module_match.group(1)
        else:
            # If no slash, use the filename without extension
            filename = os.path.basename(source_id)
            if "." in filename:
                source_module = os.path.splitext(filename)[0]
            else:
                source_module = filename
                
        if source_module:
            if source_module not in module_dependencies:
                module_dependencies[source_module] = set()
                
            # Handle different target formats
            if isinstance(targets, list):
                for target in targets:
                    target_module = None
                    module_match = re.match(MODULE_PATTERN, target)
                    if module_match:
                        target_module = module_match.group(1)
                    else:
                        # If no slash, use the filename without extension
                        filename = os.path.basename(target)
                        if "." in filename:
                            target_module = os.path.splitext(filename)[0]
                        else:
                            target_module = filename
                            
                    if target_module and target_module != source_module:
                        module_dependencies[source_module].add(target_module)
            elif isinstance(targets, dict):
                for target in targets.keys():
                    target_module = None
                    module_match = re.match(MODULE_PATTERN, target)
                    if module_match:
                        target_module = module_match.group(1)
                    else:
                        # If no slash, use the filename without extension
                        filename = os.path.basename(target)
                        if "." in filename:
                            target_module = os.path.splitext(filename)[0]
                        else:
                            target_module = filename
                            
                    if target_module and target_module != source_module:
                        module_dependencies[source_module].add(target_module)
    
    # Add nodes for each module with meaningful attributes
    for module in modules:
        file_count = len(module_files.get(module, []))
        # Choose a color based on the module type
        if module == "codex_arch":
            fillcolor = "#e3f2fd"  # Light blue for main module
            fontcolor = "#0d47a1"
        elif module in ["tests", "test"]:
            fillcolor = "#e8f5e9"  # Light green for tests
            fontcolor = "#2e7d32"
        elif module in ["docs", "documentation"]:
            fillcolor = "#fff3e0"  # Light orange for docs
            fontcolor = "#e65100"
        elif module in ["scripts", "tools"]:
            fillcolor = "#f3e5f5"  # Light purple for scripts
            fontcolor = "#6a1b9a"
        else:
            fillcolor = "#f5f5f5"  # Light gray for other modules
            fontcolor = "#212121"
            
        # Create a label with the module name and file count
        label = f"{module}\\n({file_count} files)" if file_count > 0 else module
        
        dot.node(module, label, 
                fillcolor=fillcolor, 
                fontcolor=fontcolor,
                penwidth="1.5")
    
    # Add edges for module dependencies with counts
    for source, targets in module_dependencies.items():
        for target in targets:
            # Skip self-references
            if source == target:
                continue
                
            if source in modules and target in modules:
                dot.edge(source, target)
    
    # If no modules were found, try a different approach
    if not modules:
        print("No modules detected, falling back to file-based visualization")
        # Use file names as nodes
        for node_id, node_data in node_items:
            # Get file path, trying different possible keys
            file_path = ""
            for key in ["file_path", "path", "name", "label"]:
                if key in node_data and node_data[key]:
                    file_path = node_data[key]
                    break
                    
            if file_path:
                file_name = os.path.basename(file_path)
                dot.node(file_name, file_name, fillcolor='#e1f5fe')
        
        # Create edges between files
        for source_id, targets in edge_items:
            # Find source file
            source_name = os.path.basename(source_id)
            
            # Handle different target formats
            if isinstance(targets, list):
                for target in targets:
                    target_name = os.path.basename(target)
                    if source_name != target_name:
                        dot.edge(source_name, target_name)
            elif isinstance(targets, dict):
                for target in targets.keys():
                    target_name = os.path.basename(target)
                    if source_name != target_name:
                        dot.edge(source_name, target_name)
    
    # Save the graph in both PNG and SVG formats
    try:
        dot.render(output_file, format='png', cleanup=True)
        print(f"Architecture graph saved as {output_file}.png")
        
        dot.render(output_file, format='svg', cleanup=True)
        print(f"Architecture graph saved as {output_file}.svg")
    except Exception as e:
        print(f"Error rendering graph: {e}")
        print("Make sure the Graphviz executable is installed and in your PATH.")
    
    return dot

if __name__ == "__main__":
    # Allow specifying the dependency file and output path via command line
    input_file = None
    output_file = None
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        
    generate_graph(input_file, output_file) 