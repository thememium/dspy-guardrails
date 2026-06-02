# Regex Prefilters

Most guardrails run a fast, deterministic **regex prefilter** before
delegating to the DSPy LLM. On a prefilter match the guardrail
short-circuits with `is_allowed=False` and no model call is made — so
known-bad inputs are blocked at zero API cost and zero latency
overhead. Only inputs that pass the prefilter reach the LLM.

| Guardrail | Prefilter | Custom patterns | Opt-out flag |
|---|---|---|---|
| `Pii` | email / phone / SSN / credit-card / IP | yes | `enable_regex_prefilter=False` |
| `PromptInjection` | 30+ attack patterns + typoglycemia + Base64/hex | yes | `enable_regex_prefilter=False` |
| `SecretKeys` | 24 provider patterns (OpenAI, GitHub, AWS, ...) | yes | `enable_regex_prefilter=False` |
| `Jailbreak` | 17 patterns (DAN, AIM, role-play bypass) | no | `enable_regex_prefilter=False` |
| `Keywords` | compiled user keywords (+ wildcards) | n/a (user-supplied) | `enable_regex_prefilter=False` |
| `Gibberish` | keyboard mashes, repeats, all-consonants | no | `enable_regex_prefilter=False` |
| `Language` | Unicode script detection (CJK, Cyrillic, ...) | no | `enable_script_prefilter=False` |
| `Toxicity` | conservative severe-pattern catalog | no | `enable_regex_prefilter=False` |
| `Topic` | `blocked_topics` substring match only | n/a (built-in) | `enable_blocked_topic_prefilter=False` |

`Nsfw`, `Tone`, and `Grounding` have no prefilter and are always
evaluated by the LLM.

## How It Works

```python
result = guardrail.Run(pii_guardrail, "Email me at user@example.com")

# Result metadata tells you which path handled the request:
result.metadata["method"]
#   "regex_prefilter" - the prefilter matched, no LLM call
#   "dspy"            - the prefilter passed, LLM evaluated the input

# On a prefilter match, "matches" lists what was caught:
result.metadata["matches"]    # [{"slug": "email", "matched_text": "user@example.com", ...}, ...]

# On a redact (PII), the modified text is exposed here:
result.metadata["redacted_text"]
```

All prefilters are **on by default** and **opt-out per guardrail**.
Disabling a prefilter is useful for A/B testing the LLM-only path or
when you want to bypass the catalog in favor of fully custom
patterns.

## Per-Guardrail Reference

### `Pii` — `enable_regex_prefilter=True`

**Built-in presets:** `email`, `phone`, `ssn`, `credit-card`, `ip-address`.

**Per-preset action** via `pii_actions` (`"redact"` replaces with a
labeled placeholder, request continues; `"block"` rejects with
`is_allowed=False`):

```python
pii = guardrail.Pii(
    pii_actions={
        "email": "redact",      # default
        "phone": "redact",      # default
        "ssn":   "block",       # override to block
    },
)
result = pii.check("Email me at user@example.com, SSN 123-45-6789")
# result.is_allowed = False (SSN blocked)
# result.metadata["redacted_text"] = "Email me at [EMAIL], SSN 123-45-6789"
```

**Custom patterns** (additive, never replace built-ins):

```python
pii = guardrail.Pii(
    custom_patterns=[
        {
            "name": "aws_access_key",
            "pattern": r"AKIA[0-9A-Z]{16}",
            "action": "block",
            "label": "AWS Key",   # used in the block reason
        },
    ],
)
```

Each entry requires `name`, `pattern`, and `action` (`"redact"` or
`"block"`); `label` is optional (defaults to `"[REDACTED]"` for
redact, the `name` for block). Custom patterns are ReDoS-screened at
construction time.

---

### `PromptInjection` — `enable_regex_prefilter=True`

**Built-in catalog:** 30+ patterns across direct instruction override,
developer/admin mode, prompt extraction, role manipulation, DAN-style
jailbreaks, safety bypass, tag/role spoofing, and control-token
injection. Plus evasion detectors: typoglycemia
(`"ignroe"` for `"ignore"`), Base64 decoding, hex decoding, and
character-spaced text.

**Custom patterns** (additive, ReDoS-screened):

```python
pi = guardrail.PromptInjection(
    custom_regex_patterns={
        "acme_override_token": r"acme[-_]?override[-_]?token",
    },
)
```

---

### `SecretKeys` — `enable_regex_prefilter=True`

**Built-in catalog:** OpenAI / OpenAI Project / OpenAI Service /
Anthropic / GitHub (PAT, fine-grained, OAuth, server, user, refresh) /
AWS access & session keys / Google API / Slack tokens & webhooks /
Stripe (live, test, restricted) / SendGrid / Hugging Face / JWT /
PEM private keys / `Authorization: Basic` / `Bearer ...`.

**Custom patterns** (ReDoS-screened):

```python
secrets = guardrail.SecretKeys(
    custom_patterns=[
        {
            "name": "internal_token",
            "pattern": r"INT-[A-Z0-9]{12}",
            "label": "Internal Token",   # optional
        },
    ],
)
```

**User prefix entropy filtering** — for the `key_patterns` list
(e.g. `["sk-", "ghp_"]`), the prefilter only flags a candidate if
its Shannon entropy exceeds `entropy_threshold` (default 4.0). This
prevents low-entropy false positives on common prefixes like
`"key-"` or `"token-"`.

```python
secrets = guardrail.SecretKeys(
    key_patterns=["myapp-"],
    entropy_threshold=3.0,
)
```

---

### `Jailbreak` — `enable_regex_prefilter=True`

**Built-in catalog:** 17 patterns covering `DAN` / `AIM` / `AntiGPT` /
`DUDE` / developer mode, role-play bypass templates (`pretend you
are an X with no rules`, `act as ... without restrictions`, `you
are now unrestricted`), hypothetical-unrestricted framing, evil
confidant, identity hijack (`from now on respond as ...`), safety-
training override, translation-bypass, code-only response, and token-
reward systems.

Jailbreak has no custom-pattern field; the built-in catalog is the
only thing the prefilter matches.

```python
jailbreak = guardrail.Jailbreak()        # prefilter on
jailbreak = guardrail.Jailbreak(enable_regex_prefilter=False)  # LLM-only
```

---

### `Keywords` — `enable_regex_prefilter=True`

The prefilter simply **compiles the user-supplied `blocked_keywords`
list** as regex (case-insensitive by default, with `\b` word
boundaries by default).

**Wildcards** (opt-in via `use_wildcards=True`): `*` → `.*`, `?` → `.`.

```python
keywords = guardrail.Keywords(
    blocked_keywords=["fo*bar", "crash?"],  # fo*bar, crash?
    use_wildcards=True,
    word_boundary=True,                    # \b...\b around each keyword
    case_sensitive=False,
)
```

If `word_boundary=True` (the default), `spam` matches
`"spam is bad"` but not `"spamming"`. Disable with
`word_boundary=False` if you want substring matching.

---

### `Gibberish` — `enable_regex_prefilter=True`

**Score-based** prefilter combining surface regex signals and
structural heuristics:

| Signal | Weight |
|---|---|
| All-consonant run (8+ chars) | 0.7 |
| QWERTY top row (5+ chars) | 0.25 |
| ASDF home row (5+ chars) | 0.25 |
| ZXCV bottom row (5+ chars) | 0.25 |
| Single char repeated 6+ times | 0.4 |
| Punctuation spam (5+) | 0.3 |
| Vowel ratio < 0.10 on 30+ char text (bonus) | +0.5 |
| No whitespace on 30+ char text (bonus) | +0.4 |

Score is capped at 1.0. Short text (< 10 chars) always scores 0.
The guardrail flags when score ≥ `prob_threshold` (default 0.5).

Gibberish has no custom-pattern field.

---

### `Language` — `enable_script_prefilter=True`

The prefilter does **Unicode script detection**, not true language
identification. It short-circuits when the input's dominant script
(CJK, Cyrillic, Arabic, Hebrew, Devanagari, Thai, Greek, Hangul,
Hiragana/Katakana) is unambiguously outside `allowed_languages`.
**Latin-script input always falls through to the LLM** (it covers
100+ languages).

```python
lang = guardrail.Language(allowed_languages=["en", "es", "fr"])
# Chinese input -> blocked by script prefilter
# Russian input -> blocked by script prefilter
# French input  -> falls through to LLM (Latin script)
```

If you also allow `zh` / `ja` / `ko`, CJK input falls through for
the LLM to disambiguate.

---

### `Toxicity` — `enable_regex_prefilter=True`

**Conservative, opt-out-by-default-disabled** is **not** the case —
it's on by default, but the catalog is intentionally small. Only
unambiguous, severe cases trigger the prefilter:

- Explicit threats of violence (`I will kill you`)
- Self-harm encouragement (`kys`, `go die`)
- Common obfuscated variants of severe slurs
- Sexual violence references
- Drug-use encouragement
- Doxxing indicators

Mild profanity (`"shit"`, `"damn"`, `"hell"`) is **not** flagged by
the prefilter — the LLM handles it. This catalog has high precision
and low recall on purpose; false positives on this category are very
expensive.

Toxicity has no custom-pattern field. Disable with
`enable_regex_prefilter=False` if you want the LLM to handle
everything.

---

### `Topic` — `enable_blocked_topic_prefilter=True`

**Partial** prefilter: it only checks `blocked_topics` as
case-insensitive substrings. It does **not** evaluate
`topic_scopes` — that requires the LLM.

```python
topic = guardrail.Topic(
    topic_scopes=["E-commerce", "Retail"],
    blocked_topics=["Amazon", "Walmart"],
)
# "I love shopping on Amazon" -> blocked by prefilter (substring match)
# "Explain how photosynthesis works" -> falls through to LLM
#   (off-topic but no blocked keyword)
```

The prefilter catches blocked-topic mentions early and skips the
LLM; everything else still goes through the model.

---

## Custom-Pattern Reference

`Pii` and `SecretKeys` accept a `custom_patterns` list. `PromptInjection`
takes a `custom_regex_patterns` dict.

**Schema:**

```python
# Pii
custom_patterns=[
    {
        "name":   str,    # required, used in metadata["matches"]
        "pattern": str,   # required, valid re.Pattern string
        "action":  "redact" | "block",   # required
        "label":   str,   # optional; used in reason / as redaction placeholder
    },
    ...
]

# SecretKeys
custom_patterns=[
    {
        "name":   str,
        "pattern": str,
        "label":   str,   # optional
    },
    ...
]

# PromptInjection
custom_regex_patterns={
    "name":   r"pattern",
    ...
}
```

**Action semantics (Pii only):**

| Action | `is_allowed` | `metadata["redacted_text"]` | Used when |
|---|---|---|---|
| `redact` | `True` | set (input with matches replaced) | you want the request to continue with PII removed |
| `block`  | `False` | not set | you want the request rejected outright |

**ReDoS safety:** all custom patterns are screened at construction
time. Patterns containing nested quantifiers (`(a+)+`), overlapping
alternations under a quantifier (`(a|b)+`), or other catastrophic
shapes are rejected with `ValueError`.

```python
guardrail.Pii(
    custom_patterns=[
        {"name": "bad", "pattern": r"(a+)+", "action": "redact"},
    ],
)
# ValueError: custom_patterns['bad'].pattern is rejected:
# contains nested quantifiers or overlapping alternations
# that could cause catastrophic backtracking (ReDoS)
```

## Inspecting Results

Every `GuardrailResult` exposes the path it took:

```python
result = gr.check("some text")
md = result.metadata or {}

md.get("method")         # "regex_prefilter" or "dspy"
md.get("action")         # "redact", "block", or None
md.get("matches")        # list of prefilter hits (prefilter path)
md.get("redacted_text")  # modified text (PII redact only)
```

When the prefilter short-circuits, `result.reason` is set to a
human-readable summary (e.g. `"PII detected (blocked): [SSN]"` or
`"PII redacted: email"`).

## Running Multiple Guardrails in Parallel

`guardrail.Run()` can fan guardrails out concurrently using a
`ThreadPoolExecutor`. Each text's guardrail fan-out runs on its own
thread, so a bulk check with N guardrails takes roughly the time of
the slowest single guardrail, not the sum of all of them.

```python
result = guardrail.Run(
    [pii_gr, secret_keys_gr, prompt_injection_gr],
    "Email me at user@example.com",
    parallel=True,                 # opt-in (default: sequential)
    num_threads=8,                 # optional thread pool size
)
```

Notes:

- `parallel=True` only affects the aggregated path (multiple
  guardrails or multiple texts). The single-guardrail/single-text
  fast path is unchanged.
- With `parallel=True` and `early_return=True`, all guardrails
  still execute (they run concurrently); the aggregated result
  reflects the first failure, and processing stops at the first
  text that has any failure.
- The aggregated result's metadata includes `parallel` and
  `num_threads` so you can verify the path that handled the
  request.
