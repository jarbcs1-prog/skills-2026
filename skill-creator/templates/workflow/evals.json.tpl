{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Execute the {{name}} workflow end to end",
      "expected_output": "All steps completed in order with state recorded",
      "expectations": [
        "Steps executed in documented order",
        "State recorded at each stage"
      ]
    },
    {
      "id": 2,
      "prompt": "Execute the {{name}} workflow but make step 3 fail",
      "expected_output": "Execution stops and reports the failure",
      "expectations": [
        "Failure stops the workflow",
        "Failure is reported clearly"
      ]
    }
  ]
}
