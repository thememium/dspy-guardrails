# Implementation Tasks

## Phase 1: API Design and Planning

### 1.1 Analyze Current Factory Functions
- [ ] Review existing factory functions in `factory.py`
- [ ] Document all configuration parameters for each guardrail type
- [ ] Identify common patterns and default values
- [ ] Determine optimal parameter structure for method-based API

### 1.2 Design Guardrail Module API
- [ ] Define `guardrail` module structure and function signatures
- [ ] Design parameter structure (keyword arguments vs dict-based)
- [ ] Plan error handling and validation
- [ ] Ensure backward compatibility approach

## Phase 2: Core Implementation

### 2.1 Create Guardrail Module
- [x] Create `dspy_guardrails/guardrail.py` module
- [x] Implement `configure()` function for global DSPy setup
- [x] Implement `topic()` function with keyword arguments
- [x] Implement `nsfw()` function with keyword arguments
- [x] Implement `jailbreak()` function with keyword arguments
- [x] Implement `pii()` function with keyword arguments
- [x] Implement `keywords()` function with keyword arguments
- [x] Implement `secret_keys()` function with keyword arguments

### 2.2 Update Package Imports
- [x] Update main `__init__.py` to expose the `guardrail` module
- [x] Ensure all existing imports remain available
- [x] Add type stubs if needed for better IDE support

### 2.3 Add Parameter Validation
- [ ] Add parameter validation and type checking to each function
- [ ] Implement default value handling where appropriate
- [ ] Add comprehensive error messages

## Phase 3: Testing and Validation

### 3.1 Unit Tests
- [x] Add tests for each `guardrail.*()` function
- [x] Test parameter validation and error handling
- [x] Test default value application
- [x] Test integration with existing guardrail classes

### 3.2 Backward Compatibility Tests
- [x] Verify all existing factory functions still work
- [x] Test existing user code patterns continue to function
- [x] Ensure no breaking changes to public APIs

### 3.3 Integration Tests
- [x] Test end-to-end guardrail creation and execution
- [x] Validate configuration propagation to guardrail instances
- [x] Test error scenarios and edge cases

## Phase 4: Documentation and Examples

### 4.1 Update Documentation
- [x] Update README with new method-based API examples
- [x] Add migration guide for existing users
- [x] Document all available configuration options

### 4.2 Create Usage Examples
- [x] Add code examples showing before/after patterns
- [x] Create comprehensive example in `example.py`
- [x] Add docstring examples to all guardrail functions

## Phase 5: Code Quality and Polish

### 5.1 Code Review
- [x] Run `uv run poe clean` for code quality
- [x] Ensure consistent error handling patterns
- [x] Validate type hints are complete and accurate

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
- [ ] Review current factory.py implementation thoroughly
- [ ] Understand all guardrail configuration requirements
- [ ] Test existing factory functions with various configurations
- [ ] Document current user pain points and use cases

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