"""
Complexity Analyzer Module.

This module provides functionality to analyze code complexity for different
programming languages, with a special focus on Python code.
"""

import ast
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set

class ComplexityAnalyzer:
    """Analyzer for code complexity across different languages."""
    
    def __init__(
        self,
        max_file_size: int = 1024 * 1024  # Default 1MB limit for complexity analysis
    ):
        """
        Initialize the ComplexityAnalyzer.
        
        Args:
            max_file_size: Maximum file size in bytes to process for complexity analysis
        """
        self.max_file_size = max_file_size
        
    def analyze_file(
        self, 
        file_path: Union[str, Path], 
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze complexity metrics for a single file.
        
        Args:
            file_path: Path to the file
            language: Language of the file (if None, detected from extension)
            
        Returns:
            Dictionary with complexity metrics
        """
        file_path = Path(file_path)
        
        # Get file size and check if it's too large
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return {
                    "error": f"File too large for complexity analysis (size: {file_size} bytes)",
                    "metrics": {
                        "is_analyzable": False
                    }
                }
                
            # Detect language if not provided
            if language is None:
                extension = file_path.suffix.lower()
                language = self._detect_language(extension)
            
            # Choose appropriate analyzer based on language
            if language == "Python":
                metrics = self._analyze_python_file(file_path)
            else:
                # Default to basic complexity for other languages
                metrics = self._analyze_generic_file(file_path)
                
            return {
                "file": str(file_path),
                "language": language,
                "metrics": metrics
            }
            
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "metrics": {
                    "is_analyzable": False
                }
            }
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        extension = extension.lower()
        
        if extension in ('.py', '.pyw', '.pyx'):
            return "Python"
        elif extension in ('.js', '.jsx', '.mjs'):
            return "JavaScript"
        elif extension in ('.ts', '.tsx'):
            return "TypeScript"
        elif extension in ('.java'):
            return "Java"
        elif extension in ('.c', '.h'):
            return "C"
        elif extension in ('.cpp', '.hpp', '.cc', '.hh'):
            return "C++"
        elif extension in ('.go'):
            return "Go"
        elif extension in ('.rb'):
            return "Ruby"
        elif extension in ('.php'):
            return "PHP"
        else:
            return "Other"
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze complexity metrics for a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with Python-specific complexity metrics
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the abstract syntax tree
            tree = ast.parse(content)
            
            # Extract metrics using AST
            metrics = {
                "is_analyzable": True,
                "total_lines": len(content.splitlines()),
                "non_empty_lines": len([line for line in content.splitlines() if line.strip()]),
                "complexity": {
                    "functions": [],
                    "classes": [],
                    "total_functions": 0,
                    "total_classes": 0,
                    "average_function_complexity": 0,
                    "max_function_complexity": 0,
                    "total_complexity": 0
                }
            }
            
            # Extract functions and classes
            functions = []
            classes = []
            
            # Visit each node in the tree
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_complexity = self._calculate_function_complexity(node)
                    func_info = {
                        "name": node.name,
                        "lineno": node.lineno,
                        "complexity": func_complexity,
                        "parameters": len(node.args.args),
                        "is_method": self._is_method(node)
                    }
                    functions.append(func_info)
                    metrics["complexity"]["total_complexity"] += func_complexity
                
                elif isinstance(node, ast.ClassDef):
                    class_methods = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    class_complexity = self._calculate_class_complexity(node)
                    class_info = {
                        "name": node.name,
                        "lineno": node.lineno,
                        "methods": class_methods,
                        "complexity": class_complexity
                    }
                    classes.append(class_info)
                    metrics["complexity"]["total_complexity"] += class_complexity
            
            # Calculate statistics
            metrics["complexity"]["functions"] = sorted(functions, key=lambda x: x["complexity"], reverse=True)
            metrics["complexity"]["classes"] = sorted(classes, key=lambda x: x["complexity"], reverse=True)
            metrics["complexity"]["total_functions"] = len(functions)
            metrics["complexity"]["total_classes"] = len(classes)
            
            if functions:
                metrics["complexity"]["average_function_complexity"] = round(
                    sum(func["complexity"] for func in functions) / len(functions), 2
                )
                metrics["complexity"]["max_function_complexity"] = max(
                    func["complexity"] for func in functions
                )
            
            # Calculate comment metrics
            comment_metrics = self._analyze_python_comments(content)
            metrics.update(comment_metrics)
            
            return metrics
            
        except SyntaxError as e:
            return {
                "is_analyzable": False,
                "error": f"Syntax error: {str(e)}"
            }
        except Exception as e:
            return {
                "is_analyzable": False,
                "error": str(e)
            }
    
    def _analyze_generic_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze basic complexity metrics for any file type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with basic complexity metrics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            
            # Calculate line-based metrics
            metrics = {
                "is_analyzable": True,
                "total_lines": len(lines),
                "non_empty_lines": len(non_empty_lines),
                "average_line_length": round(
                    sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
                    if non_empty_lines else 0, 2
                ),
                "max_line_length": max(len(line) for line in lines) if lines else 0,
                "complexity_estimate": {
                    "nesting_depth": self._estimate_nesting_depth(content),
                    "branches": self._estimate_branches(content)
                }
            }
            
            return metrics
            
        except Exception as e:
            return {
                "is_analyzable": False,
                "error": str(e)
            }
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate cyclomatic complexity of a function.
        
        Cyclomatic complexity is calculated as:
        1 + <number of branches>
        
        Branches include: if, elif, for, while, and, or, try, except, with
        
        Args:
            node: AST node for the function
            
        Returns:
            Cyclomatic complexity score
        """
        complexity = 1  # Base complexity for the function
        
        # Walk through the function's AST
        for child in ast.walk(node):
            # Control flow structures that increase complexity
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
            # Boolean operations also increase complexity
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # Return statements within a function (excluding the last one)
            elif isinstance(child, ast.Return):
                complexity += 1
                
        return complexity
    
    def _calculate_class_complexity(self, node: ast.ClassDef) -> int:
        """
        Calculate complexity of a class.
        
        Class complexity is calculated as:
        1 + sum(method complexities)
        
        Args:
            node: AST node for the class
            
        Returns:
            Complexity score for the class
        """
        complexity = 1  # Base complexity for the class
        
        # Add complexity for each method
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                complexity += self._calculate_function_complexity(child)
                
        return complexity
    
    def _is_method(self, node: ast.FunctionDef) -> bool:
        """
        Determine if a function is a method within a class.
        
        Args:
            node: AST node for the function
            
        Returns:
            True if the function is a method, False otherwise
        """
        # Check if the function has 'self' as its first parameter
        return (node.args.args and 
                node.args.args[0].arg == 'self')
    
    def _analyze_python_comments(self, content: str) -> Dict[str, Any]:
        """
        Analyze comments in Python code.
        
        Args:
            content: Python source code as a string
            
        Returns:
            Dictionary with comment metrics
        """
        lines = content.splitlines()
        
        # Regular expressions for different comment types
        inline_comment_pattern = re.compile(r'[^#"\']*#[^"\']*$')
        docstring_start_pattern = re.compile(r'^\s*(?:\'\'\'|""")')
        
        # Initialize metrics
        metrics = {
            "comments": {
                "total_comments": 0,
                "comment_lines": 0,
                "docstring_lines": 0,
                "comment_ratio": 0
            }
        }
        
        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx]
            
            # Check for docstrings
            if docstring_start_pattern.search(line):
                # Extract the docstring delimiter
                delimiter = '"""' if '"""' in line else "'''"
                end_idx = line_idx
                
                # Handle single-line docstrings
                if line.count(delimiter) >= 2:
                    metrics["comments"]["docstring_lines"] += 1
                    metrics["comments"]["total_comments"] += 1
                else:
                    # Multi-line docstring - find the end
                    while end_idx < len(lines) and delimiter not in lines[end_idx][lines[end_idx].find(delimiter) + 3:]:
                        metrics["comments"]["docstring_lines"] += 1
                        end_idx += 1
                        
                    # Count the end line if found
                    if end_idx < len(lines):
                        metrics["comments"]["docstring_lines"] += 1
                    
                    metrics["comments"]["total_comments"] += 1
                    line_idx = end_idx
            
            # Check for inline comments
            elif inline_comment_pattern.search(line):
                metrics["comments"]["comment_lines"] += 1
                metrics["comments"]["total_comments"] += 1
            
            line_idx += 1
        
        # Calculate ratio
        total_lines = len(lines)
        if total_lines > 0:
            total_comment_lines = metrics["comments"]["comment_lines"] + metrics["comments"]["docstring_lines"]
            metrics["comments"]["comment_ratio"] = round(total_comment_lines / total_lines * 100, 2)
        
        return metrics
    
    def _estimate_nesting_depth(self, content: str) -> int:
        """
        Estimate the maximum nesting depth of code blocks.
        This is a basic heuristic that counts indentation levels.
        
        Args:
            content: Source code as a string
            
        Returns:
            Estimated maximum nesting depth
        """
        lines = content.splitlines()
        max_indent = 0
        
        for line in lines:
            if line.strip():  # Skip empty lines
                # Count leading spaces/tabs
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent)
        
        # Approximate depth based on indentation
        # Assuming 2-4 spaces or 1 tab per indentation level
        estimated_depth = max(1, max_indent // 2)
        return min(estimated_depth, 10)  # Cap at 10 to avoid extreme values
    
    def _estimate_branches(self, content: str) -> int:
        """
        Estimate the number of branching points in code.
        This is a basic heuristic that counts keywords like if, for, while, etc.
        
        Args:
            content: Source code as a string
            
        Returns:
            Estimated number of branches
        """
        # Common branching keywords in many languages
        branch_keywords = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bfor\b', r'\bwhile\b', 
            r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\btry\b'
        ]
        
        branch_count = 0
        for keyword in branch_keywords:
            branch_count += len(re.findall(keyword, content))
        
        return branch_count 