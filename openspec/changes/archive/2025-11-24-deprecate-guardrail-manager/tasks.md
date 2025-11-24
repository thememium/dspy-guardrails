## 1. Deprecate GuardrailManager
- [ ] 1.1 Add deprecation warnings to GuardrailManager class
- [ ] 1.2 Add deprecation warnings to create_comprehensive_guardrail_suite function
- [ ] 1.3 Update __init__.py to mark GuardrailManager as deprecated in __all__

## 2. Update Documentation and Examples
- [ ] 2.1 Remove GuardrailManager usage from example.py
- [ ] 2.2 Update README.md to remove GuardrailManager documentation
- [ ] 2.3 Add migration guide in README.md showing how to migrate from GuardrailManager to Run()

## 3. Update Tests
- [ ] 3.1 Remove GuardrailManager tests from test_basic.py
- [ ] 3.2 Add tests showing migration from GuardrailManager to Run()

## 4. Remove from Public API
- [ ] 4.1 Remove GuardrailManager from __init__.py exports
- [ ] 4.2 Remove create_comprehensive_guardrail_suite from factory.py exports
- [ ] 4.3 Update factory.py to remove the function implementation

## 5. Code Quality
- [ ] 5.1 Run `uv run poe clean` to ensure code quality
- [ ] 5.2 Run all tests to ensure nothing is broken