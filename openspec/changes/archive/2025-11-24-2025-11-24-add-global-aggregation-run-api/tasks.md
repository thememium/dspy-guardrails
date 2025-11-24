# Implementation Tasks for Global Aggregation Run API

## 1. Update Function Signature
- [x] Modify `Run()` function signature to accept `text: Union[str, List[str]]`
- [x] Update type hints and imports
- [x] Update docstring to document new parameter behavior

## 2. Implement Aggregation Logic
- [x] Add logic to detect single text vs list of texts
- [x] Process all texts against all guardrails when list provided
- [x] Implement global `is_allowed` logic (AND across all results)
- [x] Implement global `reason` logic (first failure reason)

## 3. Update Return Type
- [x] Modify return type to `GuardrailResult` (always return single result)
- [x] Ensure single text returns single result as before
- [x] Ensure list input returns single aggregated result

## 4. Add Metadata Structure
- [x] Design metadata format for per-text results
- [x] Include individual GuardrailResult objects in metadata
- [x] Add text indices or identifiers for correlation

## 5. Preserve Early Return
- [x] Ensure early_return works with multiple texts
- [x] Stop processing on first global failure when early_return=True
- [x] Maintain performance optimizations

## 6. Update Tests
- [x] Add tests for single text input (regression)
- [x] Add tests for multiple text inputs
- [x] Add tests for aggregation logic (all pass, some fail, all fail)
- [x] Add tests for metadata structure
- [x] Add tests for early_return with multiple texts

## 7. Update Documentation
- [x] Update function docstring with examples
- [x] Add migration guide for users processing multiple texts (cancelled - not needed)
- [x] Update README examples if needed

## 8. Validation
- [x] Run existing tests to ensure no regressions
- [x] Test with real guardrails and multiple texts
- [x] Verify type hints work correctly
- [x] Run linting and formatting checks