# Summarization Schemas

This document outlines the principles and examples of structured summarization schemas used in the Dynamic Context Pruning Skill. The core idea is to avoid free-form summarization in favor of structured outputs that adhere to predefined schemas, ensuring consistency, extractability and utility of summarized context.

## Key Principle: Structured Outputs Only

Free-form text summaries, while seemingly flexible, often lead to loss of critical information, ambiguity and difficulty in programmatic extraction. By enforcing a schema, Manus ensures that summaries always contain specific, actionable and relevant data points.

## Example Summary Schema

```json
{
  "fields": [
    "files_modified",
    "user_goals", 
    "current_state",
    "pending_actions",
    "errors_encountered",
    "key_decisions"
  ],
  "required": [
    "user_goals", 
    "current_state"
  ]
}
```

### Field Descriptions:

-   **`files_modified`**: A list of files that have been created, modified or deleted during the summarized period, along with a brief description of the changes.
-   **`user_goals`**: The primary objectives or requests from the user that the agent is currently working towards or has addressed.
-   **`current_state`**: A concise description of the agent's operational state, including key variables, active processes or significant environmental factors.
-   **`pending_actions`**: A list of immediate next steps or planned actions the agent intends to take.
-   **`errors_encountered`**: Any significant errors, warnings or unexpected events that occurred, along with their resolution or current status.
-   **`key_decisions`**: Important decisions made by the agent, including the rationale and alternatives considered.

## Custom Schema Definition

Users can define custom schemas to tailor summarization to specific tasks or domains. A custom schema should specify:

-   **`fields`**: A list of strings, where each string is the name of a data point to be extracted into the summary.
-   **`required`**: A subset of `fields` that *must* be present in every summary generated using this schema. If a required field cannot be populated, it indicates a failure in summarization or a gap in the context.

## Benefits of Structured Summarization

-   **Consistency**: Summaries always follow a predictable format.
-   **Extractability**: Specific data points can be easily extracted and used by other tools or subsequent agent steps.
-   **Reduced Hallucination**: By guiding the model to fill specific fields, the risk of generating irrelevant or fabricated information is reduced.
-   **Actionability**: Summaries are directly useful for decision-making and planning, as they highlight critical aspects of the agent's progress and state.
