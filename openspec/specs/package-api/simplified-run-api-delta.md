# Simplified Run API Specification

## Purpose
This specification defines the requirements for simplifying the Run function import by moving it from the main package to the guardrail module while maintaining backward compatibility.

## ADDED Requirements

### Requirement: Simplified Run Function Access
The system SHALL provide the Run function through the guardrail module to enable single-import access to all guardrail functionality.

#### Scenario: Single Import Pattern
Given a user wants to use guardrails with simplified imports
When they import only the guardrail module
Then they SHALL be able to access the Run function as guardrail.Run()
And they SHALL be able to create guardrails using guardrail functions
And they SHALL not need to import the main package separately

#### Scenario: Complete Workflow with Single Import
Given a user wants the complete guardrail workflow
When they use only `from dspy_guardrails import guardrail`
Then they SHALL be able to configure DSPy with guardrail.configure()
And they SHALL be able to create guardrails with guardrail.topic(), guardrail.nsfw(), etc.
And they SHALL be able to execute guardrails with guardrail.Run()
And all functionality SHALL be available through the single import

#### Scenario: Function Signature Preservation
Given the Run function is moved to the guardrail module
When users call guardrail.Run()
Then the function signature SHALL be identical to the original
And all parameters SHALL work the same way
And return types SHALL be consistent
And all existing behavior SHALL be preserved

### Requirement: Backward Compatibility Maintenance
The system SHALL maintain backward compatibility for existing users who import Run from the main package.

#### Scenario: Legacy Import Pattern
Given an existing user imports Run from the main package
When they use `import dspy_guardrails` and call `dspy_guardrails.Run()`
Then the function SHALL continue to work without changes
And the behavior SHALL be identical to the new API
And no breaking changes SHALL be introduced

#### Scenario: Mixed Import Patterns
Given a project uses both old and new import patterns
When both `dspy_guardrails.Run` and `guardrail.Run` are used
Then both SHALL work correctly
And both SHALL produce identical results
And no conflicts SHALL occur

#### Scenario: Package Exports
Given the package maintains backward compatibility
When users import from dspy_guardrails
Then Run SHALL still be available in the package exports
And the __all__ list SHALL include Run
And existing import statements SHALL continue to work

## MODIFIED Requirements

### Requirement: Package API Import Patterns
The system SHALL update the recommended import patterns while maintaining existing functionality.

#### Scenario: Documentation Examples
Given the API documentation is updated
When users read the examples
Then they SHALL show the simplified single-import pattern as recommended
And they SHALL mention backward compatibility for existing code
And migration guidance SHALL be provided

#### Scenario: Example Code Updates
Given the example.py file demonstrates API usage
When it is updated
Then it SHALL use the new guardrail.Run() pattern
And it SHALL demonstrate the simplified import approach
And all examples SHALL continue to work correctly