"""
File Tree Extractor Module

This module provides functionality to traverse a directory structure and generate
a hierarchical representation of the file tree, with output options for both
JSON and Markdown formats.
"""

import os
import json
import re
import pathlib
from pathlib import Path
from typing import Dict, List, Set, Union, Optional, Any, Callable, Pattern, TextIO, Tuple
import io


class FileTreeExtractor:
    """A class to extract and generate file tree representations from a directory."""
    
    def __init__(
        self,
        root_path: Union[str, Path],
        max_depth: Optional[int] = None,
        exclude_dirs: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        exclude_extensions: Optional[List[str]] = None,
        include_extensions: Optional[List[str]] = None,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
    ):
        """
        Initialize the FileTreeExtractor with configuration options.
        
        Args:
            root_path: Path to the root directory to traverse
            max_depth: Maximum depth to traverse (None for unlimited)
            exclude_dirs: List of directory names to exclude (e.g., ['.git', 'node_modules'])
            exclude_patterns: List of regex patterns to exclude files and directories
            exclude_extensions: List of file extensions to exclude (e.g., ['.pyc', '.log'])
            include_extensions: List of file extensions to include (if specified, all others are excluded)
            include_hidden: Whether to include hidden files and directories
            follow_symlinks: Whether to follow symbolic links
        """
        self.root_path = Path(root_path).resolve()
        self.max_depth = max_depth
        self.exclude_dirs = exclude_dirs or ['.git', 'node_modules', '__pycache__', 'venv', '.env']
        self.exclude_patterns = [re.compile(pattern) for pattern in (exclude_patterns or [])]
        self.exclude_extensions = [ext.lower() if ext.startswith('.') else f'.{ext}'.lower() for ext in (exclude_extensions or [])]
        self.include_extensions = [ext.lower() if ext.startswith('.') else f'.{ext}'.lower() for ext in (include_extensions or [])]
        self.include_hidden = include_hidden
        self.follow_symlinks = follow_symlinks
        
        if not self.root_path.exists():
            raise FileNotFoundError(f"Directory not found: {self.root_path}")
            
    def should_include_dir(self, dir_path: Path) -> bool:
        """Determine if a directory should be included based on filters."""
        # Check for hidden directories
        if not self.include_hidden and dir_path.name.startswith('.') and dir_path.name != '.':
            return False
            
        # Check for excluded directory names
        if dir_path.name in self.exclude_dirs:
            return False
            
        # Check for pattern exclusions
        rel_path = str(dir_path.relative_to(self.root_path))
        for pattern in self.exclude_patterns:
            if pattern.search(rel_path) or pattern.search(dir_path.name):
                return False
                
        return True
    
    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included based on filters."""
        # Check for hidden files
        if not self.include_hidden and file_path.name.startswith('.'):
            return False
            
        extension = file_path.suffix.lower()
        
        # Check for pattern exclusions
        rel_path = str(file_path.relative_to(self.root_path))
        for pattern in self.exclude_patterns:
            if pattern.search(rel_path) or pattern.search(file_path.name):
                return False
        
        # If include_extensions is specified, only include files with those extensions
        if self.include_extensions:
            return extension in self.include_extensions
            
        # Otherwise, exclude files with excluded extensions
        return extension not in self.exclude_extensions
    
    def extract(self) -> Dict[str, Any]:
        """
        Extract the file tree structure starting from the root path.
        
        Returns:
            A dictionary representing the hierarchical file tree
        """
        if self.root_path.is_file():
            return {
                "name": self.root_path.name,
                "path": str(self.root_path),
                "type": "file",
                "size": self.root_path.stat().st_size,
                "extension": self.root_path.suffix
            }
        
        result = {
            "name": self.root_path.name or str(self.root_path),
            "path": str(self.root_path),
            "type": "directory",
            "children": []
        }
        
        self._traverse_recursive(self.root_path, result)
        return result
    
    def extract_tree(self) -> Dict[str, Any]:
        """
        Alias for extract() method to maintain backward compatibility.
        
        Returns:
            A dictionary representing the hierarchical file tree
        """
        return self.extract()
        
    def _traverse_recursive(self, current_path: Path, current_node: Dict[str, Any], current_depth: int = 0) -> None:
        """Recursively traverse the directory structure."""
        # Check depth limit
        if self.max_depth is not None and current_depth >= self.max_depth:
            return
        
        # Get all items in the current directory
        try:
            items = list(current_path.iterdir())
        except (PermissionError, OSError) as e:
            current_node["error"] = str(e)
            return
            
        # Sort items: directories first, then files, both alphabetically
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for item in items:
            try:
                # Handle symlinks
                is_symlink = item.is_symlink()
                if is_symlink and not self.follow_symlinks:
                    continue
                
                if item.is_dir():
                    if self.should_include_dir(item):
                        dir_node = {
                            "name": item.name,
                            "path": str(item),
                            "type": "directory",
                            "children": []
                        }
                        if is_symlink:
                            dir_node["symlink"] = True
                            dir_node["target"] = str(item.resolve())
                            
                        current_node["children"].append(dir_node)
                        self._traverse_recursive(item, dir_node, current_depth + 1)
                else:  # It's a file
                    if self.should_include_file(item):
                        try:
                            size = item.stat().st_size
                        except (PermissionError, OSError):
                            size = 0
                            
                        file_node = {
                            "name": item.name,
                            "path": str(item),
                            "type": "file",
                            "size": size,
                            "extension": item.suffix
                        }
                        
                        if is_symlink:
                            file_node["symlink"] = True
                            file_node["target"] = str(item.resolve())
                            
                        current_node["children"].append(file_node)
            except (PermissionError, OSError) as e:
                # Add error node for items we can't access
                error_node = {
                    "name": item.name,
                    "path": str(item),
                    "type": "error",
                    "error": str(e)
                }
                current_node["children"].append(error_node)
    
    def to_json(
        self, 
        output_file: Optional[Union[str, Path, TextIO]] = None, 
        indent: int = 2
    ) -> Optional[str]:
        """
        Generate a JSON representation of the file tree.
        
        Args:
            output_file: Optional file path or file-like object to write JSON to.
                         If None, returns the JSON as a string.
            indent: Number of spaces for indentation in the JSON output
            
        Returns:
            If output_file is None, returns the JSON string representation.
            Otherwise, writes to the specified file and returns None.
        """
        tree_data = self.extract()
        
        if output_file is None:
            return json.dumps(tree_data, indent=indent, ensure_ascii=False)
        
        # Handle file path or file-like object
        if isinstance(output_file, (str, Path)):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tree_data, f, indent=indent, ensure_ascii=False)
        else:
            # Assume file-like object
            json.dump(tree_data, output_file, indent=indent, ensure_ascii=False)
        
        return None
    
    def generate_json(
        self, 
        output_file: Optional[Union[str, Path, TextIO]] = None, 
        indent: int = 2,
        include_metadata: bool = True
    ) -> Optional[str]:
        """
        Generate a JSON representation of the file tree with optional metadata.
        
        Args:
            output_file: Optional file path or file-like object to write JSON to.
                         If None, returns the JSON as a string.
            indent: Number of spaces for indentation in the JSON output
            include_metadata: Whether to include metadata about the extraction
            
        Returns:
            If output_file is None, returns the JSON string representation.
            Otherwise, writes to the specified file and returns None.
        """
        tree_data = self.extract()
        
        # Add metadata if requested
        if include_metadata:
            result = {
                "metadata": {
                    "root_path": str(self.root_path),
                    "extracted_at": self._get_timestamp(),
                    "config": {
                        "max_depth": self.max_depth,
                        "exclude_dirs": self.exclude_dirs,
                        "exclude_patterns": [pattern.pattern for pattern in self.exclude_patterns],
                        "exclude_extensions": self.exclude_extensions,
                        "include_extensions": self.include_extensions,
                        "include_hidden": self.include_hidden,
                        "follow_symlinks": self.follow_symlinks
                    }
                },
                "tree": tree_data
            }
        else:
            result = tree_data
        
        if output_file is None:
            return json.dumps(result, indent=indent, ensure_ascii=False)
        
        # Handle file path or file-like object
        if isinstance(output_file, (str, Path)):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=indent, ensure_ascii=False)
        else:
            # Assume file-like object
            json.dump(result, output_file, indent=indent, ensure_ascii=False)
        
        return None
    
    def to_markdown(
        self,
        output_file: Optional[Union[str, Path, TextIO]] = None,
        include_size: bool = True,
        include_header: bool = True,
        use_emoji: bool = True,
        relative_paths: bool = False,
        indent_size: int = 2
    ) -> Optional[str]:
        """
        Generate a Markdown representation of the file tree.
        
        Args:
            output_file: Optional file path or file-like object to write Markdown to.
                         If None, returns the Markdown as a string.
            include_size: Whether to include file size information
            include_header: Whether to include a header with information about the extraction
            use_emoji: Whether to use emoji icons for files and directories
            relative_paths: Whether to display paths relative to the root path
            indent_size: Number of spaces for each level of indentation
            
        Returns:
            If output_file is None, returns the Markdown string representation.
            Otherwise, writes to the specified file and returns None.
        """
        # Get the file tree
        tree_data = self.extract()
        
        # Setup output
        if output_file is None:
            output = io.StringIO()
        elif isinstance(output_file, (str, Path)):
            output = open(output_file, 'w', encoding='utf-8')
        else:
            # Assume file-like object
            output = output_file
        
        # Write header if requested
        if include_header:
            root_name = self.root_path.name or str(self.root_path)
            output.write(f"# File Tree: {root_name}\n\n")
            output.write(f"Generated on: {self._get_timestamp()}\n\n")
            
            # Add configuration information
            output.write("**Configuration:**\n\n")
            output.write(f"- Root path: `{self.root_path}`\n")
            if self.max_depth is not None:
                output.write(f"- Max depth: {self.max_depth}\n")
            if self.exclude_dirs:
                output.write(f"- Excluded directories: {', '.join(f'`{d}`' for d in self.exclude_dirs)}\n")
            if self.exclude_patterns:
                output.write(f"- Excluded patterns: {', '.join(f'`{p.pattern}`' for p in self.exclude_patterns)}\n")
            if self.exclude_extensions:
                output.write(f"- Excluded extensions: {', '.join(f'`{e}`' for e in self.exclude_extensions)}\n")
            if self.include_extensions:
                output.write(f"- Included extensions: {', '.join(f'`{e}`' for e in self.include_extensions)}\n")
            output.write(f"- Include hidden files: {self.include_hidden}\n")
            output.write(f"- Follow symlinks: {self.follow_symlinks}\n\n")
            
            output.write("## Directory Structure\n\n")
        
        # Helper to format size
        def format_size(size_bytes: int) -> str:
            """Format size in bytes to a human-readable format."""
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024 or unit == 'TB':
                    if unit == 'B':
                        return f"{size_bytes} {unit}"
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024
        
        # Helper to get emoji for file type
        def get_file_emoji(extension: str) -> str:
            """Get emoji for different file types."""
            extension = extension.lower()
            
            # Code files
            if extension in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.go', '.rs', '.swift', '.kt']:
                return '📄 ' if use_emoji else ''
            # Web files
            elif extension in ['.html', '.css', '.htm']:
                return '🌐 ' if use_emoji else ''
            # Data files
            elif extension in ['.json', '.xml', '.csv', '.xlsx', '.xls', '.yaml', '.yml']:
                return '📊 ' if use_emoji else ''
            # Image files
            elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp', '.webp']:
                return '🖼️ ' if use_emoji else ''
            # Document files
            elif extension in ['.md', '.txt', '.pdf', '.doc', '.docx', '.odt', '.rtf']:
                return '📝 ' if use_emoji else ''
            # Config files
            elif extension in ['.conf', '.config', '.ini', '.env', '.toml']:
                return '⚙️ ' if use_emoji else ''
            # Executable files
            elif extension in ['.exe', '.sh', '.bat', '.cmd', '.app']:
                return '⚡ ' if use_emoji else ''
            # Archive files
            elif extension in ['.zip', '.rar', '.tar', '.gz', '.7z']:
                return '📦 ' if use_emoji else ''
            # Default
            else:
                return '📄 ' if use_emoji else ''
                
        def write_tree_node(node: Dict[str, Any], prefix: str = "", is_last: bool = True, depth: int = 0) -> None:
            """
            Recursively write a tree node to the output in Markdown format.
            
            Args:
                node: The tree node to write
                prefix: Current line prefix (for continuation lines)
                is_last: Whether this is the last item in its parent's children
                depth: Current depth in the tree
            """
            # Prepare the branch character
            branch = "└── " if is_last else "├── "
            
            # Prepare the line to write
            line = f"{prefix}{branch}"
            
            if node.get("type") == "directory":
                # Format directory entry
                dir_name = node["name"]
                
                if use_emoji:
                    line += f"📁 **{dir_name}**"
                else:
                    line += f"**{dir_name}/**"
                    
                if node.get("symlink"):
                    line += f" -> `{node['target']}`"
                    
                output.write(f"{line}\n")
                
                # Prepare prefix for children
                child_prefix = prefix + ("    " if is_last else "│   ")
                
                # Process children if any
                children = node.get("children", [])
                if children:
                    for i, child in enumerate(children):
                        write_tree_node(
                            child, 
                            prefix=child_prefix, 
                            is_last=(i == len(children) - 1),
                            depth=depth + 1
                        )
            
            elif node.get("type") == "file":
                # Format file entry
                file_name = node["name"]
                extension = node.get("extension", "")
                
                # Get emoji for file type
                emoji = get_file_emoji(extension)
                
                line += f"{emoji}{file_name}"
                
                # Add size if requested
                if include_size and "size" in node:
                    size_formatted = format_size(node["size"])
                    line += f" ({size_formatted})"
                    
                if node.get("symlink"):
                    line += f" -> `{node['target']}`"
                    
                output.write(f"{line}\n")
            
            elif node.get("type") == "error":
                # Format error entry
                file_name = node["name"]
                line += f"❌ {file_name} (Error: {node.get('error', 'Unknown')})"
                output.write(f"{line}\n")
        
        # Start writing the tree
        if tree_data.get("type") == "directory":
            # Start with root directory
            output.write(f"{'📁 ' if use_emoji else ''}**{tree_data['name'] or str(self.root_path)}**\n")
            
            # Process children
            children = tree_data.get("children", [])
            for i, child in enumerate(children):
                write_tree_node(
                    child, 
                    prefix="", 
                    is_last=(i == len(children) - 1)
                )
        else:
            # Handle case where root is a file
            extension = tree_data.get("extension", "")
            emoji = get_file_emoji(extension)
            file_line = f"{emoji}{tree_data['name']}"
            
            if include_size and "size" in tree_data:
                file_line += f" ({format_size(tree_data['size'])})"
                
            output.write(f"{file_line}\n")
        
        # Handle return value
        if isinstance(output_file, (str, Path)):
            output.close()
            return None
        elif output_file is None:
            markdown_content = output.getvalue()
            output.close()
            return markdown_content
        
        return None
            
    def generate_markdown(
        self,
        output_file: Optional[Union[str, Path, TextIO]] = None,
        include_size: bool = True,
        include_header: bool = True,
        use_emoji: bool = True,
        relative_paths: bool = False,
        indent_size: int = 2
    ) -> Optional[str]:
        """
        Generate a Markdown representation of the file tree.
        
        This is an alias for to_markdown with a more consistent naming convention.
        
        Args:
            output_file: Optional file path or file-like object to write Markdown to.
                         If None, returns the Markdown as a string.
            include_size: Whether to include file size information
            include_header: Whether to include a header with information about the extraction
            use_emoji: Whether to use emoji icons for files and directories
            relative_paths: Whether to display paths relative to the root path
            indent_size: Number of spaces for each level of indentation
            
        Returns:
            If output_file is None, returns the Markdown string representation.
            Otherwise, writes to the specified file and returns None.
        """
        return self.to_markdown(
            output_file=output_file,
            include_size=include_size,
            include_header=include_header,
            use_emoji=use_emoji,
            relative_paths=relative_paths,
            indent_size=indent_size
        )
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()


# Keep the standalone function for backward compatibility
def traverse_directory(
    root_path: Union[str, Path],
    max_depth: int = None,
    exclude_dirs: List[str] = None,
    exclude_extensions: List[str] = None,
    include_extensions: List[str] = None,
) -> Dict[str, Any]:
    """
    Recursively traverse a directory and build a hierarchical structure of files and folders.
    
    This is a legacy function maintained for backward compatibility.
    Consider using the FileTreeExtractor class for more advanced features.
    
    Args:
        root_path: Path to the root directory to traverse
        max_depth: Maximum depth to traverse (None for unlimited)
        exclude_dirs: List of directory names to exclude (e.g., ['.git', 'node_modules'])
        exclude_extensions: List of file extensions to exclude (e.g., ['.pyc', '.log'])
        include_extensions: List of file extensions to include (if specified, all others are excluded)
        
    Returns:
        A dictionary representing the hierarchical file tree
    """
    extractor = FileTreeExtractor(
        root_path=root_path,
        max_depth=max_depth,
        exclude_dirs=exclude_dirs,
        exclude_extensions=exclude_extensions,
        include_extensions=include_extensions
    )
    
    return extractor.extract() 