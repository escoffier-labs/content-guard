# Project Rules

- Keep the core package dependency-free unless a dependency is explicitly approved.
- Treat OpenAI Privacy Filter as inspiration and an optional runtime backend. Do not copy its implementation into this repo.
- Prefer deterministic, explainable rules for hard publish gates.
- Keep personal or environment-specific patterns in policy files, not in public default code.

## Definition of Done

Before reporting any change complete, run all four gates and re-run after the last edit:

```bash
.venv/bin/ruff check src tests
.venv/bin/ruff format --check src tests
.venv/bin/mypy src
.venv/bin/pytest -q
```

Report actual results. If anything fails, paste the failure verbatim and do not claim success. CI (`.github/workflows/ci.yml`) runs the same gates on Python 3.11/3.12/3.13.

## Rules by Trigger

- Adding or changing a rule in `src/content_guard/rules.py`: write the failing test first from a real false-positive or leak example, fix, then add a CHANGELOG entry under Unreleased.
- Rule changes that loosen matching: state in the commit message what stops matching and why that is safe.
- New CLI surface: wire it in `cli.py`, keep logic in its own module, document it in README.
- Failing test or gate: fix the cause or report the failure. Never weaken, skip, or delete a failing test to get green.
- Unknown API or behavior question: read the code first. Never invent commands or facts.
- Blocked by sandboxing, auth, or a missing tool: report the exact blocker. Do not bypass sandboxing or permissions without explicit approval.

## Review Gates

- For substantive code changes, run the smallest meaningful local verification first.
- After local verification passes, run `codex-review-bounded` (in `~/bin`; wraps `codex review` with a hard timeout because Codex hangs when rate-limited). On exit 75, fall back to the Claude Code `code-review` workflow and note the skipped gate.
- Treat external review output as read-only input. Apply fixes intentionally in the main workspace and re-run local verification.

## Publishing Boundaries

- PR bodies must go through `content_guard.pr_prepare` before a public PR create or update command uses them.
- Public repo file checks must run through `content_guard.git_scan`.
- Commit-message checks must run through `content_guard.git_commits`, because staged-file scans cannot see Git metadata such as co-author trailers.
- Never push with `--no-verify`. If the pre-push hook blocks, fix the content, or use `content-guard allow add "<exact string>" --note "<why public>"` for known-public literals.
- OpenClaw outbound-message guarding must remain single-owner. Do not enable the Content Guard OpenClaw plugin while another overlapping scrubber is active.

## Memory Handoff

At the end of any substantial task, write a handoff note to `.claude/memory-handoffs/` using that directory's `TEMPLATE.md`. Record durable discoveries, gotchas, and decisions. Do not wait to be reminded.
