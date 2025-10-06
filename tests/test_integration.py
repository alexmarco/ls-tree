"""Integration tests for trxd."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


class TestIntegration:
    """Integration tests for trxd."""

    def test_cli_basic_usage(self, sample_tree: Path) -> None:
        """Test basic CLI usage."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=sample_tree.parent,
        )

        assert result.returncode == 0
        assert "src" in result.stdout
        assert "main.py" in result.stdout
        assert "📁" in result.stdout  # Default emojis

    def test_cli_help(self) -> None:
        """Test that the help is shown correctly."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "List the contents of a directory" in result.stdout
        assert "--format" in result.stdout
        assert "--exclude" in result.stdout

    def test_cli_invalid_directory(self) -> None:
        """Test handling of invalid directory."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "/nonexistent/directory"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 1
        assert "is not a valid directory" in result.stderr

    def test_cli_tree_format(self, sample_tree: Path) -> None:
        """Test tree format."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--format", "tree", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "📁" in result.stdout
        assert "├──" in result.stdout
        assert "└──" in result.stdout

    def test_cli_ascii_format(self, sample_tree: Path) -> None:
        """Test ASCII format."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--format", "ascii", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout
        assert "[d]" in result.stdout
        assert "[f]" in result.stdout

    def test_cli_flat_format(self, sample_tree: Path) -> None:
        """Test flat format."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--format", "flat", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout
        assert "├──" not in result.stdout
        assert "src" in result.stdout
        assert "main.py" in result.stdout

    def test_cli_json_format(self, sample_tree: Path) -> None:
        """Test JSON format."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--format", "json", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0

        # Verify that it is valid JSON
        try:
            json_data = json.loads(result.stdout)
            assert isinstance(json_data, dict)
            assert "src" in json_data
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_cli_yaml_format(self, sample_tree: Path) -> None:
        """Test YAML format."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--format", "yaml", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0

        # Verify that it is valid YAML
        try:
            yaml_data = yaml.safe_load(result.stdout)
            assert isinstance(yaml_data, dict)
            assert "src" in yaml_data
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_cli_no_emoji(self, sample_tree: Path) -> None:
        """Test --no-emoji option."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--no-emoji", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout
        assert "[d]" in result.stdout

    def test_cli_show_metadata(self, sample_tree: Path) -> None:
        """Test --show-metadata option."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", "--show-metadata", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "[" in result.stdout  # Metadata
        assert "files" in result.stdout

    def test_cli_exclude_patterns(self, sample_tree: Path) -> None:
        """Test exclusion patterns."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "trxd",
                "--exclude",
                "*.pyc",
                "--exclude-dir",
                "__pycache__",
                str(sample_tree),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "main.pyc" not in result.stdout
        assert "__pycache__" not in result.stdout
        assert "main.py" in result.stdout

    def test_cli_multiple_exclusions(self, sample_tree: Path) -> None:
        """Test multiple exclusions."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "trxd",
                "-x",
                "*.pyc",
                "-x",
                "*.pyo",
                "-xd",
                "__pycache__",
                "-xd",
                "node_modules",
                str(sample_tree),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "main.pyc" not in result.stdout
        assert "main.pyo" not in result.stdout
        assert "__pycache__" not in result.stdout
        assert "node_modules" not in result.stdout
        assert "main.py" in result.stdout

    def test_cli_json_with_metadata(self, sample_tree: Path) -> None:
        """Test JSON format with metadata."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "trxd",
                "--format",
                "json",
                "--show-metadata",
                str(sample_tree),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0

        # Verify that it is valid JSON with metadata
        try:
            json_data = json.loads(result.stdout)
            assert isinstance(json_data, dict)

            # Verify that metadata is included
            if "_metadata" in json_data:
                metadata = json_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_cli_yaml_with_metadata(self, sample_tree: Path) -> None:
        """Test YAML format with metadata."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "trxd",
                "--format",
                "yaml",
                "--show-metadata",
                str(sample_tree),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0

        # Verify that it is valid YAML with metadata
        try:
            yaml_data = yaml.safe_load(result.stdout)
            assert isinstance(yaml_data, dict)

            # Verify that metadata is included
            if "_metadata" in yaml_data:
                metadata = yaml_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_cli_combined_options(self, sample_tree: Path) -> None:
        """Test combination of multiple options."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "trxd",
                "--format",
                "tree",
                "--no-emoji",
                "--show-metadata",
                "--exclude",
                "*.pyc",
                str(sample_tree),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout  # No emojis
        assert "[d]" in result.stdout  # ASCII markers
        assert "[f]" in result.stdout  # ASCII markers
        assert "[" in result.stdout  # Metadata
        assert "files" in result.stdout  # Metadata
        assert "main.pyc" not in result.stdout  # Excluded
        assert "main.py" in result.stdout  # Included

    def test_cli_current_directory(self, sample_tree: Path) -> None:
        """Test that the current directory is used by default."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=sample_tree,
        )

        assert result.returncode == 0
        assert "src" in result.stdout or "main.py" in result.stdout

    def test_cli_empty_directory(self, temp_dir: Path) -> None:
        """Test empty directory."""
        result = subprocess.run(
            [sys.executable, "-m", "trxd", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        # Should show only the root directory
        assert len(result.stdout.strip().split("\n")) <= 1

    def test_cli_single_file(self, temp_dir: Path) -> None:
        """Test directory with a single file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        result = subprocess.run(
            [sys.executable, "-m", "trxd", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "test.txt" in result.stdout

    def test_cli_nested_structure(self, temp_dir: Path) -> None:
        """Test nested structure."""
        # Crear estructura anidada
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()

        # Create files at different levels
        (temp_dir / "root.txt").write_text("root")
        (temp_dir / "level1" / "level1.txt").write_text("level1")
        (temp_dir / "level1" / "level2" / "level2.txt").write_text("level2")

        result = subprocess.run(
            [sys.executable, "-m", "trxd", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "level1" in result.stdout
        assert "level2" in result.stdout
        assert "root.txt" in result.stdout
        assert "level1.txt" in result.stdout
        assert "level2.txt" in result.stdout

    def test_cli_file_types(self, temp_dir: Path) -> None:
        """Test different file types."""
        # Create files of different types
        (temp_dir / "script.py").write_text("print('hello')")
        (temp_dir / "style.css").write_text("body { color: red; }")
        (temp_dir / "index.html").write_text("<html></html>")
        (temp_dir / "data.json").write_text('{"key": "value"}')

        result = subprocess.run(
            [sys.executable, "-m", "trxd", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        assert "script.py" in result.stdout
        assert "style.css" in result.stdout
        assert "index.html" in result.stdout
        assert "data.json" in result.stdout

    def test_cli_performance_large_directory(self, temp_dir: Path) -> None:
        """Test performance with large directory."""
        # Create many files and directories
        for i in range(100):
            (temp_dir / f"file_{i}.txt").write_text(f"content {i}")

        for i in range(10):
            subdir = temp_dir / f"dir_{i}"
            subdir.mkdir()
            for j in range(10):
                (subdir / f"file_{i}_{j}.txt").write_text(f"content {i}_{j}")

        result = subprocess.run(
            [sys.executable, "-m", "trxd", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        assert result.returncode == 0
        # Verify that all files are processed
        assert "file_0.txt" in result.stdout
        assert "file_99.txt" in result.stdout
        assert "dir_0" in result.stdout
        assert "dir_9" in result.stdout
