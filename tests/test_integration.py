"""Tests de integración para ls-tree."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


class TestIntegration:
    """Tests de integración para ls-tree."""

    def test_cli_basic_usage(self, sample_tree: Path) -> None:
        """Test uso básico de la CLI."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=sample_tree.parent
        )

        assert result.returncode == 0
        assert "src" in result.stdout
        assert "main.py" in result.stdout
        assert "📁" in result.stdout  # Emojis por defecto

    def test_cli_help(self) -> None:
        """Test que la ayuda se muestra correctamente."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "Lista el contenido de un directorio" in result.stdout
        assert "--format" in result.stdout
        assert "--exclude" in result.stdout

    def test_cli_invalid_directory(self) -> None:
        """Test manejo de directorio inválido."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "/nonexistent/directory"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 1
        assert "no es un directorio válido" in result.stderr

    def test_cli_tree_format(self, sample_tree: Path) -> None:
        """Test formato tree."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--format", "tree", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "📁" in result.stdout
        assert "├──" in result.stdout
        assert "└──" in result.stdout

    def test_cli_ascii_format(self, sample_tree: Path) -> None:
        """Test formato ASCII."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--format", "ascii", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout
        assert "[d]" in result.stdout
        assert "[f]" in result.stdout

    def test_cli_flat_format(self, sample_tree: Path) -> None:
        """Test formato flat."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--format", "flat", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout
        assert "├──" not in result.stdout
        assert "src" in result.stdout
        assert "main.py" in result.stdout

    def test_cli_json_format(self, sample_tree: Path) -> None:
        """Test formato JSON."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--format", "json", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0

        # Verificar que es JSON válido
        try:
            json_data = json.loads(result.stdout)
            assert isinstance(json_data, dict)
            assert "src" in json_data
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_cli_yaml_format(self, sample_tree: Path) -> None:
        """Test formato YAML."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--format", "yaml", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0

        # Verificar que es YAML válido
        try:
            yaml_data = yaml.safe_load(result.stdout)
            assert isinstance(yaml_data, dict)
            assert "src" in yaml_data
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_cli_no_emoji(self, sample_tree: Path) -> None:
        """Test opción --no-emoji."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--no-emoji", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout
        assert "[d]" in result.stdout

    def test_cli_show_metadata(self, sample_tree: Path) -> None:
        """Test opción --show-metadata."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", "--show-metadata", str(sample_tree)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "[" in result.stdout  # Metadatos
        assert "files" in result.stdout

    def test_cli_exclude_patterns(self, sample_tree: Path) -> None:
        """Test patrones de exclusión."""
        result = subprocess.run(
            [
                sys.executable, "-m", "ls_tree", "--exclude", "*.pyc",
                "--exclude-dir", "__pycache__", str(sample_tree)
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "main.pyc" not in result.stdout
        assert "__pycache__" not in result.stdout
        assert "main.py" in result.stdout

    def test_cli_multiple_exclusions(self, sample_tree: Path) -> None:
        """Test múltiples exclusiones."""
        result = subprocess.run(
            [
                sys.executable, "-m", "ls_tree", "-x", "*.pyc", "-x", "*.pyo",
                "-xd", "__pycache__", "-xd", "node_modules", str(sample_tree)
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "main.pyc" not in result.stdout
        assert "main.pyo" not in result.stdout
        assert "__pycache__" not in result.stdout
        assert "node_modules" not in result.stdout
        assert "main.py" in result.stdout

    def test_cli_json_with_metadata(self, sample_tree: Path) -> None:
        """Test formato JSON con metadatos."""
        result = subprocess.run(
            [
                sys.executable, "-m", "ls_tree", "--format", "json",
                "--show-metadata", str(sample_tree)
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0

        # Verificar que es JSON válido con metadatos
        try:
            json_data = json.loads(result.stdout)
            assert isinstance(json_data, dict)

            # Verificar que se incluyen metadatos
            if "_metadata" in json_data:
                metadata = json_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except json.JSONDecodeError:
            pytest.fail("Output no es JSON válido")

    def test_cli_yaml_with_metadata(self, sample_tree: Path) -> None:
        """Test formato YAML con metadatos."""
        result = subprocess.run(
            [
                sys.executable, "-m", "ls_tree", "--format", "yaml",
                "--show-metadata", str(sample_tree)
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0

        # Verificar que es YAML válido con metadatos
        try:
            yaml_data = yaml.safe_load(result.stdout)
            assert isinstance(yaml_data, dict)

            # Verificar que se incluyen metadatos
            if "_metadata" in yaml_data:
                metadata = yaml_data["_metadata"]
                assert "file_count" in metadata
                assert "total_size" in metadata
                assert "modified" in metadata
        except yaml.YAMLError:
            pytest.fail("Output no es YAML válido")

    def test_cli_combined_options(self, sample_tree: Path) -> None:
        """Test combinación de múltiples opciones."""
        result = subprocess.run(
            [
                sys.executable, "-m", "ls_tree", "--format", "tree", "--no-emoji",
                "--show-metadata", "--exclude", "*.pyc", str(sample_tree)
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "📁" not in result.stdout  # No emojis
        assert "[d]" in result.stdout     # Marcadores ASCII
        assert "[f]" in result.stdout     # Marcadores ASCII
        assert "[" in result.stdout       # Metadatos
        assert "files" in result.stdout   # Metadatos
        assert "main.pyc" not in result.stdout  # Excluido
        assert "main.py" in result.stdout       # Incluido

    def test_cli_current_directory(self, sample_tree: Path) -> None:
        """Test que se usa el directorio actual por defecto."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=sample_tree
        )

        assert result.returncode == 0
        assert "src" in result.stdout or "main.py" in result.stdout

    def test_cli_empty_directory(self, temp_dir: Path) -> None:
        """Test directorio vacío."""
        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        # Debería mostrar solo el directorio raíz
        assert len(result.stdout.strip().split('\n')) <= 1

    def test_cli_single_file(self, temp_dir: Path) -> None:
        """Test directorio con un solo archivo."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "test.txt" in result.stdout

    def test_cli_nested_structure(self, temp_dir: Path) -> None:
        """Test estructura anidada."""
        # Crear estructura anidada
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()

        # Crear archivos en diferentes niveles
        (temp_dir / "root.txt").write_text("root")
        (temp_dir / "level1" / "level1.txt").write_text("level1")
        (temp_dir / "level1" / "level2" / "level2.txt").write_text("level2")

        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "level1" in result.stdout
        assert "level2" in result.stdout
        assert "root.txt" in result.stdout
        assert "level1.txt" in result.stdout
        assert "level2.txt" in result.stdout

    def test_cli_file_types(self, temp_dir: Path) -> None:
        """Test diferentes tipos de archivo."""
        # Crear archivos de diferentes tipos
        (temp_dir / "script.py").write_text("print('hello')")
        (temp_dir / "style.css").write_text("body { color: red; }")
        (temp_dir / "index.html").write_text("<html></html>")
        (temp_dir / "data.json").write_text('{"key": "value"}')

        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        assert "script.py" in result.stdout
        assert "style.css" in result.stdout
        assert "index.html" in result.stdout
        assert "data.json" in result.stdout

    def test_cli_performance_large_directory(self, temp_dir: Path) -> None:
        """Test rendimiento con directorio grande."""
        # Crear muchos archivos y directorios
        for i in range(100):
            (temp_dir / f"file_{i}.txt").write_text(f"content {i}")

        for i in range(10):
            subdir = temp_dir / f"dir_{i}"
            subdir.mkdir()
            for j in range(10):
                (subdir / f"file_{i}_{j}.txt").write_text(f"content {i}_{j}")

        result = subprocess.run(
            [sys.executable, "-m", "ls_tree", str(temp_dir)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        assert result.returncode == 0
        # Verificar que se procesan todos los archivos
        assert "file_0.txt" in result.stdout
        assert "file_99.txt" in result.stdout
        assert "dir_0" in result.stdout
        assert "dir_9" in result.stdout
