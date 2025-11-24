# Simplify Run API Import

## Why
Users currently need to import both the guardrail module and the main package to access the Run function:
```python
from dspy_guardrails import guardrail
import dspy_guardrails

# Then use both
guardrail = guardrail.topic(...)
result = dspy_guardrails.Run(guardrail, text)
```

This creates unnecessary import overhead and API confusion.

## What Changes
Move the Run function from the main package to the guardrail module, allowing users to access everything through a single import:
```python
from dspy_guardrails import guardrail

# Create and run guardrails with single import
guardrail = guardrail.topic(...)
result = guardrail.Run(guardrail, text)
```

## Benefits
- **Simplified Imports**: Users only need to import the guardrail module
- **Consistent API**: All guardrail operations are available from the same module
- **Reduced Cognitive Load**: No need to remember which functions come from which module
- **Better Developer Experience**: Cleaner, more intuitive API surface

## Scope
- Move Run function from dspy_guardrails/__init__.py to dspy_guardrails/guardrail.py
- Update package exports to maintain backward compatibility
- Update examples and documentation
- Ensure all existing functionality is preserved

## Backward Compatibility
The current `dspy_guardrails.Run` will remain available for existing users, but documentation will recommend the new `guardrail.Run()` approach.