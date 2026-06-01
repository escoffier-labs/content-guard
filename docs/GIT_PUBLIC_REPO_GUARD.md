# Git Public Repo Guard

Public repositories need guarding around more than PR bodies.

Content Guard should protect:

- staged files before commit
- commit messages before push
- tracked files before first public push
- generated PR bodies
- release notes and changelogs
- examples, fixtures, docs, and test data
- optional Git config review for tokenized remotes

Do not scan raw `.git/objects` as normal content. It is a compressed object database, can contain historical content, and will create noise. Guard the public surfaces that leave the machine: tracked files, staged diffs, PR text, and release artifacts.

## Publish Check Wrapper

For the normal PR or repo publish path, run the combined wrapper first:

```bash
PYTHONPATH=src python3 -m content_guard.publish_check \
  --pr-body pr-body.md \
  --json
```

This prepares a sanitized PR body, scans staged files, and scans commit messages. Add `--all-tracked` before the first public push or when checking a cleanup branch:

```bash
PYTHONPATH=src python3 -m content_guard.publish_check \
  --pr-body pr-body.md \
  --all-tracked
```

The command fails on blocked staged files, blocked commit messages, or blocked all-tracked findings. PR body blockers remain advisory by default because the wrapper writes a sanitized body and prints `publish_body_file`. Use `--advisory-only` to collect the same report without a nonzero exit.

## Staged Files

Before commit:

```bash
PYTHONPATH=src python3 -m content_guard.git_scan \
  --policy policies/public-repo.json
```

This scans staged added, copied, modified, and renamed files.

## Commit Messages

Before pushing or opening a PR:

```bash
PYTHONPATH=src python3 -m content_guard.git_commits \
  --policy policies/public-repo.json
```

By default, this scans `@{upstream}..HEAD` when the current branch has an upstream, or `HEAD` when no upstream is configured. To scan a specific PR range:

```bash
PYTHONPATH=src python3 -m content_guard.git_commits \
  --range origin/main..HEAD \
  --policy policies/public-repo.json
```

This catches commit-message-only publishing risks such as co-author trailers. Staged-file scanning cannot see those because they live in Git metadata, not tracked file content.

## Entire Tracked Repo

Before making a repo public or pushing a cleanup branch:

```bash
PYTHONPATH=src python3 -m content_guard.git_scan \
  --all-tracked \
  --policy policies/public-repo.json
```

Use `git_commits --all` separately if the full public history also needs commit-message review:

```bash
PYTHONPATH=src python3 -m content_guard.git_commits \
  --all \
  --policy policies/public-repo.json
```

## Include Git Config

To check `.git/config` for accidentally tokenized remotes:

```bash
PYTHONPATH=src python3 -m content_guard.git_scan \
  --all-tracked \
  --include-git-config \
  --policy policies/public-repo.json
```

## Pre-Commit Hook

Local hook example:

```bash
#!/usr/bin/env bash
set -euo pipefail
PYTHONPATH=src python3 -m content_guard.git_scan \
  --policy policies/public-repo.json
PYTHONPATH=src python3 -m content_guard.git_commits \
  --policy policies/public-repo.json
```

Keep hooks local by default. The tool should protect the workflow without forcing every public contributor to install local private policies.

## Private Repo Policy

The public `public-repo.json` policy blocks generic leak classes. Use an untracked local policy for private names, internal project labels, hostnames, and business context:

```bash
PYTHONPATH=src python3 -m content_guard.git_scan \
  --policy policies/private-repo.local.json
```

Do not commit private policy files. A `*.local.json` gitignore rule guards the conventional name, but the safest habit is to keep the real file outside the repo entirely, at the pre-push hook's default path `~/.config/content-guard/internal.json`.

Start from the tracked template [`policies/private-repo.local.example.json`](../policies/private-repo.local.example.json). It documents the full schema with sanitized placeholders. Copy it, then replace the placeholder patterns with your own identifiers.

Two things in the template are easy to miss:

- **Downgrade generic infra rules to `warn`.** A private policy usually keeps `defaults.infrastructure: block` so its custom host/subnet rules block. But that broad default also re-flags ordinary `localhost`, loopback, and port references that the public policy correctly only warns. Mirror the public policy's overrides so the private scan does not false-positive on normal docs:

  ```json
  "rules": {"loopback-ipv4": "warn", "localhost-port": "warn", "localhost-bare": "warn", "port-reference": "warn"}
  ```

  Custom rules still block, because they resolve through their category defaults rather than these rule-id overrides.

- **`allow_values` for known-public literals.** Inline `content-guard: allow` markers cannot clear a history scan, because the marker does not exist in an old commit's diff. List the exact literal instead (a public author email, a standard example port) and it is allowed everywhere, including history. Exact full-string match only.

## Applying a Private Allowlist to the Public Scan

Keep personal literals out of the shipped `public-repo.json`. To let a private allowlist clear a scan that runs against the public policy, merge its `allow_values` in at scan time:

```bash
PYTHONPATH=src python3 -m content_guard.git_scan \
  --all-tracked \
  --policy policies/public-repo.json \
  --allow-values-from ~/.config/content-guard/internal.json
```

The flag is repeatable and only pulls in `allow_values` (not the rest of the policy). A missing file is skipped with a warning, so it never weakens a scan. The bundled pre-push hook passes the private file to every scan this way.

## Back Up the Private Policy

The real private policy is untracked by design, so nothing in git protects it. Include `~/.config/content-guard/` in your encrypted backup set so a machine rebuild does not lose your identifiers, allowlist, and rule overrides.
