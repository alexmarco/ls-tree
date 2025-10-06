"""Tests for filtering functions."""

import argparse
from pathlib import Path

from trxd import is_excluded


class TestIsExcluded:
    """Tests for the is_excluded function."""

    def test_no_exclusions(self) -> None:
        """Test that without exclusions, nothing is excluded."""
        args = argparse.Namespace(exclude=[], exclude_dir=[], exclude_file=[])

        assert not is_excluded(Path("file.txt"), args)
        assert not is_excluded(Path("directory"), args)

    def test_exclude_patterns(self) -> None:
        """Test general exclusion patterns."""
        args = argparse.Namespace(exclude=["*.pyc", "*.tmp"], exclude_dir=[], exclude_file=[])

        # Files that should be excluded
        assert is_excluded(Path("script.pyc"), args)
        assert is_excluded(Path("temp.tmp"), args)
        assert is_excluded(Path("src/script.pyc"), args)

        # Files that should not be excluded
        assert not is_excluded(Path("script.py"), args)
        assert not is_excluded(Path("file.txt"), args)

    def test_exclude_dir_patterns(self) -> None:
        """Test specific exclusion patterns for directories."""
        args = argparse.Namespace(
            exclude=[], exclude_dir=["__pycache__", "node_modules", ".git"], exclude_file=[]
        )

        # Create Path objects that simulate directories using mock
        from unittest.mock import Mock

        cache_dir = Mock(spec=Path)
        cache_dir.match.return_value = True
        cache_dir.is_dir.return_value = True

        node_dir = Mock(spec=Path)
        node_dir.match.return_value = True
        node_dir.is_dir.return_value = True

        git_dir = Mock(spec=Path)
        git_dir.match.return_value = True
        git_dir.is_dir.return_value = True

        # Directories that should be excluded
        assert is_excluded(cache_dir, args)
        assert is_excluded(node_dir, args)
        assert is_excluded(git_dir, args)

        # Files with similar names should not be excluded
        assert not is_excluded(Path("__pycache__.txt"), args)
        assert not is_excluded(Path("node_modules.zip"), args)

        # Directories that should not be excluded
        assert not is_excluded(Path("src"), args)
        assert not is_excluded(Path("docs"), args)

    def test_exclude_file_patterns(self) -> None:
        """Test specific exclusion patterns for files."""
        args = argparse.Namespace(
            exclude=[], exclude_dir=[], exclude_file=["*.log", "*.tmp", "*.bak"]
        )

        # Create Path objects that simulate files using mock
        from unittest.mock import Mock

        log_file = Mock(spec=Path)
        log_file.match.return_value = True
        log_file.is_file.return_value = True

        tmp_file = Mock(spec=Path)
        tmp_file.match.return_value = True
        tmp_file.is_file.return_value = True

        bak_file = Mock(spec=Path)
        bak_file.match.return_value = True
        bak_file.is_file.return_value = True

        # Files that should be excluded
        assert is_excluded(log_file, args)
        assert is_excluded(tmp_file, args)
        assert is_excluded(bak_file, args)

        # Directories with similar names should not be excluded
        assert not is_excluded(Path("logs"), args)  # directorio
        assert not is_excluded(Path("temp"), args)  # directorio

        # Files that should not be excluded
        assert not is_excluded(Path("script.py"), args)
        assert not is_excluded(Path("readme.md"), args)

    def test_combined_exclusions(self) -> None:
        """Test combination of different types of exclusions."""
        args = argparse.Namespace(
            exclude=["*.pyc", "*.pyo"],
            exclude_dir=["__pycache__", "node_modules"],
            exclude_file=["*.log", "*.tmp"],
        )

        # Files excluded by general patterns
        assert is_excluded(Path("script.pyc"), args)
        assert is_excluded(Path("module.pyo"), args)

        # Create Path objects that simulate directories using mock
        from unittest.mock import Mock

        cache_dir = Mock(spec=Path)
        cache_dir.match.return_value = True
        cache_dir.is_dir.return_value = True

        node_dir = Mock(spec=Path)
        node_dir.match.return_value = True
        node_dir.is_dir.return_value = True

        # Directories excluded by directory patterns
        assert is_excluded(cache_dir, args)
        assert is_excluded(node_dir, args)

        # Create Path objects that simulate files using mock
        from unittest.mock import Mock

        log_file = Mock(spec=Path)
        log_file.match.return_value = True
        log_file.is_file.return_value = True

        tmp_file = Mock(spec=Path)
        tmp_file.match.return_value = True
        tmp_file.is_file.return_value = True

        # Files excluded by file patterns
        assert is_excluded(log_file, args)
        assert is_excluded(tmp_file, args)

        # Files that should not be excluded
        assert not is_excluded(Path("script.py"), args)
        assert not is_excluded(Path("readme.md"), args)
        assert not is_excluded(Path("src"), args)

    def test_wildcard_patterns(self) -> None:
        """Test patterns with wildcards."""
        args = argparse.Namespace(exclude=["test_*", "*_test.py"], exclude_dir=[], exclude_file=[])

        # Files that match patterns
        assert is_excluded(Path("test_file.py"), args)
        assert is_excluded(Path("unit_test.py"), args)
        assert is_excluded(Path("integration_test.py"), args)

        # Files that do not match
        assert not is_excluded(Path("main.py"), args)
        assert not is_excluded(Path("helper.py"), args)

    def test_hidden_files_and_dirs(self) -> None:
        """Test hidden files and directories."""
        args = argparse.Namespace(exclude=[".*"], exclude_dir=[], exclude_file=[])

        # Hidden files and directories
        assert is_excluded(Path(".gitignore"), args)
        assert is_excluded(Path(".env"), args)
        assert is_excluded(Path(".git"), args)
        assert is_excluded(Path(".vscode"), args)

        # Normal files
        assert not is_excluded(Path("readme.md"), args)
        assert not is_excluded(Path("src"), args)

    def test_case_sensitivity(self) -> None:
        """Test case sensitivity."""
        import platform

        args = argparse.Namespace(exclude=["*.PYC"], exclude_dir=[], exclude_file=[])

        # In Windows, pathlib.Path.match is case-insensitive by default
        # In Linux/Unix, it is case-sensitive
        if platform.system() == "Windows":
            assert is_excluded(Path("script.pyc"), args)  # lowercase
        else:
            assert not is_excluded(Path("script.pyc"), args)  # lowercase does not match
        assert is_excluded(Path("script.PYC"), args)  # mayúsculas

    def test_nested_paths(self) -> None:
        """Test nested paths."""
        args = argparse.Namespace(exclude=["src/*.pyc"], exclude_dir=[], exclude_file=[])

        # Files in subdirectories
        assert is_excluded(Path("src/script.pyc"), args)
        # The pattern "src/*.pyc" does not match "src/utils/helper.pyc" because * does not include /
        # assert is_excluded(Path("src/utils/helper.pyc"), args)

        # Files in other directories
        assert not is_excluded(Path("docs/script.pyc"), args)
        assert not is_excluded(Path("script.pyc"), args)

    def test_empty_patterns(self) -> None:
        """Test with empty patterns."""
        args = argparse.Namespace(exclude=[""], exclude_dir=[""], exclude_file=[""])

        # Empty patterns should not exclude anything
        assert not is_excluded(Path("file.txt"), args)
        assert not is_excluded(Path("directory"), args)

    def test_multiple_matches(self) -> None:
        """Test when a file matches multiple patterns."""
        args = argparse.Namespace(
            exclude=["*.pyc", "*.tmp"], exclude_dir=[], exclude_file=["*.log"]
        )

        # File that matches general pattern
        assert is_excluded(Path("script.pyc"), args)

        # Create Path object that simulates file using mock
        from unittest.mock import Mock

        log_file = Mock(spec=Path)
        log_file.match.return_value = True
        log_file.is_file.return_value = True

        # File that matches file pattern
        assert is_excluded(log_file, args)

        # File that does not match any pattern
        assert not is_excluded(Path("script.py"), args)
