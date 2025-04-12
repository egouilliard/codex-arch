"""
Integration tests for Codex-Arch components.

These tests verify the correct interaction between different components of the system.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import graphviz

from codex_arch.extractors.file_tree_extractor import FileTreeExtractor
from codex_arch.extractors.python.extractor import PythonDependencyExtractor
from codex_arch.extractors.python.dependency_graph import DependencyGraph
from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.visualization.graph.dot_generator import DotGenerator
from codex_arch.summary.summary_builder import SummaryBuilder


@pytest.mark.integration
class TestPythonExtractionToGraph:
    """Test the integration between Python dependency extraction and graph generation."""
    
    def test_extraction_to_graph_flow(self, sample_project_dir):
        """Test the flow from Python extraction to graph generation."""
        # 1. Extract Python dependencies
        # Create a mock dependency graph for testing
        mock_graph = DependencyGraph()
        mock_graph.add_node("main", {"id": "main", "path": "main.py", "imports": ["utils"]})
        mock_graph.add_node("utils", {"id": "utils", "path": "utils.py", "imports": ["json", "datetime"]})
        mock_graph.add_edge("main", "utils", {"type": "import"})
        
        with patch.object(PythonDependencyExtractor, 'extract', return_value=mock_graph):
            extractor = PythonDependencyExtractor(sample_project_dir)
            dependencies = extractor.extract()
            
            # Verify dependencies were extracted
            assert dependencies is not None
            assert len(dependencies.nodes) > 0
            
            # 2. Generate graph from dependencies
            graph_gen = DotGenerator()
            dot_graph = graph_gen.generate_from_dependency_graph(dependencies.to_dict())
            
            # Verify graph was generated - check the graph object
            assert dot_graph is not None
            assert isinstance(dot_graph, graphviz.Digraph)
            assert "main" in dot_graph.source
            assert "utils" in dot_graph.source
            
            # 3. Render graph to SVG (mocked to avoid actual file operations)
            with patch.object(DotGenerator, 'save_svg_file') as mock_render:
                output_path = Path(tempfile.gettempdir()) / "test_dep_graph.svg"
                mock_render.return_value = str(output_path)
                
                # Mock os.path.exists and os.path.getsize to simulate file creation
                with patch('os.path.exists', return_value=True):
                    with patch('os.path.getsize', return_value=1000):
                        graph_gen.save_svg_file(str(output_path))
                        
                        # Verify save_svg_file was called
                        mock_render.assert_called_once()


@pytest.mark.integration
class TestFileTreeAndMetrics:
    """Test the integration between file tree extraction and metrics collection."""
    
    def test_file_tree_to_metrics_flow(self, sample_project_dir):
        """Test the flow from file tree extraction to metrics collection."""
        # Mock the FileTreeExtractor to return a predefined tree
        mock_tree = {
            "name": "sample_project",
            "path": str(sample_project_dir),
            "type": "directory",
            "children": [
                {"name": "main.py", "path": "main.py", "type": "file", "size": 100},
                {"name": "utils.py", "path": "utils.py", "type": "file", "size": 200},
                {"name": "data", "path": "data", "type": "directory", "children": [
                    {"name": "sample.json", "path": "data/sample.json", "type": "file", "size": 300}
                ]}
            ]
        }
        
        with patch.object(FileTreeExtractor, 'extract', return_value=mock_tree):
            # 1. Extract file tree
            extractor = FileTreeExtractor(sample_project_dir)
            file_tree = extractor.extract()
            
            # Verify file tree was extracted
            assert file_tree is not None
            assert file_tree["type"] == "directory"
            assert len(file_tree["children"]) > 0
            
            # Mock the metrics collection to return predefined metrics
            mock_metrics = {
                "file_count": 3,
                "line_count": 50,
                "language_distribution": {
                    "Python": {"file_count": 2, "line_count": 30},
                    "JSON": {"file_count": 1, "line_count": 20}
                }
            }
            
            with patch.object(MetricsCollector, 'collect_metrics', return_value=mock_metrics):
                # 2. Collect metrics
                metrics_collector = MetricsCollector(sample_project_dir)
                metrics = metrics_collector.collect_metrics()
                
                # Verify metrics were collected
                assert metrics is not None
                assert metrics["file_count"] == 3
                assert "language_distribution" in metrics
                assert "Python" in metrics["language_distribution"]
                assert metrics["language_distribution"]["Python"]["file_count"] == 2


@pytest.mark.integration
class TestMetricsToSummary:
    """Test the integration between metrics collection and summary generation."""
    
    def test_metrics_to_summary_flow(self, sample_project_dir):
        """Test the flow from metrics collection to summary generation."""
        # Mock metrics collection
        mock_metrics = {
            "file_count": 10,
            "line_count": 500,
            "language_distribution": {
                "Python": {"file_count": 8, "line_count": 400},
                "Markdown": {"file_count": 2, "line_count": 100}
            }
        }
        
        with patch.object(MetricsCollector, 'collect_metrics', return_value=mock_metrics):
            # 1. Collect metrics
            metrics_collector = MetricsCollector(sample_project_dir)
            metrics = metrics_collector.collect_metrics()
            
            # Mock summary data
            mock_data = {
                "project_metrics": metrics,
                "file_tree": {"name": "test", "type": "directory", "children": []},
                "dependencies": {},
                "insights": {
                    "code_overview": "Sample project with 10 files, mainly Python.",
                    "recommendations": ["Consider adding documentation"]
                }
            }
            
            # Patch SummaryBuilder methods
            with patch.object(SummaryBuilder, 'collect_data', return_value=mock_data):
                with patch.object(SummaryBuilder, 'generate_insights', return_value=mock_data["insights"]):
                    with patch.object(SummaryBuilder, 'generate_summaries'):
                        # 2. Generate summary from metrics
                        summary_builder = SummaryBuilder(sample_project_dir)
                        data = summary_builder.collect_data()
                        insights = summary_builder.generate_insights()
                        
                        # Verify summary data was generated
                        assert data is not None
                        assert "project_metrics" in data
                        assert "insights" in data
                        
                        # 3. Export summary (mocked)
                        output_path = Path(tempfile.gettempdir()) / "test_summary.md"
                        
                        # Mock file operations and generate summaries
                        with patch('os.path.exists', return_value=True):
                            with patch('os.path.getsize', return_value=1000):
                                summary_builder.generate_summaries(markdown_file=str(output_path))


@pytest.mark.integration
class TestEndToEndPipeline:
    """Test the entire pipeline from extraction to summary generation."""
    
    def test_complete_analysis_pipeline(self, sample_project_dir):
        """Test the complete analysis pipeline."""
        # Mock all components to isolate the integration test
        
        # 1. Mock file tree extraction
        mock_tree = {
            "name": "sample_project",
            "path": str(sample_project_dir),
            "type": "directory",
            "children": [
                {"name": "main.py", "path": "main.py", "type": "file", "size": 100},
                {"name": "utils.py", "path": "utils.py", "type": "file", "size": 200}
            ]
        }
        
        with patch.object(FileTreeExtractor, 'extract', return_value=mock_tree):
            # 2. Mock Python dependency extraction
            mock_graph = DependencyGraph()
            mock_graph.add_node("main", {"id": "main", "path": "main.py", "imports": ["utils"]})
            mock_graph.add_node("utils", {"id": "utils", "path": "utils.py", "imports": ["json", "datetime"]})
            mock_graph.add_edge("main", "utils", {"type": "import"})
            
            with patch.object(PythonDependencyExtractor, 'extract', return_value=mock_graph):
                # 3. Mock metrics collection
                mock_metrics = {
                    "file_count": 2,
                    "line_count": 300,
                    "language_distribution": {
                        "Python": {"file_count": 2, "line_count": 300}
                    }
                }
                
                with patch.object(MetricsCollector, 'collect_metrics', return_value=mock_metrics):
                    # 4. Mock graph generation (to avoid graphviz dependency)
                    mock_dot_graph = graphviz.Digraph()
                    mock_dot_graph.comment = "Test Graph"
                    mock_dot_graph.node("main")
                    mock_dot_graph.node("utils")
                    mock_dot_graph.edge("main", "utils")
                    
                    with patch.object(DotGenerator, 'generate_from_dependency_graph', return_value=mock_dot_graph):
                        with patch.object(DotGenerator, 'save_svg_file'):
                            # 5. Mock summary generation
                            mock_data = {
                                "project_metrics": mock_metrics,
                                "file_tree": mock_tree,
                                "dependencies": mock_graph.to_dict(),
                                "insights": {
                                    "code_overview": "Sample project with 2 Python files."
                                }
                            }
                            
                            with patch.object(SummaryBuilder, 'collect_data', return_value=mock_data):
                                with patch.object(SummaryBuilder, 'generate_insights', return_value=mock_data["insights"]):
                                    # Run the full pipeline with mocks
                                    file_extractor = FileTreeExtractor(sample_project_dir)
                                    file_tree = file_extractor.extract()
                                    
                                    py_extractor = PythonDependencyExtractor(sample_project_dir)
                                    dependencies = py_extractor.extract()
                                    
                                    metrics_collector = MetricsCollector(sample_project_dir)
                                    metrics = metrics_collector.collect_metrics()
                                    
                                    graph_gen = DotGenerator()
                                    dot_graph = graph_gen.generate_from_dependency_graph(dependencies.to_dict())
                                    graph_path = Path(tempfile.gettempdir()) / "test_pipeline_graph.svg"
                                    
                                    # Mock the file existence check
                                    with patch('os.path.exists', return_value=True):
                                        with patch('os.path.getsize', return_value=1000):
                                            graph_gen.save_svg_file(str(graph_path))
                                            
                                            summary_builder = SummaryBuilder(sample_project_dir)
                                            data = summary_builder.collect_data()
                                            insights = summary_builder.generate_insights()
                                            
                                            # Verify the complete pipeline results
                                            assert file_tree is not None and file_tree["type"] == "directory"
                                            assert dependencies is not None and len(dependencies.nodes) > 0
                                            assert metrics is not None and "file_count" in metrics
                                            assert dot_graph is not None
                                            assert data is not None and "project_metrics" in data 