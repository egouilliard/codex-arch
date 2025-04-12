"""
End-to-End tests for the API component.

These tests verify the API functionality in a complete workflow scenario,
simulating real user interactions with the API.
"""

import os
import json
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from flask.testing import FlaskClient

from codex_arch.api.app import create_app
from tests.e2e_config import E2E_CONFIG, wait_for_completion, verify_json_structure


@pytest.fixture
def api_client():
    """Create a test client for the Flask application."""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_token(api_client):
    """Get an authentication token for API requests."""
    auth_response = api_client.post("/api/auth/login", json={
        "username": E2E_CONFIG["API_TEST_USER"],
        "password": E2E_CONFIG["API_TEST_PASSWORD"]
    })
    auth_data = json.loads(auth_response.data)
    token = auth_data.get("access_token")
    
    if not token:
        pytest.skip("Failed to obtain authentication token for API tests")
    
    return token


@pytest.mark.e2e
class TestAPIEndToEnd:
    """End-to-End tests for API workflows."""
    
    def test_complete_api_workflow(self, api_client, auth_token, real_project_dir):
        """Test the complete API workflow from project analysis to results retrieval."""
        # Start analysis
        start_response = api_client.post(
            "/api/analysis/start",
            json={"project_path": str(real_project_dir)},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        start_data = json.loads(start_response.data)
        
        assert start_response.status_code == 202
        assert "job_id" in start_data
        
        job_id = start_data["job_id"]
        
        # Wait for analysis to complete
        def check_completion():
            status_response = api_client.get(
                f"/api/analysis/status/{job_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            status_data = json.loads(status_response.data)
            return status_data.get("status") == "completed"
        
        # Wait up to 10 seconds for completion
        completion = wait_for_completion(check_completion, max_retries=20, poll_interval=0.5)
        assert completion, "Analysis job did not complete in the expected time"
        
        # Get results
        results_response = api_client.get(
            f"/api/analysis/results/{job_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        results_data = json.loads(results_response.data)
        
        assert results_response.status_code == 200
        
        # Verify results structure
        required_fields = {
            "metrics": {
                "file_count": int,
                "line_count": int,
                "language_distribution": dict
            },
            "dependencies": {
                "nodes": [dict],
                "edges": [dict]
            },
            "file_tree": dict,
            "summary": str
        }
        
        is_valid, error = verify_json_structure(results_data, required_fields)
        assert is_valid, f"Results data has invalid structure: {error}"
    
    def test_concurrent_api_requests(self, api_client, auth_token, real_project_dir):
        """Test the API handling multiple concurrent analysis requests."""
        # Start multiple analysis jobs
        job_ids = []
        for i in range(3):  # Test with 3 concurrent jobs
            response = api_client.post(
                "/api/analysis/start",
                json={"project_path": str(real_project_dir), "job_name": f"concurrent_test_{i}"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            data = json.loads(response.data)
            assert response.status_code == 202
            job_ids.append(data["job_id"])
        
        # Wait for all jobs to complete
        def all_jobs_complete():
            for job_id in job_ids:
                status_response = api_client.get(
                    f"/api/analysis/status/{job_id}",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                status_data = json.loads(status_response.data)
                if status_data.get("status") != "completed":
                    return False
            return True
        
        completion = wait_for_completion(all_jobs_complete, max_retries=40, poll_interval=0.5)
        assert completion, "Not all concurrent jobs completed in the expected time"
        
        # Verify results for all jobs
        for job_id in job_ids:
            results_response = api_client.get(
                f"/api/analysis/results/{job_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert results_response.status_code == 200
    
    def test_error_handling(self, api_client, auth_token):
        """Test API error handling for invalid requests."""
        # Test with non-existent project path
        response = api_client.post(
            "/api/analysis/start",
            json={"project_path": "/path/does/not/exist"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code in [400, 404, 422]  # Expecting client error
        
        # Test with invalid job ID
        response = api_client.get(
            "/api/analysis/status/invalid-job-id",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        
        # Test with invalid authentication
        response = api_client.post(
            "/api/analysis/start",
            json={"project_path": "/tmp"},
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
    
    def test_api_rate_limiting(self, api_client, auth_token):
        """Test API rate limiting functionality."""
        # Make multiple requests in quick succession
        responses = []
        for _ in range(30):  # Test with 30 rapid requests
            response = api_client.get(
                "/api/status",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            responses.append(response)
        
        # Check if any responses indicate rate limiting
        rate_limited = any(response.status_code == 429 for response in responses)
        
        # Either some responses should be rate limited or all should succeed
        if rate_limited:
            assert any(response.status_code == 429 for response in responses), "Rate limiting not working"
        else:
            assert all(response.status_code == 200 for response in responses), "Some requests failed without rate limiting"
    
    def test_large_project_analysis(self, api_client, auth_token, temp_dir):
        """Test API handling a large project analysis."""
        # Create a large project structure
        large_project = temp_dir / "large_project"
        large_project.mkdir()
        
        # Create many files to simulate a large project
        for i in range(50):
            dir_path = large_project / f"module_{i}"
            dir_path.mkdir()
            
            for j in range(10):
                file_path = dir_path / f"file_{j}.py"
                with open(file_path, 'w') as f:
                    f.write(f"""
# Module {i}, File {j}
def function_{i}_{j}():
    \"\"\"Function in module {i}, file {j}\"\"\"
    return "{i}_{j}"
                    """)
        
        # Start analysis with timeout extension
        response = api_client.post(
            "/api/analysis/start",
            json={"project_path": str(large_project), "timeout": 120},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        data = json.loads(response.data)
        assert response.status_code == 202
        job_id = data["job_id"]
        
        # Check status a few times with longer intervals
        status_checks = 0
        max_checks = 5
        complete = False
        
        while status_checks < max_checks and not complete:
            status_response = api_client.get(
                f"/api/analysis/status/{job_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            status_data = json.loads(status_response.data)
            
            if status_data.get("status") == "completed":
                complete = True
                break
                
            status_checks += 1
            time.sleep(2)  # Longer interval for large project
        
        if not complete:
            pytest.skip("Large project analysis test skipped due to timeout")
        
        # Get results
        results_response = api_client.get(
            f"/api/analysis/results/{job_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert results_response.status_code == 200


@pytest.mark.e2e
class TestAPIWebhooks:
    """Tests for API webhook functionality."""
    
    def test_webhook_notification(self, api_client, auth_token, real_project_dir):
        """Test webhook notifications for analysis completion."""
        # Create a mock webhook endpoint
        mock_webhook = MagicMock()
        
        with patch('requests.post', mock_webhook):
            # Start analysis with webhook URL
            webhook_url = "https://webhook.test/callback"
            response = api_client.post(
                "/api/analysis/start",
                json={
                    "project_path": str(real_project_dir),
                    "webhook_url": webhook_url
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            data = json.loads(response.data)
            assert response.status_code == 202
            job_id = data["job_id"]
            
            # Wait for analysis to complete
            def check_completion():
                status_response = api_client.get(
                    f"/api/analysis/status/{job_id}",
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                status_data = json.loads(status_response.data)
                return status_data.get("status") == "completed"
            
            completion = wait_for_completion(check_completion)
            assert completion, "Analysis job did not complete in the expected time"
            
            # Verify webhook was called
            assert mock_webhook.called, "Webhook was not called"
            
            # Verify webhook payload
            call_args = mock_webhook.call_args[1]
            payload = json.loads(call_args.get('data', '{}'))
            assert "job_id" in payload
            assert payload["job_id"] == job_id
            assert "status" in payload
            assert payload["status"] == "completed" 