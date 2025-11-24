# Implementation Tasks

## Phase 1: API Design and Planning

### 1.1 Analyze Current Function Signatures
- [x] Review all function signatures in `guardrail.py`
- [x] Document parameter names, types, and default values for each function
- [x] Identify any special handling or validation logic
- [x] Plan class constructor signatures to match exactly

### 1.2 Design Class-Based API
- [x] Define class names and constructor signatures
- [x] Plan deprecation strategy for old functions
- [x] Design backward compatibility approach
- [x] Ensure no breaking changes to configuration classes

## Phase 2: Core Implementation

### 2.1 Transform Functions to Classes
- [x] Change `topic()` function to `Topic` class
- [x] Change `nsfw()` function to `Nsfw` class
- [x] Change `jailbreak()` function to `Jailbreak` class
- [x] Change `pii()` function to `Pii` class
- [x] Change `prompt_injection()` function to `PromptInjection` class
- [x] Change `keywords()` function to `Keywords` class
- [x] Change `secret_keys()` function to `SecretKeys` class

### 2.2 Add Backward Compatibility
- [x] Keep old function names as deprecated aliases
- [x] Add deprecation warnings when old functions are used
- [x] Ensure old functions return same instances as new classes
- [x] Update `__all__` exports to include both old and new names

### 2.3 Update Type Hints and Documentation
- [x] Update type hints for class constructors
- [x] Update docstrings to reflect class-based usage
- [x] Add examples showing both old and new patterns
- [x] Update function signatures in documentation

## Phase 3: Testing and Validation

### 3.1 Unit Tests for New Classes
- [x] Add tests for each new class constructor
- [x] Test parameter validation and error handling
- [x] Test default value application
- [x] Test integration with existing guardrail classes

### 3.2 Backward Compatibility Tests
- [x] Verify old functions still work with deprecation warnings
- [x] Test that old and new APIs produce identical results
- [x] Ensure no breaking changes to existing user code

### 3.3 Integration Tests
- [x] Test end-to-end guardrail creation and execution
- [x] Validate configuration propagation to guardrail instances
- [x] Test error scenarios and edge cases

## Phase 4: Documentation and Examples

### 4.1 Update Documentation
- [x] Update README with new class-based API examples
- [x] Add migration guide for existing users
- [x] Document deprecation timeline for old functions
- [x] Update all docstrings with class-based examples

### 4.2 Create Usage Examples
- [x] Add code examples showing before/after patterns
- [x] Update `example.py` to use new class-based API
- [x] Add comprehensive examples in docstrings

## Phase 5: Code Quality and Polish

### 5.1 Code Review
- [x] Run `uv run poe clean` for code quality
- [x] Ensure consistent class structure and naming
- [x] Validate type hints are complete and accurate
- [x] Check deprecation warnings are appropriate

### 5.2 Performance Validation
- [x] Test that new API doesn't impact performance
- [x] Ensure memory usage remains efficient
- [x] Validate startup time for guardrail creation

### 5.3 Final Validation
- [x] Run complete test suite
- [x] Test package installation and imports
- [x] Validate all documentation examples work
- [x] Perform cross-version compatibility testing

## Dependencies and Prerequisites

### Before Starting
- [ ] Review current `guardrail.py` implementation thoroughly
- [ ] Understand all function signatures and their purposes
- [ ] Test existing functions with various configurations
- [ ] Document current user usage patterns

### During Implementation
- [ ] Maintain backward compatibility at all times
- [ ] Test frequently against existing user patterns
- [ ] Follow project's existing code style and conventions
- [ ] Regularly run code quality checks (`uv run poe clean`)

### Before Completion
- [ ] Ensure all tests pass including new and existing
- [ ] Validate package can be installed and imported
- [ ] Test with different Python versions (3.12+)
- [ ] Verify documentation is complete and accurate
- [ ] Get feedback on API design from potential users