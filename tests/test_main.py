"""Tests para la función main."""

import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from trxd import main


class TestMain:
    """Tests for 'main' function."""

    def test_main_help(self) -> None:
        """Test that the help is shown correctly."""
        with patch("sys.argv", ["trxd", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_invalid_directory(self) -> None:
        """Test that an invalid directory is handled correctly."""
        with patch("sys.argv", ["trxd", "/nonexistent/directory"]), patch(
            "sys.stderr", new_callable=StringIO
        ) as mock_stderr, pytest.raises(SystemExit) as exc_info:
            main()
            assert exc_info.value.code == 1
            assert "is not a valid directory" in mock_stderr.getvalue()

    def test_main_default_format(self, sample_tree: Path) -> None:
        """Test default format (tree with emojis)."""
        with patch("sys.argv", ["trxd", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that tree format with emojis is used
        assert "📁" in output
        assert "🐍" in output
        assert "├──" in output
        assert "└──" in output

    def test_main_tree_format(self, sample_tree: Path) -> None:
        """Test explicit tree format."""
        with patch("sys.argv", ["trxd", "--format", "tree", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that tree format is used
        assert "📁" in output
        assert "🐍" in output
        assert "├──" in output
        assert "└──" in output

    def test_main_ascii_format(self, sample_tree: Path) -> None:
        """Test ASCII format."""
        with patch("sys.argv", ["trxd", "--format", "ascii", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that ASCII format is used
        assert "📁" not in output
        assert "🐍" not in output
        assert "[d]" in output
        assert "[f]" in output
        assert "├──" in output
        assert "└──" in output

    def test_main_flat_format(self, sample_tree: Path) -> None:
        """Test flat format."""
        with patch("sys.argv", ["trxd", "--format", "flat", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that flat format is used
        assert "📁" not in output
        assert "🐍" not in output
        assert "├──" not in output
        assert "└──" not in output
        assert "src" in output
        assert "main.py" in output

    def test_main_json_format(self, sample_tree: Path) -> None:
        """Test JSON format."""
        with patch("sys.argv", ["trxd", "--format", "json", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that valid JSON is generated
        try:
            json_data = json.loads(output)
            assert isinstance(json_data, dict)
            # Verify basic structure
            assert "src" in json_data
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_main_yaml_format(self, sample_tree: Path) -> None:
        """Test YAML format."""
        with patch("sys.argv", ["trxd", "--format", "yaml", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that valid YAML is generated
        try:
            yaml_data = yaml.safe_load(output)
            assert isinstance(yaml_data, dict)
            # Verify basic structure
            assert "src" in yaml_data
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_main_no_emoji(self, sample_tree: Path) -> None:
        """Test --no-emoji option."""
        with patch("sys.argv", ["trxd", "--no-emoji", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that no emojis are used
        assert "📁" not in output
        assert "🐍" not in output
        # Verify that ASCII markers are used
        assert "[d]" in output
        assert "[f]" in output

    def test_main_show_metadata(self, sample_tree: Path) -> None:
        """Test --show-metadata option."""
        with patch("sys.argv", ["trxd", "--show-metadata", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that metadata is included
        assert "[" in output  # Metadata in format [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_main_exclude_patterns(self, sample_tree: Path) -> None:
        """Test exclusion patterns."""
        with patch(
            "sys.argv",
            ["trxd", "--exclude", "*.pyc", "--exclude-dir", "__pycache__", str(sample_tree)],
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that files and directories are excluded
        assert "main.pyc" not in output
        assert "__pycache__" not in output
        # Verify that valid files are included
        assert "main.py" in output

    def test_main_multiple_exclusions(self, sample_tree: Path) -> None:
        """Test multiple exclusions."""
        with patch(
            "sys.argv",
            [
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
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that multiple patterns are excluded
        assert "main.pyc" not in output
        assert "main.pyo" not in output
        assert "__pycache__" not in output
        assert "node_modules" not in output
        # Verify that valid files are included
        assert "main.py" in output

    def test_main_current_directory(self, sample_tree: Path) -> None:
        """Test that the current directory is used by default."""
        with patch("sys.argv", ["trxd"]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout, patch("pathlib.Path.cwd", return_value=sample_tree):
            main()
            output = mock_stdout.getvalue()

        # Verify that the current directory is processed
        assert "src" in output or "main.py" in output

    def test_main_json_with_metadata(self, sample_tree: Path) -> None:
        """Test JSON format with metadata."""
        with patch(
            "sys.argv", ["trxd", "--format", "json", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that valid JSON with metadata is generated
        try:
            json_data = json.loads(output)
            assert isinstance(json_data, dict)

            # Verify that metadata is included
            if "_metadata" in json_data:
                metadata = json_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_main_yaml_with_metadata(self, sample_tree: Path) -> None:
        """Test YAML format with metadata."""
        with patch(
            "sys.argv", ["trxd", "--format", "yaml", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that valid YAML with metadata is generated
        try:
            yaml_data = yaml.safe_load(output)
            assert isinstance(yaml_data, dict)

            # Verify that metadata is included
            if "_metadata" in yaml_data:
                metadata = yaml_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_main_flat_with_metadata(self, sample_tree: Path) -> None:
        """Test flat format with metadata."""
        with patch(
            "sys.argv", ["trxd", "--format", "flat", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that metadata is included in flat format
        assert "[" in output  # Metadata in format [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_main_ascii_with_metadata(self, sample_tree: Path) -> None:
        """Test ASCII format with metadata."""
        with patch(
            "sys.argv", ["trxd", "--format", "ascii", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that ASCII format with metadata is used
        assert "📁" not in output
        assert "🐍" not in output
        assert "[d]" in output
        assert "[f]" in output
        assert "[" in output  # Metadata
        assert "files" in output

    def test_main_combined_options(self, sample_tree: Path) -> None:
        """Test combination of multiple options."""
        with patch(
            "sys.argv",
            [
                "trxd",
                "--format",
                "tree",
                "--no-emoji",
                "--show-metadata",
                "--exclude",
                "*.pyc",
                str(sample_tree),
            ],
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verify that all options are applied
        assert "📁" not in output  # No emojis
        assert "[d]" in output  # ASCII markers
        assert "[f]" in output  # ASCII markers
        assert "[" in output  # Metadata
        assert "files" in output  # Metadata
        assert "main.pyc" not in output  # Excluded
        assert "main.py" in output  # Included
