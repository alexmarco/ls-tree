# Fichero: src/trxd/__init__.py (versión mejorada con tipos y documentación)

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, NamedTuple, Tuple, Union

import yaml
from typing_extensions import TypeAlias


class FileMetadata(NamedTuple):
    """File metadata"""

    size: int
    modified: datetime


class DirectoryMetadata(NamedTuple):
    """Directory metadata"""

    file_count: int
    total_size: int
    modified: datetime


# Type aliases to simplify complex types
TreeItem: TypeAlias = Tuple[Path, List[str], List[str], Dict[str, Any]]
TreeGenerator: TypeAlias = Generator[TreeItem, None, None]


def is_excluded(path: Path, args: argparse.Namespace) -> bool:
    """
    Check if a file or directory should be excluded according to the filters.

    Parameters
    ----------
    path : Path
        The path of the file or directory to check.
    args : argparse.Namespace
        The command-line arguments that contain the exclusion patterns.

    Returns
    -------
    bool
        True if the path should be excluded, False otherwise.

    Examples
    --------
    >>> args = argparse.Namespace(exclude=['*.pyc'], exclude_dir=['__pycache__'])
    >>> is_excluded(Path('script.pyc'), args)
    True
    >>> is_excluded(Path('src/'), args)
    False
    """
    exclude_patterns: Iterator[str] = iter(args.exclude)
    exclude_dir_patterns: Iterator[str] = iter(args.exclude_dir)
    exclude_file_patterns: Iterator[str] = iter(args.exclude_file)

    # Check general patterns
    if any(path.match(pattern) for pattern in exclude_patterns if pattern):
        return True

    # Check specific directory patterns
    if path.is_dir() and any(path.match(pattern) for pattern in exclude_dir_patterns if pattern):
        return True

    # Check specific file patterns
    return path.is_file() and any(
        path.match(pattern) for pattern in exclude_file_patterns if pattern
    )


def build_tree(directory: Path, args: argparse.Namespace) -> TreeGenerator:
    """
    Generates the directory structure using the modern pathlib.Path.walk.

    Parameters
    ----------
    directory : Path
        The root directory from which to build the tree.
    args : argparse.Namespace
        The command-line arguments that contain the exclusion filters.

    Yields
    ------
    Tuple[Path, List[str], List[str], Dict[str, Any]]
        Tuple that contains (dirpath, dirnames, filenames, metadata) for each directory.
        The directories and files are already filtered according to the exclusion criteria.
        metadata contains information about files and directories if enabled.

    Notes
    -----
    This function uses the intelligent pruning modifying 'dirnames' in-place
    to avoid exploring excluded directories, improving efficiency.
    As a generator, it allows processing large directories efficiently without loading the entire
    structure into memory.

    Examples
    --------
    >>> args = argparse.Namespace(exclude=['*.pyc'], exclude_dir=['__pycache__'])
    >>> for dirpath, dirs, files in build_tree(Path('src/'), args):
    ...     print(f"Directorio: {dirpath}, Subdirs: {len(dirs)}, Archivos: {len(files)}")
    """
    # We use os.walk() for compatibility with Python 3.8+
    import os

    for dirpath_str, dirnames, filenames in os.walk(directory, topdown=True):
        dirpath = Path(dirpath_str)
        # --- INTELLIGENT PRUNING ---
        # Filter directories using iterators for greater efficiency
        filtered_dirs = (d for d in sorted(dirnames) if not is_excluded(dirpath / d, args))
        dirnames[:] = list(filtered_dirs)

        # --- FILE FILTERING ---
        filtered_files = (f for f in sorted(filenames) if not is_excluded(dirpath / f, args))
        filenames = list(filtered_files)

        # --- METADATA COLLECTION ---
        metadata: Dict[str, Any] = {}

        if args.show_metadata:
            # File metadata
            file_metadata: Dict[str, FileMetadata] = {}
            total_size = 0

            for filename in filenames:
                file_path = dirpath / filename
                try:
                    stat = file_path.stat()
                    file_metadata[filename] = FileMetadata(
                        size=stat.st_size,
                        modified=datetime.fromtimestamp(stat.st_mtime),
                    )
                    total_size += stat.st_size
                except (OSError, IOError):
                    # File not accessible
                    file_metadata[filename] = FileMetadata(size=0, modified=datetime.min)

            # Directory metadata
            try:
                dir_stat = dirpath.stat()
                dir_modified = datetime.fromtimestamp(dir_stat.st_mtime)
            except (OSError, IOError):
                dir_modified = datetime.min

            metadata = {
                "files": file_metadata,
                "directory": DirectoryMetadata(
                    file_count=len(filenames),
                    total_size=total_size,
                    modified=dir_modified,
                ),
            }

        # Yield the processed directory
        yield dirpath, dirnames, filenames, metadata

def _get_file_emoji(filename: str) -> str:
    """
    Get an appropriate emoji for the file type based on its extension.

    Parameters
    ----------
    filename : str
        The file name including the extension.

    Returns
    -------
    str
        Appropriate emoji for the file type, or default emoji if not found.
    """
    # Get the file extension
    extension = Path(filename).suffix.lower()

    # Mapping of extensions to emojis
    emoji_map = {
        # Documentos
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

    return emoji_map.get(extension, "📄")  # Default emoji


def _format_size(size_bytes: int) -> str:
    """
    Format the size in bytes to a readable representation.

    Parameters
    ----------
    size_bytes : int
        Size in bytes.

    Returns
    -------
    str
        Formatted size (e.g.: "1.2 KB", "3.4 MB").
    """
    if size_bytes == 0:
        return "0 B"

    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} PB"


def render_flat(
    tree_generator: TreeGenerator,
    start_path: Path = Path("."),
    show_metadata: bool = False,
) -> None:
    """
    Render the structure in flat format with full paths.

    Parameters
    ----------
    tree_generator : Generator[Tuple[Path, List[str], List[str], Dict[str, Any]], None, None]
        The generator of the directory structure.
    start_path : Path, optional
        The base path to show relative paths, default Path(".").
    show_metadata : bool, optional
        If show metadata (size, date) together with the paths.

    Examples
    --------
    >>> args = argparse.Namespace(exclude=['*.pyc'], exclude_dir=['__pycache__'])
    >>> gen = build_tree(Path('src/'), args)
    >>> render_flat(gen, Path('project/'))
    project/src
    project/src/main.py
    project/src/utils
    project/src/utils/helper.py
    """
    for dirpath, _dirnames, filenames, metadata in tree_generator:
        # Calculate relative path
        try:
            rel_path = dirpath.relative_to(start_path)
            if rel_path != Path("."):
                if show_metadata and metadata:
                    dir_meta = metadata.get("directory")
                    if dir_meta:
                        print(
                            f"{rel_path} [{dir_meta.file_count} files, "
                            f"{_format_size(dir_meta.total_size)}]"
                        )
                    else:
                        print(str(rel_path))
                else:
                    print(str(rel_path))
        except ValueError:
            # If not a subdirectory, show absolute path
            print(str(dirpath))

        # Show files in this directory
        for filename in filenames:
            file_path = dirpath / filename
            try:
                rel_file_path = file_path.relative_to(start_path)
                if show_metadata and metadata and "files" in metadata:
                    file_meta = metadata["files"].get(filename)
                    if file_meta:
                        mod_date = file_meta.modified.strftime("%Y-%m-%d %H:%M")
                        print(f"{rel_file_path} [{_format_size(file_meta.size)}, {mod_date}]")
                    else:
                        print(str(rel_file_path))
                else:
                    print(str(rel_file_path))
            except ValueError:
                print(str(file_path))


def render_tree(
    tree_generator: TreeGenerator,
    start_path: Path = Path("."),
    use_emoji: bool = True,
    show_metadata: bool = False,
) -> None:
    """
    Render the structure in tree format with ASCII connectors.

    Parameters
    ----------
    tree_generator : Generator[Tuple[Path, List[str], List[str], Dict[str, Any]], None, None]
        The generator of the directory structure.
    start_path : Path, optional
        The base path to show relative paths, default Path(".").
    use_emoji : bool, optional
        If use emojis to represent directories and files, default True.
    show_metadata : bool, optional
        If show metadata (size, date) together with the names.

    Examples
    --------
    >>> args = argparse.Namespace(exclude=['*.pyc'], exclude_dir=['__pycache__'])
    >>> gen = build_tree(Path('src/'), args)
    >>> render_tree(gen, use_emoji=False)
    ├── [d] src
    │   ├── [f] main.py
    │   └── [d] utils
    │       └── [f] helper.py
    """
    # Build complete structure for tree rendering
    tree_structure: Dict[str, Union[Dict[str, Any], None]] = {}
    dir_map: Dict[Path, Dict[str, Union[Dict[str, Any], None]]] = {start_path: tree_structure}
    metadata_map: Dict[Path, Dict[str, Any]] = {}

    # Process all elements of the generator
    for dirpath, _dirnames, _filenames, metadata in tree_generator:
        # Get the dictionary of the current directory
        current_level_tree: Dict[str, Union[Dict[str, Any], None]] = dir_map.get(dirpath, {})
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
    _render_tree_recursive(tree_structure, "", use_emoji, show_metadata, dir_map, metadata_map)


def _render_tree_recursive(
    tree: Dict[str, Union[Dict[str, Any], None]],
    prefix: str = "",
    use_emoji: bool = True,
    show_metadata: bool = False,
    dir_map: Union[Dict[Path, Dict[str, Union[Dict[str, Any], None]]], None] = None,
    metadata_map: Union[Dict[Path, Dict[str, Any]], None] = None,
) -> None:
    """
    Auxiliary function to render the tree recursively.

    Parameters
    ----------
    tree : Dict[str, Union[Dict[str, Any], None]]
        The tree of directories to render.
    prefix : str
        The prefix for the indentation.
    use_emoji : bool
        If use emojis to represent directories and files.
    """
    entries = list(tree.items())

    for i, (name, subtree) in enumerate(entries):
        is_last: bool = i == (len(entries) - 1)
        connector: str = "└── " if is_last else "├── "

        if isinstance(subtree, dict):
            icon: str = "📁 " if use_emoji else "[d] "
            name_with_meta = name
            if show_metadata and dir_map and metadata_map:
                # Search directory metadata
                for path, tree_dict in dir_map.items():
                    if tree_dict is subtree and path in metadata_map:
                        dir_metadata = metadata_map[path].get("directory")
                        if dir_metadata:
                            name_with_meta = (
                                f"{name} [{dir_metadata.file_count} files, "
                                f"{_format_size(dir_metadata.total_size)}, "
                                f"{dir_metadata.modified.strftime('%Y-%m-%d %H:%M')}]"
                            )
                        break
            print(f"{prefix}{connector}{icon}{name_with_meta}")
            extension: str = "    " if is_last else "│   "
            _render_tree_recursive(
                subtree, prefix + extension, use_emoji, show_metadata, dir_map, metadata_map
            )
        else:
            # Use specific emoji for the file type if enabled
            icon = _get_file_emoji(name) + " " if use_emoji else "[f] "

            name_with_meta = name
            if show_metadata and dir_map and metadata_map:
                # Search file metadata
                for path, tree_dict in dir_map.items():
                    if name in tree_dict and tree_dict[name] is None and path in metadata_map:
                        file_metadata = metadata_map[path].get("files", {}).get(name)
                        if file_metadata:
                            name_with_meta = (
                                f"{name} [{_format_size(file_metadata.size)}, "
                                f"{file_metadata.modified.strftime('%Y-%m-%d %H:%M')}]"
                            )
                        break
            print(f"{prefix}{connector}{icon}{name_with_meta}")


def main() -> None:
    """
    Main entry point for the command-line tool.

    This function configures the argument parser, validates the input path,
    builds the directory tree and renders the output in the requested format.

    Returns
    -------
    None
        This function does not return value, prints the output directly.

    Raises
    ------
    SystemExit
        Exit with code 1 if the provided path is not a valid directory.
    """
    # Configurar codificación UTF-8 para Windows solo si no estamos en tests
    if sys.platform == "win32":
        # Check if we are in a test
        import inspect

        frame = inspect.currentframe()
        in_test = False
        while frame:
            if "pytest" in str(frame.f_code.co_filename) or "test_" in frame.f_code.co_name:
                in_test = True
                break
            frame = frame.f_back

        if not in_test:
            try:
                import codecs

                if hasattr(sys.stdout, "detach"):
                    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
                if hasattr(sys.stderr, "detach"):
                    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
            except (AttributeError, OSError):
                # If UTF-8 cannot be configured, continue without changes
                pass
    parser = argparse.ArgumentParser(
        description="List the contents of a directory with advanced filters."
    )
    parser.add_argument("path", nargs="?", default=".", help="La ruta al directorio a listar.")
    parser.add_argument(
        "--format",
        choices=["tree", "ascii", "json", "yaml", "flat"],
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

    args: argparse.Namespace = parser.parse_args()
    start_path: Path = Path(args.path).resolve()

    if not start_path.is_dir():
        print(
            f"Error: The path '{start_path}' is not a valid directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    tree_generator: TreeGenerator = build_tree(start_path, args)

    if args.format == "tree":
        render_tree(
            tree_generator,
            start_path,
            use_emoji=not args.no_emoji,
            show_metadata=args.show_metadata,
        )
    elif args.format == "ascii":
        render_tree(
            tree_generator,
            start_path,
            use_emoji=False,
            show_metadata=args.show_metadata,
        )
    elif args.format == "flat":
        render_flat(tree_generator, start_path, show_metadata=args.show_metadata)
    elif args.format in ["json", "yaml"]:
        # For formats that need complete structure, rebuild the tree
        tree_structure: Dict[str, Any] = {}
        dir_map: Dict[Path, Dict[str, Any]] = {start_path: tree_structure}
        dir_metadata_map: Dict[Path, DirectoryMetadata] = {}

        for dirpath, dirnames, filenames, metadata in tree_generator:
            current_level_tree = dir_map.get(dirpath, {})

            # Process subdirectories
            for d_name in dirnames:
                current_level_tree[d_name] = {}
                dir_map[dirpath / d_name] = current_level_tree[d_name]

            # Process files
            for f_name in filenames:
                if args.show_metadata and metadata and "files" in metadata:
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
                    # Without metadata: simple traditional format
                    current_level_tree[f_name] = None

            # Save directory metadata
            if args.show_metadata and metadata and "directory" in metadata:
                dir_metadata_map[dirpath] = metadata["directory"]

        # Add directory metadata to the structure only if requested
        if args.show_metadata:
            for dirpath, tree_dict in dir_map.items():
                if dirpath in dir_metadata_map:
                    dir_meta = dir_metadata_map[dirpath]
                    # Convert the directory to an object with metadata
                    if dirpath != start_path:
                        # Find the parent directory and replace the reference
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
        else:
            # Without metadata: keep simple traditional structure
            # The files are already None, the directories are {}
            pass

        if args.format == "json":
            print(json.dumps(tree_structure, indent=2, default=str))
        elif args.format == "yaml":
            print(
                yaml.dump(
                    tree_structure,
                    indent=2,
                    allow_unicode=True,
                    default_flow_style=False,
                )
            )


if __name__ == "__main__":
    main()
