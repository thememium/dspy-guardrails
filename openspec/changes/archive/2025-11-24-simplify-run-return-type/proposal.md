# Simplify Run Function Return Type

## Problem
The `guardrail.Run()` function currently returns `Union[GuardrailResult, List[GuardrailResult]]` depending on whether a single guardrail or list of guardrails is passed. This creates type checking issues and requires users to cast results, making the API cumbersome.

## Solution
Modify the `Run()` function to always return `List[GuardrailResult]`, even when a single guardrail is passed. This eliminates the need for type casting and provides a consistent, predictable API.

## Impact
- **API Consistency**: Always returns a list, making the API more predictable
- **Type Safety**: Eliminates Union types and casting requirements
- **User Experience**: Cleaner code without type casting in examples and user code
- **Breaking Change**: Code expecting single results from single guardrails will need updates

## Implementation Notes
- Modify `guardrail.py` Run function to wrap single results in a list
- Update type hints to `List[GuardrailResult]`
- Update example.py to remove casting
- Update README examples accordingly
- Consider backward compatibility implications</content>
<parameter name="filePath">openspec/changes/simplify-run-return-type/proposal.md