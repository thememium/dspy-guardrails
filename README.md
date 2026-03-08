<a name="readme-top"></a>

<div align="center">
  <h3 align="center">DSPy Guardrails</h3>

  <p align="center">
    A comprehensive collection of AI guardrails built with DSPy for content moderation and security.
    <br />
    <a href="#table-of-contents"><strong>Explore the Documentation »</strong></a>
    <br />
    <a href="https://github.com/thememium/dspy-guardrails/issues">Report Bug</a>
    ·
    <a href="https://github.com/thememium/dspy-guardrails/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->

<a name="table-of-contents"></a>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about">About</a></li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#development">Development</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- ABOUT -->

## About

DSPy Guardrails is a comprehensive suite of AI guardrails built with [DSPy](https://github.com/stanfordnlp/dspy). Each guardrail is implemented as a self-contained module that can be used to test and validate different types of content moderation and security checks.

- **Modular design** — Each guardrail type is implemented as a separate, self-contained module
- **Programmatic testing** — Run guardrails directly in Python for fast iteration
- **Comprehensive coverage** — Covers major content moderation and security scenarios
- **DSPy integration** — Leverages DSPy's programmatic prompting for consistent, reliable results
- **Type safety** — Full type hints and dataclass definitions for robust implementations

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- QUICK START -->

## Quick Start

### Install

```bash
uv add dspy-guardrails
```

```bash
pip install dspy-guardrails
```

### Setup

Configure DSPy with the provider of your choice (OpenAI, Anthropic, Gemini, OpenRouter, etc.).

### Try Your First Guardrail

```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy (required)
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025")
guardrail.configure(lm=lm)

# Create and run a guardrail
topic_guardrail = guardrail.Topic(topic_scopes=["AI", "Machine Learning"])
result = guardrail.Run(topic_guardrail, "I want to learn about neural networks")

print(f"Allowed: {result.is_allowed}")  # True
```

### Multiple Guardrails

```python
all_guardrails = [
    guardrail.Topic(topic_scopes=["AI"]),
    guardrail.Nsfw(),
    guardrail.Pii(),
]
result = guardrail.Run(all_guardrails, "Safe AI content")
print(f"All passed: {result.is_allowed}")  # True
```

**[Quickstart Guide →](docs/QUICKSTART.md)** | **[Guardrail Types →](docs/GUARDRAIL_TYPES.md)**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->

## Usage

### Python Package

**Basic Usage:**

```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy (required)
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025")
guardrail.configure(lm=lm)

# Create and run guardrails
topic_guardrail = guardrail.Topic(topic_scopes=["AI", "Machine Learning"])
result = guardrail.Run(topic_guardrail, "I want to learn about neural networks")
print(f"Allowed: {result.is_allowed}")  # True

# Using kwargs for specific guardrails
ctx = "The Eiffel Tower is in Paris."
grounding_gr = guardrail.Grounding()
result = guardrail.Run(grounding_gr, "The Eiffel Tower is in Paris", context=ctx)
print(f"Grounded: {result.is_allowed}")  # True
```

### Multiple Guardrails

```python
all_guardrails = [
    guardrail.Topic(topic_scopes=["AI"]),
    guardrail.Nsfw(),
    guardrail.Pii(),
]
result = guardrail.Run(all_guardrails, "Safe AI content")
print(f"All passed: {result.is_allowed}")  # True
```

### Advanced Configuration

**Guardrail Configuration Options:**

```python
import dspy
from dspy_guardrails import guardrail

# Option 1: Configure guardrails with a specific model
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="your-key")
guardrail.configure(lm=lm)

# Option 2: Use globally configured DSPy LM for guardrails
dspy.configure(lm=lm)  # Configure DSPy globally
guardrail.configure()  # Guardrails will use the global DSPy config

# Option 3: Different models for different purposes
dspy.configure(lm=dspy.LM("openai/gpt-4", api_key="openai-key"))  # For your main app
guardrail.configure(lm=dspy.LM("openrouter/google/gemini-flash", api_key="router-key"))  # For guardrails
```

### Advanced Run Patterns

```python
# Multiple texts against single guardrail (returns aggregated result)
result = guardrail.Run(topic_guardrail, ["Text 1", "Text 2", "Text 3"])
# result.is_allowed is True only if ALL texts pass

# Multiple texts against multiple guardrails
result = guardrail.Run([topic_guardrail, nsfw_guardrail], ["Text 1", "Text 2"])

# Early return on first failure
result = guardrail.Run([topic_guardrail, nsfw_guardrail], "Text", early_return=True)
```

### Legacy Individual Check Methods

```python
# Individual guardrail check (legacy approach)
result = topic_guardrail.check("User input text")
# result.is_allowed, result.reason, result.metadata
```

### Package Installation

```sh
# Install the package
pip install dspy-guardrails

# Or install in development mode
uv pip install -e .
```

**For detailed examples and patterns, see the [complete quickstart guide](docs/QUICKSTART.md).**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DEVELOPMENT -->

## Development

### Code Quality

This project uses several tools to maintain code quality:

- **Ruff:** Linting and formatting
- **isort:** Import sorting
- **pytest:** Testing framework

**Available commands:**

```sh
# Run all quality checks
uv run poe clean

# Individual checks
uv run poe lint          # Ruff linting
uv run poe format        # Ruff formatting
uv run poe sort          # Import sorting
```

### Testing

Run tests using pytest:

```sh
# Run all tests
uv run pytest

# Run specific test
uv run pytest path/to/test.py::test_name
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Quick workflow:

1. Fork and branch: `git checkout -b feature/name`
2. Make changes
3. Run checks: `uv run poe clean-full`
4. Commit and push
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

MIT (as declared in `pyproject.toml`).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<div align="center">
  <p>
    <sub>Built by <a href="https://github.com/thememium">thememium</a></sub>
  </p>
</div>
