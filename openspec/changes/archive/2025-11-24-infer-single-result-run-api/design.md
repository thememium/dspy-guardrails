# Design for Infer Single Result Run API

## Architectural Decision

The current `Run` function always returns a list to maintain API consistency, but this creates friction for the common single guardrail use case. We need to balance API intuitiveness with consistency.

## Design Options Considered

### Option 1: Always Return List (Current)
- Pros: Consistent API, no type unions, predictable behavior
- Cons: Requires `[0]` indexing for single results, less intuitive

### Option 2: Return Type Matching Input (Proposed)
- Pros: Intuitive (single in → single out, list in → list out), eliminates indexing
- Cons: Union return type, breaking change for existing code

### Option 3: Add Separate Function
- Pros: No breaking changes, maintains current API
- Cons: API proliferation, users need to learn two functions

## Chosen Design: Option 2

We choose Option 2 because:
1. **User Experience**: The most common use case (single guardrail) becomes much simpler
2. **Intuitive Behavior**: Return type matches input type conceptually
3. **Backward Compatibility**: While breaking, the change is straightforward to migrate
4. **Type Safety**: Union types are acceptable for the improved UX

## Implementation Strategy

### Type Detection Logic
```python
def Run(guardrails: Union[BaseGuardrail, List[BaseGuardrail]], text: str) -> Union[GuardrailResult, List[GuardrailResult]]:
    if isinstance(guardrails, BaseGuardrail):
        return guardrails.check(text)  # Return single result
    else:
        # Handle list case as before
        return [gr.check(text) for gr in guardrails]
```

### Migration Path
- Existing code using `[0]` will break but can be easily fixed by removing the indexing
- Code using lists will continue to work unchanged
- Clear error messages and migration guide provided

## Risk Mitigation

### Breaking Change Impact
- **Scope**: Only affects code calling `Run(single_guardrail, text)`
- **Migration**: Simple - remove `[0]` indexing
- **Detection**: Type checkers will catch the issue immediately

### Type Safety Concerns
- Union return types are less ideal but acceptable for improved UX
- Clear documentation will help users understand the behavior
- Runtime behavior is predictable and safe

## Testing Strategy

- Unit tests for both single and list input scenarios
- Integration tests ensuring backward compatibility for list usage
- Type checking validation
- Manual testing of common usage patterns