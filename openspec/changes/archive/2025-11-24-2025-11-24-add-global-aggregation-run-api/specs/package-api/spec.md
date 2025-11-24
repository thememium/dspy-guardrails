# Package API Specification Delta

## MODIFIED Requirements

### Requirement: Run Function for Batch Guardrail Execution
The system SHALL modify the Run function to return aggregated results whenever multiple items are involved (breaking change from previous list-based behavior).

#### Scenario: Single Guardrail Execution (Unchanged)
Given a user calls guardrail.Run(single_guardrail, text)
When the function executes
Then it SHALL return a single GuardrailResult object
And users SHALL NOT need to access results[0]
And the return type SHALL match the input type intuitively

#### Scenario: Multiple Guardrail Execution (Aggregated)
Given a user calls guardrail.Run([gr1, gr2, gr3], text)
When the function executes
Then it SHALL return a single aggregated GuardrailResult
And global `is_allowed` SHALL be True only if ALL guardrails pass
And global `reason` SHALL contain the first failure reason
And metadata SHALL contain detailed per-guardrail results

#### Scenario: Multiple Text Execution with Global Aggregation
Given a user calls guardrail.Run(guardrails, ["text1", "text2", "text3"])
When the function executes
Then it SHALL process all texts against all guardrails
And it SHALL return a single GuardrailResult with global aggregation
And global `is_allowed` SHALL be True only if ALL texts pass ALL guardrails
And global `reason` SHALL contain the first failure reason encountered
And metadata SHALL contain detailed per-text results

#### Scenario: Global Aggregation Logic
Given multiple items are processed (guardrails or texts)
When any item fails any check
Then global `is_allowed` SHALL be False
And global `reason` SHALL be the reason from the first failure encountered
And processing SHALL continue unless early_return=True

#### Scenario: Metadata Structure for Aggregation
Given multiple items are processed
When the aggregated result is returned
Then metadata SHALL contain "text_results" key with per-text details
And metadata SHALL contain "guardrail_names" key with guardrail list
And each text result SHALL include individual GuardrailResult objects
And results SHALL be correlated by index

#### Scenario: Early Return with Aggregation
Given early_return=True and multiple items
When the first failure is detected
Then processing SHALL stop immediately
And global result SHALL reflect the failure
And remaining items SHALL not be processed

#### Scenario: Unified Return Type
Given the Run function handles all input combinations
When users call the function
Then it SHALL always return a single GuardrailResult
And type checkers SHALL work with consistent return type
And runtime validation SHALL handle all input combinations

#### Scenario: Breaking Change Migration
Given existing code expects lists from multiple guardrails
When the API changes to aggregated results
Then clear migration guidance SHALL be provided
And examples SHALL show how to access individual results from metadata
And the change SHALL be documented as breaking but beneficial