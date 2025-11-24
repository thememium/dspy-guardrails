# Design Document: Changing Guardrail Functions to Classes

## Architectural Overview

This change transforms the guardrail module from a functional API to a class-based API, making it more consistent with Python conventions and improving developer experience.

## Current Architecture

The current `guardrail.py` module provides factory functions:

```python
def topic(business_scopes: List[str], competitor_names: Optional[List[str]] = None) -> TopicGuardrail:
    config = TopicGuardrailConfig(...)
    return TopicGuardrail(config)
```

## Proposed Architecture

Transform these into class constructors:

```python
class Topic:
    def __init__(self, business_scopes: List[str], competitor_names: Optional[List[str]] = None) -> TopicGuardrail:
        config = TopicGuardrailConfig(...)
        return TopicGuardrail(config)
```

## Design Decisions

### 1. Class vs Factory Function Pattern

**Decision**: Use classes instead of functions
**Rationale**:
- Follows Python naming conventions (classes start with uppercase)
- Provides better IDE support and autocomplete
- More discoverable API - users can see available guardrail types
- Aligns with object-oriented design patterns
- Enables future extension through inheritance if needed

### 2. Backward Compatibility Strategy

**Decision**: Keep old functions as deprecated aliases
**Rationale**:
- Allows gradual migration for existing users
- Prevents breaking changes
- Provides clear deprecation path
- Enables testing of new API while maintaining old functionality

### 3. Constructor Signature Preservation

**Decision**: Maintain identical parameter signatures
**Rationale**:
- Zero breaking changes for configuration
- Existing code can be migrated by changing function calls to class instantiations
- All default values and validation logic preserved
- Type hints remain compatible

## Implementation Strategy

### Phase 1: Direct Transformation
- Convert each function to a class with `__new__` method that returns the guardrail instance
- This maintains the factory pattern while providing class-based API

### Phase 2: Backward Compatibility
- Keep original functions that delegate to new classes
- Add deprecation warnings using `warnings.warn()`
- Update `__all__` to export both old and new names

### Phase 3: Documentation Migration
- Update all examples to use class-based API
- Add migration guide showing before/after patterns
- Maintain old examples in deprecation documentation

## Alternative Approaches Considered

### Option A: Pure Factory Functions (Rejected)
Keep functions but change names to start with uppercase. This would violate Python conventions and confuse users expecting classes.

### Option B: Complete Class Redesign (Rejected)
Redesign as full classes with instance methods. This would be a major breaking change and require extensive refactoring of user code.

### Option C: Dual API with Different Names (Rejected)
Create new classes alongside old functions with different names. This would create API confusion and maintenance burden.

## Benefits

1. **Convention Compliance**: Follows Python naming conventions
2. **IDE Support**: Better autocomplete and type inference
3. **Discoverability**: Users can easily see available guardrail types
4. **Future Extensibility**: Class-based design allows for inheritance and extension
5. **Zero Breaking Changes**: Existing code continues to work

## Risks and Mitigations

### Risk: User Confusion During Transition
**Mitigation**: Clear deprecation warnings with migration examples

### Risk: Performance Impact
**Mitigation**: Minimal overhead - classes delegate to existing factory logic

### Risk: Documentation Inconsistency
**Mitigation**: Comprehensive update of all documentation and examples

## Success Metrics

- All existing tests pass without modification
- New class-based API works identically to old functions
- IDE autocomplete shows class constructors
- Deprecation warnings guide users to new API
- Documentation examples use class-based patterns