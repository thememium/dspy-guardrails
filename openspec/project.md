# Project Context

## Purpose
DSPy Guardrails is a comprehensive collection of AI guardrails built with DSPy and Marimo for content moderation and security. The project provides seven different types of guardrails implemented as interactive notebooks:

- **Topic Compliance**: Ensures content stays within defined business scopes
- **NSFW Content Detection**: Detects inappropriate content across multiple categories
- **Jailbreak Detection**: Advanced detection of adversarial jailbreak attempts
- **PII Detection**: Comprehensive Personally Identifiable Information detection
- **Prompt Injection Detection**: Security-focused detection of prompt injection attacks
- **Keyword Filtering**: Unicode-aware keyword filtering with precise word boundary detection
- **Secret Keys Detection**: Advanced detection of API keys, tokens, and credentials

The goal is to provide modular, testable, and reliable AI safety mechanisms for content moderation and security applications.

## Tech Stack
- **Python 3.12+**: Core programming language
- **DSPy**: Programmatic prompting framework for consistent AI responses
- **Marimo**: Interactive notebook environment for testing guardrails
- **UV**: Modern Python package manager for dependency management
- **Ruff**: Fast Python linter and formatter
- **Pytest**: Testing framework for unit and integration tests
- **OpenRouter API**: LLM provider for AI model access

## Project Conventions

### Code Style
- **Imports**: Standard library first, then third-party, then local imports. Use `uv run poe sort` to auto-sort.
- **Formatting**: Uses Ruff formatter. Run `uv run poe format` before committing.
- **Type Hints**: Required for all function signatures and class definitions using `typing` module.
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants.
- **Error Handling**: Use try/except blocks with specific exception types. Include `pass` for intentional no-op except blocks.
- **Docstrings**: Use descriptive docstrings for all public functions and classes.
- **Environment Variables**: Use `python-dotenv` for loading environment variables. Never commit secrets.

### Architecture Patterns
- **Modular Design**: Each guardrail is implemented as a separate, self-contained notebook in the `notebooks/` directory
- **DSPy Signatures**: All guardrails use DSPy Signature classes with clear InputField/OutputField definitions and descriptive docstrings
- **Marimo Pattern**: Notebooks follow consistent structure with `app.setup`, `@app.cell`, and `@app.class_definition` decorators
- **Type Safety**: Full type hints and dataclass definitions for robust implementations
- **Configuration-Driven**: Guardrails accept configuration parameters for flexibility

### Testing Strategy
- **Framework**: Pytest for all testing needs
- **Command**: `uv run pytest` for all tests, `uv run pytest path/to/test.py::test_name` for single tests
- **Coverage**: Aim for comprehensive test coverage of guardrail logic
- **Test Types**: Unit tests for individual components, integration tests for end-to-end guardrail functionality
- **CI/CD**: Run tests automatically on commits and pull requests

### Git Workflow
- **Main Branch**: `main` branch for production-ready code
- **Feature Branches**: Create feature branches for new guardrails or improvements
- **Commit Messages**: Use descriptive commit messages following conventional commits format
- **Pull Requests**: Required for all changes with code review
- **Pre-commit**: Run `uv run poe clean` before committing to ensure code quality

## Domain Context
AI guardrails are safety mechanisms that monitor and control AI system behavior to prevent harmful outputs, security breaches, and policy violations. This project focuses on content moderation guardrails that analyze text inputs and determine whether they comply with safety policies, contain inappropriate content, or attempt to bypass security measures.

Key concepts:
- **Content Moderation**: Filtering and classifying user-generated content
- **Adversarial Attacks**: Attempts to manipulate AI systems (jailbreaks, prompt injection)
- **PII Detection**: Identifying personally identifiable information for privacy compliance
- **Security Scanning**: Detecting exposed secrets and sensitive credentials

## Important Constraints
- **Python Version**: Requires Python 3.12+ for modern language features and type hints
- **Environment Variables**: Must set `OPENROUTER_API_KEY` for LLM access
- **Dependencies**: Use UV for package management to ensure reproducible environments
- **Security**: Never commit API keys, secrets, or sensitive configuration
- **Performance**: Guardrails should be fast enough for real-time content moderation

## External Dependencies
- **OpenRouter API**: Primary LLM provider for AI model inference (requires API key)
- **Python Package Index**: All dependencies managed through UV and listed in pyproject.toml
- **GitHub**: Repository hosting and CI/CD platform
- **No external databases or services**: Project is self-contained with local notebook execution
