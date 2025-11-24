# Change: Add Run Function for Batch Guardrail Execution

## Why
Users want a simple way to execute guardrails without managing a GuardrailManager instance. They want to pass either a single guardrail or a list of guardrails along with text and control execution behavior (early return vs run all).

## What Changes
- Add `Run()` function to the main dspy_guardrails module
- Function accepts single guardrail or list of guardrails, text to check, and early_return boolean (default False)
- Ensure consistent return values across all guardrail modules
- Update example.py to demonstrate the new Run() API

## Impact
- Affected specs: package-api
- Affected code: dspy_guardrails/__init__.py, dspy_guardrails/guardrail.py, example.py
- Breaking changes: None (additive API improvements)