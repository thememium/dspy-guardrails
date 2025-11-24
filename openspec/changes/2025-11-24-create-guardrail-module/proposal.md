# Create Guardrail Module with Method-Based API

## Summary
Create a `guardrail` module that provides a clean, method-based API for creating guardrails, allowing users to write `guardrail.topic(...)`, `guardrail.nsfw(...)`, etc. instead of using separate config classes and factory functions.

## Why
The current guardrail creation API requires users to:
1. Import multiple classes (guardrail + config) for each guardrail type
2. Create separate configuration objects manually
3. Use verbose factory function calls

This creates unnecessary friction for users who want to set up guardrails, leading to:
- Verbose, error-prone code
- Steep learning curve for new users
- Maintenance burden when adding new guardrails
- Poor developer experience compared to modern Python APIs

By creating a `guardrail` module with method-based access, we can:
- Provide a clean, intuitive API (`guardrail.topic(...)`)
- Reduce boilerplate significantly
- Maintain full configurability while offering sensible defaults
- Improve type safety and IDE support
- Enable easier testing and prototyping

## What Changes
- **Create new `guardrail` module** with method-based factory functions
- **Add `topic()`, `nsfw()`, `jailbreak()`, etc. functions** that accept keyword arguments
- **Add `configure()` function** to the guardrail module for global DSPy setup
- **Update package imports** to expose the new `guardrail` module
- **Maintain backward compatibility** - all existing factory functions continue to work unchanged
- **Improve type safety** with comprehensive type hints for the new API
- **Add comprehensive error handling** with clear validation messages
- **Update documentation** with examples of the new method-based API patterns

## Solution
Create a `guardrail` module that provides method-based access to guardrail creation and configuration:

```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy globally (can be done once at startup)
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key")
guardrail.configure(lm=lm)

# Now create guardrails with clean, method-based API
topic_guardrail = guardrail.topic(
    business_scopes=["Shipping Software", "Logistics"],
    competitor_names=["Shipo", "FastShip"]
)

nsfw_guardrail = guardrail.nsfw(sensitivity_level="medium")

jailbreak_guardrail = guardrail.jailbreak(detection_threshold=0.8)

# Use defaults
pii_guardrail = guardrail.pii()
keywords_guardrail = guardrail.keywords(blocked_keywords=["inappropriate"])
```

This replaces the verbose current approach:
```python
from dspy_guardrails import (
    TopicGuardrail, TopicGuardrailConfig,
    NsfwGuardrail, NsfwGuardrailConfig,
    JailbreakGuardrail, JailbreakGuardrailConfig,
)

topic_config = TopicGuardrailConfig(
    business_scopes=["Shipping Software", "Logistics"],
    competitor_names=["Shipo", "FastShip"],
)
topic_guardrail = TopicGuardrail(topic_config)
# ... repeat for each guardrail
```

## Impact
- **Reduced Boilerplate**: Users write ~70% less code to set up guardrails
- **Improved DX**: Clean method-based API (`guardrail.topic(...)`)
- **Maintained Flexibility**: All existing configuration options still available
- **Backward Compatible**: Existing factory functions continue to work
- **Type Safe**: Full type hints maintained throughout

## Scope
**In Scope:**
- Create new `guardrail` module with method-based functions
- Implement `topic()`, `nsfw()`, `jailbreak()`, `pii()`, `keywords()`, `secret_keys()` functions
- Update package imports to expose the `guardrail` module
- Maintain all existing configuration options
- Add comprehensive type hints and validation

**Out of Scope:**
- Changes to guardrail logic or DSPy signatures
- New guardrail types
- Breaking changes to existing APIs
- Performance optimizations

## Dependencies
- Existing guardrail implementations remain unchanged
- No new external dependencies
- Leverages existing factory function infrastructure

## Risks
- Risk of introducing breaking changes to existing user code
- Risk of API confusion with existing `guardrails` module
- Risk of losing type safety in the simplified API

## Success Criteria
- Users can create guardrails with `guardrail.topic(...)` style API
- Existing factory functions continue to work unchanged
- All configuration options remain accessible
- Type checking and IDE support maintained
- Documentation updated with new method-based patterns
- Tests pass for both old and new APIs