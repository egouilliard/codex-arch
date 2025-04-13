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
        
        # Store analysis results
        self.analysis_results: Dict[str, Any] = {}

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

    def add_edge(self, source: str, target: str, data: Dict[str, Any] = None) -> bool:
        """
        Add a directed edge from source to target.
        
        Args:
            source: Source node ID
            target: Target node ID
            data: Additional data to store with the edge
            
        Returns:
            Boolean indicating if the edge was successfully added
        """
        # Input validation
        if not source or not isinstance(source, str):
            logger.error(f"Invalid source node ID: {source}")
            return False
            
        if not target or not isinstance(target, str):
            logger.error(f"Invalid target node ID: {target}")
            return False
            
        if source == target:
            logger.warning(f"Self-referential edge detected: {source} -> {target}")
            # Still allow self-references but warn about them
            
        if data is None:
            data = {}
            
        # Make sure both nodes exist
        if source not in self.nodes:
            self.add_node(source)
            logger.debug(f"Created missing source node: {source}")
            
        if target not in self.nodes:
            self.add_node(target)
            logger.debug(f"Created missing target node: {target}")
            
        # Store edge metadata in a more accessible form (for future enhancements)
        edge_key = f"{source}:{target}"
        
        # Add the edge if it doesn't exist
        if target not in self.edges[source]:
            self.edges[source].append(target)
            self.reverse_edges[target].append(source)
            logger.debug(f"Added edge: {source} -> {target}")
            return True
        else:
            logger.debug(f"Edge already exists: {source} -> {target}")
            return False

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

    def edges_list(self) -> List[Tuple[str, str]]:
        """
        Get all edges in the graph as a list of (source, target) tuples.
        
        Returns:
            List of (source, target) tuples representing all edges in the graph
        """
        result = []
        for source, targets in self.edges.items():
            for target in targets:
                result.append((source, target))
        return result

    def edge_count(self) -> int:
        """
        Get the total number of edges in the graph.
        
        Returns:
            Integer count of edges in the graph
        """
        total = 0
        for targets in self.edges.values():
            total += len(targets)
        return total

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
        result = {
            "nodes": self.nodes,
            "edges": dict(self.edges),
            "unresolved_imports": dict(self.unresolved_imports),
            "external_dependencies": {k: list(v) for k, v in self.external_deps.items()}
        }
        
        # Include analysis results if they exist
        if hasattr(self, 'analysis_results') and self.analysis_results:
            result["analysis"] = self.analysis_results
            
        # Include edge errors if they exist
        if hasattr(self, 'edge_errors') and self.edge_errors:
            result["edge_errors"] = self.edge_errors
            
        return result

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the graph to a JSON string.
        
        Args:
            indent: Number of spaces to use for indentation
            
        Returns:
            JSON string representation of the graph
        """
        return json.dumps(self.to_dict(), indent=indent)

    def record_edge_error(self, source: str, target: str, error_type: str, message: str, details: Any = None) -> None:
        """
        Record an edge-related error in the graph for later analysis.
        
        Args:
            source: Source node ID
            target: Target node ID
            error_type: Type of error (e.g., 'invalid_edge', 'missing_target')
            message: Error message
            details: Additional error details (optional)
        """
        if not hasattr(self, 'edge_errors'):
            self.edge_errors = []
            
        self.edge_errors.append({
            'source': source,
            'target': target,
            'error_type': error_type,
            'message': message,
            'details': details
        })
        
        # Log the error
        logger.error(f"Edge error ({error_type}): {message}, {source} -> {target}")
        
        # Make sure the error is included in the graph serialization
        if 'edge_errors' not in self.analysis_results:
            self.analysis_results['edge_errors'] = []
            
        self.analysis_results['edge_errors'].append({
            'source': source,
            'target': target,
            'error_type': error_type,
            'message': message
        })


def build_graph_from_dependency_mapping(
    dependency_mapping: Dict[str, Dict[str, Any]], 
    exporter=None
) -> DependencyGraph:
    """
    Build a dependency graph from the dependency mapping.
    
    Args:
        dependency_mapping: Mapping of files to their dependencies
        exporter: Optional DependencyExporter for recording errors (default: None)
        
    Returns:
        A DependencyGraph instance
    """
    graph = DependencyGraph()
    
    # First pass: add all nodes
    for file_path, data in dependency_mapping.items():
        try:
            graph.add_node(file_path, {
                "file_path": file_path,
                "import_details": data.get("import_details", [])
            })
        except Exception as e:
            error_msg = f"Failed to add node for {file_path}"
            logger.error(f"{error_msg}: {str(e)}")
            if exporter:
                exporter.add_error(
                    file_path=file_path,
                    error_type='node_creation_error',
                    message=error_msg,
                    details=str(e)
                )
    
    # Second pass: add all edges
    for file_path, data in dependency_mapping.items():
        if file_path not in graph.nodes:
            continue  # Skip if source node wasn't created
            
        dependencies = data.get("dependencies", {})
        
        for import_name, resolved_path in dependencies.items():
            try:
                if resolved_path:
                    # Validate the resolved path
                    if not isinstance(resolved_path, str):
                        error_msg = f"Invalid resolved path type for import {import_name}"
                        logger.warning(f"{error_msg} in {file_path}: {type(resolved_path)}")
                        if exporter:
                            exporter.add_error(
                                file_path=file_path,
                                error_type='invalid_edge_data',
                                message=error_msg,
                                details=f"Expected string, got {type(resolved_path).__name__}"
                            )
                        graph.record_edge_error(
                            source=file_path,
                            target=str(resolved_path),  # Convert to string for safety
                            error_type='invalid_edge_data',
                            message=error_msg,
                            details=f"Expected string, got {type(resolved_path).__name__}"
                        )
                        continue
                        
                    # Add an edge for resolved imports
                    success = graph.add_edge(file_path, resolved_path, {
                        "import_name": import_name
                    })
                    
                    if not success:
                        # Edge could not be added, record the error
                        error_msg = f"Failed to add edge for import {import_name}"
                        graph.record_edge_error(
                            source=file_path,
                            target=resolved_path,
                            error_type='edge_addition_failure',
                            message=error_msg,
                            details="The edge could not be added to the graph"
                        )
                else:
                    # Track unresolved imports
                    # Check if it's likely an external dependency
                    if "." not in import_name or import_name.startswith("."):
                        # Likely a standard library or top-level third-party module
                        graph.add_external_dependency(file_path, import_name)
                    else:
                        # Unresolved import path
                        graph.add_unresolved_import(file_path, import_name)
                        if exporter:
                            exporter.add_error(
                                file_path=file_path,
                                error_type='unresolved_import',
                                message=f"Unresolved import: {import_name}",
                                details="Import could not be resolved to a file path"
                            )
                        graph.record_edge_error(
                            source=file_path,
                            target=import_name,
                            error_type='unresolved_import',
                            message=f"Unresolved import: {import_name}",
                            details="Import could not be resolved to a file path"
                        )
            except Exception as e:
                error_msg = f"Failed to process edge from {file_path} to {resolved_path} for import {import_name}"
                logger.error(f"{error_msg}: {str(e)}")
                if exporter:
                    exporter.add_error(
                        file_path=file_path,
                        error_type='edge_creation_error',
                        message=error_msg,
                        details=str(e)
                    )
                # Also record in the graph
                graph.record_edge_error(
                    source=file_path,
                    target=str(resolved_path) if resolved_path else import_name,
                    error_type='edge_creation_error',
                    message=error_msg,
                    details=str(e)
                )
    
    return graph


def analyze_dependencies(graph: DependencyGraph, exporter=None) -> Dict[str, Any]:
    """
    Analyze the dependency graph and extract useful metrics.
    
    Args:
        graph: The dependency graph to analyze
        exporter: Optional DependencyExporter for recording errors (default: None)
        
    Returns:
        Dictionary of analysis results
    """
    results = {}
    
    try:
        nodes = graph.get_all_nodes()
        results["total_modules"] = len(nodes)
        
        # Calculate dependency metrics
        dependent_counts = {}
        dependency_counts = {}
        
        for node in nodes:
            try:
                dependents = graph.get_dependents(node)
                dependencies = graph.get_dependencies(node)
                dependent_counts[node] = len(dependents)
                dependency_counts[node] = len(dependencies)
            except Exception as e:
                error_msg = f"Failed to analyze node {node}"
                logger.error(f"{error_msg}: {str(e)}")
                if exporter:
                    exporter.add_error(
                        file_path=node,
                        error_type='analysis_error',
                        message=error_msg,
                        details=str(e)
                    )
        
        # Sort nodes by various metrics
        most_depended_on = sorted(nodes, key=lambda n: dependent_counts.get(n, 0), reverse=True)
        most_dependencies = sorted(nodes, key=lambda n: dependency_counts.get(n, 0), reverse=True)
        
        # Calculate overall statistics safely
        try:
            total_dependencies = sum(dependency_counts.values())
            avg_dependencies = total_dependencies / len(nodes) if nodes else 0
            results["total_dependencies"] = total_dependencies
            results["average_dependencies"] = avg_dependencies
        except Exception as e:
            error_msg = "Failed to calculate dependency statistics"
            logger.error(f"{error_msg}: {str(e)}")
            if exporter:
                exporter.add_error(
                    file_path='graph_analysis',
                    error_type='statistics_error',
                    message=error_msg,
                    details=str(e)
                )
            results["total_dependencies"] = 0
            results["average_dependencies"] = 0
        
        # Find cycles with error handling
        try:
            cycles = graph.find_cycles()
            results["cycles"] = cycles
            results["has_cycles"] = len(cycles) > 0
        except Exception as e:
            error_msg = "Failed to detect dependency cycles"
            logger.error(f"{error_msg}: {str(e)}")
            if exporter:
                exporter.add_error(
                    file_path='graph_analysis',
                    error_type='cycle_detection_error',
                    message=error_msg,
                    details=str(e)
                )
            results["cycles"] = []
            results["has_cycles"] = False
        
        # Add dependency metrics to results
        results["most_depended_on"] = [(node, dependent_counts.get(node, 0)) for node in most_depended_on[:10]]
        results["most_dependencies"] = [(node, dependency_counts.get(node, 0)) for node in most_dependencies[:10]]
        
        # Additional analysis metrics
        results["unresolved_import_counts"] = {node: len(imports) for node, imports in graph.unresolved_imports.items() if imports}
        results["external_dependency_counts"] = {node: len(deps) for node, deps in graph.external_deps.items() if deps}
        results["orphaned_modules"] = [node for node in nodes if not graph.get_dependents(node) and not graph.get_dependencies(node)]
        
    except Exception as e:
        error_msg = "Failed to complete dependency analysis"
        logger.error(f"{error_msg}: {str(e)}")
        if exporter:
            exporter.add_error(
                file_path='graph_analysis',
                error_type='analysis_error',
                message=error_msg,
                details=str(e)
            )
        # Return minimal results in case of a major failure
        if "total_modules" not in results:
            results["total_modules"] = 0
        if "total_dependencies" not in results:
            results["total_dependencies"] = 0
    
    return results 