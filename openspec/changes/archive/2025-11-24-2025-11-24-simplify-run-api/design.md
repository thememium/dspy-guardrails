# Design: Simplify Run API Import

## Current Architecture Analysis

The current API structure has the Run function exposed at the package level:
```
dspy_guardrails/
├── __init__.py          # Exports Run function
├── guardrail.py         # Contains guardrail creation functions
└── ...
```

Users need to import both:
```python
from dspy_guardrails import guardrail
import dspy_guardrails  # For Run function
```

## Proposed Architecture

Move the Run function to the guardrail module while maintaining backward compatibility:
```
dspy_guardrails/
├── __init__.py          # Re-exports Run from guardrail
├── guardrail.py         # Contains guardrail functions + Run
└── ...
```

Users can import everything from one place:
```python
from dspy_guardrails import guardrail  # All functionality in one module
```

## Implementation Strategy

### 1. Function Migration
- Move Run function implementation from `__init__.py` to `guardrail.py`
- No changes to function signature or behavior
- Maintain all existing type hints and documentation

### 2. Backward Compatibility
- Keep Run available at package level by importing from guardrail module
- Existing code using `dspy_guardrails.Run` continues to work
- No breaking changes for current users

### 3. Import Patterns

**New Recommended Pattern:**
```python
from dspy_guardrails import guardrail

# Configure
guardrail.configure(lm=lm)

# Create guardrails
topic_gr = guardrail.topic(business_scopes=["AI"])

# Run guardrails
result = guardrail.Run(topic_gr, "text")
batch_results = guardrail.Run([topic_gr, nsfw_gr], "text")
```

**Legacy Pattern (still supported):**
```python
from dspy_guardrails import guardrail
import dspy_guardrails

# Legacy usage still works
result = dspy_guardrails.Run(guardrail, "text")
```

## Benefits

1. **Simplified Mental Model**: All guardrail operations in one module
2. **Reduced Import Overhead**: Single import for all functionality  
3. **Better Discoverability**: Users find Run function alongside guardrail creation functions
4. **Migration Path**: Clear upgrade path without breaking existing code
5. **Consistent API**: All guardrail-related functionality follows same import pattern

## Risk Assessment

**Low Risk Changes:**
- Function behavior remains identical
- Backward compatibility maintained
- No changes to core logic

**Mitigation:**
- Comprehensive testing of both import patterns
- Documentation updates showing both approaches
- Gradual migration recommendation in docs