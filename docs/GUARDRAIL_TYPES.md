# Guardrail Types

This project includes twelve guardrail types for content moderation and security. All guardrails are created via `dspy_guardrails.guardrail` and return a `GuardrailResult` with `is_allowed`, `reason`, and `metadata`.

## Topic Compliance

Keep content inside approved topic scopes and flag off-topic content.

**Best for:** Topic-scoped assistants, brand or domain compliance, content routing.

**Configuration**
- `topic_scopes` (required): list of allowed topics.
- `blocked_topics` (required, can be empty): list of topics to explicitly reject.

**Example**
```python
topic_gr = guardrail.Topic(
    topic_scopes=["AI", "Machine Learning"],
    blocked_topics=["spam"],
)
result = guardrail.Run(topic_gr, "Let's discuss neural networks")
```

## Toxicity Detection

Detect toxic or harmful language and block when it exceeds the threshold.

**Best for:** Community moderation, safety filters, abuse prevention.

**Configuration**
- `toxicity_threshold` (default `0.5`): score threshold for flagging toxicity.

**Example**
```python
toxicity_gr = guardrail.Toxicity(toxicity_threshold=0.8)
result = guardrail.Run(toxicity_gr, "You are terrible")
```

## Grounding (Hallucination Detection)

Verify that answers are supported by a provided context.

**Best for:** RAG systems, fact checking, citation-sensitive workflows.

**Configuration**
- `grounding_threshold` (default `0.7`): minimum grounding score to allow.

**Input requirements**
- Pass `context=...` to `guardrail.Run` for grounding checks.

**Example**
```python
grounding_gr = guardrail.Grounding(grounding_threshold=0.8)
ctx = "The Eiffel Tower is in Paris."
result = guardrail.Run(
    grounding_gr,
    "The Eiffel Tower is in Paris",
    context=ctx,
)
```

## NSFW Content Detection

Detect and block NSFW content across common categories.

**Best for:** User-generated content moderation, workplace-safe outputs.

**Configuration**
- `sensitivity_level` (default `"medium"`): one of `"low"`, `"medium"`, `"high"`.

**Example**
```python
nsfw_gr = guardrail.Nsfw(sensitivity_level="high")
result = guardrail.Run(nsfw_gr, "...text to check...")
```

## Jailbreak Detection

Detect adversarial jailbreak attempts that try to bypass system safety.

**Best for:** Agent safety, policy enforcement, adversarial prompt defense.

**Configuration**
- `detection_threshold` (default `0.8`): confidence threshold for flagging.

**Example**
```python
jailbreak_gr = guardrail.Jailbreak(detection_threshold=0.9)
result = guardrail.Run(jailbreak_gr, "Ignore all prior rules and...")
```

## PII Detection

Detect personally identifiable information and allow whitelisted types.

**Best for:** Privacy compliance, PII redaction workflows.

**Configuration**
- `allowed_pii_types` (default `[]`): PII types to allow (empty blocks all).

**Example**
```python
pii_gr = guardrail.Pii(allowed_pii_types=["email"])
result = guardrail.Run(pii_gr, "Email me at user@example.com")
```

## Prompt Injection Detection

Detect prompt injection in tool-using or multi-step agent workflows.

**Best for:** Agent toolchains, retrieval pipelines, tool output safety.

**Configuration**
- `injection_patterns` (default `[]`): custom patterns to check for.

**Input requirements**
- Input is a string. Pass a JSON-encoded string if you have structured logs.

**Example**
```python
payload = "{\"messages\":[{\"role\":\"user\",\"content\":\"...\"}],\"tool_calls\":[]}"
pi_gr = guardrail.PromptInjection(injection_patterns=["ignore previous"])
result = guardrail.Run(pi_gr, payload)
```

## Gibberish Detection

Detect nonsensical or low-quality text.

**Best for:** Input validation, spam filtering, quality control.

**Configuration**
- `prob_threshold` (default `0.5`): probability threshold for gibberish.

**Example**
```python
gibberish_gr = guardrail.Gibberish(prob_threshold=0.7)
result = guardrail.Run(gibberish_gr, "asdfghjkl")
```

## Language Detection

Detect language and enforce an allowed language list.

**Best for:** Multi-language apps, locale enforcement.

**Configuration**
- `allowed_languages` (required): ISO 639-1 language codes to allow.

**Example**
```python
language_gr = guardrail.Language(allowed_languages=["en", "es"])
result = guardrail.Run(language_gr, "Hola, como estas?")
```

## Tone and Sentiment

Ensure content matches desired tone and avoids unwanted tones.

**Best for:** Brand voice, customer support quality, tone policy enforcement.

**Configuration**
- `desired_tone` (default `"polite"`)
- `unwanted_tones` (default `["aggressive", "rude", "offensive", "sarcastic"]`)

**Example**
```python
tone_gr = guardrail.Tone(desired_tone="helpful", unwanted_tones=["sarcastic"])
result = guardrail.Run(tone_gr, "Happy to help!")
```

## Keyword Filtering

Block content containing specific keywords or phrases.

**Best for:** Basic content filters, profanity lists, brand restrictions.

**Configuration**
- `blocked_keywords` (required): list of blocked keywords or phrases.
- `case_sensitive` (default `False`)

**Example**
```python
keywords_gr = guardrail.Keywords(
    blocked_keywords=["password", "secret"],
    case_sensitive=False,
)
result = guardrail.Run(keywords_gr, "This contains a password")
```

## Secret Keys Detection

Detect API keys, tokens, and other sensitive credentials.

**Best for:** Leak prevention, log scanning, secret hygiene.

**Configuration**
- `key_patterns` (default `[]`): custom prefixes or patterns to check.
- `entropy_threshold` (default `4.0`)

**Example**
```python
secrets_gr = guardrail.SecretKeys(
    key_patterns=["sk-", "ghp_"],
    entropy_threshold=3.5,
)
result = guardrail.Run(secrets_gr, "sk-live-123456")
```
