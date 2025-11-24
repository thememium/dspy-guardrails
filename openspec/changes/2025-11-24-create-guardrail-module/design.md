# API Design for Guardrail Module with Method-Based Access

## Overview
This design proposes creating a `guardrail` module that provides method-based access to guardrail creation, allowing users to write clean, intuitive code like `guardrail.topic(business_scopes=["AI"])` instead of using separate config classes and factory functions.

## Current API Problems

### Verbose Configuration Pattern
```python
# Current approach - lots of imports and repetition
from dspy_guardrails import (
    TopicGuardrail, TopicGuardrailConfig,
    NsfwGuardrail, NsfwGuardrailConfig,
    JailbreakGuardrail, JailbreakGuardrailConfig,
)

# Separate config creation for each guardrail
topic_config = TopicGuardrailConfig(
    business_scopes=["Shipping Software", "Logistics", "Package Delivery"],
    competitor_names=["Shipo", "FastShip", "QuickDeliver"],
)
topic_guardrail = TopicGuardrail(topic_config)

nsfw_config = NsfwGuardrailConfig(sensitivity_level="medium")
nsfw_guardrail = NsfwGuardrail(nsfw_config)
# ... repeat for each guardrail type
```

### Issues with Current Approach
1. **Import Complexity**: Users must import both guardrail and config classes
2. **Repetitive Code**: Similar pattern repeated for each guardrail type
3. **Cognitive Load**: Users need to understand config class structure
4. **Error Prone**: Easy to mismatch config and guardrail types

## Proposed API Design

### Guardrail Module with Method-Based Functions
```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy globally before creating guardrails
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key")
guardrail.configure(lm=lm)

# Clean, method-based API
topic_guardrail = guardrail.topic(
    business_scopes=["Shipping Software", "Logistics"],
    competitor_names=["Shipo", "FastShip"]
)

nsfw_guardrail = guardrail.nsfw(sensitivity_level="medium")

jailbreak_guardrail = guardrail.jailbreak(detection_threshold=0.8)

# Use defaults for simple cases
pii_guardrail = guardrail.pii()
keywords_guardrail = guardrail.keywords(blocked_keywords=["inappropriate"])
secret_keys_guardrail = guardrail.secret_keys()
```

### Alternative: Import-Based Access
```python
from dspy_guardrails.guardrail import topic, nsfw, jailbreak

topic_guardrail = topic(business_scopes=["AI"])
nsfw_guardrail = nsfw(sensitivity_level="high")
```

## Design Decisions

### Module Structure
**Chosen: Single `guardrail` module**
- Provides a clean namespace for all guardrail creation functions
- Easy to import and use
- Consistent with Python module conventions
- Allows for future expansion

**Alternative Considered: Class-based factory**
```python
from dspy_guardrails import GuardrailFactory

factory = GuardrailFactory()
topic_gr = factory.topic(business_scopes=["AI"])
```
Rejected due to unnecessary object instantiation.

### Parameter Structure
**Chosen: Keyword arguments with defaults**
- Allows optional parameters with clear defaults
- Supports IDE autocomplete and type checking
- Easy to extend with new configuration options
- Follows Python best practices

### Function Signatures
```python
def topic(
    business_scopes: List[str],
    competitor_names: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    # ... other DSPy config options
) -> TopicGuardrail:
    """Create a topic compliance guardrail."""
    # Implementation
```

### Return Types
**Chosen: Direct guardrail instances**
- Simple and predictable
- Easy to use immediately
- Consistent with existing patterns

## Implementation Strategy

### Core Module Design
```python
# dspy_guardrails/guardrail.py
"""Guardrail creation functions with method-based API."""

from typing import List, Optional, Any
from dspy_guardrails.core.config import TopicGuardrailConfig, configure as _configure
from dspy_guardrails.guardrails import TopicGuardrail


def configure(lm=None, **kwargs):
    """
    Configure DSPy globally for guardrail usage.

    This function sets up DSPy configuration that will be used by all guardrails.
    It should be called once at application startup before creating any guardrails.

    Args:
        lm: DSPy language model to use for guardrails
        **kwargs: Additional configuration options

    Example:
        import dspy
        from dspy_guardrails import guardrail

        lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="key")
        guardrail.configure(lm=lm)
    """
    return _configure(lm=lm, **kwargs)


def topic(
    business_scopes: List[str],
    competitor_names: Optional[List[str]] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    cache_enabled: bool = False,
    timeout_seconds: Optional[float] = None,
    api_key_env_var: str = "OPENROUTER_API_KEY",
) -> TopicGuardrail:
    """
    Create a topic compliance guardrail.

    Args:
        business_scopes: List of business topics that are considered on-topic
        competitor_names: List of competitor names to flag (optional)
        model: DSPy model to use (optional, uses global config if not provided)
        temperature: Temperature for LLM calls (default: 0.0)
        max_tokens: Maximum tokens for LLM calls (optional)
        cache_enabled: Whether to enable caching (default: False)
        timeout_seconds: Timeout for LLM calls in seconds (optional)
        api_key_env_var: Environment variable for API key (default: "OPENROUTER_API_KEY")

    Returns:
        Configured TopicGuardrail instance

    Example:
        guardrail = topic(
            business_scopes=["AI", "Machine Learning"],
            competitor_names=["OpenAI", "Google"]
        )
    """
    if competitor_names is None:
        competitor_names = []

    config = TopicGuardrailConfig(
        business_scopes=business_scopes,
        competitor_names=competitor_names,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_enabled=cache_enabled,
        timeout_seconds=timeout_seconds,
        api_key_env_var=api_key_env_var,
    )
    return TopicGuardrail(config)


# Similar functions for nsfw, jailbreak, etc.
```

### Package Integration
```python
# dspy_guardrails/__init__.py
from . import guardrail  # Expose the guardrail module

__all__ = [
    "guardrail",  # New module-based API
    # ... existing exports
]
```

## Type Safety Considerations

### Type Hints
- All parameters have proper type annotations
- Return types are explicitly specified
- Generic types used appropriately
- Optional parameters use `Optional[T]`

### Runtime Validation
- Parameter types validated at runtime
- Configuration compatibility ensured
- Helpful error messages provided

## Testing Strategy

### Unit Tests
- Test each `guardrail.*()` function
- Test parameter validation and error handling
- Test default value application
- Test integration with existing guardrail classes

### Integration Tests
- Test end-to-end guardrail execution
- Test configuration propagation
- Test error scenarios

### Migration Tests
- Ensure existing code continues to work
- Test mixed usage of old and new APIs

## Performance Considerations

### Creation Time
- Minimal overhead compared to individual factory calls
- Direct function calls with no additional abstraction layers
- Same DSPy and LLM usage patterns

### Memory Usage
- No additional objects created beyond the guardrail instances
- Efficient parameter passing

## Future Extensibility

### Adding New Guardrails
- Easy to add new functions to the `guardrail` module
- Consistent API patterns maintained
- Backward compatible additions

### Advanced Features
- Could add factory functions for guardrail combinations
- Could support custom guardrail registration
- Could add preset configurations

## Migration Path

### Phase 1: Add New API
- Implement `guardrail` module alongside existing functions
- Update documentation with examples
- No breaking changes

### Phase 2: Enhance Documentation
- Update README and examples
- Create migration guide
- Highlight benefits of new API

### Phase 3: Deprecation (Future)
- Consider deprecating verbose patterns in future major version
- Maintain backward compatibility indefinitely