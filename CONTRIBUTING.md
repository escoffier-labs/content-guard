# Contributing

Thanks for helping improve content-guard. It keeps private infrastructure,
secrets, and personal context out of public surfaces, so the bar is "catches
more, with fewer false positives, and never silently regresses."

## Local setup

```bash
python3 -m pip install -e ".[dev]"
scripts/verify          # ruff, mypy, pytest
```

## What lands easily

- A new or tightened rule **with a test** that fails before and passes after,
  covering both a true positive (it catches the bad input) and a true negative
  (it leaves a similar-but-fine input alone)
- False-positive reductions, policy fixes, documentation

## What needs a conversation first

Open an issue before a PR for:

- Changing a rule's default decision (block vs. warn) or the redaction format
- Anything that changes the report or exit-code contract that pre-push hooks and
  CI depend on

## Rules

- **Every rule change ships with tests.** A guard that regresses silently is
  worse than no guard.
- **No real secrets in tests or fixtures.** Use synthetic, obviously-fake values.
- Conventional commits, no AI co-authorship trailers.
- See [AGENTS.md](AGENTS.md) for the canonical project instructions and review gates.
