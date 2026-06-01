from __future__ import annotations

# This file uses illustrative example emails (a@b.com, x@y.com, someone@else.com)
# as test data. They are not real PII, so exempt the whole file from the email
# rule for content-guard's own pre-push self-scan. This does not affect the
# scan_text() calls inside the tests, which scan Python string literals.
# content-guard: allow email file

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from content_guard.engine import scan_text
from content_guard.policy import Policy, load_policy


class AllowValuesEngineTests(unittest.TestCase):
    def test_exact_value_is_allowed_not_blocked(self) -> None:
        policy = Policy(defaults={"pii": "block"}, allow_values=["srneas@gmail.com"])
        result = scan_text("Reach me at srneas@gmail.com please", policy=policy)

        emails = [f for f in result.findings if f.rule_id == "email"]
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0].action, "allow")
        self.assertEqual(emails[0].allowed_by, "allow-value")
        self.assertFalse(result.blocked)

    def test_non_listed_value_still_blocks(self) -> None:
        policy = Policy(defaults={"pii": "block"}, allow_values=["srneas@gmail.com"])
        result = scan_text("Reach me at someone@else.com please", policy=policy)

        emails = [f for f in result.findings if f.rule_id == "email"]
        self.assertEqual(len(emails), 1)
        self.assertNotEqual(emails[0].action, "allow")
        self.assertTrue(result.blocked)

    def test_substring_value_does_not_exempt_larger_match(self) -> None:
        # Listing a substring must NOT exempt a larger matched span: the
        # allowlist is exact-match on the whole finding text.
        policy = Policy(defaults={"pii": "block"}, allow_values=["gmail.com"])
        result = scan_text("Reach me at srneas@gmail.com please", policy=policy)

        emails = [f for f in result.findings if f.rule_id == "email"]
        self.assertEqual(len(emails), 1)
        self.assertNotEqual(emails[0].action, "allow")
        self.assertTrue(result.blocked)

    def test_allow_value_overrides_block_across_rules(self) -> None:
        policy = Policy(
            defaults={"infrastructure": "block"},
            rules={"localhost-port": "block"},
            allow_values=["localhost:11434"],
        )
        result = scan_text("ollama at localhost:11434/api", policy=policy)

        ports = [f for f in result.findings if f.rule_id == "localhost-port"]
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0].action, "allow")
        self.assertFalse(result.blocked)


class AllowValuesPolicyTests(unittest.TestCase):
    def _write(self, tmp: str, payload: dict) -> Path:
        path = Path(tmp) / "policy.json"
        path.write_text(json.dumps(payload))
        return path

    def test_load_policy_parses_allow_values(self) -> None:
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, {"name": "x", "allow_values": ["a@b.com", "localhost:11434"]})
            policy = load_policy(path)
            self.assertEqual(policy.allow_values, ["a@b.com", "localhost:11434"])

    def test_allow_values_absent_defaults_empty(self) -> None:
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, {"name": "x"})
            self.assertEqual(load_policy(path).allow_values, [])

    def test_allow_values_must_be_list(self) -> None:
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, {"allow_values": "a@b.com"})
            with self.assertRaises(ValueError):
                load_policy(path)

    def test_allow_values_entries_must_be_nonempty_strings(self) -> None:
        with TemporaryDirectory() as tmp:
            path = self._write(tmp, {"allow_values": ["ok", ""]})
            with self.assertRaises(ValueError):
                load_policy(path)


class AllowValuesFromMergeTests(unittest.TestCase):
    def test_merge_extends_policy_allow_values(self) -> None:
        from content_guard.git_scan import _merge_allow_values_from

        with TemporaryDirectory() as tmp:
            extra = Path(tmp) / "internal.json"
            extra.write_text(json.dumps({"allow_values": ["x@y.com"]}))
            policy = Policy(allow_values=["a@b.com"])
            _merge_allow_values_from(policy, [str(extra)])
            self.assertIn("a@b.com", policy.allow_values)
            self.assertIn("x@y.com", policy.allow_values)

    def test_merge_is_noop_for_missing_file(self) -> None:
        from content_guard.git_scan import _merge_allow_values_from

        policy = Policy(allow_values=["a@b.com"])
        _merge_allow_values_from(policy, ["/nonexistent/internal.json"])
        self.assertEqual(policy.allow_values, ["a@b.com"])


if __name__ == "__main__":
    unittest.main()
