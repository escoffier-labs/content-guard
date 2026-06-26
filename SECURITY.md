# Security Policy

## Supported versions

content-guard is pre-1.0; security fixes land on the latest version. Please
upgrade before reporting.

## Reporting a vulnerability

Report privately, not in a public issue:

- GitHub: **Security → Report a vulnerability** (private advisory) on this repo, or
- contact the maintainer privately via [@solomonneas](https://github.com/solomonneas)

For a guard, the vulnerability that matters most is a **bypass**: content that
*should* be flagged (a secret, a private host, a PII pattern) but is missed, or a
redaction that leaves the original value recoverable. Include the input that
should have been caught and the policy you used. **Redact the real value** if it
is an actual secret; a minimal synthetic reproduction is ideal.

## Scope

In scope: the scanner rules, the bundled policies, redaction, the report and
exit-code contract, and the allow/baseline mechanisms.

Out of scope: the optional OPF backend (report to its own project), and content
you explicitly allowed.

## What content-guard is and is not

content-guard is a guardrail, not a guarantee. It catches the patterns it knows.
A clean scan means "no known pattern matched," not "safe to publish." Pair it
with human review for anything sensitive.
