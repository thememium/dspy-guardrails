# Package API Specification - Cleanup Delta

## REMOVED Requirements

### Requirement: GuardrailManager Class
The GuardrailManager class and all its methods have been removed. Use the Run() function instead for batch guardrail execution.

### Requirement: Factory Functions
All factory functions (create_topic_guardrail, create_nsfw_guardrail, etc.) have been removed. Use the guardrail module API instead.

### Requirement: Per-Guardrail Model Configuration
Model parameters in guardrail creation functions have been removed. Use global guardrail configuration instead.

## MODIFIED Requirements

### Requirement: Guardrail Configuration
The system SHALL use global guardrail configuration only. Individual guardrail functions SHALL NOT accept model parameters.

#### Scenario: Simplified Guardrail Creation
Given a user wants to create guardrails
When they call guardrail functions like `guardrail.topic()`
Then they SHALL only provide guardrail-specific parameters
And DSPy configuration SHALL be handled globally
And no model parameters SHALL be accepted

#### Scenario: Global Configuration Only
Given guardrails need DSPy configuration
When the application starts
Then users SHALL call `guardrail.configure(lm=their_lm)` once
And all guardrails SHALL use this global configuration
And per-guardrail model configuration SHALL NOT be supported

### Requirement: Package API Surface
The package SHALL export only the production-ready API components.

#### Scenario: Clean Package Imports
Given a user imports from dspy_guardrails
When they use `from dspy_guardrails import *`
Then they SHALL get only guardrail, BaseGuardrail, GuardrailResult, configure, Run, and guardrail classes
And no deprecated functions SHALL be included
And the API surface SHALL be minimal and focused</content>
<parameter name="filePath">openspec/changes/cleanup-deprecated-code-for-production/specs/package-api/spec.md