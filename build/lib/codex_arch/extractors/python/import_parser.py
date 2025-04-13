"""
Import Parser Module.

This module uses Python's ast module to parse Python files and extract import statements.
It handles both 'import' and 'from ... import' statements.
"""

import ast
import os
import logging
from typing import Dict, List, Set, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class ImportVisitor(ast.NodeVisitor):
    """AST visitor that collects import statements from Python files."""
    
    def __init__(self):
        self.imports: List[Dict[str, Any]] = []
        self._current_line = 0
    
    def visit_Import(self, node: ast.Import) -> None:
        """Process regular import statements (import x, import y)."""
        for name in node.names:
            self.imports.append({
                'type': 'import',
                'module': name.name,
                'alias': name.asname,
                'line': node.lineno,
                'col': node.col_offset
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from-import statements (from x import y)."""
        module = node.module
        level = node.level  # Level indicates relative import depth (. = 1, .. = 2)
        
        for name in node.names:
            self.imports.append({
                'type': 'from',
                'module': module,
                'name': name.name,
                'alias': name.asname,
                'level': level,
                'line': node.lineno,
                'col': node.col_offset
            })
        self.generic_visit(node)


def parse_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a Python file and extract all import statements.
    
    Args:
        file_path: Path to the Python file to parse
        
    Returns:
        List of dictionaries containing import information
        
    Raises:
        SyntaxError: If the file contains invalid Python syntax
        FileNotFoundError: If the file does not exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code, filename=file_path)
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        return visitor.imports
    
    except SyntaxError as e:
        logger.error(f"Syntax error in {file_path}: {str(e)}")
        raise
    
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    
    except Exception as e:
        logger.error(f"Error parsing {file_path}: {str(e)}")
        raise

# Add alias for compatibility with other modules
parse_python_file = parse_file


def extract_imports_from_files(file_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract imports from multiple Python files.
    
    Args:
        file_paths: List of Python file paths to process
        
    Returns:
        Dictionary mapping file paths to lists of import information
    """
    result = {}
    
    for file_path in file_paths:
        try:
            if os.path.isfile(file_path) and file_path.endswith('.py'):
                imports = parse_file(file_path)
                if imports:
                    # Store using normalized path for consistency
                    normalized_path = os.path.normpath(file_path)
                    result[normalized_path] = imports
        except Exception as e:
            logger.warning(f"Failed to extract imports from {file_path}: {str(e)}")
    
    return result


def classify_imports(imports: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Classify imports into standard library, third-party, and local imports.
    
    Args:
        imports: List of import dictionaries from parse_file
        
    Returns:
        Dictionary with keys 'standard_lib', 'third_party', and 'local' mapping to
        lists of import dictionaries
    """
    stdlib_modules = set(sys.stdlib_module_names)
    
    result = {
        'standard_lib': [],
        'third_party': [],
        'local': []
    }
    
    for imp in imports:
        if imp['type'] == 'import':
            # For direct imports, check the root module name
            root_module = imp['module'].split('.')[0]
            if root_module in stdlib_modules:
                result['standard_lib'].append(imp)
            else:
                # This is a heuristic - we can't perfectly distinguish third-party from local
                # without analyzing the project structure
                result['third_party'].append(imp)
        elif imp['type'] == 'from':
            if imp['level'] > 0:
                # Relative imports are always local
                result['local'].append(imp)
            else:
                # For absolute imports, check if it's a standard library module
                module = imp['module']
                if module and module.split('.')[0] in stdlib_modules:
                    result['standard_lib'].append(imp)
                else:
                    result['third_party'].append(imp)
    
    return result


# Patch the missing import
import sys
try:
    # Python 3.10+ has this attribute
    sys.stdlib_module_names
except AttributeError:
    # For older Python versions, use a static list of common stdlib modules
    # This is not exhaustive but covers the most common ones
    sys.stdlib_module_names = {
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'contextlib',
        'copy', 'csv', 'datetime', 'decimal', 'functools', 'glob', 'gzip', 'hashlib',
        'importlib', 'inspect', 'io', 'itertools', 'json', 'logging', 'math', 'os',
        'pathlib', 'pickle', 'random', 're', 'shutil', 'socket', 'sqlite3', 'string',
        'struct', 'subprocess', 'sys', 'tempfile', 'threading', 'time', 'traceback',
        'typing', 'urllib', 'uuid', 'warnings', 'xml', 'zipfile'
    } 