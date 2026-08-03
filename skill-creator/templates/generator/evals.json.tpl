{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to generate output from this specification",
      "expected_output": "Generated output matching the specification",
      "expectations": [
        "Output matches the spec",
        "Style and structure are consistent"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill with a vague specification",
      "expected_output": "The skill asks for clarification rather than guessing",
      "expectations": [
        "Ambiguity is flagged",
        "Output is not invented from thin air"
      ]
    }
  ]
}
