# DSPy Guardrails Quickstart

Get started with DSPy Guardrails in under 3 minutes. 

## 🚀 3-Minute Setup

### 1. Install
```bash
uv add dspy-guardrails
```

Or with pip:
```bash
pip install dspy-guardrails
```

### 2. Set Provider Credentials (If Needed)
If your model provider requires an API key, set it before running.
For OpenRouter:
```bash
export OPENROUTER_API_KEY="your-api-key-here"
```
Or pass it directly when creating the LM:
```python
lm = dspy.LM("openrouter/google/gemini-2.5-flash-preview-09-2025", api_key="...")
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
topic_guardrail = guardrail.Topic(topic_scopes=["AI", "Machine Learning"])
result = guardrail.Run(topic_guardrail, "I want to learn about neural networks")

print(f"Allowed: {result.is_allowed}")
print(f"Reason: {result.reason}")
```

Run it:
```bash
python test.py
```

You should see a result with `Allowed: True/False` depending on the model output.

### Optional: Run From the Repo (Development)
```bash
git clone https://github.com/thememium/dspy-guardrails.git
cd dspy-guardrails
uv sync
uv run example.py
```

## 🎯 What Just Happened

You created a **topic guardrail** that checks if content stays within your topic scope ("AI" and "Machine Learning"). The exact result depends on the model output.

Try changing the text to something off-topic:
```python
result = guardrail.Run(topic_guardrail, "I want to buy groceries")
```

If the content is off-topic, the guardrail will return `Allowed: False` with a reason from the model.

## 🛡️ Try Different Guardrails

### NSFW Content Detection
```python
nsfw_guardrail = guardrail.Nsfw()
result = guardrail.Run(nsfw_guardrail, "This is a safe message")
print(f"Allowed: {result.is_allowed}")
```

### PII Detection
```python
pii_guardrail = guardrail.Pii(allowed_pii_types=["email"])
result = guardrail.Run(pii_guardrail, "My email is user@example.com")
print(f"Allowed: {result.is_allowed}")  # True - email is allowed
```

### Toxicity & Tone
```python
toxic_guardrail = guardrail.Toxicity(toxicity_threshold=0.8)
tone_guardrail = guardrail.Tone(desired_tone="helpful")
result = guardrail.Run([toxic_guardrail, tone_guardrail], "You are doing a great job!")
```

### Grounding (Fact-checking)
```python
ctx = "The Eiffel Tower is 330 meters tall and located in Paris."
grounding_gr = guardrail.Grounding(grounding_threshold=0.8)
result = guardrail.Run(grounding_gr, "The Eiffel Tower is in Paris", context=ctx)
print(f"Grounded: {result.is_allowed}")  # True
```

### Multiple Guardrails at Once
```python
all_guardrails = [
    guardrail.Topic(topic_scopes=["AI"]),
    guardrail.Nsfw(),
    guardrail.Pii()
]
result = guardrail.Run(all_guardrails, "Safe AI content")
print(f"All passed: {result.is_allowed}")
```

## ⚡ Quick Usage Patterns

### Run With Early Return
```python
guardrails = [guardrail.Topic(topic_scopes=["AI"]), guardrail.Nsfw()]
result = guardrail.Run(guardrails, "Risky content", early_return=True)
print(result.is_allowed)
```

### Run Against Multiple Texts
```python
topic_guardrail = guardrail.Topic(topic_scopes=["AI"], blocked_topics=["spam"])
result = guardrail.Run(topic_guardrail, ["safe text", "another text"])
print(result.metadata["total_texts"], result.metadata["processed_texts"])
```

### Inspect Per-Guardrail Results
```python
guardrails = [guardrail.Topic(topic_scopes=["AI"]), guardrail.Nsfw()]
result = guardrail.Run(guardrails, "Safe AI content")
text_result = result.metadata["text_results"][0]
for gr_result in text_result["results"]:
    print(gr_result.guardrail_name, gr_result.is_allowed)
```

## 🔧 Troubleshooting

### "Module not found" errors
Make sure you installed the package (`uv add dspy-guardrails` or `pip install dspy-guardrails`).

### API key issues
- Check your `OPENROUTER_API_KEY` is set: `echo $OPENROUTER_API_KEY`
- Make sure your OpenRouter account has credits
- Try a different model: `dspy.LM("openai/gpt-4o-mini")` (needs OpenAI key)

### Guardrail not working
- Ensure `guardrail.configure(lm=lm)` is called before creating guardrails
- Check that your DSPy LM is properly configured
- Try running the example file: `python example.py` (repo clone) or `uv run example.py`

### Import errors
If you installed with uv/pip, verify you're running the same Python environment you installed into.

## 📚 Next Steps

- **Full API Reference**: See README.md for detailed usage
- **Guardrail Types**: Review docs/GUARDRAIL_TYPES.md for per-guardrail configuration
- **Advanced Examples**: Check example.py for comprehensive patterns

## 💡 Pro Tips

- Use `guardrail.Run([gr1, gr2], text)` for multiple guardrails
- Set `early_return=True` to stop on first failure
- Check `result.metadata` for detailed per-guardrail results
- Use environment variables for API keys in production

---

**Need help?** Check the [full documentation](../README.md) or open an issue on GitHub.
