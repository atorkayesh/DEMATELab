"""
Repository rules for `apps/api`.

Tests cover:
- Every code file is at most 300 lines
- Nothing imports or reads `qt-app/`
- `__init__.py` files hold only a docstring
"""

import ast
import unittest
from pathlib import Path

import pytest

API_ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "fixtures"}


def code_files():
    """Yield every Python file of the API (not the virtualenv or fixtures)."""
    for path in API_ROOT.rglob("*.py"):
        if not SKIP_PARTS.intersection(path.relative_to(API_ROOT).parts):
            yield path


@pytest.mark.integration
class TestRepositoryRules(unittest.TestCase):
    """Static checks of the code base."""

    def test_files_at_most_300_lines(self):
        """Test the 300-line limit."""
        long_files = [str(p) for p in code_files() if len(p.read_text(encoding="utf-8").splitlines()) > 300]
        self.assertEqual(long_files, [])

    def test_no_qt_app_references(self):
        """Test no module imports the Qt package and no string literal (outside docstrings) points into qt-app."""
        offenders = []
        for path in code_files():
            if path.name == Path(__file__).name:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            docstrings = {id(node.value) for node in ast.walk(tree) if isinstance(node, ast.Expr)}
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = [alias.name for alias in node.names] + [getattr(node, "module", None) or ""]
                    if any(name.split(".")[0] == "DEMATELab" for name in names):
                        offenders.append(f"{path}: import")
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
                    if "qt-app" in node.value:
                        offenders.append(f"{path}: {node.value[:40]}")
        self.assertEqual(offenders, [])

    def test_init_files_hold_only_a_docstring(self):
        """Test `__init__.py` files contain a docstring and nothing else."""
        for path in code_files():
            if path.name == "__init__.py":
                body = ast.parse(path.read_text(encoding="utf-8")).body
                self.assertEqual(len(body), 1, str(path))
                self.assertIsInstance(body[0].value, ast.Constant, str(path))
