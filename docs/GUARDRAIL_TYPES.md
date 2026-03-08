# Guardrail Types

This project includes twelve different types of guardrails, each addressing specific content moderation and security needs.

## Topic Compliance

Ensures content stays within defined topic scopes and flags undesirable topics.

**Features:**
- Configurable topic scopes and blocked topic lists
- Boolean flagging with detailed reasoning
- Integration with topic context validation

**Use Case:** Perfect for customer service bots, content filtering, and brand protection.

## Toxicity Detection

Detects and flags toxic, insulting, or harmful language.

**Features:**
- Configurable toxicity threshold (0.0-1.0)
- Granular toxicity type detection (insult, threat, etc.)
- Chain-of-Thought reasoning for assessments

**Use Case:** Community moderation, chat application safety, and content filtering.

## Grounding (Hallucination Detection)

Ensures that AI-generated answers are grounded in and supported by a provided context.

**Features:**
- Factual verification against source context
- Specific hallucination claim detection
- Grounding score calculation (0.0-1.0)

**Use Case:** RAG systems, fact-checking, and preventing AI hallucinations.

## NSFW Content Detection

Detects and flags Not Safe For Work content across multiple categories.

**Categories Covered:**
- Sexual content and explicit material
- Hate speech and discriminatory language
- Violence and gore
- Illegal activities
- Adult themes and mature content

**Use Case:** Content moderation for social platforms, forums, and user-generated content.

## Jailbreak Detection

Advanced detection system for adversarial jailbreak attempts using comprehensive taxonomy.

**Detection Techniques:**
- Character-level obfuscation (encoding, transliteration)
- Competing objectives and instruction override
- Lexical and semantic obfuscation
- Context-level manipulation
- Multi-turn escalation patterns

**Use Case:** Protecting AI systems from sophisticated bypass attempts and adversarial attacks.

## PII Detection

Comprehensive Personally Identifiable Information detection with global coverage.

**Supported Entities:**
- **Global:** Credit cards, emails, IP addresses, phone numbers
- **USA:** SSN, driver licenses, passports, bank numbers
- **UK:** NHS numbers, National Insurance numbers
- **Spain:** NIF, NIE
- **Italy:** Fiscal codes, VAT codes, identity cards
- **Poland:** PESEL, NIP

**Use Case:** Data privacy compliance, GDPR protection, and sensitive information filtering.

## Prompt Injection Detection

Security-focused detection of prompt injection attacks in LLM-based tool use.

**Detection Focus:**
- Tool calls with malicious arguments
- Instructions that override user goals
- Attempts to exfiltrate secrets
- Commands that ignore safety policies

**Use Case:** Securing AI agents and tool-using systems from manipulation attacks.

## Gibberish Detection

Detects nonsensical, random, or low-quality text.

**Features:**
- Probability-based gibberish scoring
- Random character string detection
- Repetitive loop and "word salad" identification

**Use Case:** Input sanitization, model output quality control, and spam filtering.

## Language Detection

Ensures content is in an allowed language and detects the input language.

**Features:**
- ISO 639-1 language code detection
- Configurable allowed language list
- Language verification for multi-lingual apps

**Use Case:** Global applications, language-specific filtering, and linguistic compliance.

## Tone and Sentiment

Ensures content matches desired tone guidelines and lacks unwanted tones.

**Features:**
- Configurable desired tone (e.g., helpful, polite)
- Blocklist for unwanted tones (e.g., aggressive, sarcastic)
- Detailed tone assessment reasoning

**Use Case:** Brand voice alignment, customer service quality assurance, and community standards.

## Keyword Filtering

Unicode-aware keyword filtering with precise word boundary detection.

**Features:**
- Configurable keyword lists
- Unicode character support
- Word boundary detection
- Dataclass-based configuration

**Use Case:** Basic content filtering, profanity detection, and custom keyword blocking.

## Secret Keys Detection

Advanced detection of API keys, tokens, and other sensitive credentials.

**Detection Patterns:**
- Common key prefixes (sk-, pk_, AKIA, etc.)
- Configurable threshold levels (strict, balanced, permissive)
- File extension awareness
- Custom regex support

**Use Case:** Preventing accidental exposure of API keys, tokens, and other credentials.
