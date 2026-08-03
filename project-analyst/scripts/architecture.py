"""
Architecture detection for project-analyst.
"""

from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import re


@dataclass
class ArchitectureResult:
    """Result of architecture detection."""
    name: str
    confidence: float
    description: str
    evidence: List[str]


class ArchitectureDetector:
    """Detects architectural patterns in a project."""
    
    def __init__(self, root_path: Path):
        self.root = root_path.resolve()
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize architectural patterns to detect."""
        return {
            "mvc": {
                "name": "Model-View-Controller (MVC)",
                "indicators": [
                    "controllers/", "models/", "views/",
                    "app/controllers", "app/models", "app/views",
                    "src/controllers", "src/models", "src/views",
                    "controller/", "model/", "view/",
                    "Controllers", "Models", "Views"
                ],
                "description": "Separates application into three interconnected components",
                "confidence_weight": 1.0
            },
            "layered": {
                "name": "Layered Architecture",
                "indicators": [
                    "presentation/", "application/", "domain/", "infrastructure/",
                    "ui/", "service/", "repository/", "model/",
                    "client/", "api/", "business/", "data/",
                    "controllers/", "services/", "repositories/", "entities/"
                ],
                "description": "Organizes code into horizontal layers with specific responsibilities",
                "confidence_weight": 1.0
            },
            "hexagonal": {
                "name": "Hexagonal/Ports and Adapters",
                "indicators": [
                    "domain/", "application/", "infrastructure/",
                    "ports/", "adapters/",
                    "core/", "inbound/", "outbound/",
                    "application/", "interface/", "infrastructure/"
                ],
                "description": "Places inputs and outputs at the edges of the design",
                "confidence_weight": 1.0
            },
            "microservices": {
                "name": "Microservices",
                "indicators": [
                    "services/", "service-", "microservice-",
                    "docker-compose.yml", "docker-compose.yaml",
                    "k8s/", "kubernetes/", "helm/",
                    "*-service", "/services/", "/microservices/"
                ],
                "description": "Structures application as a collection of loosely coupled services",
                "confidence_weight": 1.2  # Higher weight as it's more distinctive
            },
            "event-driven": {
                "name": "Event-Driven Architecture",
                "indicators": [
                    "events/", "event-handlers/", "message-handlers/",
                    "handlers/", "subscribers/", "publishers/",
                    "topics/", "queues/", "streams/",
                    "listeners/", "dispatchers/"
                ],
                "description": "Components communicate through events",
                "confidence_weight": 1.0
            },
            "pipes-and-filters": {
                "name": "Pipes and Filters",
                "indicators": [
                    "pipes/", "filters/", "processors/",
                    "steps/", "stages/", "pipeline/",
                    "filters", "pipes"
                ],
                "description": "Processes data through a sequence of processing elements",
                "confidence_weight": 1.0
            },
            "microkernel": {
                "name": "Microkernel/Plugin Architecture",
                "indicators": [
                    "plugins/", "extensions/", "modules/",
                    "addons/", "add-ins/", "bundles/",
                    "core/", "plugin-api/", "spi/"
                ],
                "description": "Core system with pluggable components",
                "confidence_weight": 1.0
            },
            "space-based": {
                "name": "Space-Based Architecture",
                "indicators": [
                    "processing-units/", "messaging/", "data-grid/",
                    "space/", "cache/", "in-memory-data-grid/"
                ],
                "description": "Addresses scalability and concurrency issues",
                "confidence_weight": 1.0
            },
            "client-server": {
                "name": "Client-Server Architecture",
                "indicators": [
                    "client/", "server/", "api/", "gateway/",
                    "frontend/", "backend/", "web/", "api/",
                    "ui/", "server/", "admin/", "webapp/"
                ],
                "description": "Separates concerns between client and server applications",
                "confidence_weight": 0.8  # Lower weight as very common
            },
            "pipe-and-filter": {
                "name": "Pipe and Filter",
                "indicators": [
                    "pipes/", "filters/", "processors/",
                    "steps/", "stages/", "pipeline/",
                    "filters", "pipes", "transformers"
                ],
                "description": "Processes data through a sequence of processing elements",
                "confidence_weight": 1.0
            },
            "broker": {
                "name": "Broker Architecture",
                "indicators": [
                    "broker/", "middleman/", "intermediary/",
                    "message-broker/", "event-bus/", "service-bus/",
                    "rabbitmq/", "kafka/", "activemq/"
                ],
                "description": "Coordinates communication between components",
                "confidence_weight": 1.0
            }
        }
    
    def detect_all(self) -> Dict[str, Any]:
        """Detect all architectural patterns and return results."""
        results = {}
        
        for pattern_key, pattern_info in self.patterns.items():
            result = self._detect_pattern(pattern_key, pattern_info)
            results[pattern_key] = result
        
        # Find the best match
        best_match = None
        highest_confidence = 0.0
        
        for pattern_key, result in results.items():
            if result.confidence > highest_confidence:
                highest_confidence = result.confidence
                best_match = result
        
        # Prepare final result
        final_result = {
            "detected": best_match.name if best_match and best_match.confidence > 0.2 else "None detected",
            "confidence": best_match.confidence if best_match else 0.0,
            "description": best_match.description if best_match else "No clear architectural pattern detected",
            "evidence": best_match.evidence if best_match else [],
            "all_patterns": {k: v for k, v in results.items() if v.confidence > 0.1}
        }
        
        return final_result
    
    def _detect_pattern(self, pattern_key: str, pattern_info: Dict[str, Any]) -> ArchitectureResult:
        """Detect a specific architectural pattern."""
        evidence = []
        score = 0.0
        max_possible_score = len(pattern_info["indicators"])
        
        # Check for directory/file indicators
        for indicator in pattern_info["indicators"]:
            # Handle wildcards and special patterns
            if "*" in indicator:
                # Simple wildcard handling
                base_pattern = indicator.rstrip("/*")
                matches = list(self.root.rglob(base_pattern.replace("*", "")))
                if matches:
                    evidence.append(f"Found {len(matches)} matches for pattern '{indicator}'")
                    score += 1
            elif "/" in indicator and not indicator.endswith("/"):
                # Path pattern
                if (self.root / indicator).exists():
                    evidence.append(f"Found path: {indicator}")
                    score += 1
                elif list(self.root.rglob(indicator)):
                    evidence.append(f"Found path pattern: {indicator}")
                    score += 1
            else:
                # Directory or file name pattern
                matches = list(self.root.rglob(f"*{indicator}*"))
                if matches:
                    # Filter to directories if it looks like a directory pattern
                    if indicator.endswith("/") or any(m.is_dir() for m in matches[:5]):
                        dir_matches = [m for m in matches if m.is_dir()]
                        if dir_matches:
                            evidence.append(f"Found {len(dir_matches)} directories matching '{indicator}'")
                            score += 1
                    else:
                        # File pattern
                        file_matches = [m for m in matches if m.is_file()]
                        if file_matches:
                            evidence.append(f"Found {len(file_matches)} files matching '{indicator}'")
                            score += 1
        
        # Calculate confidence
        confidence = min(score / max(max_possible_score, 1), 1.0) * pattern_info["confidence_weight"]
        
        return ArchitectureResult(
            name=pattern_info["name"],
            confidence=confidence,
            description=pattern_info["description"],
            evidence=evidence
        )
    
    def get_structure_overview(self) -> Dict[str, Any]:
        """Get a high-level overview of project structure."""
        # Count files by type
        file_counts = {}
        total_files = 0
        
        for file_path in self.root.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and common directories to ignore
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(part in {'node_modules', '__pycache__', '.git', 'dist', 'build', 'target'} 
                       for part in file_path.parts):
                    continue
                
                suffix = file_path.suffix.lower()
                if not suffix:
                    suffix = "(no extension)"
                
                file_counts[suffix] = file_counts.get(suffix, 0) + 1
                total_files += 1
        
        # Get top-level directories
        top_level_dirs = []
        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if item.name not in {'node_modules', '__pycache__', '.git', 'dist', 'build', 'target'}:
                    try:
                        # Count files in directory (non-recursive for quick count)
                        file_count = len([f for f in item.iterdir() if f.is_file() and not f.name.startswith('.')])
                        top_level_dirs.append({
                            "name": item.name,
                            "file_count": file_count,
                            "is_package": self._is_package_dir(item)
                        })
                    except (PermissionError, OSError):
                        pass
        
        return {
            "total_files": total_files,
            "file_types": dict(sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "top_level_directories": top_level_dirs[:10]  # Limit output
        }
    
    def _is_package_dir(self, directory: Path) -> bool:
        """Check if directory looks like a package/module."""
        # Common package indicators
        package_indicators = {
            "__init__.py",      # Python package
            "package.json",     # Node.js package
            "Cargo.toml",       # Rust crate
            "go.mod",           # Go module
            ".csproj",          # .NET project
            "pom.xml",          # Maven
            "build.gradle",     # Gradle
            "setup.py",         # Python setuptools
            "pyproject.toml"    # Modern Python
        }
        
        return any((directory / indicator).exists() for indicator in package_indicators)