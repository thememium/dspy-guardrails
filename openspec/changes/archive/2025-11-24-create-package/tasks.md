# Implementation Tasks

## Phase 1: Core Infrastructure

### 1.1 Create Package Structure
- [x] Create `dspy_guardrails` directory with `__init__.py`
- [x] Create subdirectories: `core/`, `guardrails/`, `utils/`
- [x] Add `__init__.py` files to all subdirectories
- [x] Update `pyproject.toml` to include package metadata

### 1.2 Implement Base Classes
- [x] Create `core/base.py` with `BaseGuardrail` abstract class
- [x] Define `GuardrailResult` and related result types
- [x] Create `core/exceptions.py` with custom exception hierarchy
- [x] Add type hints and docstrings to all base classes

### 1.3 Configuration System
- [x] Create `core/config.py` with base configuration classes
- [x] Implement configuration validation logic
- [x] Add support for environment variables
- [x] Create configuration dataclasses for each guardrail type

### 1.4 DSPy Configuration Utilities
- [x] Create `utils/dspy_config.py` with DSPy setup functions
- [x] Extract common DSPy configuration patterns from notebooks
- [x] Add error handling for DSPy configuration failures
- [x] Support different LLM providers and models

## Phase 2: Guardrail Extraction

### 2.1 Topic Compliance Guardrail
- [x] Extract `GuardrailsTopicSignature` from `notebooks/001-topic.py`
- [x] Create `guardrails/topic.py` with `TopicGuardrail` class
- [x] Implement configuration class for topic guardrail
- [x] Add unit tests for topic guardrail functionality

### 2.2 NSFW Detection Guardrail
- [x] Extract `GuardrailsNsfwSignature` from `notebooks/002-nsfw.py`
- [x] Create `guardrails/nsfw.py` with `NsfwGuardrail` class
- [x] Implement configuration class for NSFW guardrail
- [x] Add unit tests for NSFW guardrail functionality

### 2.3 Jailbreak Detection Guardrail
- [x] Extract signature from `notebooks/003-jailbreak.py`
- [x] Create `guardrails/jailbreak.py` with `JailbreakGuardrail` class
- [x] Implement configuration class for jailbreak guardrail
- [x] Add unit tests for jailbreak guardrail functionality

### 2.4 PII Detection Guardrail
- [x] Extract signature from `notebooks/004-pii.py`
- [x] Create `guardrails/pii.py` with `PiiGuardrail` class
- [x] Implement configuration class for PII guardrail
- [x] Add unit tests for PII guardrail functionality

### 2.5 Prompt Injection Guardrail
- [x] Extract signature from `notebooks/005-prompt-injection.py`
- [x] Create `guardrails/prompt_injection.py` with `PromptInjectionGuardrail` class
- [x] Implement configuration class for prompt injection guardrail
- [x] Add unit tests for prompt injection guardrail functionality

### 2.6 Keyword Filtering Guardrail
- [x] Extract signature from `notebooks/006-keywords.py`
- [x] Create `guardrails/keywords.py` with `KeywordsGuardrail` class
- [x] Implement configuration class for keywords guardrail
- [x] Add unit tests for keywords guardrail functionality

### 2.7 Secret Keys Detection Guardrail
- [x] Extract signature from `notebooks/007-secret-keys.py`
- [x] Create `guardrails/secret_keys.py` with `SecretKeysGuardrail` class
- [x] Implement configuration class for secret keys guardrail
- [x] Add unit tests for secret keys guardrail functionality

## Phase 3: Package Integration

### 3.1 Main Package Interface
- [x] Update main `__init__.py` with convenient imports
- [x] Create factory functions for common guardrail configurations
- [x] Add package-level documentation and examples
- [x] Implement version information and metadata

### 3.2 Guardrail Manager
- [x] Create `GuardrailManager` class for multiple guardrails
- [x] Implement batch processing capabilities
- [x] Add support for conditional guardrail execution
- [x] Create result aggregation and reporting methods

### 3.3 Testing Infrastructure
- [x] Create comprehensive test suite structure
- [ ] Add integration tests for end-to-end functionality
- [ ] Create test fixtures and mock data
- [ ] Add performance benchmarks

### 3.4 Documentation and Examples
- [x] Create README with installation and usage instructions
- [x] Add code examples for common use cases
- [x] Create API documentation for all public classes
- [ ] Add troubleshooting guide and FAQ

## Phase 4: Validation and Polish

### 4.1 Backward Compatibility
- [x] Verify all existing notebooks still function
- [ ] Test that notebooks can import and use package classes
- [x] Ensure DSPy configuration remains consistent
- [x] Validate that all original functionality is preserved

### 4.2 Code Quality
- [x] Run `uv run poe clean` to ensure code quality standards
- [x] Add type hints to all public interfaces
- [x] Ensure consistent error handling across all guardrails
- [ ] Add logging for debugging and monitoring

### 4.3 Performance Validation
- [ ] Benchmark individual guardrail performance
- [ ] Test batch processing efficiency
- [ ] Validate memory usage and resource consumption
- [ ] Optimize any identified bottlenecks

### 4.4 Final Testing
- [x] Run complete test suite
- [x] Test package installation and import
- [x] Validate all example code works correctly
- [ ] Perform integration testing with sample applications

## Dependencies and Prerequisites

### Before Starting
- [x] Review all 7 notebook files to understand implementation patterns
- [x] Identify common DSPy configuration patterns across notebooks
- [x] Document any notebook-specific quirks or edge cases
- [x] Set up proper development environment with all dependencies

### During Implementation
- [x] Continuously test against existing notebooks
- [x] Maintain compatibility with current DSPy and Marimo versions
- [x] Follow project's existing code style and conventions
- [x] Regularly run code quality checks (`uv run poe clean`)

### Before Completion
- [x] Ensure all tests pass
- [x] Validate package can be installed and imported
- [ ] Test with different Python versions (3.12+)
- [x] Verify documentation is complete and accurate