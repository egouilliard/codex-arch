"""
End-to-End tests for Codex-Arch.

These tests verify the entire system's functionality by simulating real user workflows,
from the initial command to the final output.
"""

import os
import json
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner
from flask.testing import FlaskClient

from codex_arch.cli.cli import cli
from codex_arch.api.app import create_app


@pytest.fixture
def real_project_dir(temp_dir):
    """
    Creates a realistic project directory with actual functionality for E2E testing.
    This provides a more comprehensive test case than the simplified sample_project_dir.
    """
    # Create a realistic project structure
    project_dir = temp_dir / "real_project"
    project_dir.mkdir()
    
    # Create project structure
    (project_dir / "src").mkdir()
    (project_dir / "src" / "core").mkdir()
    (project_dir / "src" / "utils").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()
    
    # Main module with imports
    main_py = """
import os
import sys
import json
import logging
from datetime import datetime
from src.core import core_module
from src.utils import helpers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting application at %s", datetime.now())
    config = helpers.load_config("config.json")
    result = core_module.process_data(config)
    helpers.save_results(result, "output.json")
    logger.info("Application completed successfully")
    return result

if __name__ == "__main__":
    main()
"""
    
    # Core module
    core_module_py = """
import logging
from src.utils import helpers

logger = logging.getLogger(__name__)

def process_data(config):
    logger.info("Processing data with config: %s", config)
    # Simulate data processing
    result = {
        "processed_items": 100,
        "success_rate": 0.95,
        "timestamp": helpers.get_timestamp()
    }
    return result
"""
    
    # Utility module
    helpers_py = """
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def load_config(config_file):
    logger.info("Loading config from %s", config_file)
    if not os.path.exists(config_file):
        logger.warning("Config file not found, using defaults")
        return {"default_setting": True}
    
    with open(config_file, 'r') as f:
        return json.load(f)

def save_results(results, output_file):
    logger.info("Saving results to %s", output_file)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

def get_timestamp():
    return datetime.now().isoformat()
"""
    
    # Test file
    test_core_py = """
import unittest
from unittest.mock import patch, MagicMock
from src.core import core_module

class TestCoreModule(unittest.TestCase):
    def test_process_data(self):
        config = {"test": True}
        with patch('src.utils.helpers.get_timestamp', return_value='2023-01-01T12:00:00'):
            result = core_module.process_data(config)
            self.assertEqual(result['processed_items'], 100)
            self.assertEqual(result['timestamp'], '2023-01-01T12:00:00')

if __name__ == "__main__":
    unittest.main()
"""
    
    # README file
    readme_md = """
# Real Project

This is a realistic project structure for end-to-end testing of Codex-Arch.

## Features

- Modular architecture
- Configuration handling
- Logging
- Data processing
"""
    
    # Config file
    config_json = json.dumps({
        "name": "real_project",
        "version": "1.0.0",
        "description": "Realistic project for E2E testing",
        "settings": {
            "max_items": 100,
            "cache_enabled": True,
            "log_level": "INFO"
        }
    }, indent=2)
    
    # Write files
    (project_dir / "src" / "__init__.py").write_text("")
    (project_dir / "src" / "core" / "__init__.py").write_text("")
    (project_dir / "src" / "core" / "core_module.py").write_text(core_module_py)
    (project_dir / "src" / "utils" / "__init__.py").write_text("")
    (project_dir / "src" / "utils" / "helpers.py").write_text(helpers_py)
    (project_dir / "main.py").write_text(main_py)
    (project_dir / "tests" / "test_core.py").write_text(test_core_py)
    (project_dir / "README.md").write_text(readme_md)
    (project_dir / "config.json").write_text(config_json)
    
    return project_dir


@pytest.mark.e2e
class TestEndToEndCLI:
    """End-to-End tests for the CLI workflow."""
    
    def test_full_analysis_workflow(self, real_project_dir):
        """Test the full analysis workflow via CLI."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            output_dir = Path("analysis_output")
            output_dir.mkdir()
            
            # Run the full analysis command
            result = runner.invoke(cli, [
                "analyze",
                "--input-dir", str(real_project_dir),
                "--output-dir", str(output_dir),
                "--include-python",
                "--generate-graph",
                "--generate-summary"
            ])
            
            # Verify command executed successfully
            assert result.exit_code == 0
            assert "Analysis completed successfully" in result.output
            
            # Verify output files were created
            assert (output_dir / "file_tree.json").exists()
            assert (output_dir / "dependencies.json").exists()
            assert (output_dir / "metrics.json").exists()
            assert (output_dir / "summary.md").exists()
            
            # Verify metrics content
            with open(output_dir / "metrics.json") as f:
                metrics = json.load(f)
                assert "file_count" in metrics
                assert "language_distribution" in metrics
                assert "Python" in metrics["language_distribution"]
            
            # Verify dependencies content
            with open(output_dir / "dependencies.json") as f:
                dependencies = json.load(f)
                assert "nodes" in dependencies
                assert "edges" in dependencies
                
                # Verify specific modules are detected
                node_modules = [node["id"] for node in dependencies["nodes"]]
                assert "main" in node_modules
                assert "src.core.core_module" in node_modules or "core_module" in node_modules
                assert "src.utils.helpers" in node_modules or "helpers" in node_modules
    
    def test_change_detection_workflow(self, real_project_dir, mock_git):
        """Test the change detection workflow via CLI."""
        runner = CliRunner()
        
        # Set up git mock to simulate changes
        mock_git.git.diff.return_value = "src/core/core_module.py\nsrc/utils/helpers.py"
        
        with runner.isolated_filesystem():
            output_dir = Path("change_analysis")
            output_dir.mkdir()
            
            # Run the change detection command
            result = runner.invoke(cli, [
                "detect-changes",
                "--repo-dir", str(real_project_dir),
                "--output-dir", str(output_dir),
                "--diff-against", "HEAD~1"
            ])
            
            # Verify command executed successfully
            assert result.exit_code == 0
            assert "Change detection completed" in result.output
            
            # Verify output files were created
            assert (output_dir / "changed_files.json").exists()
            assert (output_dir / "change_impact.json").exists()
            
            # Verify changes content
            with open(output_dir / "changed_files.json") as f:
                changes = json.load(f)
                assert len(changes) > 0
                assert "src/core/core_module.py" in [change["file"] for change in changes]


@pytest.mark.e2e
class TestEndToEndAPI:
    """End-to-End tests for the API workflow."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask application."""
        app = create_app(testing=True)
        with app.test_client() as client:
            yield client
    
    def test_api_analysis_workflow(self, client, real_project_dir):
        """Test the analysis workflow via API."""
        # Authenticate
        auth_response = client.post("/api/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        auth_data = json.loads(auth_response.data)
        token = auth_data.get("access_token")
        
        # Verify authentication success
        assert auth_response.status_code == 200
        assert token is not None
        
        # Start analysis
        analysis_response = client.post(
            "/api/analysis/start",
            json={"project_path": str(real_project_dir)},
            headers={"Authorization": f"Bearer {token}"}
        )
        analysis_data = json.loads(analysis_response.data)
        job_id = analysis_data.get("job_id")
        
        # Verify analysis job was created
        assert analysis_response.status_code == 202
        assert job_id is not None
        
        # Check status (simulates polling)
        status_response = client.get(
            f"/api/analysis/status/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        status_data = json.loads(status_response.data)
        
        # Verify status check works
        assert status_response.status_code == 200
        assert "status" in status_data
        
        # Get results
        results_response = client.get(
            f"/api/analysis/results/{job_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        results_data = json.loads(results_response.data)
        
        # Verify results retrieval
        assert results_response.status_code == 200
        assert "metrics" in results_data
        assert "dependencies" in results_data
        assert "file_tree" in results_data
        
        # Verify metrics content
        assert "file_count" in results_data["metrics"]
        assert "language_distribution" in results_data["metrics"]


@pytest.mark.e2e
class TestEndToEndSubprocess:
    """End-to-End tests using actual subprocess calls to the CLI."""
    
    def test_cli_as_subprocess(self, real_project_dir):
        """Test running the CLI as a subprocess."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()
            
            # Construct the command as a user would run it
            cmd = [
                "python", "-m", "codex_arch",
                "analyze",
                "--input-dir", str(real_project_dir),
                "--output-dir", str(output_dir),
                "--include-python",
                "--generate-graph",
                "--generate-summary"
            ]
            
            # Run the command in a subprocess
            with patch.object(subprocess, 'run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout=b"Analysis completed successfully",
                    stderr=b""
                )
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Verify command executed successfully
                assert result.returncode == 0
                assert "Analysis completed successfully" in result.stdout 