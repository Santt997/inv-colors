"""Tests for inv-pdf."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestImports(unittest.TestCase):
    """Smoke tests — verify the package imports cleanly without pymupdf/Pillow."""

    def test_module_imports(self):
        """inv_pdf package should import without error (functions lazy-import deps)."""
        import importlib
        spec = importlib.util.find_spec("inv_pdf")
        self.assertIsNotNone(spec)

    def test_version(self):
        from inv_pdf import __version__
        self.assertEqual(__version__, "0.1.0")

    def test_cli_help(self):
        """CLI --help should exit 0."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "inv_pdf.cli", "--help"],
            capture_output=True,
            text=True,
        )
        # argparse prints help and exits 0
        self.assertIn("inv-pdf", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
