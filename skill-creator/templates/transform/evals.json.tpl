{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to transform the sample data into the target schema",
      "expected_output": "Transformed data with a verification report",
      "expectations": [
        "All records transformed (counts match)",
        "Field mapping is documented"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill on data with null and malformed fields",
      "expected_output": "Missing data handled explicitly, nothing silently dropped",
      "expectations": [
        "Null handling is explicit",
        "Nothing silently dropped"
      ]
    }
  ]
}
