{
  "skill_name": "{{name}}",
  "evals": [
    {
      "id": 1,
      "prompt": "Use the {{name}} skill to connect to the external service with the configured credentials",
      "expected_output": "A working integration confirmed by a smoke test",
      "expectations": [
        "Connectivity confirmed",
        "Credentials come from environment variables"
      ]
    },
    {
      "id": 2,
      "prompt": "Use the {{name}} skill against a service that returns errors or rate limits",
      "expected_output": "Errors handled with retries and clear messages",
      "expectations": [
        "Rate limits and errors handled",
        "No secrets in logs"
      ]
    }
  ]
}
