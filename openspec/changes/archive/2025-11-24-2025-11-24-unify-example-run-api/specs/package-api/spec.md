# Package API Specification Delta

## MODIFIED Requirements

### Requirement: Run Function for Batch Guardrail Execution
The system SHALL update the example.py file to demonstrate unified bulk Run API usage as the primary pattern.

#### Scenario: Unified Bulk Testing Pattern
Given the example.py file demonstrates guardrail usage
When users run the example
Then it SHALL use guardrail.Run(all_guardrails, test_text) for testing all guardrails
And it SHALL show bulk execution as the primary pattern
And individual gr.check() calls SHALL be replaced with unified bulk calls
And all existing functionality SHALL be preserved

#### Scenario: Type-Safe Run API Demonstration
Given the Run() function has union return types
When the example demonstrates Run usage
Then it SHALL handle single results and list results correctly
And type errors SHALL be resolved
And examples SHALL be type-safe

#### Scenario: API Pattern Documentation
Given the example includes API pattern reference
When users see the "Key API patterns" section
Then it SHALL show bulk Run as the recommended primary pattern
And it SHALL reflect the actual demonstrated code patterns
And documentation SHALL be consistent with implementation</content>
<parameter name="filePath">openspec/changes/unify-example-run-api/specs/package-api/spec.md