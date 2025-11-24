# Simplify Run Return Type Tasks

## Tasks

### 1. Modify Run Function Implementation
**Status:** pending
**Description:** Update the Run function in guardrail.py to always return List[GuardrailResult] by wrapping single results in a list.

**Implementation:**
- Change the single guardrail case to return `[guardrails.check(text)]` instead of `guardrails.check(text)`
- Update type hints from `Union[GuardrailResult, List[GuardrailResult]]` to `List[GuardrailResult]`
- Ensure all existing functionality is preserved

**Validation:**
- Function still works for both single and multiple guardrails
- Type checker passes without casting
- All existing tests still pass

### 2. Update Example.py
**Status:** pending
**Description:** Remove type casting from example.py since Run now always returns a list.

**Implementation:**
- Remove `cast(List[GuardrailResult], ...)` calls
- Remove `cast(GuardrailResult, ...)` calls
- Update any code that expects single results to handle lists
- Ensure example still demonstrates the same functionality

**Validation:**
- Example runs without errors
- Type checker passes without warnings
- Output remains the same

### 3. Update README Examples
**Status:** pending
**Description:** Update README code examples to remove casting and handle the new return type.

**Implementation:**
- Remove cast statements from README examples
- Update any code that expects single results
- Ensure examples remain syntactically correct

**Validation:**
- All README code blocks are valid Python
- Examples demonstrate correct usage
- No syntax errors

### 4. Update Documentation References
**Status:** pending
**Description:** Update any documentation that references the old Union return type.

**Implementation:**
- Update docstrings in guardrail.py
- Update any comments or documentation strings
- Ensure consistency across all documentation

**Validation:**
- Documentation accurately reflects the new API
- No outdated references to Union types

### 5. Test Backward Compatibility
**Status:** pending
**Description:** Ensure the change doesn't break existing code that might expect single results.

**Implementation:**
- Check if any existing code expects single results from Run
- Consider adding deprecation warnings if needed
- Test with existing usage patterns

**Validation:**
- No breaking changes for current users
- Clear migration path if needed</content>
<parameter name="filePath">openspec/changes/simplify-run-return-type/tasks.md