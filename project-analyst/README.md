# Project Analyst

Automated project analysis tool for detecting technology stacks, architectural patterns, and dependency health.

## Features

- 🔍 **Technology Detection**: Identifies programming languages, frameworks, and build tools
- 🏗️ **Architecture Analysis**: Detects common architectural patterns (MVC, Microservices, etc.)
- 📦 **Dependency Analysis**: Lists dependencies and provides health insights
- 📊 **Health Scoring**: Rates project health based on tests, CI, documentation, and more
- 💡 **Recommendations**: Suggests improvements for code quality and maintainability
- 📄 **Multiple Formats**: Output as JSON, Markdown, SARIF, or human-readable text

## Installation

```bash
pip install -e .
```

## Usage

### Basic Analysis
```bash
project-analyst scan
```

### Specify Project Path
```bash
project-analyst scan --path ./my-project
```

### Output Formats
```bash
# JSON
project-analyst scan --format json --output analysis.json

# Markdown
project-analyst scan --format markdown --output docs/analysis.md

# SARIF (for security tools)
project-analyst scan --format sarif --output results.sarif
```

### Specialized Views
```bash
# Dependency health report
project-analyst deps

# Architecture analysis
project-analyst arch

# Project statistics
project-analyst stats
```

## Example Output

```
============================================================
PROJECT ANALYSIS REPORT
============================================================
Health Score: 78.0/100

TECHNOLOGY STACK:
  Javascript: react, next, redux
  Typescript: typescript

CONFIGURATION FILES: 5 total
  eslint: 1 files
  prettier: 1 files
  typescript: 2 files
  jest: 1 files

DEPENDENCIES:
Package              Version         License         Issues  Outdated  Health
react                18.2.0          MIT             0       No        95.0
next                 13.4.0          MIT             0       No        90.0
typescript           5.0.4           MIT             0       No        95.0
eslint               8.42.0          MIT             0       No        90.0

RECOMMENDATIONS:
 1. Add automated tests to improve code quality and prevent regressions
 2. Set up continuous integration for automated testing and deployment
 3. Add a license file to clarify usage rights
============================================================
```

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
ruff check .
black .
```

## License

MIT