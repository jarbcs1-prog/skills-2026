# CI/CD workflow scaffolded by skill-creator for {{name}}
name: Skill Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Validate skill structure
        run: python scripts/validate_skill.py .

      - name: Run skill tests
        run: |
          python -m pytest tests/ -q

      - name: Validate eval set
        run: |
          python -c "import json; json.load(open('evals/evals.json')); print('evals.json OK')"

      - name: Validate skill manifest
        run: |
          python -c "import yaml, sys; m = yaml.safe_load(open('skill.yaml')); assert m.get('name'), 'missing name'; assert m.get('version'), 'missing version'; print('skill.yaml OK')"
