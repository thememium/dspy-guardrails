## ADDED Requirements
### Requirement: Run Function for Batch Guardrail Execution
The system SHALL provide a Run() function that executes guardrails with configurable behavior.

#### Scenario: Single Guardrail Execution
Given a user has a single guardrail instance
When they call `Run(guardrail, text)`
Then the guardrail should execute on the text
And return a single GuardrailResult
And the result should include is_allowed, reason, and metadata

#### Scenario: Batch Guardrail Execution with Run All
Given a user has a list of guardrails
When they call `Run([gr1, gr2, gr3], text, early_return=False)`
Then all guardrails should execute regardless of individual failures
And return a list of GuardrailResult objects
And results should be in the same order as input guardrails

#### Scenario: Batch Guardrail Execution with Early Return
Given a user has a list of guardrails
When they call `Run([gr1, gr2, gr3], text, early_return=True)`
Then guardrails should execute in order until one fails
And execution should stop on first is_allowed=False result
And return results only up to and including the failing guardrail

#### Scenario: Default Early Return Behavior
Given a user calls Run() without early_return parameter
When they call `Run(guardrails, text)`
Then early_return should default to False (run all guardrails)
And all guardrails should execute

#### Scenario: Consistent Guardrail Results
Given any guardrail is executed via Run()
When the result is returned
Then it should always include is_allowed (bool), reason (optional str), and metadata (dict)
And the guardrail_name should be populated
And the structure should be consistent across all guardrail types