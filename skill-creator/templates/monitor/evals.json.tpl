{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to watch the sample metric feed for one cycle",
      "expected_output": "An observation log with threshold comparisons",
      "expectations": [
        "Observations are logged",
        "Threshold breaches are flagged with severity"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill when a metric is below the warning threshold",
      "expected_output": "No false alarm raised",
      "expectations": [
        "No alert for normal values",
        "Observations still recorded"
      ]
    }
  ]
}
