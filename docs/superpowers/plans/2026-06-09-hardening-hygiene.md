# Hardening and Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add CI, eliminate the Python 3.14 deprecation, establish ruff and mypy baselines, add a CHANGELOG, and clean repo tracking, with zero scanner behavior changes.

**Architecture:** Pure tooling and metadata changes. The only source edits are mechanical: an import swap in five files, two `SimpleNamespace` to `argparse.Namespace` swaps, one dead variable removal, and a one-time `ruff format` pass committed in isolation.

**Tech Stack:** GitHub Actions, ruff 0.15, mypy 2.1, pytest, setuptools.

**Spec:** `docs/superpowers/specs/2026-06-09-hardening-hygiene-design.md`

**Spec deviations discovered during planning:**
- `dist/` is already gitignored and NOT tracked by git. The untrack step is a no-op and is dropped.
- There is no `v0.1.0` tag; `v0.1.1` (commit `daf4425`) is the first release. The CHANGELOG backfills 0.1.1 as the initial release plus an Unreleased section.

**Pre-verified facts (already run locally):**
- `.venv/bin/ruff check src tests` finds exactly 1 error: F841 unused `offset` at `src/content_guard/engine.py:205`.
- `.venv/bin/mypy src` (with the config below) finds exactly 2 errors: `SimpleNamespace` vs `Namespace` at `src/content_guard/n8n_validate.py:83` and `src/content_guard/publish_check.py:196`.
- `ruff format --line-length 120` reformats 10 files.
- ruff and mypy are already installed in `.venv`.

---

### Task 1: Tooling config in pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Append dev extras and tool config**

Add at the end of `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[tool.ruff]
line-length = 120
src = ["src", "tests"]

[tool.mypy]
python_version = "3.11"
warn_unused_ignores = true
warn_redundant_casts = true
no_implicit_optional = true
check_untyped_defs = true
```

- [ ] **Step 2: Verify the package still installs and tools read the config**

Run: `.venv/bin/pip install -q -e '.[dev]' && .venv/bin/ruff check src tests; .venv/bin/mypy src | tail -3`
Expected: install succeeds; ruff reports exactly 1 error (F841 in engine.py); mypy reports exactly 2 errors (n8n_validate.py:83, publish_check.py:196).

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add dev extras plus ruff and mypy config"
```

### Task 2: Fix the importlib.abc.Traversable deprecation

**Files:**
- Modify: `src/content_guard/policy.py:7`
- Modify: `src/content_guard/pr_draft.py:5`
- Modify: `src/content_guard/n8n_advisory.py:6`
- Modify: `src/content_guard/pr_prepare.py:7`
- Modify: `src/content_guard/publish_check.py:6`

- [ ] **Step 1: Confirm the warning fires today**

Run: `.venv/bin/pytest -q -W error::DeprecationWarning 2>&1 | tail -3`
Expected: FAIL (collection error on `importlib.abc.Traversable`).

- [ ] **Step 2: Swap the import in all five files**

In each of the five files listed above, replace the line:

```python
from importlib.abc import Traversable
```

with:

```python
from importlib.resources.abc import Traversable
```

- [ ] **Step 3: Verify zero warnings**

Run: `.venv/bin/pytest -q -W error::DeprecationWarning 2>&1 | tail -3`
Expected: `101 passed`, no warnings summary.

- [ ] **Step 4: Commit**

```bash
git add src/content_guard/policy.py src/content_guard/pr_draft.py src/content_guard/n8n_advisory.py src/content_guard/pr_prepare.py src/content_guard/publish_check.py
git commit -m "fix: use importlib.resources.abc.Traversable for Python 3.14"
```

### Task 3: Fix the two mypy errors

**Files:**
- Modify: `src/content_guard/n8n_validate.py` (line 7 import, line 83 call)
- Modify: `src/content_guard/publish_check.py` (line 9 import, line 196 call)

`argparse.Namespace` accepts arbitrary kwargs exactly like `SimpleNamespace`, so the call sites can construct the type the callees actually declare. Both files already import `argparse`.

- [ ] **Step 1: Fix n8n_validate.py**

Delete line 7:

```python
from types import SimpleNamespace
```

Change line 83 (inside `run_advisory_check(...)` call) from:

```python
            SimpleNamespace(policy=args.policy, opf=args.opf, opf_bin=args.opf_bin, opf_device=args.opf_device),
```

to:

```python
            argparse.Namespace(policy=args.policy, opf=args.opf, opf_bin=args.opf_bin, opf_device=args.opf_device),
```

- [ ] **Step 2: Fix publish_check.py**

Delete line 9:

```python
from types import SimpleNamespace
```

Change line 196 from:

```python
    revs = _commit_revs(SimpleNamespace(rev_range=rev_range, all=all_commits))
```

to:

```python
    revs = _commit_revs(argparse.Namespace(rev_range=rev_range, all=all_commits))
```

- [ ] **Step 3: Verify mypy is clean and tests pass**

Run: `.venv/bin/mypy src && .venv/bin/pytest -q 2>&1 | tail -2`
Expected: `Success: no issues found in 19 source files` and `101 passed`.

- [ ] **Step 4: Commit**

```bash
git add src/content_guard/n8n_validate.py src/content_guard/publish_check.py
git commit -m "fix: construct argparse.Namespace at duck-typed call sites"
```

### Task 4: Fix the ruff F841 finding

**Files:**
- Modify: `src/content_guard/engine.py:205`

- [ ] **Step 1: Remove the dead assignment**

In `_skipped_ranges`, delete line 205:

```python
    offset = 0
```

(The variable is never read; frontmatter and code block range math below use their own accumulators.)

- [ ] **Step 2: Verify ruff is clean and tests pass**

Run: `.venv/bin/ruff check src tests && .venv/bin/pytest -q 2>&1 | tail -2`
Expected: `All checks passed!` and `101 passed`.

- [ ] **Step 3: Commit**

```bash
git add src/content_guard/engine.py
git commit -m "chore: drop unused offset variable in engine"
```

### Task 5: One-time format pass (isolated commit)

**Files:**
- Modify: ~10 files under `src/` and `tests/` (mechanical reformat only)

- [ ] **Step 1: Format**

Run: `.venv/bin/ruff format src tests`
Expected: `10 files reformatted` (count may differ by a couple after Tasks 2-4).

- [ ] **Step 2: Verify nothing broke**

Run: `.venv/bin/ruff check src tests && .venv/bin/mypy src && .venv/bin/pytest -q 2>&1 | tail -2`
Expected: all clean, `101 passed`.

- [ ] **Step 3: Commit formatting alone**

```bash
git add -u src tests
git commit -m "style: apply ruff format"
```

### Task 6: CHANGELOG.md

**Files:**
- Create: `CHANGELOG.md`

- [ ] **Step 1: Write the changelog**

```markdown
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `audit` and `baseline` CLI subcommands for repo-wide review workflows.
- History-aware scanning so previously scrubbed content stays scrubbed.
- Literal-value allowlist (`allow_values`) for known-public strings.
- File-scoped allow comments, example-pattern downgrades, and a `known_hosts` policy.
- Rule-level action defaults that override category defaults.
- Publishable OpenClaw plugin package (`@solomonneas/content-guard`) with ClawHub compatibility fields.
- `content-guard` pre-push hook.
- Private policy template (`policies/private-repo.local.example.json`) and documentation.

### Changed

- `example-email-reserved` now also covers `.test`, `.local`, and `.invalid` TLDs.
- Scanner skips `node_modules` and other generated directories.

### Fixed

- `api-key-assignment` false positive.

## [0.1.1] - 2026-04-28

Initial release.

### Added

- Core deterministic scan engine with `scan`, `redact`, and `diff` CLI commands.
- Policy JSON model: category defaults, per-rule overrides, custom rules, allow comments.
- Built-in rules for infrastructure, secrets, email, and phone patterns, including
  the `private-ipv4` / `loopback-ipv4` split.
- Optional OPF model-backed PII backend via subprocess adapter.
- PR guards: `content-guard-pr`, `content-guard-pr-prepare`, `content-guard-publish-check`.
- Git guards: `content-guard-git`, `content-guard-commits`.
- n8n advisory guard, workflow recipe, and validation pack.
- Bundled policies for public repos, public content, PR drafts, and OpenClaw messages.
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add changelog with versioning policy"
```

### Task 7: Ignore .brigade/

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Append to .gitignore**

Add at the end of `.gitignore`:

```
# Local operator-report artifacts
.brigade/
```

- [ ] **Step 2: Verify**

Run: `git status --short`
Expected: `.brigade/` no longer listed.

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: ignore local .brigade report artifacts"
```

### Task 8: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install
        run: python -m pip install -e '.[dev]'
      - name: Lint
        run: ruff check src tests
      - name: Format check
        run: ruff format --check src tests
      - name: Typecheck
        run: mypy src
      - name: Test
        run: pytest -q -W error::DeprecationWarning
```

- [ ] **Step 2: Replicate the CI steps locally**

Run: `.venv/bin/ruff check src tests && .venv/bin/ruff format --check src tests && .venv/bin/mypy src && .venv/bin/pytest -q -W error::DeprecationWarning 2>&1 | tail -2`
Expected: all clean, `101 passed`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add lint, typecheck, and test workflow"
```

### Task 9: Final verification and review gates

- [ ] **Step 1: Full local verification**

Run: `.venv/bin/ruff check src tests && .venv/bin/ruff format --check src tests && .venv/bin/mypy src && .venv/bin/pytest -q -W error::DeprecationWarning 2>&1 | tail -2`
Expected: all clean, `101 passed`.

- [ ] **Step 2: Review gates per AGENTS.md**

Run `codex review --uncommitted` if the Codex CLI is available (changes are committed, so use `codex review` against the branch range if needed). Run the Claude Code code-review workflow. Treat output as read-only input; apply fixes intentionally, then re-run Step 1.

- [ ] **Step 3: Report**

Summarize commits, verification output, and review findings. Do not push without explicit approval.
