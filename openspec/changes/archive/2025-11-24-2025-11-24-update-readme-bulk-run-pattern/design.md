# Design: Update README Bulk Run Pattern

## Architectural Context

The DSPy Guardrails package now has example.py demonstrating bulk `Run()` as the primary execution pattern. The README should be consistent with this direction to avoid user confusion about which API patterns to prefer.

## Design Decisions

### Primary Pattern Emphasis
**Decision**: Position bulk `guardrail.Run([gr1, gr2, gr3], text)` as the recommended primary pattern in README.

**Rationale**:
- Aligns with the updated example.py
- Bulk execution is more efficient for multiple guardrails
- Provides clearer API direction for new users
- Maintains backward compatibility while guiding toward best practices

### Example Structure
**Decision**: Reorder examples to show:
1. Bulk Run (recommended)
2. Single guardrail Run
3. Individual check (legacy)
4. Migration examples

**Rationale**:
- Logical progression from most recommended to legacy patterns
- Clear hierarchy of preferred usage
- Educational flow for users learning the API

### Documentation Consistency
**Decision**: Ensure README examples match the patterns and style used in example.py.

**Rationale**:
- Consistent user experience across documentation
- Reduces confusion when users compare examples
- Maintains single source of truth for API usage patterns

## Implementation Strategy

### Phase 1: Content Reordering
- Move bulk Run examples to prominent positions
- Reorganize sections for logical flow
- Preserve all existing content

### Phase 2: Preference Indicators
- Add clear labeling for recommended vs legacy patterns
- Update section headers and descriptions
- Include explanatory comments in code examples

### Phase 3: Validation
- Ensure all examples remain functional
- Verify consistency with example.py
- Test documentation readability

## Risk Mitigation

### Backward Compatibility
**Risk**: Existing users might be confused by preference changes
**Mitigation**: Keep all patterns available, just reorder and label clearly

### Documentation Drift
**Risk**: README and example.py could become inconsistent again
**Mitigation**: Establish pattern that both should be updated together for API changes

### User Confusion
**Risk**: Too many options might overwhelm new users
**Mitigation**: Clear labeling and logical ordering to guide users toward best practices</content>
<parameter name="filePath">openspec/changes/update-readme-bulk-run-pattern/design.md