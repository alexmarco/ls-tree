"""pytest configuration for trxd."""

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_tree(temp_dir: Path) -> Path:
    """Create an example directory structure for tests."""
    # Crear estructura de directorios
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "components").mkdir()
    (temp_dir / "src" / "utils").mkdir()
    (temp_dir / "docs").mkdir()

    # Create files
    (temp_dir / "README.md").write_text("# Proyecto de prueba")
    (temp_dir / "src" / "main.py").write_text("print('Hello World')")
    (temp_dir / "src" / "components" / "Button.py").write_text("class Button: pass")
    (temp_dir / "src" / "components" / "Header.py").write_text("class Header: pass")
    (temp_dir / "src" / "utils" / "helpers.py").write_text("def helper(): pass")
    (temp_dir / "docs" / "manual.pdf").write_text("PDF content")

    # Create files that will be excluded in the tests
    (temp_dir / "src" / "__pycache__").mkdir()
    (temp_dir / "src" / "__pycache__" / "main.pyc").write_text("compiled")
    (temp_dir / "src" / "main.pyc").write_text("compiled")
    (temp_dir / "node_modules").mkdir()
    (temp_dir / "node_modules" / "package").mkdir()
    (temp_dir / ".git").mkdir()
    (temp_dir / ".git" / "config").write_text("git config")

    return temp_dir
