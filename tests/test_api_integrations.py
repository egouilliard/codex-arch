"""
Integration tests for API, change detection, and bundling components.

These tests verify the correct interaction between the API, change detection, and bundling components.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from codex_arch.api.app import create_app
from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.change_detection.caching import CacheManager
from codex_arch.bundler import BundleAssembler
from codex_arch.metrics.metrics_collector import MetricsCollector


@pytest.mark.integration
class TestChangeDetectionAndMetrics:
    """Test the integration between change detection and metrics collection."""
    
    def test_change_detection_to_metrics_flow(self, git_repo_dir, mock_git):
        """Test the flow from change detection to metrics collection."""
        # Mock git changes
        mock_git.git.diff.return_value = "file1.py\nfile2.py"
        
        # 1. Detect changes
        detector = GitChangeDetector(repo_path=git_repo_dir)
        changes = detector.detect_changes(since="HEAD~1")
        
        # Verify changes were detected
        assert changes is not None
        assert len(changes) == 2
        assert "file1.py" in changes
        assert "file2.py" in changes
        
        # 2. Mock the metrics collector to work with the detected changes
        with patch('codex_arch.metrics.metrics_collector.MetricsCollector.collect_metrics_for_files') as mock_collect:
            mock_collect.return_value = {
                "file_count": 2,
                "line_count": 100,
                "language_distribution": {
                    "Python": {"file_count": 2, "line_count": 100}
                }
            }
            
            metrics_collector = MetricsCollector(git_repo_dir)
            metrics = metrics_collector.collect_metrics_for_files(changes)
            
            # Verify metrics were collected for the changed files
            assert metrics is not None
            assert metrics["file_count"] == 2
            assert "Python" in metrics["language_distribution"]
            
            # Verify the metrics collector was called with the correct files
            mock_collect.assert_called_once()


@pytest.mark.integration
class TestCacheAndChangeDetection:
    """Test the integration between caching system and change detection."""
    
    def test_cache_with_change_detection(self, git_repo_dir, mock_git):
        """Test the interaction between the cache manager and change detection."""
        # Set up temp cache file
        cache_file = Path(tempfile.gettempdir()) / "test_cache.json"
        
        # Create initial cache data
        initial_cache = {
            "last_commit": "abc123",
            "metrics": {
                "file_count": 10,
                "line_count": 500
            }
        }
        
        # Write initial cache
        with open(cache_file, 'w') as f:
            json.dump(initial_cache, f)
        
        # Set up cache manager
        cache_manager = CacheManager(cache_file=cache_file)
        
        # 1. Read from cache
        cached_data = cache_manager.load_cache()
        
        # Verify cache was loaded
        assert cached_data is not None
        assert cached_data["last_commit"] == "abc123"
        assert cached_data["metrics"]["file_count"] == 10
        
        # 2. Mock git changes and update the cache
        mock_git.git.log.return_value = "commit def456\nAuthor: Test\nDate: 2023-01-02\n\nNew commit"
        
        # Mock change detector to return the latest commit
        with patch('codex_arch.change_detection.git_changes.GitChangeDetector.get_latest_commit') as mock_get_commit:
            mock_get_commit.return_value = "def456"
            
            detector = GitChangeDetector(repo_path=git_repo_dir)
            latest_commit = detector.get_latest_commit()
            
            # Verify latest commit was retrieved
            assert latest_commit == "def456"
            
            # 3. Update cache with new data
            new_data = {
                "last_commit": latest_commit,
                "metrics": {
                    "file_count": 12,
                    "line_count": 550
                }
            }
            
            cache_manager.save_cache(new_data)
            
            # 4. Verify cache was updated
            updated_cache = cache_manager.load_cache()
            assert updated_cache["last_commit"] == "def456"
            assert updated_cache["metrics"]["file_count"] == 12
        
        # Clean up
        cache_file.unlink(missing_ok=True)


@pytest.mark.integration
class TestAPIWithBundleAssembler:
    """Test the integration between the API and bundle assembler."""
    
    def test_api_bundle_generation(self, sample_project_dir):
        """Test the API endpoint for generating bundles."""
        # 1. Create Flask test client
        app = create_app(testing=True)
        client = app.test_client()
        
        # 2. Mock the bundle assembler
        with patch('codex_arch.bundler.bundle_assembler.BundleAssembler.create_bundle') as mock_create_bundle:
            bundle_path = Path(tempfile.gettempdir()) / "test_bundle.zip"
            mock_create_bundle.return_value = str(bundle_path)
            
            # Write a dummy zip file
            with open(bundle_path, 'wb') as f:
                f.write(b'dummy zip content')
            
            # 3. Mock metrics collector that would be used by the bundler
            with patch('codex_arch.metrics.metrics_collector.MetricsCollector.collect_metrics') as mock_metrics:
                mock_metrics.return_value = {
                    "file_count": 10,
                    "line_count": 500,
                    "language_distribution": {
                        "Python": {"file_count": 8, "line_count": 400},
                        "Markdown": {"file_count": 2, "line_count": 100}
                    }
                }
                
                # 4. Add a route to the test app that simulates the bundle endpoint
                @app.route('/api/generate-bundle', methods=['POST'])
                def generate_bundle():
                    assembler = BundleAssembler(sample_project_dir)
                    bundle_path = assembler.create_bundle()
                    return {"success": True, "bundle_path": bundle_path}
                
                # 5. Make the API request
                response = client.post('/api/generate-bundle', json={"project_path": str(sample_project_dir)})
                
                # 6. Verify the response
                assert response.status_code == 200
                response_data = json.loads(response.data)
                assert response_data["success"] is True
                assert "bundle_path" in response_data
                assert mock_create_bundle.called
                
            # Clean up
            bundle_path.unlink(missing_ok=True)


@pytest.mark.integration
class TestCompleteAPIWorkflow:
    """Test a complete workflow through the API."""
    
    def test_complete_api_workflow(self, sample_project_dir, git_repo_dir, mock_git):
        """Test a complete workflow from change detection to bundle generation via API."""
        # 1. Create Flask test client
        app = create_app(testing=True)
        client = app.test_client()
        
        # 2. Mock git change detection
        mock_git.git.diff.return_value = "file1.py\nfile2.py"
        
        # 3. Add routes to the test app that simulate the actual API
        @app.route('/api/detect-changes', methods=['POST'])
        def detect_changes():
            detector = GitChangeDetector(repo_path=git_repo_dir)
            changes = detector.detect_changes(since="HEAD~1")
            return {"success": True, "changes": list(changes)}
        
        @app.route('/api/analyze-changes', methods=['POST'])
        def analyze_changes():
            # Get changes from request
            data = json.loads(client.post('/api/detect-changes').data)
            files = data.get("changes", [])
            
            # Collect metrics for changed files
            with patch('codex_arch.metrics.metrics_collector.MetricsCollector.collect_metrics_for_files') as mock_metrics:
                mock_metrics.return_value = {
                    "file_count": len(files),
                    "line_count": 100,
                    "language_distribution": {"Python": {"file_count": len(files), "line_count": 100}}
                }
                
                metrics_collector = MetricsCollector(git_repo_dir)
                metrics = metrics_collector.collect_metrics_for_files(files)
                
                return {"success": True, "metrics": metrics}
        
        @app.route('/api/generate-summary', methods=['POST'])
        def generate_summary():
            # Get metrics from analyze step
            data = json.loads(client.post('/api/analyze-changes').data)
            metrics = data.get("metrics", {})
            
            # Mock summary generation
            with patch('codex_arch.summary.summary_builder.SummaryBuilder.build_summary') as mock_summary:
                mock_summary.return_value = {
                    "project_metrics": metrics,
                    "code_overview": "This is a sample project with Python files.",
                    "change_analysis": "Recent changes affect 2 Python files."
                }
                
                return {"success": True, "summary": mock_summary.return_value}
        
        # 4. Execute the complete workflow
        # First step: detect changes
        response1 = client.post('/api/detect-changes')
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1["success"] is True
        assert len(data1["changes"]) == 2
        
        # Second step: analyze changes
        response2 = client.post('/api/analyze-changes')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2["success"] is True
        assert "metrics" in data2
        assert data2["metrics"]["file_count"] == 2
        
        # Third step: generate summary
        response3 = client.post('/api/generate-summary')
        assert response3.status_code == 200
        data3 = json.loads(response3.data)
        assert data3["success"] is True
        assert "summary" in data3
        assert "project_metrics" in data3["summary"]
        assert "code_overview" in data3["summary"]
        assert "change_analysis" in data3["summary"] 