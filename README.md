<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">DSPy Guardrails</h3>

  <p align="center">
    A comprehensive collection of AI guardrails built with DSPy and Marimo for content moderation and security.
    <br />
    <br />
    <a href="#table-of-contents"><strong>Explore the Guardrails »</strong></a>
    <br />
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
    <li>
      <a href="#about-the-project">About the Project</a>
    </li>
    <li>
      <a href="#guardrail-types">Guardrail Types</a>
      <ul>
        <li><a href="#topic-compliance">Topic Compliance</a></li>
        <li><a href="#nsfw-content-detection">NSFW Content Detection</a></li>
        <li><a href="#jailbreak-detection">Jailbreak Detection</a></li>
        <li><a href="#pii-detection">PII Detection</a></li>
        <li><a href="#prompt-injection-detection">Prompt Injection Detection</a></li>
        <li><a href="#keyword-filtering">Keyword Filtering</a></li>
        <li><a href="#secret-keys-detection">Secret Keys Detection</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li>
      <a href="#development">Development</a>
      <ul>
        <li><a href="#code-quality">Code Quality</a></li>
        <li><a href="#testing">Testing</a></li>
      </ul>
    </li>
    <li>
      <a href="#agents">Agents</a>
    </li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About the Project

This repository contains a comprehensive suite of AI guardrails built with [DSPy](https://github.com/stanfordnlp/dspy) and [Marimo](https://marimo.io/). Each guardrail is implemented as an interactive notebook that can be used to test and validate different types of content moderation and security checks.

**Key Features:**

- **Modular Design:** Each guardrail type is implemented as a separate, self-contained notebook
- **Interactive Testing:** Marimo notebooks provide real-time testing capabilities
- **Comprehensive Coverage:** Covers major content moderation and security scenarios
- **DSPy Integration:** Leverages DSPy's programmatic prompting for consistent, reliable results
- **Type Safety:** Full type hints and dataclass definitions for robust implementations

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GUARDRAIL TYPES -->

## Guardrail Types

This project includes seven different types of guardrails, each addressing specific content moderation and security needs:

### Topic Compliance

**Notebook:** `001-topic.py`

Ensures content stays within defined business scopes and flags mentions of competitors.

**Features:**
- Configurable business scopes and competitor lists
- Boolean flagging with detailed reasoning
- Integration with business context validation

**Use Case:** Perfect for customer service bots, content filtering, and brand protection.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### NSFW Content Detection

**Notebook:** `002-nsfw.py`

Detects and flags Not Safe For Work content across multiple categories.

**Categories Covered:**
- Sexual content and explicit material
- Hate speech and discriminatory language
- Violence and gore
- Illegal activities
- Adult themes and mature content

**Use Case:** Content moderation for social platforms, forums, and user-generated content.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Jailbreak Detection

**Notebook:** `003-jailbreak.py`

Advanced detection system for adversarial jailbreak attempts using comprehensive taxonomy.

**Detection Techniques:**
- Character-level obfuscation (encoding, transliteration)
- Competing objectives and instruction override
- Lexical and semantic obfuscation
- Context-level manipulation
- Multi-turn escalation patterns

**Use Case:** Protecting AI systems from sophisticated bypass attempts and adversarial attacks.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### PII Detection

**Notebook:** `004-pii.py`

Comprehensive Personally Identifiable Information detection with global coverage.

**Supported Entities:**
- **Global:** Credit cards, emails, IP addresses, phone numbers
- **USA:** SSN, driver licenses, passports, bank numbers
- **UK:** NHS numbers, National Insurance numbers
- **Spain:** NIF, NIE
- **Italy:** Fiscal codes, VAT codes, identity cards
- **Poland:** PESEL, NIP

**Use Case:** Data privacy compliance, GDPR protection, and sensitive information filtering.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Prompt Injection Detection

**Notebook:** `005-prompt-injection.py`

Security-focused detection of prompt injection attacks in LLM-based tool use.

**Detection Focus:**
- Tool calls with malicious arguments
- Instructions that override user goals
- Attempts to exfiltrate secrets
- Commands that ignore safety policies

**Use Case:** Securing AI agents and tool-using systems from manipulation attacks.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Keyword Filtering

**Notebook:** `006-keywords.py`

Unicode-aware keyword filtering with precise word boundary detection.

**Features:**
- Configurable keyword lists
- Unicode character support
- Word boundary detection
- Dataclass-based configuration

**Use Case:** Basic content filtering, profanity detection, and custom keyword blocking.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Secret Keys Detection

**Notebook:** `007-secret-keys.py`

Advanced detection of API keys, tokens, and other sensitive credentials.

**Detection Patterns:**
- Common key prefixes (sk-, pk_, AKIA, etc.)
- Configurable threshold levels (strict, balanced, permissive)
- File extension awareness
- Custom regex support

**Use Case:** Preventing accidental exposure of API keys, tokens, and other credentials.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

### Prerequisites

- **Python 3.12+**
- **UV** - Python package manager
- **OpenRouter API key** (for LLM access)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/thememium/dspy-guardrails.git
   cd dspy-guardrails
   ```

2. **Install dependencies:**
   ```sh
   uv sync
   ```

3. **Set up environment variables:**
   ```sh
   export OPENROUTER_API_KEY="your-api-key-here"
   ```

### Usage

#### Interactive Notebooks

Each guardrail can be run as an interactive Marimo notebook:

```sh
# Run a specific guardrail notebook
uv run marimo edit notebooks/001-topic.py

# Or run in presentation mode
uv run marimo run notebooks/001-topic.py
```

**Example Usage:**

1. Open the desired notebook in your browser
2. Enter test content in the text area
3. View real-time guardrail results
4. Adjust configuration as needed

#### Python Package

The guardrails are also available as a Python package for programmatic use:

**Simple Usage:**
```python
from dspy_guardrails import TopicGuardrail, NsfwGuardrail
from dspy_guardrails.core.config import TopicGuardrailConfig, NsfwGuardrailConfig

# Configure and use guardrails
topic_config = TopicGuardrailConfig(
    business_scopes=["Shipping", "Logistics"],
    competitor_names=["CompetitorA", "CompetitorB"]
)
guardrail = TopicGuardrail(topic_config)
result = guardrail.check("User input text")
# result.is_allowed, result.reason, result.metadata
```

**Factory Functions (Easy Setup):**
```python
from dspy_guardrails import create_topic_guardrail, create_nsfw_guardrail

# Quick setup with sensible defaults
topic_guardrail = create_topic_guardrail(
    business_scopes=["AI", "Machine Learning"],
    competitor_names=["OpenAI", "Google"]
)
nsfw_guardrail = create_nsfw_guardrail(sensitivity_level="high")
```

**GuardrailManager (Multiple Guardrails):**
```python
from dspy_guardrails import GuardrailManager

manager = GuardrailManager()
manager.add_guardrail("topic", topic_guardrail)
manager.add_guardrail("nsfw", nsfw_guardrail)

# Check all guardrails at once
results = manager.check("User content")
all_passed = manager.check_all_allowed("Safe content")
blocking_reasons = manager.get_blocking_reasons("Problematic content")
```

**Comprehensive Suite:**
```python
from dspy_guardrails import create_comprehensive_guardrail_suite

# Create a full guardrail suite with one function call
manager = create_comprehensive_guardrail_suite(
    business_scopes=["Your Business"],
    competitor_names=["CompetitorA"],
    blocked_keywords=["inappropriate"]
)
```

**Installation:**

```sh
# Install the package
pip install dspy-guardrails

# Or install in development mode
uv pip install -e .
```

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
