"""
Pytest configuration file with common fixtures and utilities for testing.
"""

import os
import sys
import json
import tempfile
import logging
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure that the project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Mock the missing analyzer module to avoid import errors
class MockAnalyzer:
    @staticmethod
    def run_analysis(*args, **kwargs):
        return {"status": "success", "mock": True}

# Create the mock module
sys.modules['codex_arch.analyzer'] = MagicMock()
sys.modules['codex_arch.analyzer'].run_analysis = MockAnalyzer.run_analysis

@pytest.fixture
def temp_dir():
    """Provides a temporary directory for tests that is automatically cleaned up."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_project_dir(temp_dir):
    """
    Creates a sample project directory structure for testing.
    
    The sample project includes:
    - Python files with imports
    - Subdirectories with more files
    - Various file types for testing metrics and file tree extraction
    """
    # Create a simple directory structure
    project_dir = temp_dir / "sample_project"
    project_dir.mkdir()
    
    # Create subdirectories
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()
    
    # Create Python files with imports
    main_py = """
import os
import sys
from src.utils import helper_function

def main():
    print("Hello, world!")
    helper_function()

if __name__ == "__main__":
    main()
"""
    
    utils_py = """
import json
import datetime

def helper_function():
    print("Helper function called")
    return datetime.datetime.now()
"""
    
    test_py = """
import unittest
from src.utils import helper_function

class TestHelperFunction(unittest.TestCase):
    def test_helper(self):
        result = helper_function()
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
"""
    
    # Write the files
    (project_dir / "main.py").write_text(main_py)
    (project_dir / "src" / "utils.py").write_text(utils_py)
    (project_dir / "tests" / "test_utils.py").write_text(test_py)
    
    # Create a README file
    readme_md = "# Sample Project\n\nThis is a sample project for testing purposes."
    (project_dir / "README.md").write_text(readme_md)
    
    # Create a config file
    config_json = json.dumps({
        "name": "sample_project",
        "version": "0.1.0",
        "description": "Sample project for testing"
    }, indent=2)
    (project_dir / "config.json").write_text(config_json)
    
    return project_dir


@pytest.fixture
def git_repo_dir(temp_dir):
    """
    Creates a fake Git repository directory for testing Git-related features.
    
    Note: This doesn't actually initialize a Git repo, just the directory structure
    that would be expected. For actual Git operations, use the mock_git fixture.
    """
    repo_dir = temp_dir / "git_repo"
    repo_dir.mkdir()
    
    # Create .git directory
    (repo_dir / ".git").mkdir()
    
    # Create some content
    (repo_dir / "file1.py").write_text("print('Hello, world!')")
    (repo_dir / "file2.py").write_text("# This is a comment\nprint('Another file')")
    
    return repo_dir


@pytest.fixture
def mock_git(mocker):
    """
    Provides a mock for GitPython (git.Repo) to simulate git operations without
    requiring an actual git repository.
    """
    # Create a mock Repo object
    mock_repo = mocker.MagicMock()
    
    # Mock git.Repo.init and git.Repo
    mock_repo_class = mocker.patch('git.Repo')
    mock_repo_class.init.return_value = mock_repo
    mock_repo_class.return_value = mock_repo
    
    # Mock some common git operations
    mock_repo.git.diff.return_value = "file1.py\nfile2.py"
    mock_repo.git.show.return_value = "Some changed content"
    mock_repo.git.log.return_value = "commit abc123\nAuthor: Test\nDate: 2023-01-01\n\nTest commit"
    
    # Mock the index for staging files
    mock_index = mocker.MagicMock()
    mock_repo.index = mock_index
    
    return mock_repo


@pytest.fixture
def mock_flask_app(mocker):
    """
    Creates a mock Flask application for testing API-related features.
    """
    # Mock Flask app and necessary components
    mock_app = mocker.MagicMock()
    mock_request = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    
    # Mock Flask imports
    mocker.patch('flask.Flask', return_value=mock_app)
    mocker.patch('flask.request', mock_request)
    mocker.patch('flask.jsonify', lambda x: mock_response)
    
    # Configure mock behavior
    mock_app.route = mocker.MagicMock()
    mock_request.json = {}
    mock_request.args = {}
    mock_request.headers = {}
    
    return mock_app 