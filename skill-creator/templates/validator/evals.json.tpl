{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to validate a compliant sample",
      "expected_output": "A pass/fail summary with no false violations",
      "expectations": [
        "Compliant input passes",
        "Report includes a clear summary"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill on input that violates several rules",
      "expected_output": "Each violation reported with location and rule",
      "expectations": [
        "All violations reported",
        "Each includes location and rule"
      ]
    }
  ]
}
