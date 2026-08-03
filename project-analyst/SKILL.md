---
name: project-analyst
description: Automated project analysis, technology detection, and architecture identification with dependency health reporting.
---

# Project Analyst

You deeply understand project architecture, technologies, and patterns through automated analysis.

## Capabilities

### Technology Detection
- **Package Managers**: npm/yarn/pnpm, pip/poetry/pipenv, Cargo, Go modules, Maven/Gradle, Bundler, Composer
- **Frameworks**: 25+ frameworks across JavaScript/TypeScript, Python, Rust, Go, Java ecosystems
- **Build Tools**: Webpack, Vite, Rollup, Parcel, ESBuild, Make, CMake, Gradle, Maven, etc.
- **Configuration Files**: ESLint, Prettier, Jest, Vitest, TSConfig, JSConfig, Django settings, Docker, Kubernetes, CI/CD configs

### Analysis Features
1. **Dependency Scanning**: Automatically discovers and parses package manifests
2. **Framework Detection**: Identifies frontend/backend frameworks from dependencies
3. **Architecture Pattern Recognition**: Detects MVC, Microservices, Hexagonal, Clean, Layered, Event-driven, CLI, Library, Monorepo patterns
4. **Dependency Health**: Checks for security issues, outdated packages, license information (placeholder for Phase 1)
5. **Project Health Scoring**: Computes overall health based on tests, CI, docs, licenses, etc.
6. **Recommendations**: Provides actionable suggestions for improvement

## Usage

### Basic Analysis
```bash
project-analyst scan
```

### With Custom Path
```bash
project-analyst scan --path ./my-project
```

### Output Formats
```bash
# JSON output for programmatic consumption
project-analyst scan --format json --output analysis.json

# Markdown report
project-analyst scan --format markdown --output README.md

# SARIF for security tool integration
project-analyst scan --format sarif --output results.sarif

# Human-readable text (default)
project-analyst scan
```

### Specialized Commands
```bash
# Dependency health report
project-analyst deps

# Architecture analysis
project-analyst arch

# Project statistics
project-analyst stats
```

## Output Format

### JSON Output
```json
{
  "technology_stack": {
    "javascript": ["react", "next"],
    "typescript": []
  },
  "health_score": 85.0,
  "recommendations": [
    "Add automated tests to improve code quality and prevent regressions",
    "Set up continuous integration for automated testing and deployment"
  ],
  "dependencies": {
    "react": {
      "version": "18.2.0",
      "license": "MIT",
      "security_issues": 0,
      "outdated": false,
      "health_score": 95.0
    }
  }
}
```

### Text Output (Default)
```
============================================================
PROJECT ANALYSIS REPORT
============================================================
Health Score: 85.0/100

TECHNOLOGY STACK:
  Javascript: react, next
  Typescript: None detected

CONFIGURATION FILES: 3 total
  eslint: 1 files
  prettier: 1 files
  typescript: 1 files

DEPENDENCIES:
Package              Version         License         Issues  Outdated  Health
react                18.2.0          MIT             0       No        95.0
lodash               4.17.21         MIT             0       No        90.0

RECOMMENDATIONS:
 1. Add automated tests to improve code quality and prevent regressions
 2. Set up continuous integration for automated testing and deployment
============================================================
```

## Architecture Detection

The analyzer identifies these architectural patterns:
- **MVC** (Model-View-Controller)
- **Microservices**
- **Hexagonal** (Ports and Adapters)
- **Clean Architecture**
- **Layered**
- **Event-driven**
- **CLI Application**
- **Library/Package**
- **Monorepo**

## Health Scoring

Project health is calculated based on:
- Presence of automated tests (20 points)
- CI/CD configuration (20 points)
- Documentation (README, docs/) (20 points)
- License file (10 points)
- Contributing guidelines (10 points)
- Linter/formatter configuration (10 points)
- Dependency health (10 points)

## Requirements

- Python 3.11+
- Dependencies: click, pyyaml, tomli, tomli-w, packaging, rich, httpx, sentence-transformers, numpy

## Implementation Notes

This implementation provides:
- Automated discovery of package files across multiple ecosystems
- Framework detection based on dependency analysis
- Architectural pattern recognition from directory structure
- Dependency health analysis (Phase 1: structural; Phase 2: registry integration)
- Multiple output formats for integration with other tools
- Actionable recommendations for project improvement

Future enhancements will include:
- Real-time dependency vulnerability checking
- License compliance scanning
- Outdated dependency detection with update suggestions
- Deeper architectural analysis (layer coupling, dependency cycles)
- Integration with project-planner for automated work breakdown structure generation