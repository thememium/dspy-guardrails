## 1. Add Run Function
- [ ] 1.1 Create Run() function in guardrail.py that accepts guardrail(s) and text
- [ ] 1.2 Add early_return parameter (default False = run all)
- [ ] 1.3 Handle both single guardrail and list of guardrails
- [ ] 1.4 Ensure consistent return values across guardrail modules
- [ ] 1.5 Export Run function in __init__.py

## 2. Update Example Usage
- [ ] 2.1 Modify example.py to demonstrate Run() function
- [ ] 2.2 Add examples of single guardrail and batch execution
- [ ] 2.3 Show early return vs full execution modes

## 3. Testing and Validation
- [ ] 3.1 Add tests for Run() function with single guardrail
- [ ] 3.2 Add tests for Run() function with list of guardrails
- [ ] 3.3 Add tests for early_return behavior
- [ ] 3.4 Run `uv run poe clean` to ensure code quality