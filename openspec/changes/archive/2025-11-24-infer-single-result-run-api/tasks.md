# Tasks for Infer Single Result Run API

## Implementation Tasks

1. **Modify Run function logic** - Update `dspy_guardrails/guardrail.py` Run function to return single result when single guardrail is passed
2. **Update type hints** - Change return type annotation from `List[GuardrailResult]` to `Union[GuardrailResult, List[GuardrailResult]]`
3. **Update function docstring** - Modify examples and return type documentation in Run function
4. **Update example.py** - Remove the `[0]` indexing and demonstrate improved single guardrail usage
5. **Update README** - Update examples to show both single and list return patterns
6. **Update tests** - Modify test expectations for single guardrail Run calls to expect single results instead of lists

## Validation Tasks

7. **Run existing tests** - Ensure all tests pass with the new behavior
8. **Add new tests** - Add tests specifically for the new single result behavior
9. **Type checking** - Run mypy or similar to ensure type safety
10. **Manual testing** - Test the new API interactively to ensure it works as expected

## Documentation Tasks

11. **Migration guide** - Create guidance for users migrating from list-only API
12. **Changelog entry** - Document this as a breaking change in changelog