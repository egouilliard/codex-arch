import json
import os
import sys
from pathlib import Path
import click

def convert_dependencies(input_file, output_file):
    """Convert dependency format to one that the visualizer can handle better."""
    print(f"Converting {input_file} to {output_file}...")
    
    # Load dependencies
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Extract nodes and edges
    nodes = data.get('graph', {}).get('nodes', {})
    raw_edges = data.get('graph', {}).get('edges', [])
    
    # Create a mapping from full path to simplified name
    path_to_name = {}
    simplified_nodes = {}
    
    # First pass: process all nodes
    for node_path in nodes:
        # Get filename with parent dir for uniqueness
        path = Path(node_path)
        parent = path.parent.name
        filename = path.name
        node_id = filename if parent == "" else f"{parent}/{filename}"
        
        # Ensure uniqueness
        counter = 1
        original_id = node_id
        while node_id in simplified_nodes:
            node_id = f"{original_id}_{counter}"
            counter += 1
        
        # Add to simplified nodes with type information
        node_type = "external" if ("../../../../../../Library" in node_path or "../venv/" in node_path) else "internal"
        simplified_nodes[node_id] = {
            "id": node_id,
            "path": node_path,
            "type": node_type,
            "label": node_id
        }
        
        # Map full path to simplified name
        path_to_name[node_path] = node_id
    
    # Process edges
    simplified_edges = {}
    
    # Process all raw edges
    for source, target in raw_edges:
        # Skip if source or target not found (shouldn't happen)
        if source not in path_to_name or target not in path_to_name:
            continue
            
        source_id = path_to_name[source]
        target_id = path_to_name[target]
        
        # Add edge
        if source_id not in simplified_edges:
            simplified_edges[source_id] = []
        
        if target_id not in simplified_edges[source_id]:
            simplified_edges[source_id].append(target_id)
    
    # Process detailed import information in nodes
    for node_path, node_data in nodes.items():
        if node_path not in path_to_name:
            continue
            
        source_id = path_to_name[node_path]
        
        # Skip if no import information
        if "imports" not in node_data:
            continue
            
        # Process each import
        for import_info in node_data.get("imports", []):
            module = import_info.get("module", "")
            if not module:
                continue
                
            # Find possible target files for this import
            for target_path, target_id in path_to_name.items():
                # Skip self imports
                if target_path == node_path:
                    continue
                    
                # Check if target path contains the module name
                target_file = Path(target_path).name
                if module == target_file.replace('.py', '') or f"{module}.py" == target_file:
                    # Add import edge
                    if source_id not in simplified_edges:
                        simplified_edges[source_id] = []
                    
                    if target_id not in simplified_edges[source_id]:
                        simplified_edges[source_id].append(target_id)
    
    # Create output format
    converted_data = {
        "nodes": simplified_nodes,
        "edges": simplified_edges,
        "metadata": {
            "title": "Complete Dependency Graph",
            "description": "Visualization of all module dependencies including external libraries",
            "format_version": "1.0"
        }
    }
    
    # Save to output file
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_file, 'w') as f:
        json.dump(converted_data, f, indent=2)
    
    # Count total edges
    edge_count = sum(len(targets) for targets in simplified_edges.values())
    internal_nodes = sum(1 for node in simplified_nodes.values() if node["type"] == "internal")
    external_nodes = sum(1 for node in simplified_nodes.values() if node["type"] == "external")
    
    print(f"Conversion complete. Created {output_file} with:")
    print(f"- {len(simplified_nodes)} total nodes ({internal_nodes} internal, {external_nodes} external)")
    print(f"- {edge_count} total edges")
    
    return converted_data

@click.command()
@click.argument('input_file')
@click.argument('output_file')
def convert_command(input_file, output_file):
    """
    Convert dependency data to a complete visualization format.
    
    Takes raw dependency data and converts it to a format that
    can be used by the visualization tools.
    """
    try:
        convert_dependencies(input_file, output_file)
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    convert_command() 