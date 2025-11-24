# Change: Make DSPy Configuration User-Controlled

## Why
Currently, the DSPy Guardrails package hard-codes the language model configuration (model name, temperature, etc.) in the `GuardrailConfig` class and factory functions. This prevents users from configuring their own DSPy setup, forcing them to use the pre-configured OpenRouter model. Users should be able to set up their own DSPy configuration instead of having it imposed by the package.

## What Changes
- Add `dspy_guardrails.configure()` function for guardrail-specific configuration
- Make `GuardrailConfig.model` optional (uses guardrail config when None)
- Modify guardrails to use guardrail-specific DSPy configuration
- Update factory functions to remove model parameters
- Add validation to ensure guardrails are properly configured before execution
- Update documentation and examples to show the new configuration approach

## Impact
- Affected specs: package-api (DSPy Integration requirement)
- Affected code: `dspy_guardrails/core/config.py`, `dspy_guardrails/factory.py`, all guardrail implementations
- **BREAKING**: Users must call `dspy_guardrails.configure()` before using guardrails
- Factory functions are simplified - no model parameters needed
- Users can use different models for guardrails vs their main application