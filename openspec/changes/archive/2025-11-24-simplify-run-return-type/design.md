# Design: Simplify Run Function Return Type

## Architectural Context

The current `Run()` function has a Union return type that creates type checking complexity and requires users to cast results. This violates the principle of least surprise and makes the API harder to use correctly.

## Design Decisions

### Consistent List Return Type
**Decision**: Always return `List[GuardrailResult]` from the `Run()` function, even for single guardrails.

**Rationale**:
- Eliminates Union types and casting requirements
- Provides predictable API behavior
- Simplifies type checking and IDE support
- Aligns with bulk-first design philosophy
- Makes iteration consistent (always over a list)

### Single Result Handling
**Decision**: When a single guardrail is passed, wrap the result in a list of one element.

**Rationale**:
- Maintains API consistency
- Users can always iterate over results
- Simplifies code that handles both single and multiple guardrails
- Follows principle of least surprise

### Backward Compatibility Strategy
**Decision**: Accept this as a breaking change with clear migration guidance.

**Rationale**:
- API improvement outweighs backward compatibility concerns
- Bulk execution is the recommended pattern
- Clear migration path (access `results[0]` for single results)
- Better long-term API design

## Implementation Strategy

### Phase 1: Core Function Changes
- Modify Run function to always return lists
- Update type annotations
- Ensure all internal logic works correctly

### Phase 2: Update Examples and Documentation
- Remove casting from all examples
- Update code that expects single results
- Ensure documentation reflects new behavior

### Phase 3: Migration Support
- Add clear documentation about the change
- Provide migration examples
- Consider deprecation warnings for old usage patterns

## Risk Mitigation

### Breaking Changes
**Risk**: Existing code expecting single results will break
**Mitigation**: 
- Comprehensive testing before release
- Clear migration documentation
- Deprecation period if needed

### User Confusion
**Risk**: Users might not understand why single guardrails return lists
**Mitigation**:
- Clear documentation explaining the design decision
- Consistent examples showing the pattern
- Educational materials about the benefits

### Performance Impact
**Risk**: Creating lists for single results adds overhead
**Mitigation**:
- Minimal performance impact (single element lists)
- Benefits of API consistency outweigh small overhead
- Bulk operations remain optimized</content>
<parameter name="filePath">openspec/changes/simplify-run-return-type/design.md