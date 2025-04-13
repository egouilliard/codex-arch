"""
Integration tests for CLI component interactions.

These tests verify the correct interaction between the CLI and other components of the system.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from codex_arch.cli.cli import cli
from codex_arch.extractors.file_tree_extractor import FileTreeExtractor
from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.visualization.graph.dot_generator import DotGenerator
from codex_arch.extractors.python.dependency_graph import DependencyGraph


@pytest.mark.integration
class TestCLIToFileTree:
    """Test the integration between CLI and file tree extraction."""
    
    def test_cli_file_tree_extraction(self, sample_project_dir):
        """Test the CLI command for file tree extraction."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            output_file = Path("file_tree.json")
            
            # Create a mock CLI command for tree extraction
            @cli.command()
            @patch('click.argument', return_value=lambda f: f)
            @patch('click.option', return_value=lambda f: f)
            def extract_tree():
                """Extract file tree."""
                extractor = FileTreeExtractor(sample_project_dir)
                tree = extractor.extract_tree()
                
                with open(output_file, 'w') as f:
                    json.dump(tree, f, indent=2)
                
                return 0
            
            # Run the CLI command
            result = runner.invoke(extract_tree)
            
            # Verify command executed successfully
            assert result.exit_code == 0
            
            # Verify output file was created
            assert output_file.exists()
            
            # Verify file contains valid JSON
            with open(output_file) as f:
                file_tree = json.load(f)
                
            # Verify file tree structure
            assert isinstance(file_tree, list)
            assert len(file_tree) > 0
            assert "path" in file_tree[0]
            assert "type" in file_tree[0]


@pytest.mark.integration
class TestCLIToMetrics:
    """Test the integration between CLI and metrics collection."""
    
    def test_cli_metrics_collection(self, sample_project_dir):
        """Test the CLI command for metrics collection."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            output_file = Path("metrics.json")
            
            # Create a mock CLI command for metrics collection
            @cli.command()
            @patch('click.argument', return_value=lambda f: f)
            @patch('click.option', return_value=lambda f: f)
            def collect_metrics():
                """Collect metrics."""
                metrics_collector = MetricsCollector(sample_project_dir)
                metrics = metrics_collector.collect_metrics()
                
                with open(output_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                return 0
            
            # Run the CLI command
            result = runner.invoke(collect_metrics)
            
            # Verify command executed successfully
            assert result.exit_code == 0
            
            # Verify output file was created
            assert output_file.exists()
            
            # Verify file contains valid JSON
            with open(output_file) as f:
                metrics = json.load(f)
                
            # Verify metrics structure
            assert "file_count" in metrics
            assert "line_count" in metrics
            assert "language_distribution" in metrics


@pytest.mark.integration
class TestCLIToGraph:
    """Test the integration between CLI and graph generation."""
    
    def test_cli_graph_generation(self, sample_project_dir):
        """Test the CLI command for graph generation."""
        runner = CliRunner()
        
        # Mock the PythonDependencyExtractor.extract_dependencies method
        mock_dependencies = [
            {"module": "main", "imports": ["utils"]},
            {"module": "utils", "imports": ["json", "datetime"]}
        ]
        
        with patch('codex_arch.extractors.python.extractor.PythonDependencyExtractor.extract') as mock_extract:
            # Create a mock dependency graph
            mock_graph = DependencyGraph()
            mock_graph.add_node("main", {"id": "main", "path": "main.py", "imports": ["utils"]})
            mock_graph.add_node("utils", {"id": "utils", "path": "utils.py", "imports": ["json", "datetime"]})
            mock_graph.add_edge("main", "utils", {"type": "import"})
            
            mock_extract.return_value = mock_graph
            
            with runner.isolated_filesystem():
                output_file = Path("dependencies.svg")
                
                # Create a mock CLI command for graph generation
                @cli.command()
                @patch('click.argument', return_value=lambda f: f)
                @patch('click.option', return_value=lambda f: f)
                def generate_graph():
                    """Generate dependency graph."""
                    # This would normally use the extractor, but we've mocked it
                    from codex_arch.extractors.python.extractor import PythonDependencyExtractor
                    extractor = PythonDependencyExtractor(sample_project_dir)
                    dependencies = extractor.extract()
                    
                    graph_gen = DotGenerator()
                    dot_graph = graph_gen.generate_from_dependency_graph(dependencies.to_dict())
                    graph_gen.render_to_file(dot_graph, output_file)
                    
                    return 0
                
                # Run the CLI command
                result = runner.invoke(generate_graph)
                
                # Verify command executed successfully
                assert result.exit_code == 0
                
                # Verify output file was created
                assert output_file.exists()
                assert output_file.stat().st_size > 0


@pytest.mark.integration
class TestCLIFullAnalysis:
    """Test the full analysis workflow through CLI."""
    
    def test_cli_full_analysis(self, sample_project_dir):
        """Test the CLI command for full analysis."""
        runner = CliRunner()
        
        # Mock all the necessary components
        with patch('codex_arch.extractors.file_tree_extractor.FileTreeExtractor.extract_tree') as mock_file_tree:
            mock_file_tree.return_value = [
                {"path": "main.py", "type": "file", "size": 100},
                {"path": "utils.py", "type": "file", "size": 200}
            ]
            
            with patch('codex_arch.extractors.python.extractor.PythonDependencyExtractor.extract') as mock_deps:
                # Create a mock dependency graph
                mock_graph = DependencyGraph()
                mock_graph.add_node("main", {"id": "main", "path": "main.py", "imports": ["utils"]})
                mock_graph.add_node("utils", {"id": "utils", "path": "utils.py", "imports": ["json", "datetime"]})
                mock_graph.add_edge("main", "utils", {"type": "import"})
                
                mock_deps.return_value = mock_graph
                
                with patch('codex_arch.metrics.metrics_collector.MetricsCollector.collect_metrics') as mock_metrics:
                    mock_metrics.return_value = {
                        "file_count": 2,
                        "line_count": 300,
                        "language_distribution": {
                            "Python": {"file_count": 2, "line_count": 300}
                        }
                    }
                    
                    with patch('codex_arch.visualization.graph.dot_generator.DotGenerator.generate_from_dependencies') as mock_graph:
                        mock_graph.return_value = "digraph { main -> utils }"
                        
                        with patch('codex_arch.visualization.graph.dot_generator.DotGenerator.render_to_file'):
                            with patch('codex_arch.summary.summary_builder.SummaryBuilder.build_summary') as mock_summary:
                                mock_summary.return_value = {
                                    "project_metrics": {
                                        "file_count": 2,
                                        "line_count": 300
                                    },
                                    "code_overview": "Sample project with 2 Python files."
                                }
                                
                                with runner.isolated_filesystem():
                                    output_dir = Path("analysis_output")
                                    os.makedirs(output_dir, exist_ok=True)
                                    
                                    # Create a mock CLI command for full analysis
                                    @cli.command()
                                    @patch('click.argument', return_value=lambda f: f)
                                    @patch('click.option', return_value=lambda f: f)
                                    def analyze():
                                        """Run full analysis."""
                                        # Extract file tree
                                        file_extractor = FileTreeExtractor(sample_project_dir)
                                        file_tree = file_extractor.extract_tree()
                                        
                                        # Extract dependencies
                                        from codex_arch.extractors.python.extractor import PythonDependencyExtractor
                                        py_extractor = PythonDependencyExtractor(sample_project_dir)
                                        dependencies = py_extractor.extract()
                                        
                                        # Collect metrics
                                        metrics_collector = MetricsCollector(sample_project_dir)
                                        metrics = metrics_collector.collect_metrics()
                                        
                                        # Generate graph
                                        graph_gen = DotGenerator()
                                        dot_graph = graph_gen.generate_from_dependency_graph(dependencies.to_dict())
                                        
                                        # Write output files
                                        with open(output_dir / "metrics.json", 'w') as f:
                                            json.dump(metrics, f, indent=2)
                                            
                                        with open(output_dir / "dependencies.json", 'w') as f:
                                            json.dump(dependencies, f, indent=2)
                                            
                                        graph_gen.render_to_file(dot_graph, output_dir / "dependency_graph.svg")
                                        
                                        # Generate summary
                                        from codex_arch.summary.summary_builder import SummaryBuilder
                                        summary_builder = SummaryBuilder(sample_project_dir)
                                        summary_builder.add_metrics(metrics)
                                        summary_builder.add_file_tree(file_tree)
                                        summary_builder.add_dependencies(dependencies)
                                        summary = summary_builder.build_summary()
                                        
                                        # Write summary to markdown
                                        with open(output_dir / "summary.md", 'w') as f:
                                            f.write("# Project Summary\n\n")
                                            f.write(f"File count: {summary['project_metrics']['file_count']}\n")
                                            f.write(f"Overview: {summary['code_overview']}\n")
                                        
                                        return 0
                                    
                                    # Run the CLI command
                                    result = runner.invoke(analyze)
                                    
                                    # Verify command executed successfully
                                    assert result.exit_code == 0
                                    
                                    # Verify output files were created
                                    assert (output_dir / "summary.md").exists()
                                    assert (output_dir / "metrics.json").exists()
                                    assert (output_dir / "dependencies.json").exists()
                                    assert (output_dir / "dependency_graph.svg").exists()


@pytest.mark.integration
class TestCLIWithChangeDetection:
    """Test CLI integration with change detection."""
    
    def test_cli_change_detection(self, git_repo_dir, mock_git):
        """Test the CLI command for change detection and incremental analysis."""
        runner = CliRunner()
        
        # Mock git changes
        mock_git.git.diff.return_value = "file1.py\nfile2.py"
        
        # Mock the change detector
        with patch('codex_arch.change_detection.git_changes.GitChangeDetector.detect_changes') as mock_detect:
            mock_detect.return_value = {"file1.py", "file2.py"}
            
            # Mock metrics for changed files
            with patch('codex_arch.metrics.metrics_collector.MetricsCollector.collect_metrics_for_files') as mock_metrics:
                mock_metrics.return_value = {
                    "file_count": 2,
                    "line_count": 150,
                    "language_distribution": {
                        "Python": {"file_count": 2, "line_count": 150}
                    }
                }
                
                with runner.isolated_filesystem():
                    output_file = Path("changes.json")
                    
                    # Create a mock CLI command for change detection
                    @cli.command()
                    @patch('click.argument', return_value=lambda f: f)
                    @patch('click.option', return_value=lambda f: f)
                    def detect_changes():
                        """Detect changes in git repository."""
                        from codex_arch.change_detection.git_changes import GitChangeDetector
                        detector = GitChangeDetector(repo_path=git_repo_dir)
                        changes = detector.detect_changes(since="HEAD~1")
                        
                        # Collect metrics for changed files
                        metrics_collector = MetricsCollector(git_repo_dir)
                        metrics = metrics_collector.collect_metrics_for_files(changes)
                        
                        # Output the results
                        result = {
                            "changes": list(changes),
                            "metrics": metrics
                        }
                        
                        with open(output_file, 'w') as f:
                            json.dump(result, f, indent=2)
                            
                        return 0
                    
                    # Run the CLI command
                    result = runner.invoke(detect_changes)
                    
                    # Verify command executed successfully
                    assert result.exit_code == 0
                    
                    # Verify output file was created
                    assert output_file.exists()
                    
                    # Verify file contains expected data
                    with open(output_file) as f:
                        data = json.load(f)
                        
                    assert "changes" in data
                    assert len(data["changes"]) == 2
                    assert "file1.py" in data["changes"]
                    assert "metrics" in data
                    assert data["metrics"]["file_count"] == 2 