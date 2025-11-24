## 1. Remove GuardrailManager
- [x] 1.1 Delete dspy_guardrails/core/manager.py file
- [x] 1.2 Remove GuardrailManager import from dspy_guardrails/core/__init__.py
- [x] 1.3 Remove GuardrailManager from __all__ in dspy_guardrails/core/__init__.py

## 2. Remove Factory Functions
- [x] 2.1 Delete dspy_guardrails/factory.py file
- [x] 2.2 Remove factory imports from dspy_guardrails/__init__.py
- [x] 2.3 Remove factory function names from __all__ in dspy_guardrails/__init__.py

## 3. Simplify Guardrail Module API
- [x] 3.1 Remove model, temperature, max_tokens, cache_enabled, timeout_seconds, api_key_env_var parameters from all guardrail functions in dspy_guardrails/guardrail.py
- [x] 3.2 Update function signatures to only accept guardrail-specific parameters
- [x] 3.3 Update docstrings to remove model parameter documentation
- [x] 3.4 Update config instantiation to not pass model parameters

## 4. Update Package Exports
- [x] 4.1 Update dspy_guardrails/__init__.py to remove deprecated imports
- [x] 4.2 Update __all__ list to remove deprecated function names

## 5. Update Tests
- [x] 5.1 Remove GuardrailManager-related tests from tests/test_basic.py
- [x] 5.2 Remove factory function tests from tests/test_basic.py
- [x] 5.3 Update guardrail module tests to use simplified API
- [x] 5.4 Fix type errors in test files related to Run function return types

## 6. Update Documentation
- [x] 6.1 Update README.md to remove GuardrailManager documentation
- [x] 6.2 Update README.md to remove factory function examples
- [x] 6.3 Update README.md to show simplified guardrail module API
- [x] 6.4 Update MIGRATION_GUIDE.md to reflect final API state
- [x] 6.5 Update example.py to use only the simplified API

## 7. Update Configuration Classes
- [x] 7.1 Remove model parameters from GuardrailConfig base class (keep optional for backward compatibility if needed)
- [x] 7.2 Update configure_dspy_from_config to handle cases where model is None
- [x] 7.3 Ensure all guardrails use the global guardrail configuration

## 8. Code Quality Checks
- [x] 8.1 Run uv run poe clean to ensure code quality
- [x] 8.2 Run uv run pytest to ensure all tests pass
- [x] 8.3 Check for any unused imports or dependencies
- [x] 8.4 Update pyproject.toml if any dependencies are no longer needed</content>
<parameter name="filePath">openspec/changes/cleanup-deprecated-code-for-production/tasks.md