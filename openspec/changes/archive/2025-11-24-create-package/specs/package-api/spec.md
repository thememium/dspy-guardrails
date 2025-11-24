# Package API Specification

## ADDED Requirements

### Requirement: Package Structure and Initialization
The system SHALL provide a proper Python package structure that can be imported and used programmatically.

#### Scenario: Basic Package Import
Given the DSPy Guardrails package is installed
When a user imports `from dspy_guardrails import TopicGuardrail`
Then the package should load successfully without errors
And all required dependencies should be available

#### Scenario: Package Installation
Given a user wants to install the package
When they run `pip install dspy-guardrails` 
Then the package should install correctly
And all dependencies should be resolved
And the package should be importable in Python 3.12+

### Requirement: Guardrail Base Classes
The system SHALL provide base classes that define common interfaces for all guardrails.

#### Scenario: Base Guardrail Interface
Given a developer wants to create a custom guardrail
When they extend the `BaseGuardrail` class
Then they must implement the `check()` method
And they must inherit common configuration and error handling
And the interface should be consistent across all guardrail types

#### Scenario: Result Types
Given a guardrail execution completes
When the result is returned to the user
Then it should include decision boolean (allowed/blocked)
And it should include reasoning or metadata
And it should have consistent structure across guardrail types

### Requirement: Configuration Management
The system SHALL provide a unified configuration system for all guardrails.

#### Scenario: Configuration Validation
Given a user creates guardrail configuration
When the configuration is applied to a guardrail
Then invalid configurations should raise clear exceptions
And valid configurations should be accepted without errors
And configuration should be type-safe

#### Scenario: Default Configuration
Given a user wants to use default settings
When they create a guardrail without explicit configuration
Then sensible defaults should be applied
And the guardrail should function correctly
And defaults should be documented

### Requirement: Individual Guardrail Execution
The system SHALL provide the ability to execute individual guardrails programmatically.

#### Scenario: Single Text Check
Given a user has a text input to validate
When they call `guardrail.check(text)`
Then the guardrail should process the text
And return a decision result
And the result should include reasoning if blocked

#### Scenario: Batch Processing
Given a user has multiple texts to validate
When they call `guardrail.check_batch(texts)`
Then all texts should be processed
And results should be returned in the same order
And processing should be efficient

### Requirement: DSPy Integration
The system SHALL properly integrate with DSPy for AI model execution.

#### Scenario: DSPy Configuration
Given a guardrail is initialized
When it needs to process text
Then DSPy should be properly configured
And the correct LLM model should be used
And API keys should be handled securely

#### Scenario: Model Selection
Given a user wants to use a specific LLM model
When they configure the guardrail
Then the specified model should be used
And model configuration should be validated
And fallback options should be available

### Requirement: Error Handling
The system SHALL provide comprehensive error handling for all failure scenarios.

#### Scenario: Configuration Errors
Given invalid guardrail configuration
When the guardrail is initialized
Then a clear exception should be raised
And the error message should explain the issue
And documentation should reference the solution

#### Scenario: Runtime Errors
Given an error occurs during guardrail execution
When the error happens
Then it should be caught and handled gracefully
And meaningful error information should be provided
And the application should not crash

### Requirement: Type Safety
The system SHALL provide full type hints and type safety for all public APIs.

#### Scenario: Type Hints
Given a developer uses the package
When they write code with guardrails
Then all public methods should have type hints
And IDEs should provide proper autocomplete
And static type checkers should pass

#### Scenario: Runtime Type Validation
Given method parameters are provided
When the guardrail methods are called
Then parameter types should be validated
And type errors should be caught early
And clear error messages should be provided

## MODIFIED Requirements

### Requirement: Existing Notebook Compatibility
The existing notebook functionality SHALL remain unchanged while adding package capabilities.

#### Scenario: Notebook Functionality Preservation
Given the existing guardrail notebooks
When the package is installed
Then all notebooks should continue to work exactly as before
And no notebook functionality should be broken
And users should be able to use both notebooks and package

#### Scenario: Notebook Package Integration
Given a user wants to use the package in notebooks
When they import package classes in notebooks
Then the integration should work seamlessly
And notebook execution should be enhanced
And existing patterns should still work