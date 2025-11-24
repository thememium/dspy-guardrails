# Package API Specification Delta

## MODIFIED Requirements

### Requirement: Run Function for Batch Guardrail Execution
The system SHALL modify the Run function to always return List[GuardrailResult] for consistent API behavior.

#### Scenario: Single Guardrail Execution
Given a user calls guardrail.Run(single_guardrail, text)
When the function executes
Then it SHALL return [GuardrailResult] (a list with one element)
And users SHALL access the result as results[0]
And no type casting SHALL be required

#### Scenario: Multiple Guardrail Execution
Given a user calls guardrail.Run([gr1, gr2, gr3], text)
When the function executes
Then it SHALL return List[GuardrailResult] as before
And the API behavior SHALL remain unchanged
And users SHALL iterate over results as before

#### Scenario: Type Safety Improvement
Given the Run function has consistent return types
When users write code with the function
Then no Union types SHALL be present in the API
And type checkers SHALL work without casting
And IDE autocomplete SHALL work correctly

#### Scenario: Backward Compatibility Migration
Given existing code expects single results
When the API changes
Then clear migration guidance SHALL be provided
And examples SHALL show how to access single results from lists
And the change SHALL be documented as breaking but beneficial</content>
<parameter name="filePath">openspec/changes/simplify-run-return-type/specs/package-api/spec.md