# Create DSPy Guardrails Package

## Summary
Create a Python package that encapsulates the existing DSPy guardrail notebooks, providing an easy-to-use API for configuration and decision-making. This will transform the current notebook-based guardrails into a reusable, importable package.

## Problem
Currently, the DSPy guardrails are implemented as individual Marimo notebooks that must be run manually. There's no programmatic way to use these guardrails in other applications, making it difficult to integrate them into production systems or use them in automated workflows.

## Solution
Create a `dspy_guardrails` Python package that:
- Extracts the DSPy signatures from notebooks into reusable classes
- Provides a unified API for configuring and running guardrails
- Supports both individual and batch guardrail execution
- Maintains compatibility with existing notebook functionality
- Includes proper error handling and type safety

## Impact
- Enables programmatic use of guardrails in external applications
- Simplifies guardrail configuration and execution
- Maintains existing notebook functionality for development/testing
- Provides foundation for future guardrail enhancements

## Scope
**In Scope:**
- Package structure with proper Python module organization
- Extraction of all 7 guardrail signatures (Topic, NSFW, Jailbreak, PII, Prompt Injection, Keywords, Secret Keys)
- Unified configuration API
- Decision-making API for running guardrails
- Type safety and error handling
- Basic tests for package functionality

**Out of Scope:**
- Changes to existing notebook functionality
- New guardrail types (beyond the existing 7)
- Performance optimizations
- Advanced features like caching or async execution

## Dependencies
- Existing DSPy and Marimo dependencies
- No new external dependencies required
- Python 3.12+ (maintaining current requirement)

## Risks
- Risk of breaking existing notebook functionality during extraction
- Risk of inconsistent API design across different guardrail types
- Risk of over-engineering the initial package design

## Success Criteria
- All 7 guardrails can be used programmatically via the package API
- Existing notebooks continue to function unchanged
- Package follows Python packaging best practices
- Clear documentation and examples provided
- Tests pass for all guardrail functionality