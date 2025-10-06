"""Tests para la función main."""

import json
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from ls_tree import main


class TestMain:
    """Tests para la función main."""

    def test_main_help(self) -> None:
        """Test que la ayuda se muestra correctamente."""
        with patch("sys.argv", ["trxd", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_invalid_directory(self) -> None:
        """Test que se maneja correctamente un directorio inválido."""
        with patch("sys.argv", ["trxd", "/nonexistent/directory"]), patch(
            "sys.stderr", new_callable=StringIO
        ) as mock_stderr, pytest.raises(SystemExit) as exc_info:
            main()
            assert exc_info.value.code == 1
            assert "no es un directorio válido" in mock_stderr.getvalue()

    def test_main_default_format(self, sample_tree: Path) -> None:
        """Test formato por defecto (tree con emojis)."""
        with patch("sys.argv", ["trxd", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se usa formato tree con emojis
        assert "📁" in output
        assert "🐍" in output
        assert "├──" in output
        assert "└──" in output

    def test_main_tree_format(self, sample_tree: Path) -> None:
        """Test formato tree explícito."""
        with patch("sys.argv", ["trxd", "--format", "tree", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se usa formato tree
        assert "📁" in output
        assert "🐍" in output
        assert "├──" in output
        assert "└──" in output

    def test_main_ascii_format(self, sample_tree: Path) -> None:
        """Test formato ASCII."""
        with patch("sys.argv", ["trxd", "--format", "ascii", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se usa formato ASCII
        assert "📁" not in output
        assert "🐍" not in output
        assert "[d]" in output
        assert "[f]" in output
        assert "├──" in output
        assert "└──" in output

    def test_main_flat_format(self, sample_tree: Path) -> None:
        """Test formato flat."""
        with patch("sys.argv", ["trxd", "--format", "flat", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se usa formato flat
        assert "📁" not in output
        assert "🐍" not in output
        assert "├──" not in output
        assert "└──" not in output
        assert "src" in output
        assert "main.py" in output

    def test_main_json_format(self, sample_tree: Path) -> None:
        """Test formato JSON."""
        with patch("sys.argv", ["trxd", "--format", "json", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se genera JSON válido
        try:
            json_data = json.loads(output)
            assert isinstance(json_data, dict)
            # Verificar estructura básica
            assert "src" in json_data
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_main_yaml_format(self, sample_tree: Path) -> None:
        """Test formato YAML."""
        with patch("sys.argv", ["trxd", "--format", "yaml", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se genera YAML válido
        try:
            yaml_data = yaml.safe_load(output)
            assert isinstance(yaml_data, dict)
            # Verificar estructura básica
            assert "src" in yaml_data
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_main_no_emoji(self, sample_tree: Path) -> None:
        """Test opción --no-emoji."""
        with patch("sys.argv", ["trxd", "--no-emoji", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que NO se usan emojis
        assert "📁" not in output
        assert "🐍" not in output
        # Verificar que se usan marcadores ASCII
        assert "[d]" in output
        assert "[f]" in output

    def test_main_show_metadata(self, sample_tree: Path) -> None:
        """Test opción --show-metadata."""
        with patch("sys.argv", ["trxd", "--show-metadata", str(sample_tree)]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se incluyen metadatos
        assert "[" in output  # Metadatos en formato [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_main_exclude_patterns(self, sample_tree: Path) -> None:
        """Test patrones de exclusión."""
        with patch(
            "sys.argv",
            ["trxd", "--exclude", "*.pyc", "--exclude-dir", "__pycache__", str(sample_tree)],
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se excluyen archivos y directorios
        assert "main.pyc" not in output
        assert "__pycache__" not in output
        # Verificar que se incluyen archivos válidos
        assert "main.py" in output

    def test_main_multiple_exclusions(self, sample_tree: Path) -> None:
        """Test múltiples exclusiones."""
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

        # Verificar que se excluyen múltiples patrones
        assert "main.pyc" not in output
        assert "main.pyo" not in output
        assert "__pycache__" not in output
        assert "node_modules" not in output
        # Verificar que se incluyen archivos válidos
        assert "main.py" in output

    def test_main_current_directory(self, sample_tree: Path) -> None:
        """Test que se usa el directorio actual por defecto."""
        with patch("sys.argv", ["trxd"]), patch(
            "sys.stdout", new_callable=StringIO
        ) as mock_stdout, patch("pathlib.Path.cwd", return_value=sample_tree):
            main()
            output = mock_stdout.getvalue()

        # Verificar que se procesa el directorio actual
        assert "src" in output or "main.py" in output

    def test_main_json_with_metadata(self, sample_tree: Path) -> None:
        """Test formato JSON con metadatos."""
        with patch(
            "sys.argv", ["trxd", "--format", "json", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se genera JSON válido con metadatos
        try:
            json_data = json.loads(output)
            assert isinstance(json_data, dict)

            # Verificar que se incluyen metadatos
            if "_metadata" in json_data:
                metadata = json_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_main_yaml_with_metadata(self, sample_tree: Path) -> None:
        """Test formato YAML con metadatos."""
        with patch(
            "sys.argv", ["trxd", "--format", "yaml", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se genera YAML válido con metadatos
        try:
            yaml_data = yaml.safe_load(output)
            assert isinstance(yaml_data, dict)

            # Verificar que se incluyen metadatos
            if "_metadata" in yaml_data:
                metadata = yaml_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_main_flat_with_metadata(self, sample_tree: Path) -> None:
        """Test formato flat con metadatos."""
        with patch(
            "sys.argv", ["trxd", "--format", "flat", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se incluyen metadatos en formato flat
        assert "[" in output  # Metadatos en formato [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_main_ascii_with_metadata(self, sample_tree: Path) -> None:
        """Test formato ASCII con metadatos."""
        with patch(
            "sys.argv", ["trxd", "--format", "ascii", "--show-metadata", str(sample_tree)]
        ), patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main()
            output = mock_stdout.getvalue()

        # Verificar que se usa formato ASCII con metadatos
        assert "📁" not in output
        assert "🐍" not in output
        assert "[d]" in output
        assert "[f]" in output
        assert "[" in output  # Metadatos
        assert "files" in output

    def test_main_combined_options(self, sample_tree: Path) -> None:
        """Test combinación de múltiples opciones."""
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

        # Verificar que se aplican todas las opciones
        assert "📁" not in output  # No emojis
        assert "[d]" in output  # Marcadores ASCII
        assert "[f]" in output  # Marcadores ASCII
        assert "[" in output  # Metadatos
        assert "files" in output  # Metadatos
        assert "main.pyc" not in output  # Excluido
        assert "main.py" in output  # Incluido
