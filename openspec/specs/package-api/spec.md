# Package API Specification

## Purpose
This specification defines the requirements for the DSPy Guardrails Python package API, including package structure, guardrail classes, configuration management, execution patterns, and integration with DSPy for AI model operations.
## Requirements
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

### Requirement: Guardrail Configuration
The system SHALL provide a dedicated configuration system for guardrails that works independently of global DSPy configuration, allowing users to use different models for guardrails vs other AI operations.

#### Scenario: Dedicated Guardrail Configuration
Given a user wants to use guardrails
When they set up their application
Then they SHALL call `dspy_guardrails.configure(lm=their_lm)` to configure guardrails
And guardrails SHALL use the guardrail-specific configuration
And users SHALL NOT need to specify model parameters in guardrail functions

#### Scenario: Configuration Flexibility
Given a user has different model needs
When they configure their application
Then they CAN configure DSPy globally for their main app with one model
And they CAN configure guardrails separately with a different model
And both configurations SHALL work independently

#### Scenario: Automatic Fallback
Given a user has configured DSPy globally
When they call `dspy_guardrails.configure()` without parameters
Then guardrails SHALL use the globally configured DSPy LM
And users SHALL have the option to use global or guardrail-specific config

#### Scenario: Configuration Validation
Given guardrails are configured
When a guardrail executes
Then it SHALL verify guardrail configuration exists
And it SHALL raise clear errors if configuration is missing
And it SHALL use the configured model for all operations

#### Scenario: Factory Function Simplicity
Given a user uses factory functions to create guardrails
When they call factory functions like `create_topic_guardrail()`
Then they SHALL NOT need to provide model parameters
And the factory SHALL use the configured guardrail LM
And guardrail creation SHALL be simplified

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

