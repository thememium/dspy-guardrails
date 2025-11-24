## MODIFIED Requirements

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