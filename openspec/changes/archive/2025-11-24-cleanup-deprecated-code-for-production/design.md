# Design: Cleanup Deprecated Code for Production

## Problem Statement
The DSPy Guardrails package has accumulated deprecated code from multiple API iterations:

1. **GuardrailManager**: Originally the primary way to orchestrate multiple guardrails, now replaced by the simpler `Run()` function
2. **Factory Functions**: Simple creation functions that are now redundant with the method-based `guardrail` module API
3. **Model Parameters**: Per-guardrail model configuration that conflicts with the user-controlled DSPy configuration approach

## Solution Overview
Remove all deprecated code to create a clean, production-ready API surface. The final API should consist of:

- `guardrail.configure()` - Global guardrail configuration
- `guardrail.topic()`, `guardrail.nsfw()`, etc. - Simple guardrail creation
- `guardrail.Run()` - Batch execution with early return support

## Architecture Decisions

### 1. Complete Removal vs Deprecation
**Decision**: Complete removal of deprecated code
**Rationale**: For a first production release, it's better to have a clean API than maintain backward compatibility indefinitely. Users can migrate using the existing migration guide.

### 2. Guardrail Configuration Model
**Decision**: Global guardrail configuration only
**Rationale**: Per-guardrail model parameters add complexity and conflict with the user-controlled DSPy configuration. Global configuration is simpler and more predictable.

### 3. API Surface Reduction
**Decision**: Remove factory functions entirely
**Rationale**: The `guardrail` module provides a cleaner, more discoverable API. Maintaining two ways to create guardrails increases maintenance burden.

## Migration Path
Users currently using deprecated APIs will need to migrate:

```python
# Old (deprecated)
from dspy_guardrails import GuardrailManager, create_topic_guardrail
manager = GuardrailManager()
topic_gr = create_topic_guardrail(business_scopes=["AI"])

# New (production)
from dspy_guardrails import guardrail
guardrail.configure(lm=my_lm)
topic_gr = guardrail.topic(business_scopes=["AI"])
```

## Impact Analysis
- **Breaking Changes**: Yes, but necessary for production readiness
- **Migration Effort**: Low - existing migration guide covers most cases
- **Code Reduction**: ~200+ lines of deprecated code removed
- **Maintenance**: Significantly reduced ongoing maintenance burden

## Testing Strategy
- Remove tests for deprecated functionality
- Ensure all remaining tests pass with simplified API
- Add integration tests for the final API surface
- Validate that example.py works with production API</content>
<parameter name="filePath">openspec/changes/cleanup-deprecated-code-for-production/design.md