#!/usr/bin/env python
"""
Test script to verify enhanced error handling in dependency graph edge analysis.

This script tests the enhanced error handling in the Python dependency graph
by creating a graph with deliberate errors and analyzing how they're captured.
"""

import os
import json
import sys
import logging
from pathlib import Path
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import the codex_arch modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from codex_arch.extractors.python.dependency_graph import (
    DependencyGraph, build_graph_from_dependency_mapping, analyze_dependencies
)
from codex_arch.extractors.python.json_exporter import DependencyExporter

def test_invalid_edge_data():
    """Test handling of invalid edge data."""
    logger.info("Testing invalid edge data handling...")
    
    # Create a temporary directory for test output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an exporter to track errors
        exporter = DependencyExporter(temp_dir)
        
        # Create dependency mapping with some invalid edge data
        dependency_mapping = {
            "main.py": {
                "import_details": [
                    {"type": "import", "module": "utils", "line": 10},
                    {"type": "import", "module": "missing", "line": 12}
                ],
                "dependencies": {
                    "utils": "utils.py",  # Valid
                    "invalid": 123,  # Invalid - not a string
                    "missing": None  # Valid but unresolved
                }
            },
            "utils.py": {
                "import_details": [
                    {"type": "import", "module": "os", "line": 5}
                ],
                "dependencies": {
                    "os": None,  # External library
                    "main.py": "main.py"  # Circular dependency
                }
            }
        }
        
        # Build graph with the invalid data
        graph = build_graph_from_dependency_mapping(dependency_mapping, exporter)
        
        # Verify the graph was created with proper error tracking
        assert hasattr(graph, 'edge_errors'), "Graph should have edge_errors attribute"
        assert len(graph.edge_errors) > 0, "Graph should have recorded edge errors"
        
        # Check that invalid edge was properly identified
        invalid_errors = [e for e in graph.edge_errors if e['error_type'] == 'invalid_edge_data']
        assert len(invalid_errors) > 0, "Should have recorded invalid edge data error"
        
        # Print out graph properties to debug
        logger.info(f"Unresolved imports: {dict(graph.unresolved_imports)}")
        logger.info(f"External dependencies: {dict(graph.external_deps)}")
        logger.info(f"Edge errors: {graph.edge_errors}")
        
        # We should at least have some external dependencies tracked
        assert len(graph.external_deps) > 0, "Should have tracked external dependencies"
        
        # Run dependency analysis
        analysis_results = analyze_dependencies(graph, exporter)
        
        # Verify analysis results tracked the issues
        assert "total_modules" in analysis_results, "Analysis should include module count"
        
        # Export to JSON to verify serialization works
        output_file = os.path.join(temp_dir, "test_dependency_errors.json")
        exporter.export_dependency_graph(graph, output_file)
        
        # Verify export includes errors
        with open(output_file, 'r') as f:
            export_data = json.load(f)
            assert "errors" in export_data, "Export should include errors"
            assert "edge_errors" in export_data, "Export should include edge_errors"
        
        # Print the errors that were collected
        logger.info(f"Errors in exporter: {exporter.errors}")
        logger.info(f"Errors found in graph: {len(graph.edge_errors)}")
        logger.info(f"Test results saved to {output_file}")
        
    return True

def test_record_edge_error():
    """Test the record_edge_error method."""
    logger.info("Testing record_edge_error method...")
    
    graph = DependencyGraph()
    
    # Record various types of errors
    graph.record_edge_error(
        source="source.py",
        target="target.py",
        error_type="test_error",
        message="Test error message",
        details="Detailed error information"
    )
    
    graph.record_edge_error(
        source="another.py",
        target="missing.py",
        error_type="missing_target",
        message="Target file does not exist",
        details={"file": "missing.py", "status": "not found"}
    )
    
    # Verify errors were recorded correctly
    assert hasattr(graph, 'edge_errors'), "Graph should have edge_errors attribute"
    assert len(graph.edge_errors) == 2, "Graph should have recorded 2 errors"
    
    # Check error details
    assert graph.edge_errors[0]['source'] == "source.py"
    assert graph.edge_errors[0]['error_type'] == "test_error"
    assert graph.edge_errors[1]['error_type'] == "missing_target"
    
    # Check analysis results integration
    assert 'edge_errors' in graph.analysis_results, "Analysis results should include edge errors"
    assert len(graph.analysis_results['edge_errors']) == 2, "Analysis results should include both errors"
    
    return True

def test_circular_dependency_detection():
    """Test detection of circular dependencies."""
    logger.info("Testing circular dependency detection...")
    
    graph = DependencyGraph()
    
    # Add nodes
    graph.add_node("a.py", {"path": "a.py"})
    graph.add_node("b.py", {"path": "b.py"})
    graph.add_node("c.py", {"path": "c.py"})
    
    # Create a circular dependency: a -> b -> c -> a
    graph.add_edge("a.py", "b.py")
    graph.add_edge("b.py", "c.py")
    graph.add_edge("c.py", "a.py")
    
    # Find cycles
    cycles = graph.find_cycles()
    
    # Verify cycle detection
    assert len(cycles) > 0, "Should have detected at least one cycle"
    
    # Run analysis
    with tempfile.TemporaryDirectory() as temp_dir:
        exporter = DependencyExporter(temp_dir)
        
        analysis_results = analyze_dependencies(graph, exporter)
        
        # Verify analysis identified the cycle
        assert analysis_results["has_cycles"] is True, "Analysis should detect cycles"
        assert len(analysis_results["cycles"]) > 0, "Analysis should include cycle information"
    
    return True

def test_self_referential_edge():
    """Test handling of self-referential edges."""
    logger.info("Testing self-referential edge handling...")
    
    graph = DependencyGraph()
    
    # Add a node
    graph.add_node("self_ref.py", {"path": "self_ref.py"})
    
    # Add a self-referential edge (should log a warning but still add it)
    result = graph.add_edge("self_ref.py", "self_ref.py")
    
    # Verify edge was added despite the warning
    assert result is True, "Should return True even for self-reference"
    assert "self_ref.py" in graph.edges["self_ref.py"], "Self-reference should be in edges"
    
    return True

def run_all_tests():
    """Run all the tests and report results."""
    tests = [
        test_invalid_edge_data,
        test_record_edge_error,
        test_circular_dependency_detection,
        test_self_referential_edge
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
    logger.info("=== TEST SUMMARY ===")
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")
    
    # Return overall success
    return all(result == "PASSED" for result in results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 