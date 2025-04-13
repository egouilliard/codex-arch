#!/usr/bin/env python
"""
Integration test for verifying dependency graph fixes

This test validates that the fixes for the dependency graph functionality
work correctly when used with real-world dependency data.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import the codex_arch modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from codex_arch.extractors.python.dependency_graph import (
    DependencyGraph, build_graph_from_dependency_mapping, analyze_dependencies
)
from codex_arch.extractors.python.json_exporter import DependencyExporter
from codex_arch.metrics.metrics_collector import MetricsCollector
from codex_arch.summary.summary_builder import SummaryConfig, SummaryBuilder

def test_dependency_graph_integration():
    """Test the integrated dependency graph functionality with our fixes."""
    logger.info("Testing integrated dependency graph functionality...")
    
    # Create a dependency graph
    graph = DependencyGraph()
    
    # Add nodes and edges
    graph.add_node("module_a.py", {"path": "module_a.py"})
    graph.add_node("module_b.py", {"path": "module_b.py"})
    graph.add_node("module_c.py", {"path": "module_c.py"})
    
    # Create some dependencies
    graph.add_edge("module_a.py", "module_b.py")
    graph.add_edge("module_b.py", "module_c.py")
    
    # Test our fixed methods
    edge_list = graph.edges_list()
    edge_count = graph.edge_count()
    
    # Validate results
    assert len(edge_list) == 2, f"Expected 2 edges in edge_list, got {len(edge_list)}"
    assert edge_count == 2, f"Expected edge_count to be 2, got {edge_count}"
    assert ("module_a.py", "module_b.py") in edge_list, "Edge module_a.py -> module_b.py missing from edge_list"
    
    logger.info(f"Edge list check passed: {edge_list}")
    logger.info(f"Edge count check passed: {edge_count}")
    
    return True

def test_metrics_collector_division_fix():
    """Test that the metrics collector handles division by zero properly."""
    logger.info("Testing metrics collector division by zero fixes...")
    
    # Create a temp directory with a test file
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        test_file = test_dir / "test.py"
        
        # Create a test file
        with open(test_file, 'w') as f:
            f.write("# Test file\nimport os\n\ndef test():\n    pass\n")
        
        # Test with metrics collector
        collector = MetricsCollector(root_path=test_dir)
        metrics = collector.collect_metrics()
        
        # Check that we don't have division by zero errors
        assert 'complexity_metrics' in metrics, "Complexity metrics missing from result"
        assert 'comment_metrics' in metrics['complexity_metrics'], "Comment metrics missing from complexity metrics"
        assert 'overall_comment_ratio' in metrics['complexity_metrics']['comment_metrics'], "Overall comment ratio missing"
        
        # Log the results
        ratio = metrics['complexity_metrics']['comment_metrics']['overall_comment_ratio']
        logger.info(f"Comment ratio calculated without division by zero: {ratio}")
        
        # Now test with an empty directory (edge case)
        empty_dir = test_dir / "empty"
        empty_dir.mkdir()
        
        collector = MetricsCollector(root_path=empty_dir)
        metrics = collector.collect_metrics()
        
        # Check that we don't have division by zero errors in edge case
        assert 'line_counts' in metrics, "Line counts missing from metrics"
        assert 'average_per_file' in metrics['line_counts'], "Average per file missing from line counts"
        
        # Log the results
        avg_lines = metrics['line_counts']['average_per_file']
        logger.info(f"Average lines per file with no files: {avg_lines}")
        
    return True

def test_summary_config_parameters():
    """Test that the SummaryConfig parameters work correctly."""
    logger.info("Testing SummaryConfig parameter fixes...")
    
    # Test creating a SummaryConfig with the new parameters
    config = SummaryConfig(
        template='detailed',
        include_metrics=True,
        include_dependencies=True,
        use_smart_summarization=True,
        exclude_dirs=['node_modules', '.git']
    )
    
    # Validate that the parameters were set correctly
    assert config.template == 'detailed', f"Expected template to be 'detailed', got {config.template}"
    assert config.include_metrics is True, f"Expected include_metrics to be True, got {config.include_metrics}"
    assert config.exclude_dirs == ['node_modules', '.git'], f"Expected exclude_dirs to be ['node_modules', '.git'], got {config.exclude_dirs}"
    
    # Validate that exclude_dirs were added to ignore_patterns
    assert 'node_modules' in config.ignore_patterns, "node_modules should be in ignore_patterns"
    assert '.git' in config.ignore_patterns, ".git should be in ignore_patterns"
    
    # Test config serialization
    config_dict = config.to_dict()
    assert 'template' in config_dict, "template should be in config_dict"
    assert 'include_metrics' in config_dict, "include_metrics should be in config_dict"
    assert 'exclude_dirs' in config_dict, "exclude_dirs should be in config_dict"
    
    logger.info("SummaryConfig parameter checks passed")
    return True

def run_all_tests():
    """Run all integration tests for our fixes."""
    tests = [
        test_dependency_graph_integration,
        test_metrics_collector_division_fix,
        test_summary_config_parameters
    ]
    
    results = {}
    
    for test_func in tests:
        test_name = test_func.__name__
        logger.info(f"Running test: {test_name}")
        
        try:
            result = test_func()
            results[test_name] = "PASSED" if result else "FAILED"
        except Exception as e:
            logger.error(f"Error in test {test_name}: {e}")
            results[test_name] = f"ERROR: {str(e)}"
    
    # Print summary
    logger.info("=== INTEGRATION TEST SUMMARY ===")
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")
    
    # Return overall success
    return all(result == "PASSED" for result in results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 