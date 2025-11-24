# Change Guardrail Functions to Classes

## Summary
Change the guardrail module API from lowercase functions (`guardrail.topic()`) to uppercase class constructors (`guardrail.Topic()`) to provide a more conventional Python API that aligns with class-based design patterns.

## Why
The current guardrail module uses lowercase functions that return guardrail instances, which creates an inconsistent API compared to typical Python class patterns. Users expect to see class names starting with uppercase letters when creating objects.

This change will:
- Provide a more conventional Python API
- Make the API more discoverable and intuitive
- Align with standard Python naming conventions for classes
- Improve IDE support and autocomplete
- Make the API feel more object-oriented

## What Changes
- **Change function names to class names** in `guardrail.py`: `topic()` → `Topic()`, `nsfw()` → `Nsfw()`, etc.
- **Maintain identical functionality** - classes will have the same `__init__` signatures as the original functions
- **Update all documentation and examples** to use the new class-based API
- **Add backward compatibility** by keeping the old functions as deprecated aliases
- **Update type hints** to reflect class constructors
- **Maintain all configuration options** and default values

## Solution
Transform the guardrail module to use class constructors instead of functions:

```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy globally (unchanged)
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key")
guardrail.configure(lm=lm)

# New class-based API
topic_guardrail = guardrail.Topic(
    business_scopes=["Shipping Software", "Logistics"],
    competitor_names=["Shipo", "FastShip"]
)

nsfw_guardrail = guardrail.Nsfw(sensitivity_level="medium")
jailbreak_guardrail = guardrail.Jailbreak(detection_threshold=0.8)

# Old function-based API still works (deprecated)
topic_guardrail_old = guardrail.topic(
    business_scopes=["Shipping Software", "Logistics"],
    competitor_names=["Shipo", "FastShip"]
)
```

## Impact
- **Improved API Consistency**: Follows Python naming conventions for classes
- **Better IDE Support**: Class constructors provide better autocomplete and type inference
- **Enhanced Discoverability**: Users can easily identify available guardrail types
- **Maintained Functionality**: All existing behavior and configuration options preserved
- **Backward Compatible**: Old function API remains available during transition period

## Scope
**In Scope:**
- Change all guardrail creation functions to classes in `guardrail.py`
- Update documentation and examples
- Add deprecation warnings for old function usage
- Maintain all existing configuration parameters and defaults

**Out of Scope:**
- Changes to guardrail logic or DSPy signatures
- New guardrail types
- Breaking changes to configuration classes
- Performance optimizations

## Dependencies
- No new external dependencies
- Leverages existing guardrail class infrastructure
- Maintains compatibility with all existing guardrail implementations

## Risks
- Risk of user confusion during transition period
- Risk of breaking existing code that relies on function-style API
- Risk of inconsistent usage patterns during deprecation period

## Success Criteria
- Users can create guardrails with `guardrail.Topic(...)` style API
- Old function API continues to work with deprecation warnings
- All configuration options remain accessible
- Type checking and IDE support improved
- Documentation updated with new class-based patterns
- Tests pass for both old and new APIs