"""
DOT Generator Module.

This module provides functionality to transform dependency data into DOT format
for visualization with Graphviz.
"""

import os
import logging
import colorsys
from typing import Dict, List, Set, Tuple, Optional, Any, Union
import graphviz

logger = logging.getLogger(__name__)

class DotGenerator:
    """
    Transforms dependency data into DOT format for visualization.
    
    This class provides methods to convert dependency graphs into DOT language
    for rendering with Graphviz.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the DOT generator.
        
        Args:
            output_dir: Directory where output files will be saved
                        (defaults to current directory)
        """
        self.output_dir = output_dir or "output"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.dot = None
        
        # Default color schemes
        self.theme = "light"
        self.node_color_scheme = {
            "light": {
                "default": "#E1F5FE",  # Light blue
                "file": "#E8F5E9",      # Light green
                "class": "#FFF3E0",     # Light orange
                "function": "#F3E5F5",  # Light purple
                "package": "#E0F7FA",   # Light cyan
                "module": "#FFF9C4",    # Light yellow
                "highlighted": "#FFEBEE"  # Light red
            },
            "dark": {
                "default": "#0D47A1",  # Dark blue
                "file": "#1B5E20",     # Dark green
                "class": "#E65100",    # Dark orange
                "function": "#4A148C", # Dark purple
                "package": "#006064",  # Dark cyan
                "module": "#F57F17",   # Dark yellow
                "highlighted": "#B71C1C"  # Dark red
            }
        }
        
        self.edge_color_scheme = {
            "default": "#9E9E9E",   # Gray
            "imports": "#2196F3",   # Blue
            "uses": "#4CAF50",      # Green
            "inherits": "#FF9800",  # Orange
            "critical": "#F44336"   # Red
        }
        
        # New properties for module grouping
        self.module_groups = {}
        self.module_depth = 2  # Default module depth for grouping
        
    def set_theme(self, theme: str = "light"):
        """
        Set the color theme for the generated graph.
        
        Args:
            theme: Color theme, either 'light' or 'dark'
        """
        if theme not in ["light", "dark"]:
            raise ValueError(f"Theme '{theme}' not supported. Use 'light' or 'dark'.")
        self.theme = theme
        
    def initialize_graph(self, title: str = "Dependency Graph", rankdir: str = "LR",
                         concentrate: bool = True, overlap: str = "false",
                         fontname: str = "Arial", bgcolor: str = None) -> graphviz.Digraph:
        """
        Initialize a new directed graph.
        
        Args:
            title: Graph title
            rankdir: Direction of graph layout (TB=top-bottom, LR=left-right)
            concentrate: Whether to merge edges
            overlap: How to handle node overlap ('false', 'scale', etc.)
            fontname: Default font
            bgcolor: Background color (if None, uses theme default)
            
        Returns:
            Initialized Graphviz Digraph object
        """
        # Default background color based on theme
        if bgcolor is None:
            bgcolor = "#FFFFFF" if self.theme == "light" else "#2D2D2D"
        
        # Create directed graph with specified attributes
        self.dot = graphviz.Digraph(
            comment=title,
            format='dot',
            engine='dot',
            graph_attr={
                'rankdir': rankdir,
                'label': title,
                'labelloc': 't',
                'fontname': fontname,
                'fontsize': '16',
                'bgcolor': bgcolor,
                'concentrate': 'true' if concentrate else 'false',
                'overlap': overlap,
                'splines': 'polyline',  # Curved edges for better readability
                'sep': '+10',           # Increased node separation
                'nodesep': '0.5',       # Minimum space between nodes
                'ranksep': '0.75',      # Minimum space between ranks
            },
            node_attr={
                'fontname': fontname,
                'shape': 'box',
                'style': 'filled',
                'fontsize': '12',
                'margin': '0.2,0.1',
            },
            edge_attr={
                'fontname': fontname,
                'fontsize': '10',
            }
        )
        
        return self.dot
        
    def generate_from_dependency_graph(self, dependency_graph: Dict[str, Any]) -> graphviz.Digraph:
        """
        Generate a DOT graph from a dependency graph.
        
        Args:
            dependency_graph: Dictionary representing dependency graph
                             with nodes, edges, and optional metadata
                             
        Returns:
            Graphviz Digraph object
        """
        if not dependency_graph:
            raise ValueError("Empty dependency graph provided")
            
        # Initialize graph if not already done
        if self.dot is None:
            title = dependency_graph.get("metadata", {}).get("title", "Dependency Graph")
            self.initialize_graph(title=title)
            
        # Extract graph settings from metadata if provided
        metadata = dependency_graph.get("metadata", {})
        if "theme" in metadata:
            self.set_theme(metadata["theme"])
            
        # Pre-process and identify modules for grouping
        self._identify_module_groups(dependency_graph)
            
        # Add nodes to the graph with attributes based on metadata
        for node_id, node_data in dependency_graph.get("nodes", {}).items():
            self._add_node(node_id, node_data)
            
        # Create module subgraphs (clusters) for better organization
        self._create_module_clusters()
            
        # Add edges to the graph with attributes based on relationship type
        for source, targets in dependency_graph.get("edges", {}).items():
            for target in targets:
                edge_data = {}
                # Handle both simple list of targets and dict with metadata
                if isinstance(targets, dict):
                    edge_data = targets.get(target, {})
                self._add_edge(source, target, edge_data)
                
        # Optimize graph layout
        self._optimize_layout(dependency_graph)
                
        return self.dot
        
    def _identify_module_groups(self, dependency_graph: Dict[str, Any]) -> None:
        """
        Identify module groups based on node paths.
        
        Args:
            dependency_graph: Dictionary representing dependency graph
        """
        # Get module grouping depth from metadata if provided
        metadata = dependency_graph.get("metadata", {})
        if "module_depth" in metadata:
            self.module_depth = int(metadata["module_depth"])
            
        # Reset module groups
        self.module_groups = {}
        
        for node_id, node_data in dependency_graph.get("nodes", {}).items():
            # Skip nodes marked to not be grouped
            if node_data.get("no_group", False):
                continue
                
            # Check if the node has a module path
            path_parts = node_id.split('/')
            if len(path_parts) > 1:
                # Create group based on the module depth
                group_path = '/'.join(path_parts[:min(self.module_depth, len(path_parts))])
                
                if group_path not in self.module_groups:
                    self.module_groups[group_path] = {
                        'nodes': set(),
                        'label': group_path,
                        'color': node_data.get("group_color", None)
                    }
                
                # Add node to its module group
                self.module_groups[group_path]['nodes'].add(node_id)
    
    def _create_module_clusters(self) -> None:
        """
        Create subgraphs for module clusters.
        """
        # Exit if no groups or dot graph is not initialized
        if not self.module_groups or self.dot is None:
            return
            
        # Create a subgraph for each module group
        for group_id, group_data in self.module_groups.items():
            # Skip groups with only one node
            if len(group_data['nodes']) <= 1:
                continue
                
            # Create a cluster subgraph for the module
            with self.dot.subgraph(name=f'cluster_{group_id.replace("/", "_")}') as subgraph:
                # Set subgraph attributes
                subgraph.attr(
                    label=group_data['label'],
                    style='filled,rounded',
                    color='#DDDDDD' if self.theme == 'light' else '#444444',
                    fillcolor='#F5F5F5' if self.theme == 'light' else '#333333',
                    fontcolor='#333333' if self.theme == 'light' else '#EEEEEE'
                )
                
                # Add all nodes in this group to the subgraph
                for node_id in group_data['nodes']:
                    subgraph.node(node_id)
        
    def _optimize_layout(self, dependency_graph: Dict[str, Any]) -> None:
        """
        Apply layout optimizations to improve graph readability.
        
        Args:
            dependency_graph: Dictionary representing dependency graph
        """
        if self.dot is None:
            return
            
        # Apply different layout strategies based on graph size and complexity
        node_count = len(dependency_graph.get("nodes", {}))
        edge_count = sum(len(targets) for targets in dependency_graph.get("edges", {}).values())
        
        # For large graphs, use hierarchical layout
        if node_count > 50:
            self.dot.graph_attr.update({
                'rankdir': 'TB',  # Top to bottom layout for large graphs
                'concentrate': 'true',  # Merge edges when possible
                'packMode': 'clust',  # Pack closely related nodes
                'overlap': 'prism',  # Advanced overlap removal
            })
        
        # For very complex graphs, use force-directed layout
        if edge_count > 100:
            self.dot.engine = 'fdp'  # Switch to force-directed placement
            self.dot.graph_attr.update({
                'K': '0.6',  # Optimal edge length
                'maxiter': '1000',  # More iterations for better layout
            })
        
        # For graphs with module clustering, optimize intra-cluster layout
        if self.module_groups:
            self.dot.graph_attr.update({
                'compound': 'true',  # Enable edges between clusters
                'newrank': 'true',   # Better rank assignment for clustered graphs
            })
            
    def _add_node(self, node_id: str, node_data: Dict[str, Any] = None) -> None:
        """
        Add a node to the graph with appropriate styling.
        
        Args:
            node_id: Unique identifier for the node
            node_data: Dictionary of node metadata
        """
        if self.dot is None:
            raise ValueError("Graph not initialized. Call initialize_graph() first.")
            
        if node_data is None:
            node_data = {}
            
        # Get node label
        label = self._format_node_label(node_id, node_data)
        
        # Get node attributes based on metadata
        attrs = self._get_node_attributes(node_id, node_data)
        attrs["label"] = label
        
        # Add node to graph
        self.dot.node(node_id, **attrs)
        
    def _add_edge(self, source: str, target: str, edge_data: Dict[str, Any] = None) -> None:
        """
        Add an edge to the graph with appropriate styling.
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_data: Dictionary of edge metadata
        """
        if self.dot is None:
            raise ValueError("Graph not initialized. Call initialize_graph() first.")
            
        if edge_data is None:
            edge_data = {}
            
        # Get edge attributes based on metadata
        attrs = self._get_edge_attributes(source, target, edge_data)
        
        # Check if this is an inter-cluster edge
        source_group = None
        target_group = None
        
        for group_id, group_data in self.module_groups.items():
            if source in group_data['nodes']:
                source_group = group_id
            if target in group_data['nodes']:
                target_group = group_id
                
        # Enable edge routing through clusters if needed
        if source_group and target_group and source_group != target_group:
            attrs['ltail'] = f'cluster_{source_group.replace("/", "_")}'
            attrs['lhead'] = f'cluster_{target_group.replace("/", "_")}'
            
        # Add edge to graph
        self.dot.edge(source, target, **attrs)
        
    def _format_node_label(self, node_id: str, node_data: Dict[str, Any]) -> str:
        """
        Format the label for a node.
        
        Args:
            node_id: Node identifier
            node_data: Node metadata
            
        Returns:
            Formatted label string
        """
        # Use provided label if available
        if "label" in node_data:
            label = node_data["label"]
        else:
            # Extract name from path (last component)
            if "/" in node_id:
                label = node_id.split("/")[-1]
            else:
                label = node_id
                
        # Add type prefix if available
        if "type" in node_data:
            prefix = {
                "file": "📄",
                "class": "🔷",
                "function": "🔸",
                "package": "📦",
                "module": "📚"
            }.get(node_data["type"], "")
            
            if prefix:
                label = f"{prefix} {label}"
                
        # Add additional metadata if configured
        details = []
        
        if node_data.get("show_complexity", False) and "complexity" in node_data:
            details.append(f"Complexity: {node_data['complexity']}")
            
        if node_data.get("show_size", False) and "size" in node_data:
            details.append(f"Size: {node_data['size']}")
            
        if node_data.get("show_deps", False) and "dependencies" in node_data:
            details.append(f"Deps: {node_data['dependencies']}")
            
        # Add details to label if any
        if details:
            label = f"{label}\\n{' | '.join(details)}"
            
        return label
        
    def _get_node_attributes(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Determine node attributes based on metadata.
        
        Args:
            node_id: Node identifier
            node_data: Node metadata
            
        Returns:
            Dictionary of node attributes
        """
        attrs = {}
        
        # Default shape and color
        attrs["shape"] = "box"
        attrs["style"] = "filled"
        
        # Get the color scheme based on theme
        color_scheme = self.node_color_scheme[self.theme]
        
        # Default fill color
        attrs["fillcolor"] = color_scheme["default"]
        attrs["color"] = "#000000" if self.theme == "light" else "#FFFFFF"
        
        # Adjust color based on node type
        if "type" in node_data and node_data["type"] in color_scheme:
            attrs["fillcolor"] = color_scheme[node_data["type"]]
            
        # Apply custom color if specified
        if "color" in node_data:
            attrs["fillcolor"] = node_data["color"]
            
        # Apply custom shape if specified
        if "shape" in node_data:
            attrs["shape"] = node_data["shape"]
            
        # Special styling for important nodes
        if node_data.get("important", False):
            attrs["penwidth"] = "2.0"
            attrs["fontsize"] = "14"
            attrs["fillcolor"] = color_scheme["highlighted"]
                
        # If this is a highly connected node, highlight it
        if "connections" in node_data and isinstance(node_data["connections"], (int, float)):
            connections = int(node_data["connections"])
            if connections > 10:
                attrs["penwidth"] = "2.0"
                attrs["color"] = "#FF5722"  # Highlight border for highly connected nodes
                
        return attrs
    
    def _get_edge_attributes(self, source: str, target: str, edge_data: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Determine edge attributes based on relationship metadata.
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_data: Edge metadata
            
        Returns:
            Dictionary of edge attributes
        """
        attrs = {}
        
        # Default attributes
        attrs["color"] = self.edge_color_scheme["default"]
        
        if not edge_data:
            return attrs
            
        # Determine edge type if specified
        edge_type = edge_data.get("type", "default")
        if edge_type in self.edge_color_scheme:
            attrs["color"] = self.edge_color_scheme[edge_type]
            
        # Adjust edge weight/thickness based on importance
        if "importance" in edge_data:
            importance = float(edge_data["importance"])
            attrs["penwidth"] = str(1 + min(importance * 2, 5))
            
        # Add edge labels if specified
        if "label" in edge_data:
            attrs["label"] = edge_data["label"]
            
        # Different line styles for different relationship types
        if "relationship" in edge_data:
            relationship = edge_data["relationship"]
            if relationship == "imports":
                attrs["style"] = "solid"
            elif relationship == "uses":
                attrs["style"] = "dashed"
            elif relationship == "extends" or relationship == "inherits":
                attrs["style"] = "bold"
            elif relationship == "implements":
                attrs["style"] = "dotted"
                
        # Critical path highlighting
        if edge_data.get("critical", False):
            attrs["color"] = self.edge_color_scheme["critical"]
            attrs["penwidth"] = "2.0"
            
        return attrs
    
    def save_dot_file(self, filename: str = "dependency_graph") -> str:
        """
        Save the DOT representation to a file.
        
        Args:
            filename: Output filename (without extension)
            
        Returns:
            Path to the saved DOT file
        """
        if self.dot is None:
            raise ValueError("No graph initialized. Call initialize_graph() or generate_from_dependency_graph() first.")
        
        if not filename.endswith('.dot'):
            filename = f"{filename}.dot"
            
        filepath = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        dot_source = self.dot.source
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dot_source)
            
        logger.info(f"DOT file saved to {filepath}")
        return filepath

    def render_graph(self, format: str = 'svg', cleanup: bool = True) -> str:
        """
        Render the graph in the specified format.
        
        Args:
            format: Output format ('svg', 'png', 'pdf', etc.)
            cleanup: Whether to clean up temporary files
            
        Returns:
            Rendered file data as a string (for svg) or path to rendered file (for other formats)
        """
        if self.dot is None:
            raise ValueError("No graph initialized. Call initialize_graph() or generate_from_dependency_graph() first.")
        
        # Validate format
        supported_formats = ['svg', 'png', 'pdf', 'jpg', 'jpeg', 'webp']
        if format not in supported_formats:
            raise ValueError(f"Unsupported format: {format}. Use one of: {', '.join(supported_formats)}")
        
        # Check if Graphviz is installed
        self._check_graphviz_installed()
        
        # Render the graph
        try:
            rendered = self.dot.pipe(format=format, encoding='utf-8' if format == 'svg' else None)
            logger.info(f"Graph rendered in {format} format")
            return rendered
        except Exception as e:
            logger.error(f"Error rendering graph: {str(e)}")
            raise

    def _check_graphviz_installed(self) -> bool:
        """
        Check if Graphviz executables are installed.
        
        Returns:
            True if Graphviz is installed, raises an exception otherwise
        """
        import shutil
        import subprocess
        
        # Check if the 'dot' executable is in the PATH
        dot_path = shutil.which('dot')
        
        if not dot_path:
            logger.warning("Graphviz 'dot' executable not found in PATH")
            
            # Try to get version to provide a more helpful error message
            try:
                # Try running dot -V to get version info
                subprocess.run(['dot', '-V'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               check=False)
            except FileNotFoundError:
                installation_instructions = """
                Graphviz executables are required for rendering graphs.
                
                Installation instructions:
                - macOS: brew install graphviz
                - Ubuntu/Debian: sudo apt install graphviz
                - Windows: Download installer from https://graphviz.org/download/
                
                After installation, ensure the 'dot' executable is in your system PATH.
                """
                logger.error(installation_instructions)
                raise RuntimeError(f"Graphviz executables not found. {installation_instructions}")
        
        return True

    def save_svg_file(self, filename: str = "dependency_graph") -> str:
        """
        Render and save the graph as an SVG file.
        
        Args:
            filename: Output filename (without extension)
            
        Returns:
            Path to the saved SVG file
        """
        if not filename.endswith('.svg'):
            filename = f"{filename}.svg"
            
        filepath = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Render as SVG
        svg_data = self.render_graph(format='svg')
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_data)
            
        # Get absolute path for logging
        abs_filepath = os.path.abspath(filepath)
        logger.info(f"SVG file saved to {abs_filepath}")
        return abs_filepath

    def save_rendered_file(self, filename: str, format: str = 'svg') -> str:
        """
        Render and save the graph in the specified format.
        
        Args:
            filename: Output filename (without extension)
            format: Output format ('svg', 'png', 'pdf', etc.)
            
        Returns:
            Path to the saved file
        """
        # Add appropriate extension if not present
        if not filename.endswith(f'.{format}'):
            filename = f"{filename}.{format}"
            
        filepath = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            # For SVG, use the dedicated method
            if format == 'svg':
                return self.save_svg_file(filename)
            
            # For binary formats
            rendered = self.render_graph(format=format)
            if format == 'svg':  # SVG is text
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(rendered)
            else:  # Other formats are binary
                with open(filepath, 'wb') as f:
                    f.write(rendered)
            
            # Get absolute path for logging
            abs_filepath = os.path.abspath(filepath)
            logger.info(f"{format.upper()} file saved to {abs_filepath}")
            return abs_filepath
        except Exception as e:
            logger.error(f"Error saving {format} file: {str(e)}")
            raise

    def to_dot_string(self) -> str:
        """
        Get the DOT representation as a string.
        
        Returns:
            DOT source string
        """
        if self.dot is None:
            raise ValueError("No graph initialized. Call initialize_graph() or generate_from_dependency_graph() first.")
        
        return self.dot.source 