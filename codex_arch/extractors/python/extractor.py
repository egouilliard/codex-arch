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
    
    def __init__(self, root_dir: str, output_dir: str = None, debug: bool = False):
        """
        Initialize the Python dependency extractor.
        
        Args:
            root_dir: Root directory of the Python project
            output_dir: Directory where output files will be saved (default: root_dir)
            debug: Enable debug mode for verbose logging (default: False)
        """
        self.root_dir = os.path.abspath(root_dir)
        self.output_dir = output_dir or self.root_dir
        self.debug = debug
        
        # Enable debug logging if requested
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"PythonDependencyExtractor initialized with debug mode")
        
        self.path_resolver = ImportPathResolver(self.root_dir, debug=debug)
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
                    level = imp.get('level', 0)
                    
                    # Get a list of resolved paths using the enhanced resolver
                    resolved_paths = self.path_resolver.resolve_import_with_alternatives(
                        module_name, 
                        source_file=os.path.join(self.root_dir, file_path),
                        level=level
                    )
                    
                    if resolved_paths:
                        for resolved_path in resolved_paths:
                            # Only create edges for imports we can resolve to files in our project
                            if os.path.exists(os.path.join(self.root_dir, os.path.relpath(resolved_path, self.root_dir))):
                                # Convert absolute path to relative if needed
                                if os.path.isabs(resolved_path):
                                    resolved_path = os.path.relpath(resolved_path, self.root_dir)
                                
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
                    # Use improved error details
                    error_details = self.path_resolver.improve_error_details(
                        e, module_name, os.path.join(self.root_dir, file_path), level
                    )
                    
                    self.exporter.add_error(
                        file_path=file_path,
                        error_type='resolution_error',
                        message=f"Failed to resolve import: {module_name}",
                        details=str(error_details)
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
    
    def save_debug_info(self, output_file: str = None) -> None:
        """
        Save debug information to a file.
        
        Args:
            output_file: The file path to save debug info to (default: <output_dir>/path_resolution_debug.json)
        """
        if not self.debug:
            return
            
        if output_file is None:
            output_file = os.path.join(self.output_dir, "path_resolution_debug.json")
            
        self.path_resolver.save_debug_log(output_file)
        logger.debug(f"Saved path resolution debug info to {output_file}")
        
    def extract(self, include_patterns: List[str] = None, exclude_patterns: List[str] = None, 
                save_debug: bool = True) -> DependencyGraph:
        """
        Extract dependencies from all Python files in the project.
        
        Args:
            include_patterns: List of glob patterns to include (default: ['**/*.py'])
            exclude_patterns: List of glob patterns to exclude (default: ['**/venv/**', '**/.git/**'])
            save_debug: Whether to save debug information if debug mode is enabled (default: True)
            
        Returns:
            The populated dependency graph
        """
        logger.info(f"Starting Python dependency extraction from: {self.root_dir}")
        
        # Find all Python files
        python_files = self.find_python_files(include_patterns, exclude_patterns)
        logger.info(f"Found {len(python_files)} Python files to process")
        
        # Process each Python file
        processed_count = 0
        error_count = 0
        
        # Extract imports from files
        all_imports = {}
        for file_path in python_files:
            try:
                result = self.process_file(file_path)
                if result:
                    processed_count += 1
                    # Store the imports for later dependency mapping
                    all_imports[file_path] = result.get('imports', [])
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                self.exporter.add_error(
                    file_path=file_path,
                    error_type='extraction_error',
                    message=f"Unhandled error during extraction",
                    details=str(e)
                )
                
        # Build dependency mapping with error tracking
        try:
            from codex_arch.extractors.python.path_resolver import build_dependency_mapping
            logger.info("Building dependency mapping...")
            
            dependency_mapping = build_dependency_mapping(
                python_files, 
                all_imports, 
                self.root_dir,
                self.exporter
            )
            
            # Build the graph from the mapping
            from codex_arch.extractors.python.dependency_graph import build_graph_from_dependency_mapping
            logger.info("Building dependency graph...")
            
            # Use the enhanced error handling in the graph builder
            self.dependency_graph = build_graph_from_dependency_mapping(
                dependency_mapping,
                self.exporter
            )
        except Exception as e:
            self.exporter.add_error(
                file_path='dependency_mapping',
                error_type='mapping_error',
                message=f"Failed to build dependency mapping",
                details=str(e)
            )
            logger.error(f"Failed to build dependency mapping: {str(e)}")
        
        # Perform dependency analysis
        try:
            from codex_arch.extractors.python.dependency_graph import analyze_dependencies
            analysis_results = analyze_dependencies(self.dependency_graph, self.exporter)
            
            # Log the analysis results
            logger.info(f"Dependency analysis complete.")
            logger.info(f"Found {analysis_results['total_modules']} modules with {analysis_results['total_dependencies']} dependencies.")
            
            if analysis_results['has_cycles']:
                cycle_count = len(analysis_results['cycles'])
                logger.warning(f"Found {cycle_count} dependency cycles in the project.")
            
            # Record analysis results in the dependency graph for export
            self.dependency_graph.analysis_results = analysis_results
                
        except Exception as e:
            self.exporter.add_error(
                file_path='analysis',
                error_type='analysis_error',
                message=f"Failed to analyze dependency graph",
                details=str(e)
            )
            logger.error(f"Failed to analyze dependency graph: {str(e)}")
        
        logger.info(f"Dependency extraction complete. {len(self.dependency_graph.nodes)} nodes and {self.dependency_graph.edge_count()} edges found.")
        logger.info(f"Successfully processed {processed_count} files with {error_count} errors.")
        
        # Save debug info if requested
        if self.debug and save_debug:
            self.save_debug_info()
        
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
                      include_patterns: List[str] = None, exclude_patterns: List[str] = None,
                      debug: bool = False) -> str:
    """
    Extract dependencies from a Python project and export to JSON.
    
    This is a convenience function that wraps the PythonDependencyExtractor class.
    
    Args:
        root_dir: Root directory of the Python project
        output_dir: Directory where output files will be saved (default: root_dir)
        output_file: Filename for the output JSON file (default: 'python_dependencies.json')
        include_patterns: List of glob patterns to include (default: ['**/*.py'])
        exclude_patterns: List of glob patterns to exclude (default: ['**/venv/**', '**/.git/**'])
        debug: Enable debug mode for verbose logging (default: False)
        
    Returns:
        The path to the generated output file
    """
    output_dir = output_dir or root_dir
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    output_file = output_file or 'python_dependencies.json'
    output_path = os.path.join(output_dir, output_file)
    
    # Initialize and run the extractor
    extractor = PythonDependencyExtractor(root_dir, output_dir, debug=debug)
    extractor.extract(include_patterns, exclude_patterns)
    
    # Export the results to JSON
    return extractor.export(output_file) 