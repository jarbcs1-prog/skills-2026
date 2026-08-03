"""
Dependency health analysis for project-analyst.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class HealthReport:
    """Health report for a dependency."""
    name: str
    version: str
    license: Optional[str] = None
    security_issues: int = 0
    outdated: bool = False
    days_since_update: Optional[int] = None
    download_count: Optional[int] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None


class DependencyHealth:
    """Analyzes dependency health (simplified version for Phase 1)."""
    
    def __init__(self):
        # In a full implementation, this would connect to npm, PyPI, etc. APIs
        # For Phase 1, we'll provide basic structure
        pass
    
    def analyze(self, dependencies: List[Dict[str, str]]) -> List[HealthReport]:
        """
        Analyze a list of dependencies and return health reports.
        
        For Phase 1, this returns basic information with placeholder values.
        A full implementation would query package registries for real data.
        """
        reports = []
        
        for dep in dependencies:
            # Extract name and version from dependency dict
            name = dep.get("name", "unknown")
            version = dep.get("version", "unknown")
            
            # Create a basic report - in reality, we'd query registries here
            report = HealthReport(
                name=name,
                version=version,
                license=None,  # Would be fetched from registry
                security_issues=0,  # Would be checked against vulnerability DBs
                outdated=False,  # Would be determined by checking latest version
                days_since_update=None,
                download_count=None,
                homepage=None,
                repository=None
            )
            
            reports.append(report)
        
        return reports
    
    def get_summary(self, reports: List[HealthReport]) -> Dict[str, Any]:
        """Get a summary of dependency health."""
        if not reports:
            return {
                "total": 0,
                "healthy": 0,
                "with_issues": 0,
                "outdated": 0,
                "unknown_license": 0
            }
        
        total = len(reports)
        with_issues = sum(1 for r in reports if r.security_issues > 0)
        outdated = sum(1 for r in reports if r.outdated)
        unknown_license = sum(1 for r in reports if not r.license)
        
        return {
            "total": total,
            "healthy": total - with_issues - outdated,  # Simplified
            "with_issues": with_issues,
            "outdated": outdated,
            "unknown_license": unknown_license
        }


# Example usage function for testing
def example_usage():
    """Example of how to use the DependencyHealth analyzer."""
    # Sample dependencies (as would come from scanner)
    sample_deps = [
        {"name": "react", "version": "18.2.0"},
        {"name": "lodash", "version": "4.17.21"},
        {"name": "express", "version": "4.18.2"}
    ]
    
    analyzer = DependencyHealth()
    reports = analyzer.analyze(sample_deps)
    summary = analyzer.get_summary(reports)
    
    return reports, summary