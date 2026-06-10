# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-06-10

### Added

- `audit` and `baseline` CLI subcommands for repo-wide review workflows.
- History-aware scanning so previously scrubbed content stays scrubbed.
- Literal-value allowlist (`allow_values`) for known-public strings.
- File-scoped allow comments, example-pattern downgrades, and a `known_hosts` policy.
- Rule-level action defaults that override category defaults.
- Example OpenClaw plugin adapter (`openclaw-plugin/`) that reuses the same Python engine. It is installed from source and is not published to a registry.
- `content-guard` pre-push hook.
- Private policy template (`policies/private-repo.local.example.json`) and documentation.
- Continuous integration with lint, format, typecheck, and test gates.

### Changed

- `example-email-reserved` now also covers `.test`, `.local`, and `.invalid` TLDs.
- Scanner skips `node_modules` and other generated directories.

### Fixed

- `api-key-assignment` false positive.
- Deprecated `importlib.abc.Traversable` import, removed in Python 3.14.
- `email` rule no longer matches SSH and scp remote URLs such as `git@github.com:owner/repo.git`.

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
