# DSPy Guardrails Quickstart

Get started with DSPy Guardrails in under 5 minutes! This guide shows you how to install and run your first guardrail with minimal setup.

## 🚀 3-Minute Setup

### 1. Install Dependencies
```bash
git clone https://github.com/thememium/dspy-guardrails.git
cd dspy-guardrails
uv sync
```

### 2. Set Your API Key
Get an API key from [OpenRouter](https://openrouter.ai/) and set it:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```

### 3. Run Your First Guardrail
Create a file called `test.py`:
```python
import dspy
from dspy_guardrails import guardrail

# Configure DSPy (required)
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025")
guardrail.configure(lm=lm)

# Create and run a guardrail
topic_guardrail = guardrail.topic(business_scopes=["AI", "Machine Learning"])
result = guardrail.Run(topic_guardrail, "I want to learn about neural networks")

print(f"Allowed: {result.is_allowed}")
print(f"Reason: {result.reason}")
```

Run it:
```bash
python test.py
```

You should see:
```
Allowed: True
Reason: Content is within business scope
```

## 🎯 What Just Happened

You created a **topic guardrail** that checks if content stays within your business scope ("AI" and "Machine Learning"). The guardrail passed because "neural networks" is related to AI/ML.

Try changing the text to something off-topic:
```python
result = guardrail.Run(topic_guardrail, "I want to buy groceries")
```

Now it should show:
```
Allowed: False
Reason: Content is outside business scope
```

## 🛡️ Try Different Guardrails

### NSFW Content Detection
```python
nsfw_guardrail = guardrail.nsfw()
result = guardrail.Run(nsfw_guardrail, "This is a safe message")
print(f"Allowed: {result.is_allowed}")
```

### PII Detection
```python
pii_guardrail = guardrail.pii()
result = guardrail.Run(pii_guardrail, "My email is user@example.com")
print(f"Allowed: {result.is_allowed}")  # False - contains PII
```

### Multiple Guardrails at Once
```python
all_guardrails = [
    guardrail.topic(business_scopes=["AI"]),
    guardrail.nsfw(),
    guardrail.pii()
]
result = guardrail.Run(all_guardrails, "Safe AI content")
print(f"All passed: {result.is_allowed}")
```

## 🔧 Troubleshooting

### "Module not found" errors
Make sure you ran `uv sync` to install dependencies.

### API key issues
- Check your `OPENROUTER_API_KEY` is set: `echo $OPENROUTER_API_KEY`
- Make sure your OpenRouter account has credits
- Try a different model: `dspy.LM("openai/gpt-4o-mini")` (needs OpenAI key)

### Guardrail not working
- Ensure `guardrail.configure(lm=lm)` is called before creating guardrails
- Check that your DSPy LM is properly configured
- Try running the example.py file: `python example.py`

### Import errors
Make sure you're in the project directory and have activated the environment:
```bash
cd dspy-guardrails
source .venv/bin/activate  # or however you activate uv environments
```

## 📚 Next Steps

- **Interactive Notebooks**: Try `uv run marimo edit notebooks/001-topic.py`
- **Full API Reference**: See README.md for detailed usage
- **Advanced Examples**: Check example.py for comprehensive patterns
- **Configuration Options**: Explore different guardrail settings

## 💡 Pro Tips

- Use `guardrail.Run([gr1, gr2], text)` for multiple guardrails
- Set `early_return=True` to stop on first failure
- Check `result.metadata` for detailed per-guardrail results
- Use environment variables for API keys in production

---

**Need help?** Check the [full documentation](README.md) or open an issue on GitHub.