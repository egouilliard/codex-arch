"""
Python Dependency Extractor.

This module provides the main functionality for extracting dependencies from Python files.
It integrates the import parser, path resolver, dependency graph, and JSON exporter components.
"""

import os
import logging
import glob
from typing import Dict, List, Set, Tuple, Optional, Any

from codex_arch.extractors.python.import_parser import ImportVisitor, parse_python_file
from codex_arch.extractors.python.path_resolver import ImportPathResolver
from codex_arch.extractors.python.dependency_graph import DependencyGraph
from codex_arch.extractors.python.json_exporter import DependencyExporter

logger = logging.getLogger(__name__)

class PythonDependencyExtractor:
    """Main class for extracting dependencies from Python files."""
    
    def __init__(self, root_dir: str, output_dir: str = None):
        """
        Initialize the Python dependency extractor.
        
        Args:
            root_dir: Root directory of the Python project
            output_dir: Directory where output files will be saved (default: root_dir)
        """
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = output_dir or self.root_dir
        
        self.path_resolver = ImportPathResolver(self.root_dir)
        self.dependency_graph = DependencyGraph()
        self.exporter = DependencyExporter(self.output_dir)
        
    def find_python_files(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> List[str]:
        """
        Find Python files in the root directory based on include/exclude patterns.
        
        Args:
            include_patterns: List of glob patterns to include (default: ['**/*.py'])
            exclude_patterns: List of glob patterns to exclude (default: ['**/venv/**', '**/.git/**'])
            
        Returns:
            List of Python file paths relative to root_dir
        """
        if include_patterns is None:
            include_patterns = ['**/*.py']
            
        if exclude_patterns is None:
            exclude_patterns = ['**/venv/**', '**/.git/**', '**/__pycache__/**']
            
        python_files = []
        
        for pattern in include_patterns:
            if not os.path.isabs(pattern):
                pattern = os.path.join(self.root_dir, pattern)
                
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path) and file_path.endswith('.py'):
                    # Convert to relative path
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    
                    # Check if file matches any exclude pattern
                    excluded = False
                    for exclude in exclude_patterns:
                        if glob.fnmatch.fnmatch(rel_path, exclude):
                            excluded = True
                            break
                            
                    if not excluded:
                        python_files.append(rel_path)
                        
        return sorted(python_files)
        
    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Process a single Python file to extract its imports.
        
        Args:
            file_path: Path to the Python file (relative to root_dir)
            
        Returns:
            Dictionary with file info and extracted imports, or None if processing failed
        """
        abs_path = os.path.join(self.root_dir, file_path)
        
        try:
            # Parse the file to extract imports
            imports = parse_python_file(abs_path)
            
            if imports is None:
                return None
                
            # Create a node representing this file
            node_id = file_path
            node_data = {
                'id': node_id,
                'path': file_path,
                'type': 'python_module',
                'imports': imports
            }
            
            # Add the node to the dependency graph
            self.dependency_graph.add_node(node_id, node_data)
            
            # Process each import to resolve its path
            for imp in imports:
                try:
                    # Resolve the import to a file path
                    imp_type = imp['type']
                    module_name = imp['module']
                    
                    resolved_paths = self.path_resolver.resolve_import(module_name, from_file=file_path)
                    
                    if resolved_paths:
                        for resolved_path in resolved_paths:
                            # Only create edges for imports we can resolve to files in our project
                            if os.path.exists(os.path.join(self.root_dir, resolved_path)):
                                # Add an edge to represent the dependency
                                self.dependency_graph.add_edge(node_id, resolved_path, {
                                    'type': 'import',
                                    'import_type': imp_type,
                                    'line': imp.get('line', 0)
                                })
                    else:
                        # This is likely an external library import
                        logger.debug(f"Could not resolve import: {module_name} in {file_path}")
                except Exception as e:
                    self.exporter.add_error(
                        file_path=file_path,
                        error_type='resolution_error',
                        message=f"Failed to resolve import: {module_name}",
                        details=str(e)
                    )
            
            return node_data
            
        except Exception as e:
            self.exporter.add_error(
                file_path=file_path,
                error_type='process_error',
                message=f"Failed to process file",
                details=str(e)
            )
            return None
    
    def extract(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> DependencyGraph:
        """
        Extract dependencies from all Python files in the project.
        
        Args:
            include_patterns: List of glob patterns to include (default: ['**/*.py'])
            exclude_patterns: List of glob patterns to exclude (default: ['**/venv/**', '**/.git/**'])
            
        Returns:
            The populated dependency graph
        """
        logger.info(f"Starting Python dependency extraction from: {self.root_dir}")
        
        # Find all Python files
        python_files = self.find_python_files(include_patterns, exclude_patterns)
        logger.info(f"Found {len(python_files)} Python files to process")
        
        # Process each Python file
        for file_path in python_files:
            try:
                self.process_file(file_path)
            except Exception as e:
                self.exporter.add_error(
                    file_path=file_path,
                    error_type='extraction_error',
                    message=f"Unhandled error during extraction",
                    details=str(e)
                )
        
        logger.info(f"Dependency extraction complete. {len(self.dependency_graph.nodes)} nodes and {self.dependency_graph.edge_count()} edges found.")
        return self.dependency_graph
        
    def export(self, output_file: str = None) -> str:
        """
        Export the dependency graph to a JSON file.
        
        Args:
            output_file: Name of the output file (default: python_dependencies.json)
            
        Returns:
            Path to the generated JSON file
        """
        return self.exporter.export_dependency_graph(self.dependency_graph, output_file)


def extract_dependencies(root_dir: str, output_dir: str = None, output_file: str = None,
                        include_patterns: List[str] = None, exclude_patterns: List[str] = None) -> str:
    """
    Convenience function to extract Python dependencies from a project.
    
    Args:
        root_dir: Root directory of the Python project
        output_dir: Directory where output files will be saved (default: root_dir)
        output_file: Name of the output file (default: python_dependencies.json)
        include_patterns: List of glob patterns to include (default: ['**/*.py'])
        exclude_patterns: List of glob patterns to exclude (default: ['**/venv/**', '**/.git/**'])
        
    Returns:
        Path to the generated JSON file
    """
    extractor = PythonDependencyExtractor(root_dir, output_dir)
    extractor.extract(include_patterns, exclude_patterns)
    return extractor.export(output_file) 