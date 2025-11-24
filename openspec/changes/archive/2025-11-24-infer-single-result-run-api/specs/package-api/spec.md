# Package API Specification Delta

## MODIFIED Requirements

### Requirement: Run Function for Batch Guardrail Execution
The system SHALL modify the Run function to return a single GuardrailResult when a single guardrail is passed, and List[GuardrailResult] when multiple guardrails are passed.

#### Scenario: Single Guardrail Execution
Given a user calls guardrail.Run(single_guardrail, text)
When the function executes
Then it SHALL return a single GuardrailResult object
And users SHALL NOT need to access results[0]
And the return type SHALL match the input type intuitively

#### Scenario: Multiple Guardrail Execution
Given a user calls guardrail.Run([gr1, gr2, gr3], text)
When the function executes
Then it SHALL return List[GuardrailResult] as before
And the API behavior SHALL remain unchanged for list inputs
And users SHALL iterate over results as before

#### Scenario: Type Safety with Union Types
Given the Run function has different return types based on input
When users write code with the function
Then Union[GuardrailResult, List[GuardrailResult]] SHALL be the return type
And type checkers SHALL work with proper type narrowing
And IDE autocomplete SHALL work correctly with the union

#### Scenario: Backward Compatibility Migration
Given existing code expects lists from single guardrails
When the API changes
Then clear migration guidance SHALL be provided
And examples SHALL show how to remove [0] indexing
And the change SHALL be documented as breaking but beneficial</content>
<parameter name="filePath">openspec/changes/infer-single-result-run-api/specs/package-api/spec.md