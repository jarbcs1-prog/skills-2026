"""Test scaffolding for test-driven-development skill."""
from pathlib import Path


LANGUAGE_EXTENSIONS = {
    "python": {"test_suffix": "_test.py", "test_prefix": "test_", "source_ext": ".py"},
    "javascript": {"test_suffix": ".test.js", "test_prefix": "", "source_ext": ".js"},
    "rust": {"test_suffix": "_test.rs", "test_prefix": "", "source_ext": ".rs"},
    "go": {"test_suffix": "_test.go", "test_prefix": "", "source_ext": ".go"},
    "java": {"test_suffix": "Test.java", "test_prefix": "", "source_ext": ".java"},
}


def scaffold_test(language: str, feature: str, output_dir: Path) -> dict:
    ext = LANGUAGE_EXTENSIONS.get(language, LANGUAGE_EXTENSIONS["python"])
    test_name = f"{ext['test_prefix']}{feature.replace(' ', '_').lower()}{ext['test_suffix']}"
    test_path = output_dir / test_name

    template = _get_test_template(language, feature)
    test_path.write_text(template)

    return {
        "test_file": str(test_path),
        "language": language,
        "feature": feature,
        "template_used": language,
    }


def _get_test_template(language: str, feature: str) -> str:
    templates = {
        "python": f'''"""Test for {feature}."""
import pytest


def test_{feature.replace(" ", "_")}_basic():
    """Test basic functionality."""
    pass


def test_{feature.replace(" ", "_")}_edge_case():
    """Test edge case."""
    pass
''',
        "javascript": f'''/**
 * Test for {feature}
 */
describe('{feature}', () => {{
  test('basic functionality', () => {{
    // TODO: implement
  }});

  test('edge case', () => {{
    // TODO: implement
  }});
}});
''',
        "rust": f'''#[cfg(test)]
mod tests {{
    #[test]
    fn test_{feature.replace(" ", "_")}_basic() {{
        // TODO: implement
    }}

    #[test]
    fn test_{feature.replace(" ", "_")}_edge_case() {{
        // TODO: implement
    }}
}}
''',
        "go": f'''package main

import "testing"

func Test{feature.replace(" ", "")}_Basic(t *testing.T) {{
    // TODO: implement
}}

func Test{feature.replace(" ", "")}_EdgeCase(t *testing.T) {{
    // TODO: implement
}}
''',
        "java": f'''import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class {feature.replace(" ", "")}Test {{
    @Test
    void testBasic() {{
        // TODO: implement
    }}

    @Test
    void testEdgeCase() {{
        // TODO: implement
    }}
}}
''',
    }
    return templates.get(language, templates["python"])