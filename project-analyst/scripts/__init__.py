"""
Project Analyst - Automated project analysis and technology detection.
"""

from .scanner import ProjectScanner, ProjectAnalysis
from .architecture import ArchitectureDetector, ArchitectureResult
from .dependency_health import DependencyHealth, HealthReport

__all__ = [
    "ProjectScanner",
    "ProjectAnalysis",
    "ArchitectureDetector",
    "ArchitectureResult",
    "DependencyHealth",
    "HealthReport",
]