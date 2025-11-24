# Design: Unify Example.py Run API

## Architectural Context

The DSPy Guardrails package provides two execution patterns:
1. **Individual execution**: `guardrail.check(text)` - returns single `GuardrailResult`
2. **Bulk execution**: `guardrail.Run(guardrails, text)` - returns `List[GuardrailResult]` or single `GuardrailResult`

The current example.py demonstrates both patterns inconsistently, which can confuse users about the preferred approach.

## Design Decisions

### Unified Bulk Pattern
**Decision**: Use bulk `Run()` as the primary demonstration pattern for all guardrail testing.

**Rationale**:
- Bulk execution is more efficient for multiple guardrails
- Aligns with the simplified Run API specification
- Provides consistent return types (always lists for multiple guardrails)
- Better demonstrates real-world usage patterns
- Reduces API surface confusion for new users

### Type Safety Considerations
**Decision**: Ensure type-safe handling of Run() return values.

**Rationale**:
- Current code has type errors due to inconsistent handling of single vs. list results
- Type safety improves developer experience and catches errors early
- Maintains backward compatibility while fixing inconsistencies

### User Experience Flow
**Decision**: Structure example to show:
1. Bulk testing of all guardrails (primary pattern)
2. Detailed Run() API examples (educational)
3. API pattern reference (documentation)

**Rationale**:
- Clear progression from basic usage to advanced patterns
- Educational value without overwhelming new users
- Maintains comprehensive API coverage

## Implementation Strategy

### Phase 1: Core Unification
- Replace individual checks with single bulk Run call
- Fix type handling for consistent list processing
- Preserve all existing functionality

### Phase 2: API Documentation Update
- Update printed patterns to reflect bulk-first approach
- Ensure examples match demonstrated code
- Maintain backward compatibility notes

### Phase 3: Validation
- Type checking passes
- Runtime execution works
- Output remains user-friendly

## Risk Mitigation

### Backward Compatibility
**Risk**: Users might expect individual check patterns
**Mitigation**: Keep individual check capability, just don't demonstrate it as primary

### Type Safety
**Risk**: Run() API has union return types that are confusing
**Mitigation**: Use consistent patterns in examples, document the union behavior clearly

### Performance
**Risk**: Bulk execution might be less efficient for single guardrails
**Mitigation**: Run() handles single guardrails efficiently, examples show appropriate usage patterns</content>
<parameter name="filePath">openspec/changes/unify-example-run-api/design.md