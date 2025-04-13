"""
Tests for the change detection module.
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from codex_arch.change_detection.git_changes import GitChangeDetector
from codex_arch.change_detection.caching import CacheManager


class TestGitChangeDetector:
    """Test cases for the GitChangeDetector class."""

    def test_initialization(self):
        """Test basic initialization of the GitChangeDetector."""
        detector = GitChangeDetector()
        assert detector is not None
        assert detector.repo_path is None
        assert detector.verbose is False

    def test_initialization_with_params(self):
        """Test initialization with custom parameters."""
        detector = GitChangeDetector(repo_path="/test/repo", verbose=True)
        assert detector.repo_path == Path("/test/repo")
        assert detector.verbose is True

    def test_detect_changes_with_mock_git(self, mock_git, git_repo_dir):
        """Test detecting changes using a mocked git repository."""
        # Configure mock
        mock_git.git.diff.return_value = "file1.py\nfile2.py"
        
        # Run the change detector
        detector = GitChangeDetector(repo_path=git_repo_dir)
        changes = detector.detect_changes(since="HEAD~1")
        
        # Verify the changes were detected
        assert changes is not None
        assert len(changes) == 2
        assert "file1.py" in changes
        assert "file2.py" in changes

    def test_detect_changes_with_custom_ref(self, mock_git, git_repo_dir):
        """Test detecting changes using a custom git reference."""
        # Configure mock with different output for custom ref
        def mock_diff_call(param):
            if param == "--name-only HEAD~2":
                return "file3.py\nfile4.py"
            return "file1.py\nfile2.py"
        
        mock_git.git.diff.side_effect = mock_diff_call
        
        # Run with custom reference
        detector = GitChangeDetector(repo_path=git_repo_dir)
        changes = detector.detect_changes(since="HEAD~2")
        
        # Verify the custom reference was used
        mock_git.git.diff.assert_called_with("--name-only HEAD~2")
        assert len(changes) == 2
        assert "file3.py" in changes or "file4.py" in changes

    def test_detect_changes_empty_result(self, mock_git, git_repo_dir):
        """Test handling of no changes detected."""
        # Configure mock to return empty result
        mock_git.git.diff.return_value = ""
        
        detector = GitChangeDetector(repo_path=git_repo_dir)
        changes = detector.detect_changes()
        
        # Verify empty changes list
        assert changes is not None
        assert len(changes) == 0

    def test_detect_changes_with_error(self, mock_git, git_repo_dir):
        """Test error handling during change detection."""
        # Configure mock to raise an exception
        mock_git.git.diff.side_effect = Exception("Git command failed")
        
        detector = GitChangeDetector(repo_path=git_repo_dir)
        
        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            detector.detect_changes()
        
        assert "Git command failed" in str(exc_info.value)

    def test_get_file_content_at_revision(self, mock_git, git_repo_dir):
        """Test retrieving file content at a specific revision."""
        # Configure mock for git show
        mock_git.git.show.return_value = "def test_function():\n    return True"
        
        detector = GitChangeDetector(repo_path=git_repo_dir)
        content = detector.get_file_content_at_revision("file1.py", "HEAD~1")
        
        # Verify the content was retrieved
        assert content is not None
        assert "def test_function()" in content
        assert "return True" in content
        
        # Verify the correct git command was called
        mock_git.git.show.assert_called_with("HEAD~1:file1.py")

    def test_get_file_content_error(self, mock_git, git_repo_dir):
        """Test error handling when retrieving file content."""
        # Configure mock to raise an exception
        mock_git.git.show.side_effect = Exception("File not found in revision")
        
        detector = GitChangeDetector(repo_path=git_repo_dir)
        
        # Verify exception is raised
        with pytest.raises(Exception) as exc_info:
            detector.get_file_content_at_revision("file1.py", "HEAD~1")
        
        assert "File not found in revision" in str(exc_info.value)


class TestCacheManager:
    """Test cases for the CacheManager class."""

    def test_initialization(self):
        """Test basic initialization of the CacheManager."""
        cache_manager = CacheManager()
        assert cache_manager is not None
        assert cache_manager.cache_dir is not None
        assert not cache_manager.cache_file.exists()  # Default file should not exist yet

    def test_initialization_with_params(self, temp_dir):
        """Test initialization with custom parameters."""
        cache_dir = temp_dir / "custom_cache"
        cache_manager = CacheManager(cache_dir=cache_dir)
        assert cache_manager.cache_dir == cache_dir
        assert str(cache_manager.cache_file).startswith(str(cache_dir))

    def test_save_load_cache(self, temp_dir):
        """Test saving and loading cache data."""
        cache_dir = temp_dir / "test_cache"
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Create test data
        test_data = {
            "metrics": {"files": 10, "lines": 1000},
            "last_commit": "abc123"
        }
        
        # Save the data
        cache_manager.save_cache(test_data)
        
        # Verify cache file exists
        assert cache_manager.cache_file.exists()
        
        # Load the data and verify it matches
        loaded_data = cache_manager.load_cache()
        assert loaded_data is not None
        assert loaded_data == test_data
        assert loaded_data["metrics"]["files"] == 10
        assert loaded_data["metrics"]["lines"] == 1000
        assert loaded_data["last_commit"] == "abc123"

    def test_load_nonexistent_cache(self, temp_dir):
        """Test loading cache when file doesn't exist."""
        cache_dir = temp_dir / "nonexistent_cache"
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Load without creating first
        loaded_data = cache_manager.load_cache()
        
        # Verify default empty data is returned
        assert loaded_data is not None
        assert loaded_data == {}

    def test_corrupted_cache_file(self, temp_dir):
        """Test handling of corrupted cache file."""
        cache_dir = temp_dir / "corrupted_cache"
        cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Create a corrupted JSON file
        cache_file = cache_dir / "cache.json"
        with open(cache_file, 'w') as f:
            f.write("{ this is not valid JSON }")
        
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Load should handle the corruption and return empty dict
        loaded_data = cache_manager.load_cache()
        assert loaded_data == {}

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_cache_write_error(self, mock_json_dump, mock_file, temp_dir):
        """Test error handling during cache write operations."""
        # Configure mock to raise an exception
        mock_json_dump.side_effect = Exception("Write error")
        
        cache_dir = temp_dir / "error_cache"
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Attempt to save cache
        test_data = {"key": "value"}
        result = cache_manager.save_cache(test_data)
        
        # Verify error was handled
        assert result is False

    def test_cache_update(self, temp_dir):
        """Test updating specific fields in the cache."""
        cache_dir = temp_dir / "update_cache"
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Initial data
        initial_data = {
            "metrics": {"files": 10, "lines": 1000},
            "last_commit": "abc123"
        }
        cache_manager.save_cache(initial_data)
        
        # Update specific field
        cache_manager.update_cache("last_commit", "def456")
        
        # Load and verify update
        loaded_data = cache_manager.load_cache()
        assert loaded_data["last_commit"] == "def456"
        assert loaded_data["metrics"]["files"] == 10  # Should be unchanged

    def test_clear_cache(self, temp_dir):
        """Test clearing the cache."""
        cache_dir = temp_dir / "clear_cache"
        cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Create initial data
        test_data = {"key": "value"}
        cache_manager.save_cache(test_data)
        assert cache_manager.cache_file.exists()
        
        # Clear cache
        cache_manager.clear_cache()
        
        # Verify cache file is removed
        assert not cache_manager.cache_file.exists()
        
        # Load should return empty dict
        loaded_data = cache_manager.load_cache()
        assert loaded_data == {} 