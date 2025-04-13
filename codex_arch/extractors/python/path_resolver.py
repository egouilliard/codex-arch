"""
Import Path Resolution Module.

This module resolves Python import statements to actual file paths in the repository.
It handles both absolute and relative imports, supporting various Python project structures.

Key features:
- Resolution of absolute imports by searching in sys.path
- Resolution of relative imports by level (e.g., from . import x, from .. import y)
- Support for package resolution using __init__.py files
- Support for PEP 420 namespace packages
- Alternative resolution strategies for common project structures
- Detailed error reporting for better debugging of resolution issues
"""

import os
import sys
import logging
import json
from typing import Dict, List, Set, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class ImportPathResolver:
    """Resolves Python import paths to actual files in the repository."""
    
    def __init__(self, root_dir: str, python_ext: str = '.py', debug: bool = False):
        """
        Initialize the resolver with a root directory.
        
        Args:
            root_dir: The root directory of the Python project
            python_ext: The file extension for Python files (default: '.py')
            debug: Enable debug mode for verbose logging (default: False)
        """
        self.root_dir = os.path.abspath(root_dir)
        self.python_ext = python_ext
        self.debug = debug
        self.sys_path = list(sys.path)
        
        # Add the root directory to the front of the path resolution list
        if self.root_dir not in self.sys_path:
            self.sys_path.insert(0, self.root_dir)
        
        # Cache for resolved paths
        self._path_cache: Dict[str, List[str]] = {}
        
        # Debug log for resolution attempts
        self.debug_log = [] if debug else None
        
        if debug:
            logger.setLevel(logging.DEBUG)
            logger.debug(f"Initialized ImportPathResolver with root_dir={self.root_dir}")
            logger.debug(f"sys.path for resolution: {self.sys_path}")
    
    def _log_debug(self, message: str, context: Dict[str, Any] = None) -> None:
        """
        Log a debug message if debug mode is enabled.
        
        Args:
            message: The debug message to log
            context: Additional context information
        """
        if not self.debug:
            return
            
        log_entry = {
            'message': message,
            'context': context or {}
        }
        
        # Add to in-memory debug log
        if self.debug_log is not None:
            self.debug_log.append(log_entry)
            
        # Also log to the logger
        if context:
            logger.debug(f"{message} - {json.dumps(context)}")
        else:
            logger.debug(message)
    
    def save_debug_log(self, output_file: str) -> None:
        """
        Save the debug log to a file.
        
        Args:
            output_file: The file path to save the debug log to
        """
        if not self.debug or not self.debug_log:
            return
            
        try:
            with open(output_file, 'w') as f:
                json.dump(self.debug_log, f, indent=2)
            logger.info(f"Saved debug log to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save debug log: {str(e)}")
            
    def resolve_import(self, import_name: str, source_file: str = None, level: int = 0) -> List[str]:
        """
        Resolves an import to actual file paths.
        
        Args:
            import_name: The import name to resolve (e.g., 'package.module')
            source_file: The file containing the import (for relative imports)
            level: The level of relative import (0 for absolute, >= 1 for relative)
            
        Returns:
            List of resolved file paths, empty list if none found
        """
        # Generate a cache key to avoid redundant resolution
        cache_key = f"{import_name}:{source_file}:{level}"
        
        self._log_debug(f"Resolving import", {
            'import_name': import_name,
            'source_file': source_file,
            'level': level,
            'cache_key': cache_key
        })
        
        if cache_key in self._path_cache:
            self._log_debug(f"Found in cache", {'cache_key': cache_key, 'result': self._path_cache[cache_key]})
            return self._path_cache[cache_key]
        
        try:
            resolved_paths = []
            
            if level > 0:
                # Handle relative imports
                if not source_file:
                    logger.warning(f"Cannot resolve relative import {import_name} without source file")
                    self._log_debug("Relative import missing source file", {'import_name': import_name, 'level': level})
                    return []
                
                # Get the directory of the source file
                source_dir = os.path.dirname(os.path.abspath(source_file))
                
                # Go up 'level' directories
                original_source_dir = source_dir
                for i in range(level - 1):
                    source_dir = os.path.dirname(source_dir)
                    self._log_debug(f"Relative import level {i+1}", {'path': source_dir})
                
                # Calculate the relative import path
                if import_name:
                    module_path = os.path.join(source_dir, *import_name.split('.'))
                else:
                    # For "from . import x" cases
                    module_path = source_dir
                
                self._log_debug("Checking relative module path", {'module_path': module_path})
                path = self._find_module_path(module_path)
                if path:
                    resolved_paths.append(path)
            else:
                # Handle absolute imports, search in sys.path order
                self._log_debug("Resolving absolute import", {'import_name': import_name})
                for path in self.sys_path:
                    module_path = os.path.join(path, *import_name.split('.'))
                    self._log_debug("Checking path", {'module_path': module_path})
                    result = self._find_module_path(module_path)
                    if result:
                        self._log_debug("Found module", {'result': result})
                        resolved_paths.append(result)
                        # Don't break here - collect all matching paths
            
            # Cache the result
            self._path_cache[cache_key] = resolved_paths
            self._log_debug("Resolution result", {'import_name': import_name, 'paths': resolved_paths})
            return resolved_paths
        
        except Exception as e:
            logger.error(f"Error resolving import {import_name}: {str(e)}")
            self._log_debug("Resolution error", {'import_name': import_name, 'error': str(e)})
            return []
    
    def _find_module_path(self, module_path: str) -> Optional[str]:
        """
        Find the actual file path for a module.
        
        This handles both direct file matches and __init__.py files in packages.
        
        Args:
            module_path: The filesystem path to check
            
        Returns:
            The resolved file path, or None if not found
        """
        self._log_debug("Finding module path", {'module_path': module_path})
        
        # Check for direct .py file
        py_path = f"{module_path}{self.python_ext}"
        if os.path.isfile(py_path):
            self._log_debug("Found direct Python file", {'path': py_path})
            return py_path
        
        # Check for package (__init__.py)
        init_path = os.path.join(module_path, f"__init__{self.python_ext}")
        if os.path.isfile(init_path):
            self._log_debug("Found package __init__.py", {'path': init_path})
            return init_path
        
        # Check for PEP 420 namespace packages (directories without __init__.py)
        if os.path.isdir(module_path):
            self._log_debug("Checking for namespace package", {'dir': module_path})
            # Look for any Python files in the directory to confirm it's a namespace package
            for item in os.listdir(module_path):
                if item.endswith(self.python_ext) and os.path.isfile(os.path.join(module_path, item)):
                    # Return the directory as the namespace package
                    self._log_debug("Found namespace package", {'dir': module_path, 'file': item})
                    return module_path
        
        # Last resort: check for .pyd, .so, .pyc extensions for binary modules
        for ext in ['.pyd', '.so', '.pyc']:
            bin_path = f"{module_path}{ext}"
            if os.path.isfile(bin_path):
                self._log_debug("Found binary module", {'path': bin_path})
                return bin_path
        
        self._log_debug("Module path not found", {'module_path': module_path})
        return None
    
    def resolve_import_with_alternatives(self, import_name: str, source_file: str = None, level: int = 0) -> List[str]:
        """
        More robust import resolution that tries alternative module path patterns.
        
        Args:
            import_name: The import name to resolve (e.g., 'package.module')
            source_file: The file containing the import (for relative imports)
            level: The level of relative import (0 for absolute, >= 1 for relative)
            
        Returns:
            List of resolved file paths, empty list if none found
        """
        # Try standard resolution first
        paths = self.resolve_import(import_name, source_file, level)
        if paths:
            return paths
            
        # If standard resolution fails, try some common Python project structures
        if level == 0 and import_name and '.' in import_name:
            alt_paths = []
            
            # Handle src/package/module pattern common in many projects
            parts = import_name.split('.')
            if len(parts) >= 2:
                # Try with 'src' prefix
                src_path = os.path.join(self.root_dir, 'src', *parts)
                src_result = self._find_module_path(src_path)
                if src_result:
                    alt_paths.append(src_result)
                
                # Try with main module name removed (for projects where imports don't include the top package)
                partial_path = os.path.join(self.root_dir, *parts[1:])
                partial_result = self._find_module_path(partial_path)
                if partial_result:
                    alt_paths.append(partial_result)
            
            return alt_paths
            
        return []

    def improve_error_details(self, error: Exception, import_name: str, source_file: str = None, level: int = 0) -> Dict[str, Any]:
        """
        Create detailed error information for import resolution failures.
        
        Args:
            error: The exception that occurred
            import_name: The import name that failed to resolve
            source_file: The file containing the import
            level: The level of relative import
            
        Returns:
            Dictionary with detailed error information
        """
        details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'import_name': import_name,
            'source_file': source_file,
            'level': level,
            'context': {}
        }
        
        # Add additional context information
        if source_file:
            details['context']['source_dir'] = os.path.dirname(os.path.abspath(source_file))
            
        if level > 0:
            # For relative imports, show the calculated base path
            source_dir = os.path.dirname(os.path.abspath(source_file)) if source_file else None
            if source_dir:
                for _ in range(level - 1):
                    source_dir = os.path.dirname(source_dir)
                details['context']['relative_base_dir'] = source_dir
        
        # For absolute imports, show the sys.path that was used
        if level == 0:
            details['context']['sys_paths_checked'] = self.sys_path
            
        return details
    
    def resolve_imports_in_file(self, file_path: str, imports: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Resolve all imports found in a file.
        
        Args:
            file_path: The path to the file containing the imports
            imports: List of import dictionaries from the import_parser module
            
        Returns:
            Dictionary mapping import specifiers to lists of resolved file paths
        """
        result = {}
        
        for imp in imports:
            try:
                if imp['type'] == 'import':
                    module_name = imp['module']
                    resolved_paths = self.resolve_import(module_name, file_path, 0)
                    result[module_name] = resolved_paths
                    
                elif imp['type'] == 'from':
                    module_name = imp['module'] or ''  # Handle 'from . import x' case
                    level = imp.get('level', 0)
                    
                    # Validate level (must be non-negative)
                    if level < 0:
                        logger.warning(f"Invalid import level {level} in {file_path} for module {module_name}")
                        level = 0
                        
                    resolved_paths = self.resolve_import(module_name, file_path, level)
                    
                    if module_name:
                        import_key = f"{'.' * level}{module_name}"
                    else:
                        import_key = '.' * level
                        
                    result[import_key] = resolved_paths
                else:
                    # Unknown import type
                    logger.warning(f"Unknown import type '{imp.get('type', 'unknown')}' in {file_path}")
                    
            except Exception as e:
                import_repr = f"{imp.get('type', 'unknown')} {imp.get('module', '?')}"
                logger.error(f"Error resolving import {import_repr} in {file_path}: {str(e)}")
                
                # Still add an entry to the result, but with an empty list as the resolved path
                if imp.get('type') == 'import':
                    result[imp.get('module', f"unknown_import_{len(result)}")] = []
                elif imp.get('type') == 'from':
                    module = imp.get('module', '')
                    level = imp.get('level', 0)
                    if module:
                        import_key = f"{'.' * level}{module}"
                    else:
                        import_key = '.' * level
                    result[import_key] = []
        
        return result


def build_dependency_mapping(
    file_paths: List[str], 
    imports_by_file: Dict[str, List[Dict[str, Any]]],
    root_dir: str,
    exporter=None
) -> Dict[str, Dict[str, Any]]:
    """
    Build a mapping of files to their dependencies.
    
    Args:
        file_paths: List of Python file paths
        imports_by_file: Dictionary mapping file paths to their imports
        root_dir: Root directory of the project
        exporter: Optional DependencyExporter for recording errors (default: None)
        
    Returns:
        Dictionary mapping file paths to their resolved dependencies
    """
    resolver = ImportPathResolver(root_dir)
    result = {}
    
    for file_path in file_paths:
        if file_path in imports_by_file and imports_by_file[file_path]:
            imports = imports_by_file[file_path]
            
            try:
                resolved_imports = resolver.resolve_imports_in_file(file_path, imports)
                
                # Store with additional metadata
                result[file_path] = {
                    'dependencies': resolved_imports,
                    'import_details': imports
                }
                
                # Check for unresolved imports
                unresolved_imports = []
                for imp_name, paths in resolved_imports.items():
                    if not paths:  # Empty list means unresolved
                        unresolved_imports.append(imp_name)
                
                if unresolved_imports and exporter:
                    exporter.add_error(
                        file_path=file_path,
                        error_type='unresolved_imports',
                        message=f"File has {len(unresolved_imports)} unresolved imports",
                        details=f"Unresolved imports: {unresolved_imports}"
                    )
                    
            except Exception as e:
                if exporter:
                    exporter.add_error(
                        file_path=file_path,
                        error_type='dependency_mapping_error',
                        message=f"Failed to build dependency mapping",
                        details=str(e)
                    )
                logger.error(f"Error building dependency mapping for {file_path}: {str(e)}")
                
                # Include partial results if possible
                result[file_path] = {
                    'dependencies': {},
                    'import_details': imports,
                    'error': str(e)
                }
    
    return result 