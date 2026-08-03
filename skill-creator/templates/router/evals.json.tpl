{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Route a request that clearly matches one handler via the {{name}} skill",
      "expected_output": "The matching handler is chosen with rationale",
      "expectations": [
        "Correct handler selected",
        "Rationale is stated"
      ]
    },
    {
      "id": 2,
      "prompt": "Route an ambiguous request via the {{name}} skill",
      "expected_output": "Ambiguity is flagged or a sensible default with rationale is chosen",
      "expectations": [
        "Ambiguity is handled explicitly",
        "No silent misrouting"
      ]
    }
  ]
}
