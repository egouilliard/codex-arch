"""
Metrics Collector Module.

This module calculates fundamental code metrics such as file count, 
lines of code, and basic complexity measures.
"""

import os
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Optional, Union, TextIO, Pattern

from .language_analyzer import analyze_language_distribution
from .complexity_analyzer import ComplexityAnalyzer

class MetricsCollector:
    """
    A class to collect and calculate code metrics from a directory.
    
    This class allows for calculating basic metrics like file counts, line counts,
    and language distribution for a codebase.
    """
    
    def __init__(
        self,
        root_path: Union[str, Path],
        exclude_dirs: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        exclude_extensions: Optional[List[str]] = None,
        include_extensions: Optional[List[str]] = None,
        include_hidden: bool = False,
        max_file_size: Optional[int] = 10 * 1024 * 1024,  # Default 10MB limit
        analyze_complexity: bool = True,
        complexity_max_file_size: Optional[int] = 1024 * 1024  # Default 1MB for complexity
    ):
        """
        Initialize the MetricsCollector.
        
        Args:
            root_path: The root directory to analyze
            exclude_dirs: List of directory names to exclude
            exclude_patterns: List of regex patterns to exclude
            exclude_extensions: List of file extensions to exclude
            include_extensions: List of file extensions to include (if specified, only these are processed)
            include_hidden: Whether to include hidden files/directories
            max_file_size: Maximum file size in bytes to process for line counting
            analyze_complexity: Whether to perform complexity analysis
            complexity_max_file_size: Maximum file size in bytes for complexity analysis
        """
        self.root_path = Path(root_path)
        self.exclude_dirs = set(exclude_dirs or [])
        self.exclude_patterns = [re.compile(pattern) for pattern in (exclude_patterns or [])]
        self.exclude_extensions = set(exclude_extensions or [])
        self.include_extensions = set(include_extensions or [])
        self.include_hidden = include_hidden
        self.max_file_size = max_file_size
        self.analyze_complexity = analyze_complexity
        
        # Initialize complexity analyzer if needed
        self.complexity_analyzer = ComplexityAnalyzer(
            max_file_size=complexity_max_file_size
        ) if analyze_complexity else None
        
        # Results storage
        self.metrics = {}
        self.complexity_metrics = {}
        self.files_analyzed_for_complexity = 0
        self.files_skipped_for_complexity = 0
        
    def should_include_dir(self, dir_path: Path) -> bool:
        """Determine if a directory should be included in metrics."""
        if not self.include_hidden and dir_path.name.startswith('.'):
            return False
            
        return dir_path.name not in self.exclude_dirs
    
    def should_include_file(self, file_path: Path) -> bool:
        """Determine if a file should be included in metrics."""
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
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics for the specified directory.
        
        Returns:
            A dictionary containing the collected metrics
        """
        # Reset metrics
        self.metrics = {
            "file_counts": {
                "total": 0,
                "by_extension": defaultdict(int),
                "by_directory": defaultdict(int)
            },
            "line_counts": {
                "total": 0,
                "by_extension": defaultdict(int),
                "by_directory": defaultdict(int),
                "average_per_file": 0
            },
            "size_metrics": {
                "total_bytes": 0,
                "by_extension": defaultdict(int),
                "average_file_size": 0,
                "largest_file": {"path": None, "size": 0}
            },
            "language_distribution": {
                "by_files": {},
                "by_lines": {}
            }
        }
        
        # Reset complexity metrics
        self.complexity_metrics = {
            "files_analyzed": 0,
            "files_skipped": 0,
            "complexity_by_language": {},
            "most_complex_files": [],
            "total_complexity": 0,
            "average_complexity": 0,
            "comment_metrics": {
                "total_comment_lines": 0,
                "overall_comment_ratio": 0
            }
        }
        
        # Collect metrics
        self._collect_file_metrics(self.root_path)
        
        # Calculate averages and percentages
        self._calculate_derived_metrics()
        
        # Perform detailed language analysis
        language_analysis = analyze_language_distribution(
            self.metrics["file_counts"]["by_extension"],
            self.metrics["line_counts"]["by_extension"]
        )
        self.metrics["language_analysis"] = language_analysis
        
        # Add complexity metrics if they were collected
        if self.analyze_complexity:
            # Calculate average complexity if any files were analyzed
            if self.complexity_metrics["files_analyzed"] > 0:
                self.complexity_metrics["average_complexity"] = round(
                    self.complexity_metrics["total_complexity"] / 
                    self.complexity_metrics["files_analyzed"], 2
                )
            else:
                self.complexity_metrics["average_complexity"] = 0
            
            # Sort most complex files by complexity
            self.complexity_metrics["most_complex_files"] = sorted(
                self.complexity_metrics["most_complex_files"],
                key=lambda x: x["complexity"],
                reverse=True
            )[:10]  # Limit to top 10
            
            # Calculate overall comment ratio
            total_lines = self.metrics["line_counts"]["total"]
            if total_lines > 0:
                self.complexity_metrics["comment_metrics"]["overall_comment_ratio"] = round(
                    self.complexity_metrics["comment_metrics"]["total_comment_lines"] /
                    total_lines * 100, 2
                )
            else:
                self.complexity_metrics["comment_metrics"]["overall_comment_ratio"] = 0
            
            self.metrics["complexity_metrics"] = self.complexity_metrics
        
        # Restore original language distribution calculation
        # Calculate language distribution by files
        total_files = self.metrics["file_counts"]["total"]
        if total_files > 0:
            for ext, count in self.metrics["file_counts"]["by_extension"].items():
                self.metrics["language_distribution"]["by_files"][ext] = round(
                    (count / total_files) * 100, 2
                )
                
        # Calculate language distribution by lines
        total_lines = self.metrics["line_counts"]["total"]
        if total_lines > 0:
            for ext, count in self.metrics["line_counts"]["by_extension"].items():
                self.metrics["language_distribution"]["by_lines"][ext] = round(
                    (count / total_lines) * 100, 2
                )
        
        return self.metrics
    
    def _collect_file_metrics(self, directory: Path) -> None:
        """
        Recursively collect file metrics from a directory.
        
        Args:
            directory: The directory to process
        """
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    if self.should_include_dir(item):
                        self._collect_file_metrics(item)
                elif item.is_file():
                    if self.should_include_file(item):
                        self._process_file(item)
        except (PermissionError, OSError) as e:
            # Log the error but continue processing
            print(f"Error accessing {directory}: {e}")
    
    def _process_file(self, file_path: Path) -> None:
        """
        Process a single file for metrics.
        
        Args:
            file_path: The file to process
        """
        try:
            # Get file size
            file_size = file_path.stat().st_size
            
            # Update file count metrics
            self.metrics["file_counts"]["total"] += 1
            
            extension = file_path.suffix.lower() or "no_extension"
            self.metrics["file_counts"]["by_extension"][extension] += 1
            
            # Get relative directory path for grouping
            rel_dir = str(file_path.parent.relative_to(self.root_path)) or "."
            self.metrics["file_counts"]["by_directory"][rel_dir] += 1
            
            # Update size metrics
            self.metrics["size_metrics"]["total_bytes"] += file_size
            self.metrics["size_metrics"]["by_extension"][extension] += file_size
            
            # Track largest file
            if file_size > self.metrics["size_metrics"]["largest_file"]["size"]:
                self.metrics["size_metrics"]["largest_file"] = {
                    "path": str(file_path.relative_to(self.root_path)),
                    "size": file_size
                }
            
            # Count lines if file is not too large
            if self.max_file_size is None or file_size <= self.max_file_size:
                line_count = self._count_lines(file_path)
                self.metrics["line_counts"]["total"] += line_count
                self.metrics["line_counts"]["by_extension"][extension] += line_count
                self.metrics["line_counts"]["by_directory"][rel_dir] += line_count
            
            # Analyze complexity if enabled
            if self.analyze_complexity and self.complexity_analyzer:
                self._analyze_file_complexity(file_path, extension)
                
        except (PermissionError, OSError) as e:
            # Log the error but continue processing
            print(f"Error processing {file_path}: {e}")
    
    def _count_lines(self, file_path: Path) -> int:
        """
        Count the number of lines in a file.
        
        Args:
            file_path: The file to count lines in
            
        Returns:
            The number of lines in the file
        """
        try:
            line_count = 0
            with file_path.open('rb') as f:
                for _ in f:
                    line_count += 1
            return line_count
        except (UnicodeDecodeError, PermissionError, OSError) as e:
            # Return 0 for files we can't read
            print(f"Error counting lines in {file_path}: {e}")
            return 0
    
    def _analyze_file_complexity(self, file_path: Path, extension: str) -> None:
        """
        Analyze complexity of a single file.
        
        Args:
            file_path: Path to the file to analyze
            extension: File extension (with dot)
        """
        # Get complexity metrics
        result = self.complexity_analyzer.analyze_file(file_path)
        
        # Skip if analysis failed
        if not result["metrics"].get("is_analyzable", False):
            self.complexity_metrics["files_skipped"] += 1
            return
            
        self.complexity_metrics["files_analyzed"] += 1
        metrics = result["metrics"]
        language = result["language"]
        
        # Initialize language entry if needed
        if language not in self.complexity_metrics["complexity_by_language"]:
            self.complexity_metrics["complexity_by_language"][language] = {
                "file_count": 0,
                "total_complexity": 0,
                "average_complexity": 0,
                "functions": 0,
                "classes": 0,
                "comment_ratio": 0,
                "total_comments": 0
            }
            
        lang_metrics = self.complexity_metrics["complexity_by_language"][language]
        lang_metrics["file_count"] += 1
        
        # Track most complex files
        rel_path = str(file_path.relative_to(self.root_path))
        complexity_val = metrics.get("complexity", {}).get("total_complexity", 0)
        if complexity_val > 0:
            self.complexity_metrics["total_complexity"] += complexity_val
            lang_metrics["total_complexity"] += complexity_val
            
            # Add to most complex files list
            self.complexity_metrics["most_complex_files"].append({
                "path": rel_path,
                "language": language,
                "complexity": complexity_val,
                "lines": metrics.get("total_lines", 0)
            })
        
        # Update language-specific metrics
        if "complexity" in metrics:
            lang_metrics["functions"] += metrics["complexity"].get("total_functions", 0)
            lang_metrics["classes"] += metrics["complexity"].get("total_classes", 0)
            
        # Track comment metrics
        if "comments" in metrics:
            comment_lines = (metrics["comments"].get("comment_lines", 0) + 
                            metrics["comments"].get("docstring_lines", 0))
            
            lang_metrics["total_comments"] += comment_lines
            self.complexity_metrics["comment_metrics"]["total_comment_lines"] += comment_lines
            
        # Calculate average complexity for the language
        if lang_metrics["file_count"] > 0:
            lang_metrics["average_complexity"] = round(
                lang_metrics["total_complexity"] / lang_metrics["file_count"], 2
            )
            
            # Calculate comment ratio for the language
            total_lines_for_lang = sum(self.metrics["line_counts"]["by_extension"].get(ext, 0) 
                                         for ext in self.metrics["line_counts"]["by_extension"]
                                         if self.complexity_analyzer._detect_language(ext) == language)
            
            # Prevent division by zero
            if total_lines_for_lang > 0:
                lang_metrics["comment_ratio"] = round(
                    lang_metrics["total_comments"] / total_lines_for_lang * 100, 2
                )
            else:
                lang_metrics["comment_ratio"] = 0
        else:
            lang_metrics["average_complexity"] = 0
            lang_metrics["comment_ratio"] = 0
    
    def _calculate_derived_metrics(self) -> None:
        """Calculate averages and percentages for metrics that require file and line counts."""
        # Average lines per file
        if self.metrics["file_counts"]["total"] > 0:  # Prevent division by zero
            self.metrics["line_counts"]["average_per_file"] = round(
                self.metrics["line_counts"]["total"] / self.metrics["file_counts"]["total"], 2
            )
        else:
            self.metrics["line_counts"]["average_per_file"] = 0
            
        # Average file size
        if self.metrics["file_counts"]["total"] > 0:  # Prevent division by zero
            self.metrics["size_metrics"]["average_file_size"] = round(
                self.metrics["size_metrics"]["total_bytes"] / self.metrics["file_counts"]["total"], 2
            )
        else:
            self.metrics["size_metrics"]["average_file_size"] = 0
            
        # Calculate percentage distributions for file extensions
        total_files = self.metrics["file_counts"]["total"]
        extension_percentages = {}
        
        if total_files > 0:  # Prevent division by zero
            for ext, count in self.metrics["file_counts"]["by_extension"].items():
                extension_percentages[ext] = round((count / total_files) * 100, 2)
        
        self.metrics["file_counts"]["extension_percentages"] = extension_percentages
    
    def to_json(
        self, 
        output_file: Optional[Union[str, Path, TextIO]] = None,
        indent: int = 2,
        include_metadata: bool = True
    ) -> Optional[str]:
        """
        Output the metrics data as JSON.
        
        Args:
            output_file: Optional file path or file-like object to write JSON to.
                         If None, returns the JSON as a string.
            indent: Number of spaces for indentation in JSON output
            include_metadata: Whether to include metadata about the extraction
            
        Returns:
            If output_file is None, returns the JSON string.
            Otherwise, writes to the file and returns None.
        """
        # Make sure metrics are collected
        if not self.metrics:
            self.collect_metrics()
            
        # Prepare output data
        output_data = self.metrics.copy()
        
        # Add metadata if requested
        if include_metadata:
            output_data = {
                "metadata": {
                    "root_path": str(self.root_path),
                    "extracted_at": self._get_timestamp(),
                    "config": {
                        "exclude_dirs": list(self.exclude_dirs),
                        "exclude_patterns": [p.pattern if hasattr(p, 'pattern') else str(p) 
                                            for p in self.exclude_patterns],
                        "exclude_extensions": list(self.exclude_extensions),
                        "include_extensions": list(self.include_extensions),
                        "include_hidden": self.include_hidden,
                        "max_file_size": self.max_file_size,
                        "analyze_complexity": self.analyze_complexity
                    }
                },
                "metrics": output_data
            }
        
        # Convert defaultdicts to regular dicts for JSON serialization
        output_data = json.loads(json.dumps(output_data, default=self._json_serialize))
        
        # Output as requested
        if output_file is None:
            return json.dumps(output_data, indent=indent)
        
        if isinstance(output_file, (str, Path)):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=indent)
        else:
            # Assume file-like object
            json.dump(output_data, output_file, indent=indent)
            
        return None
    
    def _json_serialize(self, obj):
        """Helper method to serialize objects that aren't JSON serializable by default."""
        if isinstance(obj, defaultdict):
            return dict(obj)
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, 'pattern'):  # Handle compiled regex patterns
            return obj.pattern
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def _get_timestamp(self) -> str:
        """Get the current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat() 