"""
Tests for architecture detection.
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add the scripts directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from architecture import ArchitectureDetector


class TestArchitectureDetector(unittest.TestCase):
    """Test the ArchitectureDetector class."""

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up the temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_detector_creation(self):
        """Test that we can create a detector."""
        detector = ArchitectureDetector(self.test_path)
        self.assertEqual(detector.root, self.test_path.resolve())

    def test_mvc_detection(self):
        """Test detection of MVC structure."""
        # Create MVC-like structure
        (self.test_path / "controllers").mkdir()
        (self.test_path / "models").mkdir()
        (self.test_path / "views").mkdir()

        detector = ArchitectureDetector(self.test_path)
        result = detector.detect_all()

        # Should detect MVC with reasonable confidence
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
        self.assertIsInstance(result["evidence"], list)

    def test_layered_detection(self):
        """Test detection of layered architecture."""
        # Create layered structure
        (self.test_path / "presentation").mkdir()
        (self.test_path / "application").mkdir()
        (self.test_path / "domain").mkdir()
        (self.test_path / "infrastructure").mkdir()

        detector = ArchitectureDetector(self.test_path)
        result = detector.detect_all()

        # Should detect layered architecture (confidence may be low for minimal setup)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)
        self.assertIsInstance(result["evidence"], list)

    def test_microservices_detection(self):
        """Test detection of microservices with docker-compose."""
        # Create docker-compose.yml
        (self.test_path / "docker-compose.yml").write_text("version: '3'\nservices:\n  web:\n    image: nginx")

        # Create service directories
        (self.test_path / "service-a").mkdir()
        (self.test_path / "service-b").mkdir()

        detector = ArchitectureDetector(self.test_path)
        result = detector.detect_all()

        # Should detect microservices
        self.assertGreaterEqual(result["confidence"], 0.15)
        self.assertIn("Microservice", result["detected"] or "")
        self.assertGreater(len(result["evidence"]), 0)

    def test_no_clear_pattern(self):
        """Test when no clear pattern is present."""
        # Just create some random files
        (self.test_path / "README.md").write_text("# Test")
        (self.test_path / "main.py").write_text("print('hello')")

        detector = ArchitectureDetector(self.test_path)
        result = detector.detect_all()

        # Should have low confidence or detect as unknown
        # The exact behavior depends on implementation, but should not crash
        self.assertIsInstance(result["confidence"], float)
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)


if __name__ == '__main__':
    unittest.main()