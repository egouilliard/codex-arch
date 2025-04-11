"""
Data Collection and Aggregation Service

This module is responsible for collecting and aggregating data from various
extractors and analyzers into a unified data structure for summary generation.
"""

import json
import os
from typing import Dict, Any, Optional, List

from codex_arch.extractors.file_tree_extractor import FileTreeExtractor
from codex_arch.extractors.python.extractor import PythonDependencyExtractor
from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.visualization.graph.dot_generator import DotGenerator


class DataCollector:
    """
    Data Collection and Aggregation Service

    Collects and aggregates data from all the extractors and analyzers
    to provide a unified data structure for summary generation.
    """

    def __init__(self, repo_path: str, output_dir: Optional[str] = None):
        """
        Initialize the DataCollector.

        Args:
            repo_path: Path to the repository to analyze
            output_dir: Directory to store output files (defaults to './output')
        """
        self.repo_path = os.path.abspath(repo_path)
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'output')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the data structure
        self.data = {
            'repo_path': self.repo_path,
            'file_tree': None,
            'python_dependencies': None,
            'metrics': None,
            'visualizations': [],
        }
        
        # Initialize extractors and analyzers
        self.file_tree_extractor = FileTreeExtractor(self.repo_path)
        self.python_dependency_extractor = PythonDependencyExtractor(self.repo_path)
        self.metrics_collector = MetricsCollector(self.repo_path)
        self.dot_generator = DotGenerator()

    def collect_file_tree(self, ignore_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Collect file tree data.

        Args:
            ignore_patterns: List of patterns to ignore when collecting file tree

        Returns:
            File tree data structure
        """
        ignore_patterns = ignore_patterns or [
            '.git', '__pycache__', '*.pyc', '*.pyo', '*.pyd', 
            'venv', 'env', '.env', 'node_modules'
        ]
        
        file_tree = self.file_tree_extractor.extract_file_tree(
            ignore_patterns=ignore_patterns,
            output_format='json'
        )
        
        self.data['file_tree'] = file_tree
        return file_tree

    def collect_python_dependencies(self) -> Dict[str, Any]:
        """
        Collect Python dependency data.

        Returns:
            Python dependency data structure
        """
        dependencies = self.python_dependency_extractor.extract_dependencies()
        
        # Save dependencies to JSON file
        dependency_path = os.path.join(self.output_dir, 'python_dependencies.json')
        with open(dependency_path, 'w') as f:
            json.dump(dependencies, f, indent=2)
        
        self.data['python_dependencies'] = dependencies
        self.data['dependency_file_path'] = dependency_path
        return dependencies

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect code metrics.

        Returns:
            Code metrics data structure
        """
        metrics = self.metrics_collector.collect_metrics()
        
        # Save metrics to JSON file
        metrics_path = os.path.join(self.output_dir, 'metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        self.data['metrics'] = metrics
        self.data['metrics_file_path'] = metrics_path
        return metrics

    def generate_visualizations(self) -> List[str]:
        """
        Generate visualizations based on the collected data.

        Returns:
            List of paths to generated visualization files
        """
        visualization_paths = []
        
        # Generate dependency graph visualization if we have Python dependencies
        if self.data['python_dependencies']:
            # Create DOT representation
            dot_content = self.dot_generator.generate_dot(
                self.data['python_dependencies'],
                group_by_directory=True
            )
            
            # Save DOT file
            dot_path = os.path.join(self.output_dir, 'dependencies.dot')
            with open(dot_path, 'w') as f:
                f.write(dot_content)
            visualization_paths.append(dot_path)
            
            # Generate SVG from DOT if graphviz is available
            try:
                svg_path = self.dot_generator.render_svg(
                    dot_content, 
                    output_path=os.path.join(self.output_dir, 'dependencies.svg')
                )
                visualization_paths.append(svg_path)
            except Exception as e:
                print(f"Warning: Could not generate SVG visualization: {str(e)}")
                
        self.data['visualizations'] = visualization_paths
        return visualization_paths

    def collect_all(self, ignore_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Collect all data from all extractors and analyzers.

        Args:
            ignore_patterns: List of patterns to ignore for file tree extraction

        Returns:
            Complete aggregated data structure
        """
        print("Collecting file tree data...")
        self.collect_file_tree(ignore_patterns)
        
        print("Collecting Python dependency data...")
        self.collect_python_dependencies()
        
        print("Collecting code metrics...")
        self.collect_metrics()
        
        print("Generating visualizations...")
        self.generate_visualizations()
        
        # Save the complete data to a JSON file
        complete_data_path = os.path.join(self.output_dir, 'complete_data.json')
        with open(complete_data_path, 'w') as f:
            # Create a copy of the data with only serializable elements
            serializable_data = self.data.copy()
            
            # Handle non-serializable elements if needed
            # For example, convert complex objects to their string representation
            
            json.dump(serializable_data, f, indent=2)
        
        return self.data 