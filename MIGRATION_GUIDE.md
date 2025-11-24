# Migration Guide

## Run API Return Type Changes (Latest)

### What Changed
The `guardrail.Run()` function now returns different types based on input:
- **Single guardrail**: Returns a single `GuardrailResult` (not a list)
- **Multiple guardrails**: Returns `List[GuardrailResult]` (unchanged)

### Migration
```python
# Before (required [0] indexing)
results = guardrail.Run(topic_guardrail, "content")
result = results[0]  # Had to access first element

# After (direct access)
result = guardrail.Run(topic_guardrail, "content")
# result is already a GuardrailResult
```

### Impact
- **Breaking change**: Code expecting lists from single guardrails will break
- **Simple fix**: Remove `[0]` indexing when using single guardrails
- **List usage**: Multiple guardrail calls work exactly the same

---

## DSPy Configuration Changes (Previous)

## Overview

As of this version, DSPy Guardrails no longer hard-codes the language model configuration. Users must now explicitly configure DSPy before using guardrails. This change provides greater flexibility and allows users to choose their preferred LLM provider.

## What Changed

### Before (Hard-coded Configuration)
```python
from dspy_guardrails import create_topic_guardrail

# This worked before - model was hard-coded internally
guardrail = create_topic_guardrail(
    business_scopes=["AI", "ML"],
    competitor_names=["OpenAI", "Google"]
)
```

### After (User-Controlled Configuration)
```python
import dspy
from dspy_guardrails import create_topic_guardrail

# Step 1: Configure DSPy first (required)
dspy.configure(
    lm=dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key")
    # Or any other DSPy-supported provider
)

# Step 2: Create guardrails (no model specification needed)
guardrail = create_topic_guardrail(
    business_scopes=["AI", "ML"],
    competitor_names=["OpenAI", "Google"]
)
```

## Migration Steps

### 1. Add Guardrail Configuration
At the beginning of your application, configure guardrails with your preferred LLM:

```python
import dspy
from dspy_guardrails import configure

# Option 1: Configure guardrails directly
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key")
configure(lm=lm)

# Option 2: Use globally configured DSPy LM
dspy.configure(lm=lm)  # Configure DSPy globally first
configure()  # Guardrails will use the global DSPy config

# Option 3: Different models for different purposes
dspy.configure(lm=dspy.LM("openai/gpt-4", api_key="openai-key"))  # For your main app
configure(lm=dspy.LM("openrouter/google/gemini-flash", api_key="router-key"))  # For guardrails
```

### 2. Factory Functions Remain Simple
Factory functions work the same way (no model parameters needed):

```python
# These work exactly the same as before
topic_guardrail = create_topic_guardrail(business_scopes=["AI"])
nsfw_guardrail = create_nsfw_guardrail()
```

### 3. Direct Config Instantiation Unchanged
`GuardrailConfig` instantiations work the same way:

```python
# These work exactly the same as before
config = TopicGuardrailConfig(business_scopes=["AI"])
```

### 4. Comprehensive Suite Creation Unchanged
```python
# This works exactly the same as before
suite = create_comprehensive_guardrail_suite(business_scopes=["AI"])
```

### 2. Update Factory Function Calls
Add the `model` parameter to all factory function calls:

```python
# Before
topic_guardrail = create_topic_guardrail(business_scopes=["AI"])
nsfw_guardrail = create_nsfw_guardrail()

# After
topic_guardrail = create_topic_guardrail(
    business_scopes=["AI"],
    model="openrouter/google/gemini-2.5-flash-preview-09-2025"
)
nsfw_guardrail = create_nsfw_guardrail(
    model="openrouter/google/gemini-2.5-flash-preview-09-2025"
)
```

### 3. Update Direct Config Instantiation
Add the `model` parameter to all `GuardrailConfig` instantiations:

```python
# Before
config = TopicGuardrailConfig(business_scopes=["AI"])

# After
config = TopicGuardrailConfig(
    model="openrouter/google/gemini-2.5-flash-preview-09-2025",
    business_scopes=["AI"]
)
```

### 4. Update Comprehensive Suite Creation
```python
# Before
suite = create_comprehensive_guardrail_suite(business_scopes=["AI"])

# After
suite = create_comprehensive_guardrail_suite(
    business_scopes=["AI"],
    model="openrouter/google/gemini-2.5-flash-preview-09-2025"
)
```

## Error Messages

If you forget to configure DSPy, you'll see this error:
```
DSPy is not properly configured. Please configure DSPy before using guardrails.
```

If you try to provide a model parameter (which is no longer needed), you'll see:
```
TypeError: got an unexpected keyword argument 'model'
```

## Benefits

1. **Flexibility**: Use any DSPy-supported LLM provider
2. **Control**: Configure temperature, tokens, caching, and other parameters
3. **Cost Optimization**: Choose models based on your needs and budget
4. **Future-Proof**: Easy to switch providers or update model versions

## Examples by Provider

### OpenRouter
```python
dspy.configure(lm=dspy.LM(
    "openrouter/google/gemini-2.5-flash-preview-09-2025",
    api_key=os.getenv("OPENROUTER_API_KEY")
))
```

### OpenAI
```python
dspy.configure(lm=dspy.LM(
    "openai/gpt-4",
    api_key=os.getenv("OPENAI_API_KEY")
))
```

### Anthropic (via DSPy)
```python
dspy.configure(lm=dspy.LM(
    "anthropic/claude-3-sonnet-20240229",
    api_key=os.getenv("ANTHROPIC_API_KEY")
))
```

## Testing

Update your tests to configure DSPy:

```python
import pytest
import dspy

@pytest.fixture(scope="session", autouse=True)
def configure_dspy():
    dspy.configure(lm=dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="test-key"))
```

## Need Help?

If you encounter issues during migration:
1. Check that DSPy is configured before creating guardrails
2. Ensure all factory functions and config instantiations include the `model` parameter
3. Verify your API keys are set correctly
4. Test with a simple guardrail first

For questions, please check the updated README.md or create an issue on GitHub.