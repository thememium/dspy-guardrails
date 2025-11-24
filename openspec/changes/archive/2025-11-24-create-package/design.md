# Design: DSPy Guardrails Package Architecture

## Overview
This document outlines the architectural design for the DSPy Guardrails package, which will transform the current notebook-based guardrails into a reusable Python package.

## Current State Analysis
The project currently contains 7 guardrail notebooks, each following a consistent pattern:
- DSPy Signature class defining input/output fields
- Marimo notebook with configuration, input UI, and execution logic
- Individual DSPy configuration for each notebook
- Similar but slightly varying implementation patterns

## Proposed Architecture

### Package Structure
```
dspy_guardrails/
├── __init__.py                 # Main package exports
├── core/
│   ├── __init__.py
│   ├── base.py                 # Base guardrail class
│   ├── config.py               # Configuration management
│   └── exceptions.py           # Custom exceptions
├── guardrails/
│   ├── __init__.py
│   ├── topic.py                # Topic compliance guardrail
│   ├── nsfw.py                 # NSFW detection guardrail
│   ├── jailbreak.py            # Jailbreak detection guardrail
│   ├── pii.py                  # PII detection guardrail
│   ├── prompt_injection.py     # Prompt injection guardrail
│   ├── keywords.py             # Keyword filtering guardrail
│   └── secret_keys.py          # Secret keys detection guardrail
└── utils/
    ├── __init__.py
    └── dspy_config.py          # DSPy configuration utilities
```

### Core Components

#### 1. BaseGuardrail Class
Abstract base class that defines the common interface for all guardrails:
- `__init__(config: GuardrailConfig)`: Initialize with configuration
- `check(input_text: str) -> GuardrailResult`: Main decision method
- `check_batch(input_texts: List[str]) -> List[GuardrailResult]`: Batch processing
- `configure_dspy()`: DSPy configuration method

#### 2. Configuration System
Unified configuration approach:
- `GuardrailConfig`: Base configuration with common settings
- Specific config classes for each guardrail type
- Support for environment variables and config files
- Validation of configuration parameters

#### 3. Result Types
Standardized result objects:
- `GuardrailResult`: Base result with decision and metadata
- Specific result types for each guardrail
- Consistent error handling and status reporting

### API Design

#### Simple Usage
```python
from dspy_guardrails import TopicGuardrail

guardrail = TopicGuardrail(
    business_scopes=["Shipping Software", "Logistics"],
    competitor_names=["CompetitorA", "CompetitorB"]
)

result = guardrail.check("Tell me about shipping labels")
if result.is_allowed:
    print("Content is allowed")
else:
    print(f"Content blocked: {result.reason}")
```

#### Advanced Usage
```python
from dspy_guardrails import GuardrailManager

manager = GuardrailManager()
manager.add_guardrail("topic", TopicGuardrail(config))
manager.add_guardrail("nsfw", NsfwGuardrail(config))

results = manager.check_all("User input text")
if all(result.is_allowed for result in results.values()):
    print("All guardrails passed")
```

### Design Decisions

#### 1. Signature Extraction Strategy
- Extract DSPy signatures from notebooks into separate classes
- Maintain exact same signature definitions to preserve behavior
- Add type hints and documentation for better usability

#### 2. Configuration Approach
- Use dataclasses for configuration objects
- Support both direct instantiation and config file loading
- Validate configurations at initialization time
- Provide sensible defaults where possible

#### 3. Error Handling Strategy
- Custom exception hierarchy for different error types
- Graceful degradation when possible
- Detailed error messages for debugging
- Logging integration for production use

#### 4. Backward Compatibility
- Keep existing notebooks unchanged
- Allow notebooks to import and use package classes
- Maintain same DSPy configuration approach
- Preserve all existing functionality

### Implementation Phases

#### Phase 1: Core Infrastructure
- Create base classes and interfaces
- Implement configuration system
- Set up package structure
- Add basic error handling

#### Phase 2: Guardrail Extraction
- Extract all 7 guardrail signatures
- Implement individual guardrail classes
- Add comprehensive tests
- Create usage examples

#### Phase 3: Advanced Features
- Implement batch processing
- Add guardrail manager
- Performance optimizations
- Documentation and examples

### Trade-offs

#### Simplicity vs. Flexibility
- **Chosen**: Prioritize simplicity for common use cases
- **Rationale**: Most users need basic guardrail checking, not complex configurations
- **Mitigation**: Provide advanced API for power users

#### Performance vs. Maintainability
- **Chosen**: Prioritize maintainability with clear abstractions
- **Rationale**: Code clarity is more important than micro-optimizations
- **Mitigation**: Profile and optimize bottlenecks later

#### Feature Completeness vs. Time to Market
- **Chosen**: Focus on core functionality first
- **Rationale**: Better to have working basic package than delayed feature-complete version
- **Mitigation**: Design extensibility into the architecture

### Future Extensibility

The architecture supports future enhancements:
- New guardrail types can be added by extending BaseGuardrail
- Custom DSPy models can be plugged in
- Async execution can be added without breaking changes
- Caching and performance optimizations can be layered on top
- Configuration sources can be extended (databases, remote configs, etc.)

### Testing Strategy

- Unit tests for each guardrail class
- Integration tests for end-to-end functionality
- Configuration validation tests
- Error handling tests
- Performance benchmarks
- Compatibility tests with existing notebooks