# Change: Cleanup Deprecated Code for Production Release

## Why
The DSPy Guardrails package has accumulated deprecated code and unused functionality that should be removed before the first production release. This includes the deprecated GuardrailManager class, redundant factory functions, and legacy model parameters that are no longer needed with the new user-controlled DSPy configuration system.

## What Changes
- **BREAKING**: Remove GuardrailManager class completely (was deprecated with warnings)
- **BREAKING**: Remove all factory functions (create_topic_guardrail, create_nsfw_guardrail, etc.) as they're redundant with the guardrail module API
- **BREAKING**: Remove model parameters from guardrail module functions since DSPy configuration is now user-controlled
- Update main package exports to remove deprecated functions
- Update documentation to remove references to deprecated APIs
- Update tests to remove deprecated code tests
- Update migration guide to reflect final API state

## Impact
- Affected specs: package-api
- Affected code: dspy_guardrails/core/manager.py, dspy_guardrails/factory.py, dspy_guardrails/guardrail.py, dspy_guardrails/__init__.py, tests, README.md, MIGRATION_GUIDE.md
- **BREAKING CHANGES**: Multiple deprecated APIs will be completely removed
- Benefits: Cleaner API, reduced maintenance burden, production-ready codebase</content>
<parameter name="filePath">openspec/changes/cleanup-deprecated-code-for-production/proposal.md