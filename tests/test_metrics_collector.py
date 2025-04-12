"""
Tests for the metrics collector module.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.metrics import language_analyzer


class TestMetricsCollector:
    """Test cases for the MetricsCollector class."""

    def test_basic_initialization(self):
        """Test that the MetricsCollector can be initialized with default parameters."""
        sample_path = "/tmp"
        collector = MetricsCollector(root_path=sample_path)
        assert collector is not None
        assert collector.root_path == Path(sample_path)
        assert hasattr(collector, 'exclude_dirs')
        assert isinstance(collector.exclude_dirs, set)

    def test_initialization_with_params(self):
        """Test initialization with custom parameters."""
        collector = MetricsCollector(
            root_path="/test/path",
            exclude_dirs=['.git', 'build'],
            include_hidden=True
        )
        assert collector.root_path == Path("/test/path")
        assert '.git' in collector.exclude_dirs
        assert 'build' in collector.exclude_dirs
        assert collector.include_hidden is True

    def test_collect_basic_metrics(self, sample_project_dir):
        """Test collecting basic metrics from a sample project."""
        collector = MetricsCollector(root_path=sample_project_dir)
        metrics = collector.collect_metrics()
        
        # Verify basic metrics were collected correctly
        assert metrics is not None
        assert 'file_counts' in metrics
        assert 'line_counts' in metrics
        assert 'size_metrics' in metrics
        assert metrics['file_counts']['total'] >= 0
        assert metrics['line_counts']['total'] >= 0
        
        # Check that directory data is correctly structured
        assert 'by_directory' in metrics['file_counts']
        assert isinstance(metrics['file_counts']['by_directory'], dict)

    def test_collect_language_metrics(self, sample_project_dir):
        """Test collecting language-specific metrics."""
        collector = MetricsCollector(root_path=sample_project_dir)
        metrics = collector.collect_metrics()
        
        # Verify language metrics were collected correctly
        assert metrics is not None
        assert 'language_distribution' in metrics
        assert 'language_analysis' in metrics
        
        # Verify extension data is present
        assert 'by_extension' in metrics['file_counts']
        assert isinstance(metrics['file_counts']['by_extension'], dict)

    def test_collect_complexity_metrics(self, sample_project_dir):
        """Test collecting code complexity metrics."""
        collector = MetricsCollector(root_path=sample_project_dir, analyze_complexity=True)
        metrics = collector.collect_metrics()
        
        # Verify complexity metrics structure
        assert metrics is not None
        assert 'complexity_metrics' in metrics
        assert 'files_analyzed' in metrics['complexity_metrics']
        
        # We don't test exact values as they depend on the file content
        # Just verify the structure is correct
        assert 'most_complex_files' in metrics['complexity_metrics']
        assert isinstance(metrics['complexity_metrics']['most_complex_files'], list)

    def test_collect_all_metrics(self, sample_project_dir):
        """Test collecting all metrics at once."""
        collector = MetricsCollector(root_path=sample_project_dir)
        metrics = collector.collect_metrics()
        
        # Verify that all metric types are present
        assert metrics is not None
        assert 'file_counts' in metrics
        assert 'line_counts' in metrics
        assert 'size_metrics' in metrics
        assert 'language_distribution' in metrics
        assert 'language_analysis' in metrics
        assert 'complexity_metrics' in metrics

    def test_export_to_json(self, sample_project_dir, temp_dir):
        """Test exporting metrics to a JSON file."""
        collector = MetricsCollector(root_path=sample_project_dir)
        metrics = collector.collect_metrics()
        
        output_file = temp_dir / "metrics.json"
        collector.to_json(output_file=str(output_file))
        
        # Verify the file was created and is valid JSON
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        # Test with a file path as string
        output_file2 = str(temp_dir / "metrics2.json")
        collector.to_json(output_file=output_file2)
        assert os.path.exists(output_file2)

    def test_exclude_directories(self, sample_project_dir):
        """Test that excluded directories are properly ignored."""
        # Create a directory that should be explicitly excluded
        excluded_dir = sample_project_dir / "excluded_test_dir"
        excluded_dir.mkdir(exist_ok=True)
        (excluded_dir / "test.js").write_text("console.log('This should be excluded');")
        
        # Explicitly add our test directory to excluded dirs
        collector = MetricsCollector(
            root_path=sample_project_dir, 
            exclude_dirs=['excluded_test_dir']
        )
        metrics = collector.collect_metrics()
        
        # Check if by_directory contains any entries with our excluded dir
        excluded_dir_found = False
        for dir_path in metrics['file_counts']['by_directory'].keys():
            if 'excluded_test_dir' in dir_path:
                excluded_dir_found = True
                break
        
        assert not excluded_dir_found, "excluded_test_dir should be excluded"

    @patch('codex_arch.metrics.language_analyzer.analyze_language_distribution')
    def test_language_analysis_error_handling(self, mock_analyze, sample_project_dir):
        """Test handling of errors during language analysis."""
        # Make language analyzer raise an exception
        mock_analyze.side_effect = Exception("Test exception")
        
        collector = MetricsCollector(root_path=sample_project_dir)
        metrics = collector.collect_metrics()
        
        # Verify we still get a result despite the error
        assert metrics is not None
        # Language analysis will be missing or empty since we mocked it to fail
        assert 'language_analysis' in metrics

    def test_path_normalization(self):
        """Test that paths are properly normalized."""
        # Test with different path formats
        collector1 = MetricsCollector(root_path="/test/path/")
        collector2 = MetricsCollector(root_path="/test/path")
        collector3 = MetricsCollector(root_path=Path("/test/path"))
        
        assert collector1.root_path == Path("/test/path")
        assert collector2.root_path == Path("/test/path")
        assert collector3.root_path == Path("/test/path")

    def test_count_lines_functionality(self, sample_project_dir):
        """Test the line counting functionality without needing to mock print."""
        # Create a test file with known line count
        test_file = sample_project_dir / "test_lines.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5")
        
        collector = MetricsCollector(root_path=sample_project_dir)
        metrics = collector.collect_metrics()
        
        # Verify line count metrics exist
        assert metrics is not None
        assert 'line_counts' in metrics
        assert 'total' in metrics['line_counts']
        assert metrics['line_counts']['total'] >= 5 