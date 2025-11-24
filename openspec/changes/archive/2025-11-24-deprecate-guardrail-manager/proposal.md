# Change: Deprecate and Remove GuardrailManager

## Why
The GuardrailManager class is no longer needed since the new Run() function provides a simpler and more direct way to execute multiple guardrails. The Run() function eliminates the need for managing guardrail instances separately and provides better ergonomics for batch execution with configurable early return behavior.

## What Changes
- **BREAKING**: Deprecate GuardrailManager class with warnings
- Remove GuardrailManager from public API exports
- Update example.py to remove GuardrailManager usage
- Update factory.py to remove create_comprehensive_guardrail_suite function
- Update tests to remove GuardrailManager tests
- Update README.md to remove GuardrailManager documentation
- Provide migration guide from GuardrailManager to Run() function

## Impact
- Affected specs: package-api
- Affected code: dspy_guardrails/core/manager.py, dspy_guardrails/__init__.py, example.py, factory.py, tests, README.md
- **BREAKING CHANGES**: GuardrailManager will be removed in a future version