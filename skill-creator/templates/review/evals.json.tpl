{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to review the sample code or document",
      "expected_output": "A prioritized report with evidence and fix suggestions",
      "expectations": [
        "Findings include evidence",
        "Issues are prioritized by severity"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill on a target with no obvious issues",
      "expected_output": "A report that explicitly states nothing blocking was found",
      "expectations": [
        "Clear conclusion",
        "Remaining risks or style nits still listed"
      ]
    }
  ]
}
