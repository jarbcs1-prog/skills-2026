"""
Basic tests for project-analyst functionality.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path

# Add the scripts directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scanner import ProjectScanner


class TestProjectScanner(unittest.TestCase):
    """Test the ProjectScanner class."""

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create a basic package.json
        package_data = {
            "name": "test-project",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.2.0",
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }
        with open(self.test_path / "package.json", "w") as f:
            json.dump(package_data, f)

        # Create a simple source file
        (self.test_path / "src").mkdir()
        (self.test_path / "src" / "index.js").write_text("console.log('hello');")

    def tearDown(self):
        """Clean up the temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_scanner_creation(self):
        """Test that we can create a scanner."""
        scanner = ProjectScanner(self.test_path)
        self.assertEqual(scanner.root, self.test_path.resolve())

    def test_package_file_detection(self):
        """Test that package.json is detected."""
        scanner = ProjectScanner(self.test_path)
        scanner._discover_package_files()

        # Should have found package.json
        self.assertGreater(len(scanner.package_files_found), 0)

        # Look for our package.json
        package_json_found = False
        for file_path, language, manager in scanner.package_files_found:
            if "package.json" in file_path:
                package_json_found = True
                self.assertEqual(language, "javascript")
                self.assertEqual(manager, "npm")
                break

        self.assertTrue(package_json_found, "package.json should be detected")

    def test_dependency_extraction(self):
        """Test that dependencies are extracted from package.json."""
        scanner = ProjectScanner(self.test_path)
        scanner._discover_package_files()
        scanner._parse_dependencies()

        # Should have dependencies from package.json
        self.assertIn("package.json", scanner.dependencies)
        deps = scanner.dependencies["package.json"]

        # Should have 3 dependencies (2 prod, 1 dev)
        self.assertEqual(len(deps), 3)

        # Check that we found the expected packages
        dep_names = [dep["name"] for dep in deps]
        self.assertIn("react", dep_names)
        self.assertIn("lodash", dep_names)
        self.assertIn("jest", dep_names)


if __name__ == '__main__':
    unittest.main()