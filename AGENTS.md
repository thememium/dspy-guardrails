# DSPy Guardrails - Agent Guidelines

## Build/Lint/Test Commands
- `uv run poe clean` - Run all code quality checks (isort, ruff check, ruff format, deptry)
- `uv run poe lint` - Run Ruff linting
- `uv run poe format` - Run Ruff formatting  
- `uv run poe sort` - Run isort import sorting
- `uv run poe deptry` - Check for missing/unused dependencies
- `uv run pytest` - Run all tests
- `uv run pytest path/to/test.py::test_name` - Run single test

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local imports. Use `uv run poe sort` to auto-sort.
- **Formatting**: Uses Ruff formatter. Run `uv run poe format` before committing.
- **Type Hints**: Required for all function signatures and class definitions using `typing` module.
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants.
- **Error Handling**: Use try/except blocks with specific exception types. Include `pass` for intentional no-op except blocks.
- **Marimo Apps**: All notebooks follow the pattern with `app.setup`, `@app.cell`, and `@app.class_definition` decorators.
- **DSPy Signatures**: Use descriptive docstrings and clear InputField/OutputField descriptions.