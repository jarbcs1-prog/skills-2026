"""Language configuration for test-driven-development skill."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LanguageConfig:
    name: str
    test_framework: str
    test_command: str
    coverage_command: str
    mutation_command: str
    test_naming: str
    test_pattern: str
    default_coverage_threshold: float = 0.8


LANGUAGE_CONFIGS: dict[str, LanguageConfig] = {
    "python": LanguageConfig(
        name="python",
        test_framework="pytest",
        test_command="pytest {test_file} -v",
        coverage_command="pytest --cov={source} --cov-fail-under=80",
        mutation_command="mutmut run --paths-to-mutate {source}",
        test_naming="test_*.py",
        test_pattern="def test_.*:",
        default_coverage_threshold=0.8,
    ),
    "javascript": LanguageConfig(
        name="javascript",
        test_framework="jest",
        test_command="jest {test_file} --verbose",
        coverage_command="jest --coverage --coverageThreshold='{\"global\":{\"statements\":80}}'",
        mutation_command="stryker run",
        test_naming="*.test.js",
        test_pattern="test\\(|it\\(",
        default_coverage_threshold=0.8,
    ),
    "rust": LanguageConfig(
        name="rust",
        test_framework="cargo",
        test_command="cargo test {test_name} -- --nocapture",
        coverage_command="cargo tarpaulin --fail-under 80",
        mutation_command="cargo mutate",
        test_naming="#[test]",
        test_pattern="#\\[test\\]",
        default_coverage_threshold=0.8,
    ),
    "go": LanguageConfig(
        name="go",
        test_framework="go test",
        test_command="go test -v -run {test_name} ./...",
        coverage_command="go test -coverprofile=coverage.out && go tool cover -func=coverage.out",
        mutation_command="go-mutesting",
        test_naming="*_test.go",
        test_pattern="func Test.*\\(",
        default_coverage_threshold=0.8,
    ),
    "java": LanguageConfig(
        name="java",
        test_framework="JUnit",
        test_command="mvn test -Dtest={test_name}",
        coverage_command="mvn jacoco:report -Djacoco.coverageGoal=80",
        mutation_command="pitest",
        test_naming="*Test.java",
        test_pattern="@Test",
        default_coverage_threshold=0.8,
    ),
}


def get_config(language: str) -> Optional[LanguageConfig]:
    return LANGUAGE_CONFIGS.get(language)


def list_languages() -> list[str]:
    return list(LANGUAGE_CONFIGS.keys())