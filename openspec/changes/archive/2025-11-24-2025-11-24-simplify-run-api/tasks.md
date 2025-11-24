# Simplify Run API Implementation Tasks

## Tasks

1. **Move Run function to guardrail module**
   - Move Run function from dspy_guardrails/__init__.py to dspy_guardrails/guardrail.py
   - Ensure all imports and dependencies are properly maintained
   - Verify function signature and behavior remain identical

2. **Update package exports for backward compatibility**
   - Keep Run function in dspy_guardrails/__init__.py by importing from guardrail module
   - Update __all__ list to maintain current exports
   - Ensure existing code using dspy_guardrails.Run continues to work

3. **Update example.py to use new API**
   - Change imports to only use guardrail module
   - Update all Run() calls to use guardrail.Run()
   - Verify example works correctly with new API

4. **Update documentation and docstrings**
   - Update all examples in docstrings to use guardrail.Run()
   - Update README.md examples if they exist
   - Ensure API documentation reflects the simplified approach

5. **Run tests and validation**
   - Run existing test suite to ensure no regressions
   - Test both old and new API patterns work correctly
   - Verify type hints and IDE autocomplete work properly

6. **Code quality checks**
   - Run `uv run poe clean` to ensure formatting and linting
   - Check import sorting with `uv run poe sort`
   - Verify no dependency issues with `uv run poe deptry`

## Dependencies
- Task 1 must be completed before Task 2
- Task 2 must be completed before Task 3
- Task 3 should be completed before Task 4
- Task 5 should be done after all implementation tasks
- Task 6 should be the final validation step