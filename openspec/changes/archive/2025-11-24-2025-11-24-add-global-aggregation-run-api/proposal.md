# Add Global Aggregation to Run API

## Problem
Currently, the `Run()` function only accepts a single `text: str` parameter. When users need to check multiple texts against guardrails, they must call the function multiple times or use `check_batch()` on individual guardrails. This creates inconvenience for bulk processing scenarios where users want a single pass/fail decision across multiple texts.

Current usage pattern for multiple texts:
```python
# Check multiple texts - requires multiple calls or manual aggregation
result1 = guardrail.Run(topic_guardrail, text1)
result2 = guardrail.Run(topic_guardrail, text2)
# Manual aggregation logic needed
all_allowed = result1.is_allowed and result2.is_allowed
```

## Why
This change improves the developer experience for bulk text processing by providing a single API call that handles multiple texts and returns a globally aggregated result. Users processing batches of content (like forum posts, chat messages, or document collections) currently need to implement their own aggregation logic. This change makes the API more convenient for common use cases while maintaining backward compatibility for single text processing.

## Solution
Modify the `Run()` function to return aggregated results whenever multiple items are involved (either multiple guardrails or multiple texts). The function now:

- `Run(single_guardrail, single_text)` → `GuardrailResult` (unchanged)
- `Run(multiple_guardrails, single_text)` → `GuardrailResult` (aggregated)
- `Run(any_guardrails, multiple_texts)` → `GuardrailResult` (aggregated)

Aggregated results include:
- `is_allowed`: `True` only if ALL items pass ALL checks
- `reason`: First failure reason encountered
- `metadata`: Detailed per-item results with correlation information
- `guardrail_name`: "aggregated" to indicate this is a summary result

## Impact
- **Breaking Change**: Multiple guardrails now return single result instead of list
- **User Experience**: Consistent global pass/fail for all bulk operations
- **API Simplification**: Always returns single `GuardrailResult` with rich metadata
- **Backward Compatibility**: Single guardrail + single text unchanged

## Alternatives Considered
- **New Function**: `Run.batch()` - Rejected for API complexity and discoverability
- **Modify check_batch()**: Only works per-guardrail, not across multiple guardrails
- **Keep Current API**: Forces users to implement aggregation manually

## Implementation Notes
- Maintain existing behavior for single text inputs
- Aggregate results using AND logic (all texts must pass all guardrails)
- Include detailed per-text results in metadata for debugging
- Preserve early_return functionality for performance optimization
- Update type hints to `text: Union[str, List[str]]`