# Unify Example.py Run API Tasks

## Tasks

### 1. Replace Individual Guardrail Checks with Bulk Run
**Status:** pending  
**Description:** Replace the individual `gr.check(test_text)` loop (lines 64-78) with a single `guardrail.Run(all_guardrails, test_text)` call that checks all guardrails at once.

**Implementation:**
- Collect all guardrail instances into a list
- Replace the loop with `results = guardrail.Run(all_guardrails, test_text)`
- Update result processing to handle the list of GuardrailResult objects
- Maintain the same output format for consistency

**Validation:**
- All guardrails are still tested
- Output shows results for each guardrail
- No functionality is lost

### 2. Fix Type Inconsistencies in Run Examples
**Status:** pending  
**Description:** The current Run examples have type issues where single guardrail calls return single results but batch calls return lists. Ensure consistent handling.

**Implementation:**
- For single guardrail examples, ensure proper single result handling
- For batch examples, ensure proper list result handling
- Add type checking or consistent patterns

**Validation:**
- Run `uv run poe lint` to ensure no type errors
- Test that all examples execute without runtime errors

### 3. Update API Pattern Documentation
**Status:** pending  
**Description:** Update the "Key API patterns" section at the end to reflect the unified bulk approach as the primary pattern.

**Implementation:**
- Modify the printed patterns to show bulk Run as the main approach
- Keep individual check as secondary/legacy pattern
- Update examples to match the new unified approach

**Validation:**
- Documentation accurately reflects the code
- Examples are consistent with demonstrated patterns

### 4. Test Complete Example Execution
**Status:** pending  
**Description:** Run the updated example.py to ensure it works correctly and produces expected output.

**Implementation:**
- Execute `python example.py`
- Verify all guardrails are tested
- Check that output is clear and informative
- Ensure no runtime errors

**Validation:**
- Example runs without errors
- All guardrail types are demonstrated
- Output is user-friendly and informative</content>
<parameter name="filePath">openspec/changes/unify-example-run-api/tasks.md