"""
Tests for the file tree extractor module.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codex_arch.extractors.file_tree_extractor import FileTreeExtractor, traverse_directory


class TestFileTreeExtractor(unittest.TestCase):
    """Test cases for the FileTreeExtractor class."""
    
    def setUp(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        
        # Create a test directory structure
        (self.test_dir / "dir1").mkdir()
        (self.test_dir / "dir1" / "file1.txt").write_text("test content")
        (self.test_dir / "dir1" / "file2.py").write_text("print('Hello world')")
        (self.test_dir / "dir2").mkdir()
        (self.test_dir / "dir2" / "subdir").mkdir()
        (self.test_dir / "dir2" / "subdir" / "file3.json").write_text("{}")
        (self.test_dir / ".hidden_dir").mkdir()
        (self.test_dir / ".hidden_file").write_text("hidden content")
        
    def tearDown(self):
        """Clean up the temporary directory."""
        self.temp_dir.cleanup()
        
    def test_extract_basic(self):
        """Test basic extraction functionality."""
        extractor = FileTreeExtractor(self.test_dir)
        result = extractor.extract()
        
        self.assertEqual(result["type"], "directory")
        self.assertEqual(result["name"], self.test_dir.name)
        
        # Should have 2 directories (dir1, dir2) but not .hidden_dir
        children = [c for c in result["children"] if c["type"] == "directory"]
        self.assertEqual(len(children), 2)
        
        # Should have no files at the root level (excluding .hidden_file)
        root_files = [c for c in result["children"] if c["type"] == "file"]
        self.assertEqual(len(root_files), 0)
        
    def test_include_hidden(self):
        """Test including hidden files and directories."""
        extractor = FileTreeExtractor(self.test_dir, include_hidden=True)
        result = extractor.extract()
        
        # Should now have 3 directories (dir1, dir2, .hidden_dir)
        children = [c for c in result["children"] if c["type"] == "directory"]
        self.assertEqual(len(children), 3)
        
        # Should have 1 file at the root level (.hidden_file)
        root_files = [c for c in result["children"] if c["type"] == "file"]
        self.assertEqual(len(root_files), 1)
        
    def test_max_depth(self):
        """Test the max_depth parameter."""
        extractor = FileTreeExtractor(self.test_dir, max_depth=1)
        result = extractor.extract()
        
        # Find dir2 in the result
        dir2 = next((c for c in result["children"] if c["name"] == "dir2"), None)
        self.assertIsNotNone(dir2)
        
        # dir2/subdir should not be in the result because of max_depth=1
        children = dir2.get("children", [])
        self.assertEqual(len(children), 0)
        
    def test_exclude_dirs(self):
        """Test excluding directories."""
        extractor = FileTreeExtractor(self.test_dir, exclude_dirs=["dir2"])
        result = extractor.extract()
        
        # Should only have 1 directory (dir1) but not dir2
        children = [c for c in result["children"] if c["type"] == "directory"]
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]["name"], "dir1")
        
    def test_include_extensions(self):
        """Test including only specific file extensions."""
        extractor = FileTreeExtractor(self.test_dir, include_extensions=[".py"])
        result = extractor.extract()
        
        # Find dir1 in the result
        dir1 = next((c for c in result["children"] if c["name"] == "dir1"), None)
        self.assertIsNotNone(dir1)
        
        # dir1 should only have file2.py (not file1.txt)
        files = [c for c in dir1["children"] if c["type"] == "file"]
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "file2.py")
        
    def test_to_json(self):
        """Test generating JSON output."""
        extractor = FileTreeExtractor(self.test_dir)
        json_output = extractor.to_json()
        
        # Verify that the output is valid JSON
        parsed = json.loads(json_output)
        self.assertEqual(parsed["type"], "directory")
        self.assertEqual(parsed["name"], self.test_dir.name)
        
    def test_to_markdown(self):
        """Test generating Markdown output."""
        extractor = FileTreeExtractor(self.test_dir)
        md_output = extractor.to_markdown()
        
        # Simple verification that the Markdown contains expected elements
        self.assertIn(self.test_dir.name, md_output)
        self.assertIn("dir1", md_output)
        self.assertIn("dir2", md_output)
        
    def test_legacy_traverse_directory(self):
        """Test the legacy traverse_directory function."""
        result = traverse_directory(self.test_dir, max_depth=2)
        
        self.assertEqual(result["type"], "directory")
        self.assertEqual(result["name"], self.test_dir.name)
        
        # Should have 2 directories (dir1, dir2) but not .hidden_dir
        children = [c for c in result["children"] if c["type"] == "directory"]
        self.assertEqual(len(children), 2)


if __name__ == "__main__":
    unittest.main() 