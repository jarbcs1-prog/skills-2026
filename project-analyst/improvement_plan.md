# Improvement Plan: project-analyst

## Current State Assessment

**Tier:** 🟠 Functional but Thin (Needs Substantial Expansion)
**Lines:** 65 | **Version:** 1.0 (implied)

### Strengths
- Clear technology detection from package files
- Covers 7 package managers, 6 frameworks, 4 build tools
- 5-step analysis process
- Structured output format

### Gaps Identified
1. **No automated detection** - Manual inspection only
2. **Limited framework coverage** - Only 6 frameworks
3. **No architecture analysis** - Only basic pattern detection
4. **No dependency analysis** - No version checking, vulnerabilities, outdated
4. **No configuration detection** - Missing config files (tsconfig, pyproject, etc.)
5. **No project health metrics** - No code quality, test coverage, build status
6. **No CLI tooling** - Manual skill invocation only
7. **No integration with project-planner** - Should feed into planning
8. **No monorepo support** - Single project only
9. **No output formats** - Only markdown
10. **No continuous analysis** - One-time only

---

## Improvement Roadmap

### Phase 1: Automation & Coverage (Week 1)
- [ ] Build automated project scanner (CLI)
- [ ] Expand framework detection to 20+ frameworks
- [ ] Add configuration file detection (20+ config types)
- [ ] Implement dependency parsing with version analysis

### Phase 2: Deep Analysis (Week 2)
- [ ] Add architecture pattern detection (MVC, microservices, hexagonal, etc.)
- [ ] Implement dependency health (vulnerabilities, outdated, license)
- [ ] Add code quality metrics (complexity, duplication, coverage)
- [ ] Create project health scorecard

### Phase 3: Integration & Tooling (Week 3)
- [ ] Build CLI with multiple output formats
- [ ] Integrate with `project-planner` (auto-generate WBS from analysis)
- [ ] Add monorepo support (detect workspace, analyze each package)
- [ ] Create IDE integration (VS Code extension)

### Phase 4: Continuous Monitoring (Week 4)
- [ ] Add git hook for change detection
- [ ] Implement trend tracking (health over time)
- [ ] Create project dashboard
- [ ] Add alerting for regressions

---

## Specific Technical Tasks

### Automated Scanner
```python
# scanner.py
class ProjectScanner:
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
        },
        "rust": {
            "actix": ["actix-web"],
            "axum": ["axum"],
            "rocket": ["rocket"],
            "warp": ["warp"],
            "tokio": ["tokio"],
        },
        "go": {
            "gin": ["github.com/gin-gonic/gin"],
            "echo": ["github.com/labstack/echo"],
            "fiber": ["github.com/gofiber/fiber"],
            "chi": ["github.com/go-chi/chi"],
        }
    }
    
    CONFIG_FILES = {
        "typescript": ["tsconfig.json", "tsconfig.*.json"],
        "eslint": [".eslintrc*", "eslint.config.*"],
        "prettier": [".prettierrc*", "prettier.config.*"],
        "jest": ["jest.config.*", "jest.*.config.*"],
        "vitest": ["vitest.config.*"],
        "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg"],
        "mypy": ["mypy.ini", "pyproject.toml"],
        "ruff": ["ruff.toml", "pyproject.toml"],
        "black": ["pyproject.toml"],
        "cargo": ["Cargo.toml"],
        "golangci": [".golangci.yml"],
        "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        "kubernetes": ["k8s/", "kubernetes/", "*.yaml"],
        "github": [".github/workflows/", ".github/actions/"],
        "gitlab": [".gitlab-ci.yml"],
        "circleci": [".circleci/config.yml"],
    }
    
    def scan(self, root: Path) -> ProjectAnalysis:
        # 1. Detect package files
        # 2. Parse dependencies
        # 3. Identify frameworks
        # 4. Detect config files
        # 5. Analyze directory structure
        # 6. Detect architecture patterns
        pass
```

### Architecture Detection
```python
# architecture.py
class ArchitectureDetector:
    PATTERNS = {
        "mvc": {
            "indicators": ["controllers/", "models/", "views/", "app/controllers", "app/models", "app/views"],
            "confidence": 0.8
        },
        "hexagonal": {
            "indicators": ["domain/", "application/", "infrastructure/", "ports/", "adapters/"],
            "confidence": 0.9
        },
        "microservices": {
            "indicators": ["services/", "service-", "docker-compose.yml", "kubernetes/"],
            "confidence": 0.7
        },
        "monorepo": {
            "indicators": ["packages/", "apps/", "libs/", "workspace.json", "pnpm-workspace.yaml", "turbo.json"],
            "confidence": 0.9
        },
        "clean": {
            "indicators": ["entities/", "use-cases/", "interface-adapters/", "frameworks/"],
            "confidence": 0.8
        },
        "layered": {
            "indicators": ["presentation/", "business/", "data/", "persistence/"],
            "confidence": 0.7
        }
    }
    
    def detect(self, structure: DirectoryStructure) -> ArchitectureResult:
        pass
```

### Dependency Health
```python
# dependency_health.py
class DependencyHealth:
    def analyze(self, dependencies: List[Dependency]) -> HealthReport:
        report = HealthReport()
        for dep in dependencies:
            # Check for vulnerabilities (OSV, GitHub Advisory)
            # Check for outdated versions
            # Check license compatibility
            # Check maintenance status (last commit, release frequency)
            # Check transitive dependencies
            pass
        return report
```

### CLI Design
```bash
# project-analyst scan --path . --format json
# project-analyst scan --path . --format markdown --output analysis.md
# project-analyst scan --path . --format sarif
# project-analyst health --path . --check-vulns --check-outdated
# project-analyst arch --path . --detect-patterns
# project-analyst monorepo --path . --analyze-all
# project-analyst watch --path . --on-change "reanalyze"
```

### Integration with project-planner
```python
# planner_integration.py
def generate_wbs_from_analysis(analysis: ProjectAnalysis) -> ProjectPlan:
    # Map detected tech stack to task templates
    # Identify setup tasks from missing configs
    # Suggest modernization tasks from outdated deps
    # Create architecture improvement tasks
    pass
```

---

## Acceptance Criteria
- [ ] Scanner detects 20+ frameworks across 8 languages
- [ ] Config detection covers 15+ tool types
- [ ] Architecture detection accuracy >85%
- [ ] Dependency health checks 100% of deps
- [ ] CLI completes scan in <10s for typical project
- [ ] Monorepo analysis handles 50+ packages
- [ ] Integration generates valid project-planner input
- [ ] Output formats: JSON, Markdown, SARIF, HTML

---

## Dependencies
- `project-planner` (planning integration)
- `code-quality` (quality metrics)
- `verification-before-completion` (health claims)
- `docs-write` (report generation)

---

## Risk Mitigation
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False framework detection | Medium | Low | Confidence scoring, manual override |
| Large monorepo performance | Low | Medium | Incremental scanning, caching |
| Config file false positives | Low | Low | Validation rules, allowlist |

---

## Success Metrics
- Detection accuracy: >90% for top 20 frameworks
- Scan speed: <5s for 10K file project
- Health score correlation: >0.8 with manual assessment
- Integration usage: >50% of project-planner invocations