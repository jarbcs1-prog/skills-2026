{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to analyze the sample dataset and report the key findings",
      "expected_output": "A report with concrete numbers, methodology and caveats",
      "expectations": [
        "Findings backed by concrete numbers",
        "Methodology is reproducible"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill with a dataset that has missing values",
      "expected_output": "Analysis that handles missing data explicitly",
      "expectations": [
        "Missing data is handled or documented",
        "Results are still computed"
      ]
    }
  ]
}
