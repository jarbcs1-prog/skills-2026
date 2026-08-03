"""
Core project scanning functionality.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import tomli
import yaml


@dataclass
class ProjectAnalysis:
    """Result of project analysis."""
    technology_stack: Dict[str, List[str]]
    architecture: Dict[str, any]
    dependencies: Dict[str, List[Dict]]
    config_files: Dict[str, List[str]]
    structure: Dict[str, any]
    health_score: float
    recommendations: List[str]


class ProjectScanner:
    """Automated project scanner that detects technology stack, architecture, and dependencies."""

    PACKAGE_FILES = {
        "package.json": ("javascript", "npm"),
        "package-lock.json": ("javascript", "npm"),
        "yarn.lock": ("javascript", "yarn"),
        "pnpm-lock.yaml": ("javascript", "pnpm"),
        "requirements.txt": ("python", "pip"),
        "pyproject.toml": ("python", "poetry|pip"),
        "setup.py": ("python", "setuptools"),
        "Pipfile": ("python", "pipenv"),
        "poetry.lock": ("python", "poetry"),
        "Cargo.toml": ("rust", "cargo"),
        "Cargo.lock": ("rust", "cargo"),
        "go.mod": ("go", "go modules"),
        "go.sum": ("go", "go modules"),
        "pom.xml": ("java", "maven"),
        "build.gradle": ("java", "gradle"),
        "build.gradle.kts": ("java", "gradle"),
        "Gemfile": ("ruby", "bundler"),
        "Gemfile.lock": ("ruby", "bundler"),
        "composer.json": ("php", "composer"),
        "composer.lock": ("php", "composer"),
    }

    FRAMEWORKS = {
        "javascript": {
            "react": ["react", "react-dom"],
            "next": ["next"],
            "vue": ["vue"],
            "nuxt": ["nuxt"],
            "svelte": ["svelte"],
            "astro": ["astro"],
            "remix": ["@remix-run/react"],
            "express": ["express"],
            "fastify": ["fastify"],
            "nestjs": ["@nestjs/core"],
            "angular": ["@angular/core"],
            "solid": ["solid-js"],
            "qwik": ["@builder.io/qwik"],
            "sveltekit": ["@sveltejs/kit"],
            "gatsby": ["gatsby"],
            "three": ["three"],
            "d3": ["d3"],
            "chart.js": ["chart.js"],
            "lodash": ["lodash"],
            "moment": ["moment"],
            "redux": ["redux"],
            "zustand": ["zustand"],
            "xstate": ["xstate"],
            "formik": ["formik"],
            "react-hook-form": ["react-hook-form"],
            "tailwindcss": ["tailwindcss"],
            "bootstrap": ["bootstrap"],
            "material-ui": ["@mui/material"],
            "ant-design": ["antd"],
        },
        "python": {
            "django": ["django"],
            "flask": ["flask"],
            "fastapi": ["fastapi"],
            "starlette": ["starlette"],
            "tornado": ["tornado"],
            "quart": ["quart"],
            "pydantic": ["pydantic"],
            "sqlalchemy": ["sqlalchemy"],
            "celery": ["celery"],
            "pytest": ["pytest"],
            "black": ["black"],
            "ruff": ["ruff"],
            "mypy": ["mypy"],
            "numpy": ["numpy"],
            "pandas": ["pandas"],
            "scipy": ["scipy"],
            "tensorflow": ["tensorflow"],
            "torch": ["torch"],
            "matplotlib": ["matplotlib"],
            "seaborn": ["seaborn"],
            "scikit-learn": ["scikit-learn"],
            "requests": ["requests"],
            "beautifulsoup4": ["beautifulsoup4"],
            "scrapy": ["scrapy"],
            "django-rest-framework": ["djangorestframework"],
            "sqlmodel": ["sqlmodel"],
            "alembic": ["alembic"],
            "factory-boy": ["factory_boy"],
            "faker": ["faker"],
            "httpx": ["httpx"],
            "aiohttp": ["aiohttp"],
            "uvicorn": ["uvicorn"],
            "gunicorn": ["gunicorn"],
            "poetry": ["poetry"],
            "pipenv": ["pipenv"],
        },
        "rust": {
            "actix": ["actix-web"],
            "axum": ["axum"],
            "rocket": ["rocket"],
            "warp": ["warp"],
            "tokio": ["tokio"],
            "tide": ["tide"],
            "warp": ["warp"],
            "hyper": ["hyper"],
        },
        "go": {
            "gin": ["github.com/gin-gonic/gin"],
            "echo": ["github.com/labstack/echo"],
            "fiber": ["github.com/gofiber/fiber"],
            "chi": ["github.com/go-chi/chi"],
            "fyne": ["fyne.io/fyne/v2"],
            "kitex": ["github.com/cloudwego/kitex"],
            "go-zero": ["github.com/zeromicro/go-zero"],
            "ent": ["go.ent.io/ent"],
            "sqlc": ["github.com/kyleconroy/sqlc"],
            "air": ["github.com/cosmtrek/air"],
        },
        "java": {
            "spring-boot": ["org.springframework.boot:spring-boot-starter"],
            "spring": ["org.springframework:spring-context"],
            "hibernate": ["org.hibernate:hibernate-core"],
            "mybatis": ["org.mybatis:mybatis"],
            "junit": ["junit:junit"],
            "mockito": ["org.mockito:mockito-core"],
            "log4j": ["org.apache.logging.log4j:log4j-core"],
            "slf4j": ["org.slf4j:slf4j-api"],
            "jakartaee": ["jakarta.platform:jakarta.jakartaee-api"],
            "micronaut": ["io.micronaut:micronaut-runtime"],
            "quarkus": ["io.quarkus:quarkus-bom"],
            "dropwizard": ["io.dropwizard:dropwizard-core"],
            "vertx": ["io.vertx:vertx-core"],
        },
    }

    CONFIG_FILES = {
        "typescript": ["tsconfig.json", "tsconfig.*.json"],
        "javascript": ["jsconfig.json", "jsconfig.*.json"],
        "eslint": [".eslintrc*", "eslint.config.*"],
        "prettier": [".prettierrc*", "prettier.config.*"],
        "jest": ["jest.config.*", "jest.*.config.*"],
        "vitest": ["vitest.config.*"],
        "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg"],
        "mypy": ["mypy.ini", "pyproject.toml"],
        "ruff": ["ruff.toml", "pyproject.toml"],
        "black": ["pyproject.toml"],
        "django": ["settings.py", "urls.py", "wsgi.py", "asgi.py"],
        "flask": ["app.py", "application.py", "wsgi.py"],
        "fastapi": ["main.py", "app.py"],
        "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        "kubernetes": ["k8s/", "kubernetes/", "*.yaml", "*.yml"],
        "github": [".github/workflows/", ".github/actions/"],
        "gitlab": [".gitlab-ci.yml"],
        "circleci": [".circleci/config.yml"],
        "webpack": ["webpack.config.js", "webpack.config.ts"],
        "vite": ["vite.config.js", "vite.config.ts"],
        "rollup": ["rollup.config.js"],
        "babel": [".babelrc", "babel.config.js"],
        "storybook": [".storybook/", "storybook.config.js"],
    }

    def __init__(self, root_path: Path):
        self.root = root_path.resolve()
        self.package_files_found = []
        self.dependencies = {}
        self.frameworks_detected = {}
        self.config_files_found = {}
        self.directory_structure = {}

    def scan(self) -> ProjectAnalysis:
        """Perform full project scan."""
        self._discover_package_files()
        self._parse_dependencies()
        self._detect_frameworks()
        self._discover_config_files()
        self._analyze_structure()
        self._detect_architecture()
        self._analyze_dependency_health()
        health_score = self._calculate_health_score()
        recommendations = self._generate_recommendations()

        return ProjectAnalysis(
            technology_stack=self.frameworks_detected,
            architecture=self._detect_architecture(),
            dependencies=self.dependencies,
            config_files=self.config_files_found,
            structure=self.directory_structure,
            health_score=health_score,
            recommendations=recommendations,
        )

    def _discover_package_files(self):
        """Find all package manifest files."""
        for package_file, (language, manager) in self.PACKAGE_FILES.items():
            matches = list(self.root.rglob(package_file))
            if matches:
                self.package_files_found.extend(
                    [(str(match.relative_to(self.root)), language, manager) for match in matches]
                )

    def _parse_dependencies(self):
        """Parse dependencies from package files."""
        for rel_path, language, manager in self.package_files_found:
            file_path = self.root / rel_path
            try:
                deps = self._parse_package_file(file_path, language, manager)
                if deps:
                    self.dependencies[rel_path] = deps
            except Exception as e:
                # Log error but continue
                pass

    def _parse_package_file(self, file_path: Path, language: str, manager: str) -> List[Dict]:
        """Parse a specific package file."""
        deps = []
        try:
            if file_path.name == "package.json" or file_path.name.endswith("-lock.json"):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    deps.extend(self._extract_npm_deps(data))
            elif file_path.name == "requirements.txt":
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            deps.append(self._parse_pip_line(line))
            elif file_path.name == "pyproject.toml":
                with open(file_path, 'rb') as f:
                    data = tomli.load(f)
                    deps.extend(self._extract_python_deps(data))
            elif file_path.name == "Pipfile":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    deps.extend(self._extract_pipfile_deps(data))
            elif file_path.name == "poetry.lock":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    deps.extend(self._extract_poetry_lock_deps(data))
            elif file_path.name in ["Cargo.toml", "Cargo.lock"]:
                with open(file_path, 'r') as f:
                    data = tomli.load(f)
                    deps.extend(self._extract_rust_deps(data))
            elif file_path.name in ["go.mod", "go.sum"]:
                with open(file_path, 'r') as f:
                    content = f.read()
                    deps.extend(self._extract_go_deps(content))
            elif file_path.name == "pom.xml":
                deps.extend(self._extract_maven_deps(file_path))
            elif file_path.name.endswith("build.gradle") or file_path.name.endswith("build.gradle.kts"):
                deps.extend(self._extract_gradle_deps(file_path))
            elif file_path.name in ["Gemfile", "Gemfile.lock"]:
                deps.extend(self._extract_bundler_deps(file_path))
            elif file_path.name in ["composer.json", "composer.lock"]:
                deps.extend(self._extract_composer_deps(file_path))
        except Exception:
            pass
        return deps

    def _extract_npm_deps(self, data: dict) -> List[Dict]:
        """Extract dependencies from package.json or lock file."""
        deps = []
        for dep_type in ["dependencies", "devDependencies", "peerDependencies"]:
            if dep_type in data:
                for name, version in data[dep_type].items():
                    deps.append({
                        "name": name,
                        "version": version,
                        "type": dep_type.replace("Dependencies", "").lower() or "runtime",
                        "source": "npm"
                    })
        return deps

    def _parse_pip_line(self, line: str) -> Dict:
        """Parse a single line from requirements.txt."""
        # Handle various formats: package, package==version, package>=version, etc.
        import re
        match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*)([=<>!~]+.*)?$', line)
        if match:
            name = match.group(1)
            version_spec = match.group(2) if match.group(2) else ""
            return {
                "name": name,
                "version": version_spec if version_spec else "latest",
                "type": "runtime",
                "source": "pip"
            }
        return {"name": line, "version": "unknown", "type": "runtime", "source": "pip"}

    def _extract_python_deps(self, data: dict) -> List[Dict]:
        """Extract dependencies from pyproject.toml."""
        deps = []
        # Handle [project] dependencies
        if "project" in data:
            if "dependencies" in data["project"]:
                for dep in data["project"]["dependencies"]:
                    deps.append(self._parse_pip_line(dep))
            if "optional-dependencies" in data["project"]:
                for group, deps_list in data["project"]["optional-dependencies"].items():
                    for dep in deps_list:
                        dep_info = self._parse_pip_line(dep)
                        dep_info["type"] = f"optional-{group}"
                        deps.append(dep_info)
        # Handle [tool.poetry] dependencies
        if "tool" in data and "poetry" in data["tool"]:
            poetry = data["tool"]["poetry"]
            if "dependencies" in poetry:
                for name, version_spec in poetry["dependencies"].items():
                    if name != "python":
                        if isinstance(version_spec, str):
                            deps.append({
                                "name": name,
                                "version": version_spec,
                                "type": "runtime",
                                "source": "poetry"
                            })
                        elif isinstance(version_spec, dict):
                            deps.append({
                                "name": name,
                                "version": version_spec.get("version", "*"),
                                "type": "runtime",
                                "source": "poetry"
                            })
            if "group" in poetry:
                for group, group_deps in poetry["group"].items():
                    if "dependencies" in group_deps:
                        for name, version_spec in group_deps["dependencies"].items():
                            if isinstance(version_spec, str):
                                deps.append({
                                    "name": name,
                                    "version": version_spec,
                                    "type": group,
                                    "source": "poetry"
                                })
                            elif isinstance(version_spec, dict):
                                deps.append({
                                    "name": name,
                                    "version": version_spec.get("version", "*"),
                                    "type": group,
                                    "source": "poetry"
                                })
        return deps

    def _extract_pipfile_deps(self, data: dict) -> List[Dict]:
        """Extract dependencies from Pipfile."""
        deps = []
        for section in ["packages", "dev-packages"]:
            if section in data:
                for name, version_spec in data[section].items():
                    deps.append({
                        "name": name,
                        "version": version_spec if isinstance(version_spec, str) else "*",
                        "type": "dev" if section == "dev-packages" else "runtime",
                        "source": "pipenv"
                    })
        return deps

    def _extract_poetry_lock_deps(self, data: dict) -> List[Dict]:
        """Extract dependencies from poetry.lock."""
        deps = []
        if "package" in data:
            for package in data["package"]:
                deps.append({
                    "name": package["name"],
                    "version": package["version"],
                    "type": "runtime",
                    "source": "poetry"
                })
        return deps

    def _extract_rust_deps(self, data: dict) -> List[Dict]:
        """Extract dependencies from Cargo.toml or Cargo.lock."""
        deps = []
        if "dependencies" in data:
            for name, version_spec in data["dependencies"].items():
                if isinstance(version_spec, str):
                    deps.append({
                        "name": name,
                        "version": version_spec,
                        "type": "runtime",
                        "source": "cargo"
                    })
                elif isinstance(version_spec, dict):
                    deps.append({
                        "name": name,
                        "version": version_spec.get("version", "*"),
                        "type": "runtime",
                        "source": "cargo"
                    })
        # Also check dev-dependencies, build-dependencies
        for dep_type in ["dev-dependencies", "build-dependencies"]:
            if dep_type in data:
                for name, version_spec in data[dep_type].items():
                    if isinstance(version_spec, str):
                        deps.append({
                            "name": name,
                            "version": version_spec,
                            "type": dep_type.replace("-dependencies", ""),
                            "source": "cargo"
                        })
                    elif isinstance(version_spec, dict):
                        deps.append({
                            "name": name,
                            "version": version_spec.get("version", "*"),
                            "type": dep_type.replace("-dependencies", ""),
                            "source": "cargo"
                        })
        return deps

    def _extract_go_deps(self, content: str) -> List[Dict]:
        """Extract dependencies from go.mod or go.sum."""
        deps = []
        lines = content.split('\n')
        in_require = False
        for line in lines:
            line = line.strip()
            if line.startswith('require ('):
                in_require = True
                continue
            elif line == ')':
                in_require = False
                continue
            elif in_require and line and not line.startswith('//'):
                parts = line.split()
                if len(parts) >= 2:
                    deps.append({
                        "name": parts[0],
                        "version": parts[1] if len(parts) > 1 else "latest",
                        "type": "runtime",
                        "source": "go"
                    })
            elif line.startswith('require ') and not line.startswith('require ('):
                parts = line.split()
                if len(parts) >= 3:
                    deps.append({
                        "name": parts[1],
                        "version": parts[2],
                        "type": "runtime",
                        "source": "go"
                    })
        return deps

    def _extract_maven_deps(self, file_path: Path) -> List[Dict]:
        """Extract dependencies from pom.xml (simplified)."""
        # For brevity, returning empty list - would need XML parsing
        return []

    def _extract_gradle_deps(self, file_path: Path) -> List[Dict]:
        """Extract dependencies from build.gradle (simplified)."""
        # For brevity, returning empty list - would need regex parsing
        return []

    def _extract_bundler_deps(self, file_path: Path) -> List[Dict]:
        """Extract dependencies from Gemfile/Gemfile.lock (simplified)."""
        # For brevity, returning empty list - would need regex parsing
        return []

    def _extract_composer_deps(self, file_path: Path) -> List[Dict]:
        """Extract dependencies from composer.json/composer.lock (simplified)."""
        # For brevity, returning empty list - would need JSON parsing
        return []

    def _detect_frameworks(self):
        """Detect frameworks from dependencies."""
        for file_path, deps in self.dependencies.items():
            # Determine language from file path
            language = None
            if any(ext in file_path for ext in ["package.json", "yarn.lock", "pnpm-lock", "lock.json"]):
                language = "javascript"
            elif any(ext in file_path for ext in ["requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock", "setup.py"]):
                language = "python"
            elif any(ext in file_path for ext in ["Cargo.toml", "Cargo.lock"]):
                language = "rust"
            elif any(ext in file_path for ext in ["go.mod", "go.sum"]):
                language = "go"
            elif any(ext in file_path for ext in ["pom.xml", "build.gradle", "build.gradle.kts"]):
                language = "java"
            elif any(ext in file_path for ext in ["Gemfile", "Gemfile.lock"]):
                language = "ruby"
            elif any(ext in file_path for ext in ["composer.json", "composer.lock"]):
                language = "php"

            if language and language in self.FRAMEWORKS:
                detected = []
                for dep in deps:
                    dep_name = dep["name"].lower()
                    for framework, indicators in self.FRAMEWORKS[language].items():
                        if any(indicator.lower() in dep_name for indicator in indicators):
                            if framework not in detected:
                                detected.append(framework)
                if detected:
                    self.frameworks_detected[file_path] = detected

    def _discover_config_files(self):
        """Discover configuration files."""
        for config_type, patterns in self.CONFIG_FILES.items():
            matches = []
            for pattern in patterns:
                if '*' in pattern:
                    matches.extend(self.root.rglob(pattern))
                else:
                    matches.extend(self.root.glob(f"**/{pattern}"))
            if matches:
                self.config_files_found[config_type] = [str(m.relative_to(self.root)) for m in matches]

    def _analyze_structure(self):
        """Analyze directory structure."""
        # Get all directories (excluding common ignored ones)
        ignored_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env',
                       'dist', 'build', 'target', 'bin', 'obj', '.idea', '.vscode', '.pytest_cache',
                       '.ruff_cache', 'coverage', '.coverage', '.cache', '.parcel-cache', '.next',
                       '.nuxt', '.output', '.svelte-kit', '.cache', 'tmp', 'temp'}

        structure = {}
        for item in self.root.rglob('*'):
            if item.is_dir() and not any(ignored in item.parts for ignored in ignored_dirs):
                rel_path = str(item.relative_to(self.root))
                level = rel_path.count(os.sep) if os.sep in rel_path else 0
                if level not in structure:
                    structure[level] = []
                structure[level].append(rel_path)

        self.directory_structure = structure

    def _detect_architecture(self) -> Dict[str, any]:
        """Detect architectural patterns."""
        # This would use the ArchitectureDetector class
        detector = ArchitectureDetector(self.root)
        return detector.detect_all()

    def _analyze_dependency_health(self):
        """Analyze dependency health (simplified)."""
        # This would use DependencyHealth class
        pass

    def _calculate_health_score(self) -> float:
        """Calculate project health score."""
        score = 50.0  # Base score

        # Add points for having tests
        if any(self.root.rglob('test*.py')) or any(self.root.rglob('*test.py')) or \
           any(self.root.rglob('tests/')) or any(self.root.rglob('__tests__/')):
            score += 10

        # Add points for having CI
        if any(self.root.rglob('.github/workflows/')) or any(self.root.rglob('.gitlab-ci.yml')) or \
           any(self.root.rglob('Jenkinsfile')) or any(self.root.rglob('.circleci/')):
            score += 10

        # Add points for having docs
        if any(self.root.rglob('README.*')) or any(self.root.rglob('docs/')):
            score += 10

        # Add points for having linter/formatter config
        if any(self.root.rglob('.eslintrc*')) or any(self.root.rglob('.prettierrc*')) or \
           any(self.root.rglob('pyproject.toml')) or any(self.root.rglob('ruff.toml')) or \
           any(self.root.rglob('.flake8')) or any(self.root.rglob('pylintrc')):
            score += 10

        # Add points for having license
        if any(self.root.rglob('LICENSE*')) or any(self.root.rglob('COPYING*')):
            score += 5

        # Add points for having contributing guidelines
        if any(self.root.rglob('CONTRIBUTING*')):
            score += 5

        return min(100.0, max(0.0, score))

    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Check for missing tests
        if not (any(self.root.rglob('test*.py')) or any(self.root.rglob('*test.py')) or
                any(self.root.rglob('tests/')) or any(self.root.rglob('__tests__/'))):
            recommendations.append("Add automated tests to improve code quality and prevent regressions")

        # Check for missing CI
        if not (any(self.root.rglob('.github/workflows/')) or any(self.root.rglob('.gitlab-ci.yml')) or
                any(self.root.rglob('Jenkinsfile')) or any(self.root.rglob('.circleci/'))):
            recommendations.append("Set up continuous integration for automated testing and deployment")

        # Check for missing docs
        if not (any(self.root.rglob('README.*')) or any(self.root.rglob('docs/'))):
            recommendations.append("Add documentation to help users and contributors understand the project")

        # Check for missing license
        if not (any(self.root.rglob('LICENSE*')) or any(self.root.rglob('COPYING*'))):
            recommendations.append("Add a license file to clarify usage rights")

        # Check for missing contribution guidelines
        if not any(self.root.rglob('CONTRIBUTING*')):
            recommendations.append("Add contributing guidelines to help contributors")

        # Check for missing linter/formatter
        if not (any(self.root.rglob('.eslintrc*')) or any(self.root.rglob('.prettierrc*')) or
                any(self.root.rglob('pyproject.toml')) or any(self.root.rglob('ruff.toml')) or
                any(self.root.rglob('.flake8')) or any(self.root.rglob('pylintrc'))):
            recommendations.append("Add code formatting and linting tools to maintain code quality")

        return recommendations