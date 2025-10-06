"""Tests for metadata classes."""

from datetime import datetime

import pytest

from trxd import DirectoryMetadata, FileMetadata


class TestFileMetadata:
    """Tests for the FileMetadata class."""

    def test_file_metadata_creation(self) -> None:
        """Test basic creation of FileMetadata."""
        size = 1024
        modified = datetime(2024, 1, 15, 14, 30, 0)

        metadata = FileMetadata(size=size, modified=modified)

        assert metadata.size == size
        assert metadata.modified == modified

    def test_file_metadata_immutable(self) -> None:
        """Test that FileMetadata is immutable (NamedTuple)."""
        metadata = FileMetadata(size=1024, modified=datetime.now())

        # NamedTuple is immutable, cannot be modified
        with pytest.raises(AttributeError):
            metadata.size = 2048  # type: ignore

    def test_file_metadata_equality(self) -> None:
        """Test equality of FileMetadata."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        metadata1 = FileMetadata(size=1024, modified=dt)
        metadata2 = FileMetadata(size=1024, modified=dt)
        metadata3 = FileMetadata(size=2048, modified=dt)

        assert metadata1 == metadata2
        assert metadata1 != metadata3

    def test_file_metadata_repr(self) -> None:
        """Test string representation of FileMetadata."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        metadata = FileMetadata(size=1024, modified=dt)

        repr_str = repr(metadata)
        assert "FileMetadata" in repr_str
        assert "1024" in repr_str
        assert "2024" in repr_str


class TestDirectoryMetadata:
    """Tests for the DirectoryMetadata class."""

    def test_directory_metadata_creation(self) -> None:
        """Test basic creation of DirectoryMetadata."""
        file_count = 5
        total_size = 2048
        modified = datetime(2024, 1, 15, 14, 30, 0)

        metadata = DirectoryMetadata(
            file_count=file_count, total_size=total_size, modified=modified
        )

        assert metadata.file_count == file_count
        assert metadata.total_size == total_size
        assert metadata.modified == modified

    def test_directory_metadata_immutable(self) -> None:
        """Test that DirectoryMetadata is immutable (NamedTuple)."""
        metadata = DirectoryMetadata(file_count=5, total_size=2048, modified=datetime.now())

        # NamedTuple is immutable, cannot be modified
        with pytest.raises(AttributeError):
            metadata.file_count = 10  # type: ignore

    def test_directory_metadata_equality(self) -> None:
        """Test equality of DirectoryMetadata."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        metadata1 = DirectoryMetadata(file_count=5, total_size=2048, modified=dt)
        metadata2 = DirectoryMetadata(file_count=5, total_size=2048, modified=dt)
        metadata3 = DirectoryMetadata(file_count=10, total_size=2048, modified=dt)

        assert metadata1 == metadata2
        assert metadata1 != metadata3

    def test_directory_metadata_repr(self) -> None:
        """Test string representation of DirectoryMetadata."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        metadata = DirectoryMetadata(file_count=5, total_size=2048, modified=dt)

        repr_str = repr(metadata)
        assert "DirectoryMetadata" in repr_str
        assert "5" in repr_str
        assert "2048" in repr_str
        assert "2024" in repr_str
