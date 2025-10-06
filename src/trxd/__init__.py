# Fichero: src/trxd/__init__.py (versión refactorizada)

import argparse
import csv
import json
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, NamedTuple, Tuple, Union

import yaml
from typing_extensions import TypeAlias

# Type aliases
TreeItem: TypeAlias = Tuple[Path, List[str], List[str], Dict[str, Any]]
TreeGenerator: TypeAlias = Generator[TreeItem, None, None]


class FileMetadata(NamedTuple):
    """File metadata"""

    size: int
    modified: datetime


class DirectoryMetadata(NamedTuple):
    """Directory metadata"""

    file_count: int
    total_size: int
    modified: datetime


class FileTypeDetector:
    """Handles file type detection and emoji mapping"""

    EMOJI_MAP = {
        # Documents
        ".pdf": "📄",
        ".doc": "📝",
        ".docx": "📝",
        ".txt": "📄",
        ".md": "📝",
        ".rst": "📝",
        ".rtf": "📄",
        # Images
        ".jpg": "🖼️",
        ".jpeg": "🖼️",
        ".png": "🖼️",
        ".gif": "🖼️",
        ".bmp": "🖼️",
        ".svg": "🖼️",
        ".webp": "🖼️",
        ".ico": "🖼️",
        ".tiff": "🖼️",
        ".tif": "🖼️",
        # Videos
        ".mp4": "🎥",
        ".avi": "🎥",
        ".mkv": "🎥",
        ".mov": "🎥",
        ".wmv": "🎥",
        ".flv": "🎥",
        ".webm": "🎥",
        ".m4v": "🎥",
        # Audio
        ".mp3": "🎵",
        ".wav": "🎵",
        ".flac": "🎵",
        ".aac": "🎵",
        ".ogg": "🎵",
        ".m4a": "🎵",
        ".wma": "🎵",
        # Source code
        ".py": "🐍",
        ".js": "📜",
        ".ts": "📜",
        ".jsx": "📜",
        ".tsx": "📜",
        ".html": "🌐",
        ".htm": "🌐",
        ".css": "🎨",
        ".scss": "🎨",
        ".sass": "🎨",
        ".php": "🐘",
        ".rb": "💎",
        ".go": "🐹",
        ".rs": "🦀",
        ".java": "☕",
        ".c": "⚙️",
        ".cpp": "⚙️",
        ".cxx": "⚙️",
        ".h": "⚙️",
        ".hpp": "⚙️",
        ".cs": "🔷",
        ".vb": "🔷",
        ".swift": "🦉",
        ".kt": "🟣",
        ".scala": "🔺",
        ".r": "📊",
        ".m": "🍎",
        ".sh": "🐚",
        ".bash": "🐚",
        ".zsh": "🐚",
        ".fish": "🐚",
        ".ps1": "💻",
        ".bat": "💻",
        ".cmd": "💻",
        # Data
        ".json": "📋",
        ".xml": "📋",
        ".yaml": "📋",
        ".yml": "📋",
        ".csv": "📊",
        ".xlsx": "📊",
        ".xls": "📊",
        ".sql": "🗄️",
        ".db": "🗄️",
        ".sqlite": "🗄️",
        ".sqlite3": "🗄️",
        # Configuration
        ".ini": "⚙️",
        ".cfg": "⚙️",
        ".conf": "⚙️",
        ".config": "⚙️",
        ".toml": "⚙️",
        ".env": "🔐",
        ".gitignore": "🙈",
        ".dockerfile": "🐳",
        ".dockerignore": "🐳",
        # Compressed
        ".zip": "📦",
        ".rar": "📦",
        ".7z": "📦",
        ".tar": "📦",
        ".gz": "📦",
        ".bz2": "📦",
        ".xz": "📦",
        # Executables
        ".exe": "⚡",
        ".msi": "⚡",
        ".deb": "📱",
        ".rpm": "📱",
        ".dmg": "📱",
        ".app": "📱",
        ".run": "⚡",
        # Fonts
        ".ttf": "🔤",
        ".otf": "🔤",
        ".woff": "🔤",
        ".woff2": "🔤",
        # Others
        ".lock": "🔒",
        ".log": "📋",
        ".tmp": "🗑️",
        ".bak": "💾",
        ".old": "🗑️",
        ".orig": "🗑️",
    }

    @classmethod
    def get_emoji(cls, filename: str) -> str:
        """Get emoji for file type based on extension"""
        extension = Path(filename).suffix.lower()
        return cls.EMOJI_MAP.get(extension, "📄")

    @classmethod
    def format_size(cls, size_bytes: int) -> str:
        """Format size in bytes to readable representation"""
        if size_bytes == 0:
            return "0 B"

        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} PB"


class MetadataCollector:
    """Handles metadata collection for files and directories"""

    @staticmethod
    def collect_file_metadata(file_path: Path) -> FileMetadata:
        """Collect metadata for a single file"""
        try:
            stat = file_path.stat()
            return FileMetadata(size=stat.st_size, modified=datetime.fromtimestamp(stat.st_mtime))
        except (OSError, IOError):
            return FileMetadata(size=0, modified=datetime.min)

    @staticmethod
    def collect_directory_metadata(dir_path: Path, filenames: List[str]) -> DirectoryMetadata:
        """Collect metadata for a directory"""
        total_size = 0
        dir_modified = datetime.min

        try:
            dir_stat = dir_path.stat()
            dir_modified = datetime.fromtimestamp(dir_stat.st_mtime)
        except (OSError, IOError):
            pass

        return DirectoryMetadata(
            file_count=len(filenames), total_size=total_size, modified=dir_modified
        )

    @classmethod
    def collect_metadata(
        cls, dirpath: Path, filenames: List[str], show_metadata: bool
    ) -> Dict[str, Any]:
        """Collect all metadata for a directory"""
        if not show_metadata:
            return {}

        # File metadata
        file_metadata = {}
        total_size = 0

        for filename in filenames:
            file_path = dirpath / filename
            file_meta = cls.collect_file_metadata(file_path)
            file_metadata[filename] = file_meta
            total_size += file_meta.size

        # Directory metadata
        dir_metadata = cls.collect_directory_metadata(dirpath, filenames)
        dir_metadata = dir_metadata._replace(total_size=total_size)

        return {"files": file_metadata, "directory": dir_metadata}


class TreeBuilder:
    """Builds directory tree structure with filtering and metadata"""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.metadata_collector = MetadataCollector()

    def is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded based on filters"""
        exclude_patterns = iter(self.args.exclude)
        exclude_dir_patterns = iter(self.args.exclude_dir)
        exclude_file_patterns = iter(self.args.exclude_file)

        # Check general patterns
        if any(path.match(pattern) for pattern in exclude_patterns if pattern):
            return True

        # Check specific directory patterns
        if path.is_dir() and any(
            path.match(pattern) for pattern in exclude_dir_patterns if pattern
        ):
            return True

        # Check specific file patterns
        return path.is_file() and any(
            path.match(pattern) for pattern in exclude_file_patterns if pattern
        )

    def build_tree(self, directory: Path) -> TreeGenerator:
        """Generate directory structure with filtering and metadata"""
        import os

        for dirpath_str, dirnames, filenames in os.walk(directory, topdown=True):
            dirpath = Path(dirpath_str)

            # Filter directories (intelligent pruning)
            filtered_dirs = (d for d in sorted(dirnames) if not self.is_excluded(dirpath / d))
            dirnames[:] = list(filtered_dirs)

            # Filter files
            filtered_files = (f for f in sorted(filenames) if not self.is_excluded(dirpath / f))
            filenames = list(filtered_files)

            # Collect metadata
            metadata = self.metadata_collector.collect_metadata(
                dirpath, filenames, self.args.show_metadata
            )

            yield dirpath, dirnames, filenames, metadata


class Renderer(ABC):
    """Abstract base class for all renderers"""

    def __init__(self, start_path: Path, show_metadata: bool = False):
        self.start_path = start_path
        self.show_metadata = show_metadata

    @abstractmethod
    def render(self, tree_generator: TreeGenerator) -> None:
        """Render the tree structure"""
        pass

    def _get_relative_path(self, path: Path) -> str:
        """Get relative path string"""
        try:
            rel_path = path.relative_to(self.start_path)
            return str(rel_path) if rel_path != Path(".") else "."
        except ValueError:
            return str(path)


class FlatRenderer(Renderer):
    """Renders tree in flat format with full paths"""

    def render(self, tree_generator: TreeGenerator) -> None:
        for dirpath, _dirnames, filenames, metadata in tree_generator:
            # Show directory
            rel_path = self._get_relative_path(dirpath)
            if rel_path != ".":
                if self.show_metadata and metadata:
                    dir_meta = metadata.get("directory")
                    if dir_meta:
                        print(
                            f"{rel_path} [{dir_meta.file_count} files, "
                            f"{FileTypeDetector.format_size(dir_meta.total_size)}]"
                        )
                    else:
                        print(rel_path)
                else:
                    print(rel_path)

            # Show files
            for filename in filenames:
                file_path = dirpath / filename
                rel_file_path = self._get_relative_path(file_path)

                if self.show_metadata and metadata and "files" in metadata:
                    file_meta = metadata["files"].get(filename)
                    if file_meta:
                        mod_date = file_meta.modified.strftime("%Y-%m-%d %H:%M")
                        size_str = FileTypeDetector.format_size(file_meta.size)
                        print(f"{rel_file_path} [{size_str}, {mod_date}]")
                    else:
                        print(rel_file_path)
                else:
                    print(rel_file_path)


class CSVRenderer(Renderer):
    """Renders tree in CSV format"""

    def render(self, tree_generator: TreeGenerator) -> None:
        headers = ["type", "path", "name", "extension"]
        if self.show_metadata:
            headers.extend(["size", "modified", "file_count", "total_size"])

        writer = csv.writer(sys.stdout)
        writer.writerow(headers)

        for dirpath, _dirnames, filenames, metadata in tree_generator:
            # Directory row
            rel_path = self._get_relative_path(dirpath)
            row = ["directory", rel_path, dirpath.name, ""]

            if self.show_metadata and metadata:
                dir_meta = metadata.get("directory")
                if dir_meta:
                    row.extend(
                        [
                            "0",  # Directory size
                            dir_meta.modified.strftime("%Y-%m-%d %H:%M:%S"),
                            str(dir_meta.file_count),
                            str(dir_meta.total_size),
                        ]
                    )
                else:
                    row.extend(["", "", "", ""])
            elif self.show_metadata:
                row.extend(["", "", "", ""])

            writer.writerow(row)

            # File rows
            for filename in filenames:
                file_path = dirpath / filename
                rel_file_path = self._get_relative_path(file_path)
                extension = file_path.suffix[1:] if file_path.suffix else ""

                row = ["file", rel_file_path, filename, extension]

                if self.show_metadata and metadata and "files" in metadata:
                    file_meta = metadata["files"].get(filename)
                    if file_meta:
                        row.extend(
                            [
                                str(file_meta.size),
                                file_meta.modified.strftime("%Y-%m-%d %H:%M:%S"),
                                "",
                                "",  # file_count and total_size empty for files
                            ]
                        )
                    else:
                        row.extend(["", "", "", ""])
                elif self.show_metadata:
                    row.extend(["", "", "", ""])

                writer.writerow(row)


class TreeRenderer(Renderer):
    """Renders tree in tree format with ASCII connectors"""

    def __init__(self, start_path: Path, show_metadata: bool = False, use_emoji: bool = True):
        super().__init__(start_path, show_metadata)
        self.use_emoji = use_emoji

    def render(self, tree_generator: TreeGenerator) -> None:
        # Build complete structure for tree rendering
        tree_structure: Dict[str, Union[Dict[str, Any], None]] = {}
        dir_map = {self.start_path: tree_structure}
        metadata_map = {}

        # Process all elements
        for dirpath, _dirnames, _filenames, metadata in tree_generator:
            current_level_tree = dir_map.get(dirpath, {})
            metadata_map[dirpath] = metadata

            # Add subdirectories
            for d_name in _dirnames:
                subdir_dict: Dict[str, Union[Dict[str, Any], None]] = {}
                current_level_tree[d_name] = subdir_dict
                dir_map[dirpath / d_name] = subdir_dict

            # Add files
            for f_name in _filenames:
                current_level_tree[f_name] = None

        # Render the built tree
        self._render_recursive(tree_structure, "", dir_map, metadata_map)

    def _render_recursive(
        self,
        tree: Dict[str, Union[Dict[str, Any], None]],
        prefix: str,
        dir_map: Dict[Path, Dict[str, Union[Dict[str, Any], None]]],
        metadata_map: Dict[Path, Dict[str, Any]],
    ) -> None:
        """Render tree recursively"""
        entries = list(tree.items())

        for i, (name, subtree) in enumerate(entries):
            is_last = i == (len(entries) - 1)
            connector = "└── " if is_last else "├── "

            if isinstance(subtree, dict):
                # Directory
                icon = "📁 " if self.use_emoji else "[d] "
                name_with_meta = self._get_directory_name_with_metadata(
                    name, subtree, dir_map, metadata_map
                )
                print(f"{prefix}{connector}{icon}{name_with_meta}")

                # Recursive call for subdirectories
                extension = "    " if is_last else "│   "
                self._render_recursive(subtree, prefix + extension, dir_map, metadata_map)
            else:
                # File
                icon = FileTypeDetector.get_emoji(name) + " " if self.use_emoji else "[f] "
                name_with_meta = self._get_file_name_with_metadata(
                    name, tree, dir_map, metadata_map
                )
                print(f"{prefix}{connector}{icon}{name_with_meta}")

    def _get_directory_name_with_metadata(
        self,
        name: str,
        subtree: Dict[str, Any],
        dir_map: Dict[Path, Dict[str, Any]],
        metadata_map: Dict[Path, Dict[str, Any]],
    ) -> str:
        """Get directory name with metadata"""
        if not self.show_metadata:
            return name

        for path, tree_dict in dir_map.items():
            if tree_dict is subtree and path in metadata_map:
                dir_metadata = metadata_map[path].get("directory")
                if dir_metadata:
                    return (
                        f"{name} [{dir_metadata.file_count} files, "
                        f"{FileTypeDetector.format_size(dir_metadata.total_size)}, "
                        f"{dir_metadata.modified.strftime('%Y-%m-%d %H:%M')}]"
                    )
        return name

    def _get_file_name_with_metadata(
        self,
        name: str,
        tree: Dict[str, Any],
        dir_map: Dict[Path, Dict[str, Any]],
        metadata_map: Dict[Path, Dict[str, Any]],
    ) -> str:
        """Get file name with metadata"""
        if not self.show_metadata:
            return name

        for path, tree_dict in dir_map.items():
            if name in tree_dict and tree_dict[name] is None and path in metadata_map:
                file_metadata = metadata_map[path].get("files", {}).get(name)
                if file_metadata:
                    return (
                        f"{name} [{FileTypeDetector.format_size(file_metadata.size)}, "
                        f"{file_metadata.modified.strftime('%Y-%m-%d %H:%M')}]"
                    )
        return name


class JSONRenderer(Renderer):
    """Renders tree in JSON format"""

    def render(self, tree_generator: TreeGenerator) -> None:
        tree_structure = self._build_complete_structure(tree_generator)
        print(json.dumps(tree_structure, indent=2, default=str))

    def _build_complete_structure(self, tree_generator: TreeGenerator) -> Dict[str, Any]:
        """Build complete tree structure for JSON output"""
        tree_structure: Dict[str, Any] = {}
        dir_map = {self.start_path: tree_structure}
        dir_metadata_map = {}

        for dirpath, dirnames, filenames, metadata in tree_generator:
            current_level_tree = dir_map.get(dirpath, {})

            # Process subdirectories
            for d_name in dirnames:
                current_level_tree[d_name] = {}
                dir_map[dirpath / d_name] = current_level_tree[d_name]

            # Process files
            for f_name in filenames:
                if self.show_metadata and metadata and "files" in metadata:
                    file_meta = metadata["files"].get(f_name)
                    if file_meta:
                        current_level_tree[f_name] = {
                            "type": "file",
                            "size": file_meta.size,
                            "modified": file_meta.modified.isoformat(),
                        }
                    else:
                        current_level_tree[f_name] = {"type": "file"}
                else:
                    current_level_tree[f_name] = None

            # Save directory metadata
            if self.show_metadata and metadata and "directory" in metadata:
                dir_metadata_map[dirpath] = metadata["directory"]

        # Add directory metadata
        if self.show_metadata:
            self._add_directory_metadata(tree_structure, dir_map, dir_metadata_map)

        return tree_structure

    def _add_directory_metadata(
        self,
        tree_structure: Dict[str, Any],
        dir_map: Dict[Path, Dict[str, Any]],
        dir_metadata_map: Dict[Path, DirectoryMetadata],
    ) -> None:
        """Add directory metadata to tree structure"""
        for dirpath, tree_dict in dir_map.items():
            if dirpath in dir_metadata_map:
                dir_meta = dir_metadata_map[dirpath]
                if dirpath != self.start_path:
                    # Find parent and replace reference
                    for _parent_path, parent_tree in dir_map.items():
                        if isinstance(parent_tree, dict):
                            for name, child in parent_tree.items():
                                if child is tree_dict:
                                    parent_tree[name] = {
                                        "type": "directory",
                                        "file_count": dir_meta.file_count,
                                        "total_size": dir_meta.total_size,
                                        "modified": dir_meta.modified.isoformat(),
                                        "contents": tree_dict,
                                    }
                                    break
                else:
                    # Root directory
                    tree_structure["_metadata"] = {
                        "file_count": dir_meta.file_count,
                        "total_size": dir_meta.total_size,
                        "modified": dir_meta.modified.isoformat(),
                    }


class YAMLRenderer(JSONRenderer):
    """Renders tree in YAML format"""

    def render(self, tree_generator: TreeGenerator) -> None:
        tree_structure = self._build_complete_structure(tree_generator)
        print(
            yaml.dump(
                tree_structure,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
            )
        )


class TreeApplication:
    """Main application class that orchestrates the tree listing process"""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description="List the contents of a directory with advanced filters."
        )
        parser.add_argument(
            "path", nargs="?", default=".", help="The path to the directory to list."
        )
        parser.add_argument(
            "--format",
            choices=["tree", "ascii", "json", "yaml", "flat", "csv"],
            default="tree",
            help="Output format.",
        )
        parser.add_argument(
            "-x",
            "--exclude",
            action="append",
            default=[],
            help="Pattern to exclude (files and directories).",
        )
        parser.add_argument(
            "-xd",
            "--exclude-dir",
            action="append",
            default=[],
            help="Pattern to exclude (only directories).",
        )
        parser.add_argument(
            "-xf",
            "--exclude-file",
            action="append",
            default=[],
            help="Pattern to exclude (only files).",
        )
        parser.add_argument(
            "-m",
            "--show-metadata",
            action="store_true",
            help="Show metadata (size, modification date) for files and directories.",
        )
        parser.add_argument(
            "--no-emoji",
            action="store_true",
            help="Disable emojis in tree format (use ASCII characters instead).",
        )
        return parser

    def _setup_encoding(self) -> None:
        """Setup UTF-8 encoding for Windows"""
        if sys.platform == "win32":
            import codecs
            import inspect

            # Check if we are in a test
            frame = inspect.currentframe()
            in_test = False
            while frame:
                if "pytest" in str(frame.f_code.co_filename) or "test_" in frame.f_code.co_name:
                    in_test = True
                    break
                frame = frame.f_back

            if not in_test:
                try:
                    if hasattr(sys.stdout, "detach"):
                        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
                    if hasattr(sys.stderr, "detach"):
                        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
                except (AttributeError, OSError):
                    pass

    def _get_renderer(self, args: argparse.Namespace, start_path: Path) -> Renderer:
        """Get appropriate renderer based on format"""
        if args.format == "tree":
            return TreeRenderer(start_path, args.show_metadata, not args.no_emoji)
        elif args.format == "ascii":
            return TreeRenderer(start_path, args.show_metadata, False)
        elif args.format == "flat":
            return FlatRenderer(start_path, args.show_metadata)
        elif args.format == "csv":
            return CSVRenderer(start_path, args.show_metadata)
        elif args.format == "json":
            return JSONRenderer(start_path, args.show_metadata)
        elif args.format == "yaml":
            return YAMLRenderer(start_path, args.show_metadata)
        else:
            raise ValueError(f"Unknown format: {args.format}")

    def run(self) -> None:
        """Main entry point"""
        self._setup_encoding()
        args = self.parser.parse_args()
        start_path = Path(args.path).resolve()

        if not start_path.is_dir():
            print(f"Error: The path '{start_path}' is not a valid directory.", file=sys.stderr)
            sys.exit(1)

        # Build tree and render
        tree_builder = TreeBuilder(args)
        tree_generator = tree_builder.build_tree(start_path)
        renderer = self._get_renderer(args, start_path)
        renderer.render(tree_generator)


# Compatibility functions for existing tests
def build_tree(directory: Path, args: argparse.Namespace) -> TreeGenerator:
    """Compatibility function for existing tests"""
    tree_builder = TreeBuilder(args)
    return tree_builder.build_tree(directory)


def is_excluded(path: Path, args: argparse.Namespace) -> bool:
    """Compatibility function for existing tests"""
    tree_builder = TreeBuilder(args)
    return tree_builder.is_excluded(path)


def render_tree(tree_generator: TreeGenerator, start_path: Path = Path("."),
                use_emoji: bool = True, show_metadata: bool = False) -> None:
    """Compatibility function for existing tests"""
    renderer = TreeRenderer(start_path, show_metadata, use_emoji)
    renderer.render(tree_generator)


def render_flat(tree_generator: TreeGenerator, start_path: Path = Path("."),
                show_metadata: bool = False) -> None:
    """Compatibility function for existing tests"""
    renderer = FlatRenderer(start_path, show_metadata)
    renderer.render(tree_generator)


def render_csv(tree_generator: TreeGenerator, start_path: Path = Path("."),
               show_metadata: bool = False) -> None:
    """Compatibility function for existing tests"""
    renderer = CSVRenderer(start_path, show_metadata)
    renderer.render(tree_generator)


def _format_size(size_bytes: int) -> str:
    """Compatibility function for existing tests"""
    return FileTypeDetector.format_size(size_bytes)


def _get_file_emoji(filename: str) -> str:
    """Compatibility function for existing tests"""
    return FileTypeDetector.get_emoji(filename)


def main() -> None:
    """Main entry point for the command-line tool"""
    app = TreeApplication()
    app.run()


if __name__ == "__main__":
    main()
