# Changelog

All notable changes to DSPy Guardrails will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: `guardrail.Run()` now returns a single `GuardrailResult` when passed a single guardrail, instead of a list. Multiple guardrails still return a `List[GuardrailResult]`. This eliminates the need for `[0]` indexing when using single guardrails.

### Migration
If you were previously doing:
```python
results = guardrail.Run(topic_guardrail, "content")
result = results[0]  # Remove this line
```

You can now simply do:
```python
result = guardrail.Run(topic_guardrail, "content")
```

Multiple guardrail usage remains unchanged:
```python
results = guardrail.Run([gr1, gr2, gr3], "content")  # Still returns a list
```