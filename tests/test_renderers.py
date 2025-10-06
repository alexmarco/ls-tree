"""Tests for the render functions."""

import argparse
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from trxd import build_tree, render_flat, render_tree


class TestRenderFlat:
    """Tests for the render_flat function."""

    def test_render_flat_basic(self, sample_tree: Path) -> None:
        """Test basic rendering in flat format."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree)
            output = mock_stdout.getvalue()

        # Verify that directories and files are included
        assert "src" in output
        assert "src\\main.py" in output or "src/main.py" in output
        assert "src\\components" in output or "src/components" in output
        assert "src\\components\\Button.py" in output or "src/components/Button.py" in output
        assert "src\\components\\Header.py" in output or "src/components/Header.py" in output
        assert "src\\utils" in output or "src/utils" in output
        assert "src\\utils\\helpers.py" in output or "src/utils/helpers.py" in output
        assert "docs" in output
        assert "docs\\manual.pdf" in output or "docs/manual.pdf" in output

    def test_render_flat_with_metadata(self, sample_tree: Path) -> None:
        """Test flat rendering with metadata."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=True)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree, show_metadata=True)
            output = mock_stdout.getvalue()

        # Verify that metadata is included
        assert "[" in output  # Metadata in format [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_render_flat_with_exclusions(self, sample_tree: Path) -> None:
        """Test flat rendering with exclusions."""
        args = argparse.Namespace(
            exclude=["*.pyc"],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[],
            show_metadata=False,
        )

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree)
            output = mock_stdout.getvalue()

        # Verify that files and directories are excluded
        assert "main.pyc" not in output
        assert "__pycache__" not in output
        assert "node_modules" not in output
        assert ".git" not in output

        # Verify that valid files are included
        assert "main.py" in output
        assert "Button.py" in output

    def test_render_flat_empty_directory(self, temp_dir: Path) -> None:
        """Test flat rendering in empty directory."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, temp_dir)
            output = mock_stdout.getvalue()

        # Should show only the root directory (may be empty)
        assert output.strip() == "." or output.strip() == ""

    def test_render_flat_single_file(self, temp_dir: Path) -> None:
        """Test flat rendering with a single file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, temp_dir)
            output = mock_stdout.getvalue()

        # Should show the directory and the file
        assert "test.txt" in output

    def test_render_flat_relative_paths(self, sample_tree: Path) -> None:
        """Test that relative paths are shown correctly."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree)
            output = mock_stdout.getvalue()

        # Verify that absolute paths are not included
        assert str(sample_tree) not in output
        # Verify that relative paths are included
        assert "src" in output
        assert "src\\main.py" in output or "src/main.py" in output


class TestRenderTree:
    """Tests for the render_tree function."""

    def test_render_tree_basic(self, sample_tree: Path) -> None:
        """Test basic rendering in tree format."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verify that elements of the tree are included
        assert "📁" in output  # Directory emoji
        assert "🐍" in output  # Python emoji
        assert "├──" in output  # Tree connectors
        assert "└──" in output  # Tree connectors
        assert "src" in output
        assert "main.py" in output

    def test_render_tree_no_emoji(self, sample_tree: Path) -> None:
        """Test tree rendering without emojis."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=False)
            output = mock_stdout.getvalue()

        # Verify that emojis are not included
        assert "📁" not in output
        assert "🐍" not in output
        # Verify that ASCII markers are included
        assert "[d]" in output  # Directory marker
        assert "[f]" in output  # File marker
        assert "├──" in output  # Tree connectors
        assert "└──" in output  # Tree connectors

    def test_render_tree_with_metadata(self, sample_tree: Path) -> None:
        """Test tree rendering with metadata."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=True)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True, show_metadata=True)
            output = mock_stdout.getvalue()

        # Verify that metadata is included
        assert "[" in output  # Metadata in format [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_render_tree_with_exclusions(self, sample_tree: Path) -> None:
        """Test tree rendering with exclusions."""
        args = argparse.Namespace(
            exclude=["*.pyc"],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[],
            show_metadata=False,
        )

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verify that files and directories are excluded
        assert "main.pyc" not in output
        assert "__pycache__" not in output
        assert "node_modules" not in output
        assert ".git" not in output

        # Verify that valid files are included
        assert "main.py" in output
        assert "Button.py" in output

    def test_render_tree_empty_directory(self, temp_dir: Path) -> None:
        """Test tree rendering in empty directory."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Should show only the root directory (may be empty)
        assert "📁" in output or "[d]" in output or output.strip() == ""

    def test_render_tree_single_file(self, temp_dir: Path) -> None:
        """Test tree rendering with a single file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Should show the directory and the file
        assert "test.txt" in output
        # In directory with a single file, the root directory may not be shown
        assert "📄" in output or "[f]" in output

    def test_render_tree_nested_structure(self, temp_dir: Path) -> None:
        """Test tree rendering with nested structure."""
        # Crear estructura anidada
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()

        # Create files at different levels
        (temp_dir / "root.txt").write_text("root")
        (temp_dir / "level1" / "level1.txt").write_text("level1")
        (temp_dir / "level1" / "level2" / "level2.txt").write_text("level2")

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verify that all levels are included
        assert "level1" in output
        assert "level2" in output
        assert "root.txt" in output
        assert "level1.txt" in output
        assert "level2.txt" in output

        # Verify tree connectors
        assert "├──" in output
        assert "└──" in output
        assert "│   " in output  # Indentation

    def test_render_tree_file_types(self, temp_dir: Path) -> None:
        """Test tree rendering with different file types."""
        # Create files of different types
        (temp_dir / "script.py").write_text("print('hello')")
        (temp_dir / "style.css").write_text("body { color: red; }")
        (temp_dir / "index.html").write_text("<html></html>")
        (temp_dir / "data.json").write_text('{"key": "value"}')
        (temp_dir / "image.png").write_text("fake png")

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verify that specific emojis are included for each type
        assert "🐍" in output  # Python
        assert "🎨" in output  # CSS
        assert "🌐" in output  # HTML
        assert "📋" in output  # JSON
        assert "🖼️" in output  # PNG

    def test_render_tree_relative_paths(self, sample_tree: Path) -> None:
        """Test that relative paths are shown correctly."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verify that absolute paths are not included
        assert str(sample_tree) not in output
        # Verify that relative paths are included
        assert "src" in output
        assert "main.py" in output
