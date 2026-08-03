{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to convert a sample input document into the target output format",
      "expected_output": "A valid output file in the target format",
      "expectations": [
        "Output file is created",
        "Output opens and matches the documented format"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill on an empty or malformed input file",
      "expected_output": "A clear error message and no crash",
      "expectations": [
        "Graceful error handling",
        "Useful diagnostic message"
      ]
    }
  ]
}
