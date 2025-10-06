"""Tests para la función build_tree."""

import argparse
from pathlib import Path

from ls_tree import build_tree


class TestBuildTree:
    """Tests para la función build_tree."""

    def test_build_tree_basic(self, sample_tree: Path) -> None:
        """Test construcción básica del árbol."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Debería incluir todos los directorios
        dir_paths = [result[0] for result in results]
        assert sample_tree in dir_paths
        assert sample_tree / "src" in dir_paths
        assert sample_tree / "src" / "components" in dir_paths
        assert sample_tree / "src" / "utils" in dir_paths
        assert sample_tree / "docs" in dir_paths

    def test_build_tree_with_exclusions(self, sample_tree: Path) -> None:
        """Test construcción del árbol con exclusiones."""
        args = argparse.Namespace(
            exclude=["*.pyc"],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Verificar que se excluyen los directorios
        dir_paths = [result[0] for result in results]
        assert sample_tree / "src" / "__pycache__" not in dir_paths
        assert sample_tree / "node_modules" not in dir_paths
        assert sample_tree / ".git" not in dir_paths

        # Verificar que se incluyen los directorios válidos
        assert sample_tree / "src" in dir_paths
        assert sample_tree / "src" / "components" in dir_paths
        assert sample_tree / "src" / "utils" in dir_paths
        assert sample_tree / "docs" in dir_paths

    def test_build_tree_file_exclusions(self, sample_tree: Path) -> None:
        """Test exclusión de archivos específicos."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=["*.pyc"],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Encontrar el directorio src
        src_result = None
        for dirpath, dirnames, filenames, metadata in results:
            if dirpath == sample_tree / "src":
                src_result = (dirpath, dirnames, filenames, metadata)
                break

        assert src_result is not None
        _, _, filenames, _ = src_result

        # main.pyc debería estar excluido
        assert "main.pyc" not in filenames
        # main.py debería estar incluido
        assert "main.py" in filenames

    def test_build_tree_with_metadata(self, sample_tree: Path) -> None:
        """Test construcción del árbol con metadatos."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=True
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Verificar que se incluyen metadatos
        for _dirpath, _dirnames, filenames, metadata in results:
            assert isinstance(metadata, dict)
            if filenames:  # Si hay archivos, debería haber metadatos de archivos
                assert "files" in metadata
                assert "directory" in metadata

                # Verificar estructura de metadatos de archivos
                file_metadata = metadata["files"]
                for filename in filenames:
                    assert filename in file_metadata
                    file_meta = file_metadata[filename]
                    assert hasattr(file_meta, 'size')
                    assert hasattr(file_meta, 'modified')

                # Verificar metadatos del directorio
                dir_metadata = metadata["directory"]
                assert hasattr(dir_metadata, 'file_count')
                assert hasattr(dir_metadata, 'total_size')
                assert hasattr(dir_metadata, 'modified')
                assert dir_metadata.file_count == len(filenames)

    def test_build_tree_without_metadata(self, sample_tree: Path) -> None:
        """Test construcción del árbol sin metadatos."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Verificar que no se incluyen metadatos
        for _dirpath, _dirnames, _filenames, metadata in results:
            assert metadata == {}

    def test_build_tree_generator_behavior(self, sample_tree: Path) -> None:
        """Test que build_tree es un generador."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)

        # Verificar que es un generador
        assert hasattr(tree_generator, '__iter__')
        assert hasattr(tree_generator, '__next__')

        # Verificar que se puede iterar
        first_result = next(tree_generator)
        assert len(first_result) == 4  # (dirpath, dirnames, filenames, metadata)

        # Verificar que se puede continuar iterando
        remaining_results = list(tree_generator)
        assert len(remaining_results) > 0

    def test_build_tree_empty_directory(self, temp_dir: Path) -> None:
        """Test construcción del árbol en directorio vacío."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # Debería haber al menos un resultado (el directorio raíz)
        assert len(results) >= 1

        # El directorio raíz debería estar vacío
        root_result = results[0]
        dirpath, dirnames, filenames, metadata = root_result
        assert dirpath == temp_dir
        assert len(dirnames) == 0
        assert len(filenames) == 0

    def test_build_tree_single_file(self, temp_dir: Path) -> None:
        """Test construcción del árbol con un solo archivo."""
        # Crear un archivo
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # Debería haber un resultado
        assert len(results) == 1

        dirpath, dirnames, filenames, metadata = results[0]
        assert dirpath == temp_dir
        assert len(dirnames) == 0
        assert len(filenames) == 1
        assert "test.txt" in filenames

    def test_build_tree_nested_structure(self, temp_dir: Path) -> None:
        """Test construcción del árbol con estructura anidada."""
        # Crear estructura anidada
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()
        (temp_dir / "level1" / "level2" / "level3").mkdir()

        # Crear archivos en diferentes niveles
        (temp_dir / "root.txt").write_text("root")
        (temp_dir / "level1" / "level1.txt").write_text("level1")
        (temp_dir / "level1" / "level2" / "level2.txt").write_text("level2")
        (temp_dir / "level1" / "level2" / "level3" / "level3.txt").write_text("level3")

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=False
        )

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # Debería haber 4 directorios
        assert len(results) == 4

        # Verificar que todos los directorios están incluidos
        dir_paths = [result[0] for result in results]
        assert temp_dir in dir_paths
        assert temp_dir / "level1" in dir_paths
        assert temp_dir / "level1" / "level2" in dir_paths
        assert temp_dir / "level1" / "level2" / "level3" in dir_paths

    def test_build_tree_metadata_calculation(self, temp_dir: Path) -> None:
        """Test cálculo correcto de metadatos."""
        # Crear archivos con contenido conocido
        file1 = temp_dir / "file1.txt"
        file1.write_text("content1")  # 8 bytes

        file2 = temp_dir / "file2.txt"
        file2.write_text("content2")  # 8 bytes

        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[],
            show_metadata=True
        )

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # Debería haber un resultado
        assert len(results) == 1

        dirpath, dirnames, filenames, metadata = results[0]
        assert dirpath == temp_dir

        # Verificar metadatos
        assert "files" in metadata
        assert "directory" in metadata

        # Verificar metadatos de archivos
        file_metadata = metadata["files"]
        assert "file1.txt" in file_metadata
        assert "file2.txt" in file_metadata

        # Verificar tamaños (aproximadamente 8 bytes cada uno)
        assert file_metadata["file1.txt"].size >= 8
        assert file_metadata["file2.txt"].size >= 8

        # Verificar metadatos del directorio
        dir_metadata = metadata["directory"]
        assert dir_metadata.file_count == 2
        assert dir_metadata.total_size >= 16  # Al menos 16 bytes total
