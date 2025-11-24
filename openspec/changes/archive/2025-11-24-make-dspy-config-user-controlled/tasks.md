## 1. Core Configuration Changes
- [x] 1.1 Add `dspy_guardrails.configure()` function for guardrail-specific config
- [x] 1.2 Make model parameter optional in `GuardrailConfig` (uses guardrail config when None)
- [x] 1.3 Update validation to allow None model values
- [x] 1.4 Fix type annotations for optional list fields

## 2. Factory Function Updates
- [x] 2.1 Remove model parameters from all factory functions
- [x] 2.2 Update function signatures to not require model specification
- [x] 2.3 Update factory function docstrings to reflect guardrail configuration

## 3. Guardrail Implementation Updates
- [x] 3.1 Update all guardrail classes to validate guardrail configuration on execution
- [x] 3.2 Modify `_configure_dspy()` methods to use guardrail-specific configuration
- [x] 3.3 Add checks to prevent guardrail execution without proper guardrail setup

## 4. Utility Function Updates
- [x] 4.1 Update `configure_dspy_from_config()` to handle optional model parameter
- [x] 4.2 Update `is_dspy_configured()` to check guardrail configuration
- [x] 4.3 Remove unused `get_default_dspy_config()` function

## 5. Documentation and Examples
- [x] 5.1 Update README.md with guardrail configuration instructions
- [x] 5.2 Update example.py to show guardrail configuration
- [x] 5.3 Notebooks already use global DSPy configuration

## 6. Testing Updates
- [x] 6.1 Update existing tests to remove model parameters
- [x] 6.2 Add guardrail configuration fixture for test setup
- [x] 6.3 Add config validation tests

## 7. Migration Guide
- [x] 7.1 Create migration guide for existing users
- [x] 7.2 Update AGENTS.md with new guardrail configuration requirements