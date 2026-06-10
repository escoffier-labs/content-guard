# Hardening and Hygiene Design

Date: 2026-06-09
Status: approved

## Goal

Make the repo durable and publishable: continuous integration, zero deprecation
warnings, lint and typecheck baselines, a changelog, and clean tracking of
build artifacts. No behavior changes to the scanner or CLI.

## Scope

### 1. GitHub Actions CI

- File: `.github/workflows/ci.yml`
- Triggers: push to `main`, pull requests.
- Matrix: Python 3.11, 3.12, 3.13.
- Steps: checkout, set up Python, `pip install -e .[dev]`, `ruff check`,
  `ruff format --check`, `mypy src`, `pytest`.

### 2. Python 3.14 deprecation fix

- `src/content_guard/policy.py` imports `importlib.abc.Traversable`, which is
  deprecated and slated for removal in Python 3.14.
- Replace with `importlib.resources.abc.Traversable` (available since 3.11,
  matching `requires-python`).
- Acceptance: `pytest` runs with zero warnings.

### 3. Lint and typecheck baseline

- Add `[project.optional-dependencies] dev = ["pytest", "ruff", "mypy"]`.
- Add `[tool.ruff]` config to `pyproject.toml`; run ruff and fix findings.
- Add `[tool.mypy]` with a pragmatic baseline (not strict); fix real findings.
- Install dev tools into `.venv` so the same checks run locally and in CI.

### 4. CHANGELOG and versioning policy

- `CHANGELOG.md` in Keep a Changelog format, semver.
- Backfill 0.1.0 and 0.1.1 from git history; add Unreleased section covering
  audit/baseline subcommands, history-aware scanning, literal-value allowlist,
  rule extensions, and the OpenClaw plugin packaging work.

### 5. Repo cleanliness

- Untrack `dist/` (`git rm --cached`, add to `.gitignore`); wheel stays on disk.
- Add `.brigade/` to `.gitignore`.

## Non-goals

- PyPI release automation, pre-commit framework, coverage gates.
- Any scanner, rule, or policy behavior change.

## Verification

- `.venv/bin/pytest -q` passes with zero warnings.
- `ruff check` and `mypy src` pass locally.
- `git status` clean of artifact noise.
- Review gates per `AGENTS.md`: codex review and code-review workflow after
  local verification.
