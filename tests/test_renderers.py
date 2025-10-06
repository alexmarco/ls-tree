"""Tests para las funciones de renderizado."""

import argparse
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from ls_tree import build_tree, render_flat, render_tree


class TestRenderFlat:
    """Tests para la función render_flat."""

    def test_render_flat_basic(self, sample_tree: Path) -> None:
        """Test renderizado básico en formato plano."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree)
            output = mock_stdout.getvalue()

        # Verificar que se incluyen directorios y archivos
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
        """Test renderizado plano con metadatos."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=True
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree, show_metadata=True)
            output = mock_stdout.getvalue()

        # Verificar que se incluyen metadatos
        assert "[" in output  # Metadatos en formato [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_render_flat_with_exclusions(self, sample_tree: Path) -> None:
        """Test renderizado plano con exclusiones."""
        args = argparse.Namespace(
            exclude=["*.pyc"],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree)
            output = mock_stdout.getvalue()

        # Verificar que se excluyen archivos y directorios
        assert "main.pyc" not in output
        assert "__pycache__" not in output
        assert "node_modules" not in output
        assert ".git" not in output

        # Verificar que se incluyen archivos válidos
        assert "main.py" in output
        assert "Button.py" in output

    def test_render_flat_empty_directory(self, temp_dir: Path) -> None:
        """Test renderizado plano en directorio vacío."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, temp_dir)
            output = mock_stdout.getvalue()

        # Debería mostrar solo el directorio raíz (puede estar vacío)
        assert output.strip() == "." or output.strip() == ""

    def test_render_flat_single_file(self, temp_dir: Path) -> None:
        """Test renderizado plano con un solo archivo."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, temp_dir)
            output = mock_stdout.getvalue()

        # Debería mostrar el directorio y el archivo
        assert "test.txt" in output

    def test_render_flat_relative_paths(self, sample_tree: Path) -> None:
        """Test que se muestran rutas relativas correctamente."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_flat(tree_generator, sample_tree)
            output = mock_stdout.getvalue()

        # Verificar que no se incluyen rutas absolutas
        assert str(sample_tree) not in output
        # Verificar que se incluyen rutas relativas
        assert "src" in output
        assert "src\\main.py" in output or "src/main.py" in output


class TestRenderTree:
    """Tests para la función render_tree."""

    def test_render_tree_basic(self, sample_tree: Path) -> None:
        """Test renderizado básico en formato árbol."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verificar que se incluyen elementos del árbol
        assert "📁" in output  # Emoji de directorio
        assert "🐍" in output  # Emoji de Python
        assert "├──" in output  # Conectores del árbol
        assert "└──" in output  # Conectores del árbol
        assert "src" in output
        assert "main.py" in output

    def test_render_tree_no_emoji(self, sample_tree: Path) -> None:
        """Test renderizado en formato árbol sin emojis."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=False)
            output = mock_stdout.getvalue()

        # Verificar que NO se incluyen emojis
        assert "📁" not in output
        assert "🐍" not in output
        # Verificar que se incluyen marcadores ASCII
        assert "[d]" in output  # Marcador de directorio
        assert "[f]" in output  # Marcador de archivo
        assert "├──" in output  # Conectores del árbol
        assert "└──" in output  # Conectores del árbol

    def test_render_tree_with_metadata(self, sample_tree: Path) -> None:
        """Test renderizado en formato árbol con metadatos."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=True
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True, show_metadata=True)
            output = mock_stdout.getvalue()

        # Verificar que se incluyen metadatos
        assert "[" in output  # Metadatos en formato [X files, Y KB]
        assert "files" in output
        assert "KB" in output or "B" in output

    def test_render_tree_with_exclusions(self, sample_tree: Path) -> None:
        """Test renderizado en formato árbol con exclusiones."""
        args = argparse.Namespace(
            exclude=["*.pyc"],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verificar que se excluyen archivos y directorios
        assert "main.pyc" not in output
        assert "__pycache__" not in output
        assert "node_modules" not in output
        assert ".git" not in output

        # Verificar que se incluyen archivos válidos
        assert "main.py" in output
        assert "Button.py" in output

    def test_render_tree_empty_directory(self, temp_dir: Path) -> None:
        """Test renderizado en formato árbol en directorio vacío."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Debería mostrar solo el directorio raíz (puede estar vacío)
        assert "📁" in output or "[d]" in output or output.strip() == ""

    def test_render_tree_single_file(self, temp_dir: Path) -> None:
        """Test renderizado en formato árbol con un solo archivo."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Debería mostrar el directorio y el archivo
        assert "test.txt" in output
        # En directorio con un solo archivo, puede no mostrar el directorio raíz
        assert "📄" in output or "[f]" in output

    def test_render_tree_nested_structure(self, temp_dir: Path) -> None:
        """Test renderizado en formato árbol con estructura anidada."""
        # Crear estructura anidada
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()

        # Crear archivos en diferentes niveles
        (temp_dir / "root.txt").write_text("root")
        (temp_dir / "level1" / "level1.txt").write_text("level1")
        (temp_dir / "level1" / "level2" / "level2.txt").write_text("level2")

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verificar que se incluyen todos los niveles
        assert "level1" in output
        assert "level2" in output
        assert "root.txt" in output
        assert "level1.txt" in output
        assert "level2.txt" in output

        # Verificar conectores del árbol
        assert "├──" in output
        assert "└──" in output
        assert "│   " in output  # Indentación

    def test_render_tree_file_types(self, temp_dir: Path) -> None:
        """Test renderizado en formato árbol con diferentes tipos de archivo."""
        # Crear archivos de diferentes tipos
        (temp_dir / "script.py").write_text("print('hello')")
        (temp_dir / "style.css").write_text("body { color: red; }")
        (temp_dir / "index.html").write_text("<html></html>")
        (temp_dir / "data.json").write_text('{"key": "value"}')
        (temp_dir / "image.png").write_text("fake png")

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, temp_dir, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verificar que se incluyen emojis específicos para cada tipo
        assert "🐍" in output  # Python
        assert "🎨" in output  # CSS
        assert "🌐" in output  # HTML
        assert "📋" in output  # JSON
        assert "🖼️" in output  # PNG

    def test_render_tree_relative_paths(self, sample_tree: Path) -> None:
        """Test que se muestran rutas relativas correctamente."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            render_tree(tree_generator, sample_tree, use_emoji=True)
            output = mock_stdout.getvalue()

        # Verificar que no se incluyen rutas absolutas
        assert str(sample_tree) not in output
        # Verificar que se incluyen rutas relativas
        assert "src" in output
        assert "main.py" in output
