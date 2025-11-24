# Migration Guide

## Production Release - Deprecated Code Removal

As of this version, DSPy Guardrails has been cleaned up for production release. All deprecated code has been completely removed to provide a clean, maintainable API surface.

## What Was Removed

### 1. GuardrailManager Class
The `GuardrailManager` class and all its methods have been completely removed. Use the `guardrail.Run()` function instead for batch guardrail execution.

### 2. Factory Functions
All factory functions (`create_topic_guardrail`, `create_nsfw_guardrail`, etc.) have been removed. Use the `guardrail` module API instead.

### 3. Model Parameters
Model parameters in guardrail creation functions have been removed. DSPy configuration is now handled globally.

## Current Production API

```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy globally (required)
dspy.configure(lm=dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key"))

# Create guardrails using the clean API
topic_guardrail = guardrail.topic(
    business_scopes=["AI", "Machine Learning"],
    competitor_names=["OpenAI", "Google"]
)

nsfw_guardrail = guardrail.nsfw(sensitivity_level="high")

# Run guardrails
single_result = guardrail.Run(topic_guardrail, "content")  # Returns GuardrailResult
batch_results = guardrail.Run([topic_guardrail, nsfw_guardrail], "content")  # Returns List[GuardrailResult]
```

## Migration from Previous Versions

If you were using deprecated APIs, here's how to migrate:

### From GuardrailManager
```python
# Old (no longer available)
from dspy_guardrails import GuardrailManager
manager = GuardrailManager()
manager.add_guardrail("topic", topic_guardrail)
results = manager.check("content")

# New
from dspy_guardrails import guardrail
results = guardrail.Run([topic_guardrail], "content")
```

### From Factory Functions
```python
# Old (no longer available)
from dspy_guardrails import create_topic_guardrail
guardrail = create_topic_guardrail(
    business_scopes=["AI"],
    model="openrouter/google/gemini-2.5-flash-preview-09-2025"
)

# New
from dspy_guardrails import guardrail
guardrail.configure(lm=dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="key"))
topic_guardrail = guardrail.topic(business_scopes=["AI"])
```

### From Model Parameters
```python
# Old (no longer available)
guardrail = guardrail.topic(
    business_scopes=["AI"],
    model="openrouter/google/gemini-2.5-flash-preview-09-2025",
    temperature=0.5
)

# New
# Configure globally, then create with only guardrail-specific parameters
guardrail.configure(lm=dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="key"))
topic_guardrail = guardrail.topic(business_scopes=["AI"])
```

## Benefits of the Production API

1. **Simplified API**: Fewer concepts to learn and maintain
2. **Global Configuration**: DSPy configuration is handled once at the application level
3. **Type Safety**: Better type hints and validation
4. **Performance**: Reduced overhead from deprecated code paths
5. **Maintainability**: Smaller codebase with focused functionality

## Error Messages

If you forget to configure DSPy, you'll see:
```
DSPy is not properly configured. Please configure DSPy before using guardrails.
```

## Need Help?

The production API is designed to be intuitive and self-documenting. Check the README.md for comprehensive examples and API documentation.