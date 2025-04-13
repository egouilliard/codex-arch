#!/usr/bin/env python
import json
import os
import re
import sys
from graphviz import Digraph

# Allow specifying the dependency file and output path
input_file = "visualization_output/python_dependencies.json"
output_file = "visualization_output/architecture_graph"

if len(sys.argv) > 1:
    input_file = sys.argv[1]
if len(sys.argv) > 2:
    output_file = sys.argv[2]

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

# If no modules were found, try a different approach using filenames
if not modules:
    print("No modules detected with standard pattern, trying alternative approach...")
    # Use file names as nodes instead
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
        source_node = None
        for nid, ndata in node_items:
            if nid == source_id:
                source_node = ndata
                break
                
        if not source_node:
            continue
            
        # Get source path
        source_path = ""
        for key in ["file_path", "path", "name", "label"]:
            if key in source_node and source_node[key]:
                source_path = source_node[key]
                break
                
        if not source_path:
            continue
            
        source_name = os.path.basename(source_path)
        
        # Handle different target formats
        if isinstance(targets, dict):
            target_ids = list(targets.keys())
        elif isinstance(targets, list):
            target_ids = targets
        else:
            target_ids = [targets]
            
        for target_id in target_ids:
            # Find target file
            target_node = None
            for nid, ndata in node_items:
                if nid == target_id:
                    target_node = ndata
                    break
                    
            if not target_node:
                continue
                
            # Get target path
            target_path = ""
            for key in ["file_path", "path", "name", "label"]:
                if key in target_node and target_node[key]:
                    target_path = target_node[key]
                    break
                    
            if not target_path:
                continue
                
            target_name = os.path.basename(target_path)
            dot.edge(source_name, target_name)
else:
    # Create module nodes with their file counts
    for module in sorted(modules):
        file_count = len(module_files.get(module, []))
        label = f"{module}\\n({file_count} files)"
        dot.node(module, label, fillcolor='#e1f5fe')

    # Create submodule nodes
    for submodule in sorted(submodules):
        parts = submodule.split('/')
        if len(parts) >= 2:
            module, sub = parts
            if f"{module}/{sub}" != submodule:
                continue
            dot.node(submodule, sub, fillcolor='#fff9c4')

    # Create edges between modules based on dependencies
    module_dependencies = {}

    # Process edges between modules
    for source_id, targets in edge_items:
        # Find source module
        source_module = None
        source_path = ""
        
        # Find the source node
        source_node = None
        for nid, ndata in node_items:
            if nid == source_id:
                source_node = ndata
                break
                
        if not source_node:
            continue
            
        # Get source path
        for key in ["file_path", "path", "name", "label"]:
            if key in source_node and source_node[key]:
                source_path = source_node[key]
                break
                
        if not source_path:
            continue
        
        # Get the module for the source file
        source_module_match = re.match(MODULE_PATTERN, source_path)
        if source_module_match:
            source_module = source_module_match.group(1)
        else:
            # If no slash, use the basename without extension
            source_module = os.path.basename(source_path)
            if "." in source_module:
                source_module = os.path.splitext(source_module)[0]
        
        if not source_module:
            continue
            
        # Handle different target formats
        if isinstance(targets, dict):
            target_ids = list(targets.keys())
        elif isinstance(targets, list):
            target_ids = targets
        else:
            target_ids = [targets]
            
        for target_id in target_ids:
            # Find target node
            target_node = None
            for nid, ndata in node_items:
                if nid == target_id:
                    target_node = ndata
                    break
                    
            if not target_node:
                continue
                
            # Get target path
            target_path = ""
            for key in ["file_path", "path", "name", "label"]:
                if key in target_node and target_node[key]:
                    target_path = target_node[key]
                    break
                    
            if not target_path:
                continue
                
            # Get the module for the target file
            target_module = None
            target_module_match = re.match(MODULE_PATTERN, target_path)
            if target_module_match:
                target_module = target_module_match.group(1)
            else:
                # If no slash, use the basename without extension
                target_module = os.path.basename(target_path)
                if "." in target_module:
                    target_module = os.path.splitext(target_module)[0]
            
            if not target_module:
                continue
                
            if source_module != target_module:
                key = (source_module, target_module)
                module_dependencies[key] = module_dependencies.get(key, 0) + 1

    # Debug information about dependencies
    print(f"Found {len(module_dependencies)} module dependencies")

    # Create module to submodule edges
    for submodule in sorted(submodules):
        parts = submodule.split('/')
        if len(parts) >= 2:
            module = parts[0]
            dot.edge(module, submodule, style='dashed')

    # Add edges with counts
    for (source, target), count in sorted(module_dependencies.items()):
        dot.edge(source, target, label=str(count))

    # Generate a more detailed subgraph for the main components
    with dot.subgraph(name='cluster_core') as c:
        c.attr(label='Core Architecture Components', style='filled', fillcolor='#e8f5e9')
        
        # Add key files as nodes
        core_files = [
            ("cli/cli.py", "CLI"),
            ("cli/main.py", "MainCLI"),
            ("extractors/python/extractor.py", "PythonExtractor"),
            ("visualization/graph/dot_generator.py", "DotGenerator"),
            ("api/server.py", "APIServer"),
            ("metrics/collector.py", "MetricsCollector"),
        ]
        
        # Check if at least some of these files exist in the data
        core_file_exists = False
        for file_path, label in core_files:
            if any(file_path in files or file_path.replace('/', os.sep) in files for files in module_files.values()):
                c.node(file_path, label, fillcolor='#bbdefb', shape='box')
                core_file_exists = True
                print(f"Added core file: {file_path}")
        
        # If no core files were found, add some based on what we have
        if not core_file_exists:
            print("No core files found, adding some based on available data...")
            key_files = []
            # Find some important looking files
            for module, files in module_files.items():
                for file in files:
                    if 'main' in file.lower() or 'server' in file.lower() or 'cli' in file.lower() or 'extractor' in file.lower():
                        key_files.append((file, os.path.basename(file)))
                        if len(key_files) >= 5:
                            break
                if len(key_files) >= 5:
                    break
            
            for file_path, label in key_files[:5]:  # Add up to 5 key files
                c.node(file_path, label, fillcolor='#bbdefb', shape='box')
                print(f"Added detected key file: {file_path}")

# Render the graph
output_formats = ['svg', 'png']
for fmt in output_formats:
    dot.render(output_file, format=fmt, cleanup=True)
    print(f"Architecture graph generated at {output_file}.{fmt}") 