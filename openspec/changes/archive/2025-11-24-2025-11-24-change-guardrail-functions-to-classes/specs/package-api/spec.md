# Package API Specification - Change Guardrail Functions to Classes

## ADDED Requirements

### Requirement: Class-Based Guardrail API
The system SHALL provide class constructors in the `guardrail` module for creating guardrails, following Python naming conventions.

#### Scenario: Class Constructor Availability
Given a user wants to create guardrails
When they import the `guardrail` module
Then they can call `guardrail.Topic(...)`, `guardrail.Nsfw(...)`, etc.
And each class constructor returns a properly configured guardrail instance
And constructors accept identical parameters as the original functions

#### Scenario: Identical Functionality
Given guardrails created via class constructors
When they are used for content checking
Then they should behave identically to guardrails created via functions
And all configuration options should work the same way
And performance should be equivalent

#### Scenario: Improved IDE Support
Given users import the guardrail module
When they type `guardrail.` in their IDE
Then they should see class names starting with uppercase letters
And autocomplete should work for class constructors
And type hints should be properly displayed

### Requirement: Breaking Change - No Backward Compatibility
The system SHALL implement a breaking change by removing the old function-based API entirely.

#### Scenario: Old Functions Removed
Given users attempt to call old function-based API
When they try to access `guardrail.topic()`, `guardrail.nsfw()`, etc.
Then AttributeError should be raised
And no backward compatibility should be provided
And users must migrate to class-based API immediately

#### Scenario: Class-Only API
Given the guardrail module
When users import and use it
Then only class constructors should be available
And no function-based alternatives should exist
And the API should be purely class-based

## MODIFIED Requirements

### Requirement: Updated Documentation and Examples
The system SHALL update all documentation to prominently feature the class-based API.

#### Scenario: Primary API Documentation
Given the package README and documentation
When users read about guardrail creation
Then only the class-based API should be documented
And examples should show only class constructors
And no mention of old function-based API should remain

#### Scenario: Breaking Change Documentation
Given users of the package
When they read the documentation
Then they should be informed of the breaking change
And migration from functions to classes should be clearly explained
And no backward compatibility should be promised

### Requirement: Enhanced Type Safety
The system SHALL provide improved type hints for the class-based API.

#### Scenario: Constructor Type Hints
Given the class constructors in the guardrail module
When users use them in IDEs with type checking
Then all parameters should have proper type annotations
And return types should be clearly specified
And generic types should be used appropriately

#### Scenario: Class Discovery
Given users exploring the guardrail module
When they use dir() or IDE inspection
Then class names should be clearly distinguishable from functions
And class constructors should be properly typed