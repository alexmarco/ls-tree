"""Tests for the build_tree function."""

import argparse
from pathlib import Path

from trxd import build_tree


class TestBuildTree:
    """Tests for the build_tree function."""

    def test_build_tree_basic(self, sample_tree: Path) -> None:
        """Test basic tree construction."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Should include all directories
        dir_paths = [result[0] for result in results]
        assert sample_tree in dir_paths
        assert sample_tree / "src" in dir_paths
        assert sample_tree / "src" / "components" in dir_paths
        assert sample_tree / "src" / "utils" in dir_paths
        assert sample_tree / "docs" in dir_paths

    def test_build_tree_with_exclusions(self, sample_tree: Path) -> None:
        """Test tree construction with exclusions."""
        args = argparse.Namespace(
            exclude=["*.pyc"],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[],
            show_metadata=False,
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Verify that directories are excluded
        dir_paths = [result[0] for result in results]
        assert sample_tree / "src" / "__pycache__" not in dir_paths
        assert sample_tree / "node_modules" not in dir_paths
        assert sample_tree / ".git" not in dir_paths

        # Verify that valid directories are included
        assert sample_tree / "src" in dir_paths
        assert sample_tree / "src" / "components" in dir_paths
        assert sample_tree / "src" / "utils" in dir_paths
        assert sample_tree / "docs" in dir_paths

    def test_build_tree_file_exclusions(self, sample_tree: Path) -> None:
        """Test specific file exclusions."""
        args = argparse.Namespace(
            exclude=[], exclude_dir=[], exclude_file=["*.pyc"], show_metadata=False
        )

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Find the src directory
        src_result = None
        for dirpath, dirnames, filenames, metadata in results:
            if dirpath == sample_tree / "src":
                src_result = (dirpath, dirnames, filenames, metadata)
                break

        assert src_result is not None
        _, _, filenames, _ = src_result

        # main.pyc should be excluded
        assert "main.pyc" not in filenames
        # main.py debería estar incluido
        assert "main.py" in filenames

    def test_build_tree_with_metadata(self, sample_tree: Path) -> None:
        """Test tree construction with metadata."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=True)

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Verify that metadata is included
        for _dirpath, _dirnames, filenames, metadata in results:
            assert isinstance(metadata, dict)
            if filenames:  # If there are files, there should be file metadata
                assert "files" in metadata
                assert "directory" in metadata

                # Verify file metadata structure
                file_metadata = metadata["files"]
                for filename in filenames:
                    assert filename in file_metadata
                    file_meta = file_metadata[filename]
                    assert hasattr(file_meta, "size")
                    assert hasattr(file_meta, "modified")

                # Verify directory metadata
                dir_metadata = metadata["directory"]
                assert hasattr(dir_metadata, "file_count")
                assert hasattr(dir_metadata, "total_size")
                assert hasattr(dir_metadata, "modified")
                assert dir_metadata.file_count == len(filenames)

    def test_build_tree_without_metadata(self, sample_tree: Path) -> None:
        """Test tree construction without metadata."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)
        results = list(tree_generator)

        # Verify that metadata is not included
        for _dirpath, _dirnames, _filenames, metadata in results:
            assert metadata == {}

    def test_build_tree_generator_behavior(self, sample_tree: Path) -> None:
        """Test that build_tree is a generator."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(sample_tree, args)

        # Verify that it is a generator
        assert hasattr(tree_generator, "__iter__")
        assert hasattr(tree_generator, "__next__")

        # Verify that it can be iterated
        first_result = next(tree_generator)
        assert len(first_result) == 4  # (dirpath, dirnames, filenames, metadata)

        # Verify that it can be continued iterating
        remaining_results = list(tree_generator)
        assert len(remaining_results) > 0

    def test_build_tree_empty_directory(self, temp_dir: Path) -> None:
        """Test tree construction in empty directory."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # There should be at least one result (the root directory)
        assert len(results) >= 1

        # The root directory should be empty
        root_result = results[0]
        dirpath, dirnames, filenames, metadata = root_result
        assert dirpath == temp_dir
        assert len(dirnames) == 0
        assert len(filenames) == 0

    def test_build_tree_single_file(self, temp_dir: Path) -> None:
        """Test tree construction with a single file."""
        # Crear un archivo
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # There should be one result
        assert len(results) == 1

        dirpath, dirnames, filenames, metadata = results[0]
        assert dirpath == temp_dir
        assert len(dirnames) == 0
        assert len(filenames) == 1
        assert "test.txt" in filenames

    def test_build_tree_nested_structure(self, temp_dir: Path) -> None:
        """Test tree construction with nested structure."""
        # Crear estructura anidada
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()
        (temp_dir / "level1" / "level2" / "level3").mkdir()

        # Create files at different levels
        (temp_dir / "root.txt").write_text("root")
        (temp_dir / "level1" / "level1.txt").write_text("level1")
        (temp_dir / "level1" / "level2" / "level2.txt").write_text("level2")
        (temp_dir / "level1" / "level2" / "level3" / "level3.txt").write_text("level3")

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=False)

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # There should be 4 directories
        assert len(results) == 4

        # Verify that all directories are included
        dir_paths = [result[0] for result in results]
        assert temp_dir in dir_paths
        assert temp_dir / "level1" in dir_paths
        assert temp_dir / "level1" / "level2" in dir_paths
        assert temp_dir / "level1" / "level2" / "level3" in dir_paths

    def test_build_tree_metadata_calculation(self, temp_dir: Path) -> None:
        """Test correct metadata calculation."""
        # Crear archivos con contenido conocido
        file1 = temp_dir / "file1.txt"
        file1.write_text("content1")  # 8 bytes

        file2 = temp_dir / "file2.txt"
        file2.write_text("content2")  # 8 bytes

        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[], show_metadata=True)

        tree_generator = build_tree(temp_dir, args)
        results = list(tree_generator)

        # There should be one result
        assert len(results) == 1

        dirpath, dirnames, filenames, metadata = results[0]
        assert dirpath == temp_dir

        # Verify metadata
        assert "files" in metadata
        assert "directory" in metadata

        # Verify file metadata
        file_metadata = metadata["files"]
        assert "file1.txt" in file_metadata
        assert "file2.txt" in file_metadata

        # Verify sizes (approximately 8 bytes each)
        assert file_metadata["file1.txt"].size >= 8
        assert file_metadata["file2.txt"].size >= 8

        # Verify directory metadata
        dir_metadata = metadata["directory"]
        assert dir_metadata.file_count == 2
        assert dir_metadata.total_size >= 16  # Al menos 16 bytes total
