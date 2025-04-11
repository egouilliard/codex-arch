"""
Dependency Graph Construction Module.

This module builds a graph representation of Python module dependencies.
It uses the data from the import parser and path resolver modules.
"""

import os
import json
import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union, DefaultDict
from collections import defaultdict

logger = logging.getLogger(__name__)

class DependencyGraph:
    """Represents a dependency graph of Python modules."""
    
    def __init__(self):
        """Initialize an empty dependency graph."""
        # Map of node IDs to node data
        self.nodes: Dict[str, Dict[str, Any]] = {}
        
        # Map of source node ID to list of target node IDs
        self.edges: DefaultDict[str, List[str]] = defaultdict(list)
        
        # Track reverse dependencies (which modules import a given module)
        self.reverse_edges: DefaultDict[str, List[str]] = defaultdict(list)
        
        # Keep track of imports that couldn't be resolved to actual files
        self.unresolved_imports: DefaultDict[str, List[str]] = defaultdict(list)
        
        # Track standard library and third-party dependencies
        self.external_deps: DefaultDict[str, Set[str]] = defaultdict(set)

    def add_node(self, node_id: str, data: Dict[str, Any] = None) -> None:
        """
        Add a node to the graph.
        
        Args:
            node_id: Unique identifier for the node (usually the file path)
            data: Additional data to store with the node
        """
        if not data:
            data = {}
        
        if node_id not in self.nodes:
            self.nodes[node_id] = data

    def add_edge(self, source: str, target: str, data: Dict[str, Any] = None) -> None:
        """
        Add a directed edge from source to target.
        
        Args:
            source: Source node ID
            target: Target node ID
            data: Additional data to store with the edge
        """
        if not data:
            data = {}
            
        # Make sure both nodes exist
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)
            
        # Add the edge if it doesn't exist
        if target not in self.edges[source]:
            self.edges[source].append(target)
            self.reverse_edges[target].append(source)

    def add_unresolved_import(self, source: str, import_name: str) -> None:
        """
        Add an import that couldn't be resolved to an actual file.
        
        Args:
            source: Source node ID
            import_name: The import statement that couldn't be resolved
        """
        self.unresolved_imports[source].append(import_name)

    def add_external_dependency(self, source: str, module_name: str) -> None:
        """
        Add a dependency on a standard library or third-party module.
        
        Args:
            source: Source node ID
            module_name: Name of the external module
        """
        self.external_deps[source].add(module_name)

    def get_dependencies(self, node_id: str) -> List[str]:
        """
        Get all modules that a module directly depends on.
        
        Args:
            node_id: The node ID to get dependencies for
            
        Returns:
            List of node IDs that are direct dependencies
        """
        return self.edges.get(node_id, [])

    def get_dependents(self, node_id: str) -> List[str]:
        """
        Get all modules that directly depend on a module.
        
        Args:
            node_id: The node ID to get dependents for
            
        Returns:
            List of node IDs that directly depend on the given node
        """
        return self.reverse_edges.get(node_id, [])

    def get_external_dependencies(self, node_id: str) -> Set[str]:
        """
        Get all external dependencies of a module.
        
        Args:
            node_id: The node ID to get external dependencies for
            
        Returns:
            Set of external module names
        """
        return self.external_deps.get(node_id, set())

    def get_all_nodes(self) -> List[str]:
        """
        Get all node IDs in the graph.
        
        Returns:
            List of all node IDs
        """
        return list(self.nodes.keys())

    def find_cycles(self) -> List[List[str]]:
        """
        Find all cycles in the dependency graph.
        
        Returns:
            List of cycles, where each cycle is a list of node IDs
        """
        cycles = []
        visited = set()
        path = []
        path_set = set()
        
        def dfs(node: str) -> None:
            nonlocal cycles, visited, path, path_set
            
            # Skip if already fully processed
            if node in visited:
                return
                
            # Check for cycle
            if node in path_set:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
                
            # Add to current path
            path.append(node)
            path_set.add(node)
            
            # Visit all dependencies
            for dep in self.get_dependencies(node):
                dfs(dep)
                
            # Remove from current path
            path.pop()
            path_set.remove(node)
            
            # Mark as fully processed
            visited.add(node)
        
        # Run DFS from all nodes
        for node in self.get_all_nodes():
            if node not in visited:
                dfs(node)
                
        return cycles

    def get_transitive_dependencies(self, node_id: str) -> Set[str]:
        """
        Get all direct and indirect dependencies of a module.
        
        Args:
            node_id: The node ID to get transitive dependencies for
            
        Returns:
            Set of all node IDs that the given node depends on, directly or indirectly
        """
        result = set()
        visited = set()
        
        def dfs(node: str) -> None:
            if node in visited:
                return
                
            visited.add(node)
            for dep in self.get_dependencies(node):
                result.add(dep)
                dfs(dep)
        
        dfs(node_id)
        return result

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the graph to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the graph
        """
        return {
            "nodes": self.nodes,
            "edges": dict(self.edges),
            "unresolved_imports": dict(self.unresolved_imports),
            "external_dependencies": {k: list(v) for k, v in self.external_deps.items()}
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the graph to a JSON string.
        
        Args:
            indent: Number of spaces to use for indentation
            
        Returns:
            JSON string representation of the graph
        """
        return json.dumps(self.to_dict(), indent=indent)


def build_graph_from_dependency_mapping(dependency_mapping: Dict[str, Dict[str, Any]]) -> DependencyGraph:
    """
    Build a dependency graph from the dependency mapping.
    
    Args:
        dependency_mapping: Mapping of files to their dependencies
        
    Returns:
        A DependencyGraph instance
    """
    graph = DependencyGraph()
    
    # First pass: add all nodes
    for file_path, data in dependency_mapping.items():
        graph.add_node(file_path, {
            "file_path": file_path,
            "import_details": data.get("import_details", [])
        })
    
    # Second pass: add all edges
    for file_path, data in dependency_mapping.items():
        dependencies = data.get("dependencies", {})
        
        for import_name, resolved_path in dependencies.items():
            if resolved_path:
                # Add an edge for resolved imports
                graph.add_edge(file_path, resolved_path, {
                    "import_name": import_name
                })
            else:
                # Track unresolved imports
                # Check if it's likely an external dependency
                if "." not in import_name or import_name.startswith("."):
                    # Likely a standard library or top-level third-party module
                    graph.add_external_dependency(file_path, import_name)
                else:
                    # Unresolved import path
                    graph.add_unresolved_import(file_path, import_name)
    
    return graph


def analyze_dependencies(graph: DependencyGraph) -> Dict[str, Any]:
    """
    Analyze the dependency graph and extract useful metrics.
    
    Args:
        graph: The dependency graph to analyze
        
    Returns:
        Dictionary of analysis results
    """
    nodes = graph.get_all_nodes()
    cycles = graph.find_cycles()
    
    # Calculate dependency metrics
    dependent_counts = {}
    dependency_counts = {}
    
    for node in nodes:
        dependent_counts[node] = len(graph.get_dependents(node))
        dependency_counts[node] = len(graph.get_dependencies(node))
    
    # Sort nodes by various metrics
    most_depended_on = sorted(nodes, key=lambda n: dependent_counts[n], reverse=True)
    most_dependencies = sorted(nodes, key=lambda n: dependency_counts[n], reverse=True)
    
    # Calculate overall statistics
    total_dependencies = sum(dependency_counts.values())
    avg_dependencies = total_dependencies / len(nodes) if nodes else 0
    
    return {
        "total_modules": len(nodes),
        "total_dependencies": total_dependencies,
        "average_dependencies": avg_dependencies,
        "most_depended_on": [(node, dependent_counts[node]) for node in most_depended_on[:10]],
        "most_dependencies": [(node, dependency_counts[node]) for node in most_dependencies[:10]],
        "cycles": cycles,
        "has_cycles": len(cycles) > 0
    } 