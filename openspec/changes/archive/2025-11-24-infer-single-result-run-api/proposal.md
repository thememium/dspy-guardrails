# Infer Single Result for Run API

## Problem
The `guardrail.Run()` function currently always returns a `List[GuardrailResult]`, even when a single guardrail is passed. This requires users to manually access `results[0]` to get the single result, creating unnecessary friction in the API.

Current usage pattern:
```python
single_results = guardrail.Run(topic_guardrail, safe_content)
single_result = single_results[0]  # Run always returns a list
```

## Why
This change improves the developer experience by making the API more intuitive. When users pass a single guardrail, they expect a single result, not a list. The current API requires unnecessary indexing that adds friction to the most common use case. While this is a breaking change, the migration is simple (remove `[0]` indexing) and the improvement in usability justifies the change.

## Solution
Modify the `Run()` function to return a single `GuardrailResult` when a single guardrail is passed, and a `List[GuardrailResult]` when multiple guardrails are passed. This provides intuitive behavior where the return type matches the input type.

## Impact
- **User Experience**: Eliminates the need for `[0]` indexing when using single guardrails
- **API Intuitiveness**: Return type matches input type (single → single, list → list)
- **Backward Compatibility**: Breaking change for code expecting lists from single guardrails
- **Type Safety**: Requires Union return type but provides more intuitive usage

## Implementation Notes
- Modify `guardrail.py` Run function to check input type and return accordingly
- Update type hints to `Union[GuardrailResult, List[GuardrailResult]]`
- Update example.py to demonstrate the improved single guardrail usage
- Update README examples to show both patterns
- Consider migration path for existing code</content>
<parameter name="filePath">openspec/changes/infer-single-result-run-api/proposal.md