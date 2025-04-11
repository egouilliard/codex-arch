"""
JSON Export and Error Handling Module.

This module exports Python dependency data to JSON format and provides
comprehensive error handling for the Python dependency extraction process.
"""

import os
import json
import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class DependencyExporter:
    """Exports Python dependency data to JSON format with error handling."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the exporter with an output directory.
        
        Args:
            output_dir: Directory where output files will be saved (default: current dir)
        """
        self.output_dir = output_dir or os.getcwd()
        self.errors: List[Dict[str, Any]] = []
        
    def add_error(self, file_path: str, error_type: str, message: str, details: Any = None) -> None:
        """
        Add an error to the error collection.
        
        Args:
            file_path: Path to the file where the error occurred
            error_type: Type of error (e.g., 'parse_error', 'resolution_error')
            message: Error message
            details: Additional error details (optional)
        """
        self.errors.append({
            'file_path': file_path,
            'error_type': error_type,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        logger.error(f"Error in {file_path}: {error_type} - {message}")

    def export_dependency_graph(self, dependency_graph: Any, output_file: str = None) -> str:
        """
        Export the dependency graph to a JSON file.
        
        Args:
            dependency_graph: The dependency graph object to export
            output_file: Name of the output file (default: python_dependencies.json)
            
        Returns:
            Path to the generated JSON file
        """
        if output_file is None:
            output_file = "python_dependencies.json"
            
        if not os.path.isabs(output_file):
            output_file = os.path.join(self.output_dir, output_file)
            
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create the export data structure
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0',
                'error_count': len(self.errors)
            },
            'graph': {
                'nodes': dependency_graph.nodes,
                'edges': dependency_graph.edges_list()
            },
            'errors': self.errors if self.errors else None
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, sort_keys=True)
            logger.info(f"Dependency graph exported to {output_file}")
            return output_file
        except Exception as e:
            error_msg = f"Failed to export dependency graph: {str(e)}"
            logger.error(error_msg)
            self.add_error('exporter', 'export_error', error_msg, str(e))
            raise

    def export_errors(self, output_file: str = None) -> Optional[str]:
        """
        Export only the errors to a separate JSON file.
        
        Args:
            output_file: Name of the output file (default: python_extraction_errors.json)
            
        Returns:
            Path to the generated JSON file or None if no errors
        """
        if not self.errors:
            logger.info("No errors to export")
            return None
            
        if output_file is None:
            output_file = "python_extraction_errors.json"
            
        if not os.path.isabs(output_file):
            output_file = os.path.join(self.output_dir, output_file)
            
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        export_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'version': '1.0',
                'error_count': len(self.errors)
            },
            'errors': self.errors
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, sort_keys=True)
            logger.info(f"Errors exported to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Failed to export errors: {str(e)}")
            # Don't add an error for failing to export errors to avoid potential recursion
            return None


class SafeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable objects safely."""
    
    def default(self, obj):
        """
        Convert non-serializable objects to serializable representations.
        
        Args:
            obj: Object to convert
            
        Returns:
            A serializable representation of the object
        """
        try:
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            elif hasattr(obj, '_asdict'):
                return obj._asdict()
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            else:
                return str(obj)
        except Exception:
            return f"<Unserializable object of type {type(obj).__name__}>" 