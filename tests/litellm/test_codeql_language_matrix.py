"""Check the backport and Rust-bearing CodeQL source inventories."""

import importlib.util
from pathlib import Path
import unittest

SCRIPT_PATH = Path(__file__).parents[2] / ".github/scripts/codeql_language_matrix.py"
SPEC = importlib.util.spec_from_file_location("codeql_language_matrix", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LanguageMatrixTests(unittest.TestCase):
    """Language selection must depend on tracked source, not branch naming."""

    def test_backport_languages(self):
        """Preserve Python, JavaScript, Go and Ruby without nonexistent Rust."""
        matrix = MODULE.language_matrix(
            ["litellm/proxy.py", "ui/page.tsx", "cookbook/main.go", "tests/spec.rb"]
        )
        self.assertEqual(
            matrix,
            {
                "include": [
                    {"language": "actions", "build-mode": "none"},
                    {"language": "javascript-typescript", "build-mode": "none"},
                    {"language": "python", "build-mode": "none"},
                    {"language": "go", "build-mode": "autobuild"},
                    {"language": "ruby", "build-mode": "none"},
                ]
            },
        )

    def test_rust_source_is_not_suppressed(self):
        """Rust-bearing revisions retain Rust while keeping Python enabled."""
        rows = MODULE.language_matrix(["src/lib.rs", "litellm/main.py"])["include"]
        self.assertIn({"language": "rust", "build-mode": "none"}, rows)
        self.assertIn({"language": "python", "build-mode": "none"}, rows)
        self.assertNotIn(
            {"language": "rust", "build-mode": "none"},
            MODULE.language_matrix(["README.rs.md"])["include"],
        )


if __name__ == "__main__":
    unittest.main()
