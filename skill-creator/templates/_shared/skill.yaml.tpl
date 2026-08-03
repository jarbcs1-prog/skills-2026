# skill.yaml — machine-readable manifest for {{name}}
name: "{{name}}"
version: "{{version}}"
description: "{{description}}"
author: "{{author}}"
license: "MIT"
compatibility:
  opencode: ">=0.1.0"
  platforms: ["opencode-code", "opencode-ai", "cowork"]
dependencies: {{dependencies}}
scripts:
  - "scripts/__init__.py"
  - "scripts/validate_skill.py"
references:
  - "references/README.md"
assets:
  - "assets/README.md"
tests:
  - "tests/test_skill.py"
evals:
  - "evals/evals.json"
