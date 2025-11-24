# Package API Specification - Guardrail Module with Method-Based API

## ADDED Requirements

### Requirement: Guardrail Module API
The system SHALL provide a `guardrail` module with method-based functions for creating guardrails and global configuration.

#### Scenario: Global DSPy Configuration
Given a user wants to configure DSPy for guardrails
When they call `guardrail.configure(lm=lm)` before creating guardrails
Then DSPy should be configured globally for all guardrail operations
And subsequent guardrail creation should use the configured model
And configuration should persist for the application session

#### Scenario: Method-Based Guardrail Creation
Given a user wants to create guardrails
When they import the `guardrail` module
Then they can call `guardrail.topic(...)`, `guardrail.nsfw(...)`, etc.
And each function returns a properly configured guardrail instance
And functions accept keyword arguments for configuration

#### Scenario: Simplified Configuration with Defaults
Given a user wants to use default settings for guardrails
When they call guardrail functions with minimal parameters
Then guardrails should be created with sensible default values
And all required parameters should have appropriate defaults

#### Scenario: Parameter Validation
Given a user provides invalid configuration parameters
When guardrail functions are called
Then validation errors should be raised immediately
And clear error messages should indicate the specific problem
And no partial guardrail creation should occur

### Requirement: Enhanced Individual Guardrail Functions
The system SHALL provide enhanced individual guardrail creation functions with better defaults and consistency.

#### Scenario: Consistent Parameter Naming
Given different guardrail functions in the module
When users call them with configuration parameters
Then parameter names should be consistent across all functions
And naming conventions should follow Python best practices

#### Scenario: Improved Default Handling
Given guardrail functions with optional parameters
When users omit optional parameters
Then sensible defaults should be applied automatically
And documentation should clearly indicate default values

### Requirement: Type Safety and IDE Support
The system SHALL provide excellent type hints and IDE support for the guardrail module.

#### Scenario: Complete Type Hints
Given the guardrail module functions
When users use them in IDEs with type checking
Then all parameters should have proper type annotations
And return types should be clearly specified
And generic types should be used appropriately

#### Scenario: Function Autocomplete
Given users import the guardrail module
When they type `guardrail.` in their IDE
Then they should see autocomplete suggestions for all guardrail types
And function signatures should be displayed correctly

### Requirement: Comprehensive Error Handling
The system SHALL provide clear, actionable error messages for all failure scenarios.

#### Scenario: Configuration Validation Errors
Given invalid guardrail configuration
When guardrail functions are called
Then specific validation errors should be raised
And error messages should indicate which guardrail and parameter failed
And suggestions for fixes should be provided where possible

#### Scenario: Missing Required Parameters
Given guardrail functions are called without required parameters
When the functions execute
Then clear errors should indicate missing requirements
And examples of correct usage should be provided

### Requirement: Documentation and Examples
The system SHALL provide comprehensive documentation for the guardrail module API.

#### Scenario: Updated Package Documentation
Given the package README and documentation
When users read about guardrail creation
Then the method-based API should be prominently featured
And examples should show both old and new patterns
And migration guidance should be provided

#### Scenario: Function Docstrings
Given all guardrail module functions
When users access docstrings
Then comprehensive examples should be included
And all parameters should be documented with types and descriptions
And default values should be clearly indicated

### Requirement: Performance and Efficiency
The system SHALL ensure the guardrail module API doesn't impact performance or efficiency.

#### Scenario: Creation Performance
Given the guardrail module functions
When creating guardrails
Then creation time should be comparable to existing factory calls
And memory usage should remain efficient
And no unnecessary object creation should occur

#### Scenario: Execution Performance
Given guardrails created through the module API
When they execute content checks
Then performance should be identical to individually created guardrails
And DSPy configuration and LLM usage should be unchanged

## MODIFIED Requirements

### Requirement: Backward Compatibility
The system SHALL maintain full backward compatibility with existing factory functions and APIs.

#### Scenario: Existing Factory Functions Continue Working
Given existing user code using individual factory functions
When the code is executed after API changes
Then all existing factory functions should work unchanged
And no breaking changes should be introduced

#### Scenario: Existing Imports Remain Available
Given users importing guardrail classes and configs
When they use existing import patterns
Then all imports should continue to work
And no deprecation warnings should be added initially