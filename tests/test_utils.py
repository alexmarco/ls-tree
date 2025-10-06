"""Tests para funciones utilitarias."""



from ls_tree import _format_size, _get_file_emoji


class TestGetFileEmoji:
    """Tests para la función _get_file_emoji."""

    def test_python_file_emoji(self) -> None:
        """Test emoji para archivos Python."""
        assert _get_file_emoji("script.py") == "🐍"
        assert _get_file_emoji("module.py") == "🐍"

    def test_javascript_file_emoji(self) -> None:
        """Test emoji para archivos JavaScript."""
        assert _get_file_emoji("app.js") == "📜"
        assert _get_file_emoji("script.js") == "📜"

    def test_html_file_emoji(self) -> None:
        """Test emoji para archivos HTML."""
        assert _get_file_emoji("index.html") == "🌐"
        assert _get_file_emoji("page.htm") == "🌐"

    def test_css_file_emoji(self) -> None:
        """Test emoji para archivos CSS."""
        assert _get_file_emoji("styles.css") == "🎨"
        assert _get_file_emoji("main.scss") == "🎨"

    def test_image_file_emoji(self) -> None:
        """Test emoji para archivos de imagen."""
        assert _get_file_emoji("photo.jpg") == "🖼️"
        assert _get_file_emoji("image.png") == "🖼️"
        assert _get_file_emoji("logo.svg") == "🖼️"

    def test_video_file_emoji(self) -> None:
        """Test emoji para archivos de video."""
        assert _get_file_emoji("movie.mp4") == "🎥"
        assert _get_file_emoji("clip.avi") == "🎥"

    def test_audio_file_emoji(self) -> None:
        """Test emoji para archivos de audio."""
        assert _get_file_emoji("song.mp3") == "🎵"
        assert _get_file_emoji("music.wav") == "🎵"

    def test_document_file_emoji(self) -> None:
        """Test emoji para archivos de documento."""
        assert _get_file_emoji("readme.md") == "📝"
        assert _get_file_emoji("manual.pdf") == "📄"
        assert _get_file_emoji("notes.txt") == "📄"

    def test_config_file_emoji(self) -> None:
        """Test emoji para archivos de configuración."""
        assert _get_file_emoji("config.json") == "📋"
        assert _get_file_emoji("settings.yaml") == "📋"
        # .env no tiene extensión, por lo que usa el emoji por defecto
        assert _get_file_emoji(".env") == "📄"

    def test_compressed_file_emoji(self) -> None:
        """Test emoji para archivos comprimidos."""
        assert _get_file_emoji("archive.zip") == "📦"
        assert _get_file_emoji("backup.tar.gz") == "📦"

    def test_executable_file_emoji(self) -> None:
        """Test emoji para archivos ejecutables."""
        assert _get_file_emoji("program.exe") == "⚡"
        assert _get_file_emoji("installer.msi") == "⚡"

    def test_unknown_extension_emoji(self) -> None:
        """Test emoji por defecto para extensiones desconocidas."""
        assert _get_file_emoji("unknown.xyz") == "📄"
        assert _get_file_emoji("file") == "📄"

    def test_case_insensitive(self) -> None:
        """Test que la función es insensible a mayúsculas/minúsculas."""
        assert _get_file_emoji("script.PY") == "🐍"
        assert _get_file_emoji("SCRIPT.PY") == "🐍"
        assert _get_file_emoji("Script.Py") == "🐍"

    def test_no_extension(self) -> None:
        """Test archivos sin extensión."""
        assert _get_file_emoji("README") == "📄"
        assert _get_file_emoji("Makefile") == "📄"

    def test_hidden_files(self) -> None:
        """Test archivos ocultos."""
        # .gitignore no tiene extensión, por lo que usa el emoji por defecto
        assert _get_file_emoji(".gitignore") == "📄"
        assert _get_file_emoji(".env") == "📄"
        assert _get_file_emoji(".bashrc") == "📄"  # Sin extensión conocida


class TestFormatSize:
    """Tests para la función _format_size."""

    def test_zero_bytes(self) -> None:
        """Test formateo de 0 bytes."""
        assert _format_size(0) == "0 B"

    def test_bytes(self) -> None:
        """Test formateo de bytes."""
        assert _format_size(512) == "512.0 B"
        assert _format_size(1023) == "1023.0 B"

    def test_kilobytes(self) -> None:
        """Test formateo de kilobytes."""
        assert _format_size(1024) == "1.0 KB"
        assert _format_size(1536) == "1.5 KB"
        assert _format_size(2048) == "2.0 KB"

    def test_megabytes(self) -> None:
        """Test formateo de megabytes."""
        assert _format_size(1024 * 1024) == "1.0 MB"
        assert _format_size(1024 * 1024 * 1.5) == "1.5 MB"
        assert _format_size(1024 * 1024 * 2) == "2.0 MB"

    def test_gigabytes(self) -> None:
        """Test formateo de gigabytes."""
        assert _format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert _format_size(1024 * 1024 * 1024 * 1.5) == "1.5 GB"
        assert _format_size(1024 * 1024 * 1024 * 2) == "2.0 GB"

    def test_terabytes(self) -> None:
        """Test formateo de terabytes."""
        assert _format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
        assert _format_size(1024 * 1024 * 1024 * 1024 * 1.5) == "1.5 TB"

    def test_petabytes(self) -> None:
        """Test formateo de petabytes."""
        assert _format_size(1024 * 1024 * 1024 * 1024 * 1024) == "1.0 PB"
        assert _format_size(1024 * 1024 * 1024 * 1024 * 1024 * 2) == "2.0 PB"

    def test_large_numbers(self) -> None:
        """Test formateo de números muy grandes."""
        # 5 TB
        size_5tb = 5 * 1024 * 1024 * 1024 * 1024
        assert _format_size(size_5tb) == "5.0 TB"

        # 10 PB
        size_10pb = 10 * 1024 * 1024 * 1024 * 1024 * 1024
        assert _format_size(size_10pb) == "10.0 PB"

    def test_precision(self) -> None:
        """Test precisión decimal."""
        # 1.5 KB
        assert _format_size(1536) == "1.5 KB"

        # 1.25 MB
        assert _format_size(1024 * 1024 * 1.25) == "1.2 MB"  # Redondeado a 1 decimal

        # 1.75 GB
        assert _format_size(1024 * 1024 * 1024 * 1.75) == "1.8 GB"  # Redondeado
