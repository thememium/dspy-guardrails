# Reporting a Vulnerability

To report a security vulnerability, please email boswell.labs@gmail.com.

We take security seriously and will respond to security reports within 48 hours. Please include as much detail as possible about the vulnerability, including:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

While the discovery of new vulnerabilities is rare, we also recommend always using the latest version of dspy-guardrails to ensure your application remains as secure as possible.

## Security Considerations for dspy-guardrails

As dspy-guardrails is a CLI tool that runs commands concurrently, please be aware of the following security practices:

- **Command Execution**: dspy-guardrails executes system commands. Ensure you trust the source of any dspy-guardrails commands you run.
- **File System Access**: dspy-guardrails can read from and write to the file system (for example, when commands you run do so). Be cautious when running dspy-guardrails in directories with sensitive files.

## Security Hall of Fame

We would like to thank the following security researchers for responsibly disclosing security issues to us.

*No security researchers have been added to the hall of fame yet. Will you be the first?*
