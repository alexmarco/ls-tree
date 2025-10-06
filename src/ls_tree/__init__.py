# Fichero: src/ls_tree/__init__.py (versión mejorada con tipos y documentación)

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, NamedTuple, Tuple, Union

import yaml
from typing_extensions import TypeAlias


class FileMetadata(NamedTuple):
    """Metadatos de un archivo."""

    size: int
    modified: datetime


class DirectoryMetadata(NamedTuple):
    """Metadatos de un directorio."""

    file_count: int
    total_size: int
    modified: datetime


# Type aliases para simplificar tipos complejos
TreeItem: TypeAlias = Tuple[Path, List[str], List[str], Dict[str, Any]]
TreeGenerator: TypeAlias = Generator[TreeItem, None, None]


def is_excluded(path: Path, args: argparse.Namespace) -> bool:
    """
    Comprueba si un fichero o directorio debe ser excluido según los filtros.

    Parameters
    ----------
    path : Path
        La ruta del fichero o directorio a verificar.
    args : argparse.Namespace
        Los argumentos de línea de comandos que contienen los patrones de exclusión.

    Returns
    -------
    bool
        True si el path debe ser excluido, False en caso contrario.

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

    # Verificar patrones generales
    if any(path.match(pattern) for pattern in exclude_patterns if pattern):
        return True

    # Verificar patrones específicos de directorio
    if path.is_dir() and any(path.match(pattern) for pattern in exclude_dir_patterns if pattern):
        return True

    # Verificar patrones específicos de fichero
    return path.is_file() and any(
        path.match(pattern) for pattern in exclude_file_patterns if pattern
    )


def build_tree(directory: Path, args: argparse.Namespace) -> TreeGenerator:
    """
    Genera la estructura del directorio usando el moderno pathlib.Path.walk.

    Parameters
    ----------
    directory : Path
        El directorio raíz desde el cual construir el árbol.
    args : argparse.Namespace
        Los argumentos de línea de comandos que contienen los filtros de exclusión.

    Yields
    ------
    Tuple[Path, List[str], List[str], Dict[str, Any]]
        Tupla que contiene (dirpath, dirnames, filenames, metadata) para cada directorio.
        Los directorios y ficheros ya están filtrados según los criterios de exclusión.
        metadata contiene información sobre archivos y directorios si está habilitada.

    Notes
    -----
    Esta función utiliza la poda inteligente modificando 'dirnames' in-place
    para evitar explorar directorios excluidos, mejorando la eficiencia.
    Al ser un generador, permite procesar directorios grandes de forma eficiente
    sin cargar toda la estructura en memoria.

    Examples
    --------
    >>> args = argparse.Namespace(exclude=['*.pyc'], exclude_dir=['__pycache__'])
    >>> for dirpath, dirs, files in build_tree(Path('src/'), args):
    ...     print(f"Directorio: {dirpath}, Subdirs: {len(dirs)}, Archivos: {len(files)}")
    """
    # Usamos os.walk() para compatibilidad con Python 3.8+
    import os

    for dirpath_str, dirnames, filenames in os.walk(directory, topdown=True):
        dirpath = Path(dirpath_str)
        # --- PODA INTELIGENTE ---
        # Filtramos directorios usando iteradores para mayor eficiencia
        filtered_dirs = (d for d in sorted(dirnames) if not is_excluded(dirpath / d, args))
        dirnames[:] = list(filtered_dirs)

        # --- FILTRADO DE FICHEROS ---
        filtered_files = (f for f in sorted(filenames) if not is_excluded(dirpath / f, args))
        filenames = list(filtered_files)

        # --- RECOLECCIÓN DE METADATOS ---
        metadata: Dict[str, Any] = {}

        if args.show_metadata:
            # Metadatos de archivos
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
                    # Archivo no accesible
                    file_metadata[filename] = FileMetadata(size=0, modified=datetime.min)

            # Metadatos del directorio
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

        # Yield del directorio procesado
        yield dirpath, dirnames, filenames, metadata


# --- El resto del script (renderizadores y función main) no necesita cambios ---


def _get_file_emoji(filename: str) -> str:
    """
    Obtiene un emoji apropiado para el tipo de archivo basado en su extensión.

    Parameters
    ----------
    filename : str
        Nombre del archivo incluyendo extensión.

    Returns
    -------
    str
        Emoji apropiado para el tipo de archivo, o emoji por defecto si no se encuentra.
    """
    # Obtener extensión del archivo
    extension = Path(filename).suffix.lower()

    # Mapeo de extensiones a emojis
    emoji_map = {
        # Documentos
        ".pdf": "📄",
        ".doc": "📝",
        ".docx": "📝",
        ".txt": "📄",
        ".md": "📝",
        ".rst": "📝",
        ".rtf": "📄",
        # Imágenes
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
        # Código fuente
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
        # Datos
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
        # Configuración
        ".ini": "⚙️",
        ".cfg": "⚙️",
        ".conf": "⚙️",
        ".config": "⚙️",
        ".toml": "⚙️",
        ".env": "🔐",
        ".gitignore": "🙈",
        ".dockerfile": "🐳",
        ".dockerignore": "🐳",
        # Comprimidos
        ".zip": "📦",
        ".rar": "📦",
        ".7z": "📦",
        ".tar": "📦",
        ".gz": "📦",
        ".bz2": "📦",
        ".xz": "📦",
        # Ejecutables
        ".exe": "⚡",
        ".msi": "⚡",
        ".deb": "📱",
        ".rpm": "📱",
        ".dmg": "📱",
        ".app": "📱",
        ".run": "⚡",
        # Fuentes
        ".ttf": "🔤",
        ".otf": "🔤",
        ".woff": "🔤",
        ".woff2": "🔤",
        # Otros
        ".lock": "🔒",
        ".log": "📋",
        ".tmp": "🗑️",
        ".bak": "💾",
        ".old": "🗑️",
        ".orig": "🗑️",
    }

    return emoji_map.get(extension, "📄")  # Emoji por defecto


def _format_size(size_bytes: int) -> str:
    """
    Formatea el tamaño en bytes a una representación legible.

    Parameters
    ----------
    size_bytes : int
        Tamaño en bytes.

    Returns
    -------
    str
        Tamaño formateado (ej: "1.2 KB", "3.4 MB").
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
    Renderiza la estructura en formato plano con rutas completas.

    Parameters
    ----------
    tree_generator : Generator[Tuple[Path, List[str], List[str], Dict[str, Any]], None, None]
        El generador de la estructura del directorio.
    start_path : Path, optional
        La ruta base para mostrar las rutas relativas, por defecto Path(".").
    show_metadata : bool, optional
        Si mostrar metadatos (tamaño, fecha) junto con las rutas.

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
        # Calcular ruta relativa
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
            # Si no es subdirectorio, mostrar ruta absoluta
            print(str(dirpath))

        # Mostrar archivos en este directorio
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
    Renderiza la estructura en formato de árbol con conectores ASCII.

    Parameters
    ----------
    tree_generator : Generator[Tuple[Path, List[str], List[str], Dict[str, Any]], None, None]
        El generador de la estructura del directorio.
    start_path : Path, optional
        La ruta base para mostrar las rutas relativas, por defecto Path(".").
    use_emoji : bool, optional
        Si usar emojis para representar directorios y ficheros, por defecto True.
    show_metadata : bool, optional
        Si mostrar metadatos (tamaño, fecha) junto con los nombres.

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
    # Construir estructura completa para renderizado en árbol
    tree_structure: Dict[str, Union[Dict[str, Any], None]] = {}
    dir_map: Dict[Path, Dict[str, Union[Dict[str, Any], None]]] = {start_path: tree_structure}
    metadata_map: Dict[Path, Dict[str, Any]] = {}

    # Procesar todos los elementos del generador
    for dirpath, _dirnames, _filenames, metadata in tree_generator:
        # Obtener el diccionario del directorio actual
        current_level_tree: Dict[str, Union[Dict[str, Any], None]] = dir_map.get(dirpath, {})
        metadata_map[dirpath] = metadata

        # Añadir subdirectorios
        for d_name in _dirnames:
            subdir_dict: Dict[str, Union[Dict[str, Any], None]] = {}
            current_level_tree[d_name] = subdir_dict
            dir_map[dirpath / d_name] = subdir_dict

        # Añadir archivos
        for f_name in _filenames:
            current_level_tree[f_name] = None

    # Renderizar el árbol construido
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
    Función auxiliar para renderizar recursivamente el árbol.

    Parameters
    ----------
    tree : Dict[str, Union[Dict[str, Any], None]]
        El árbol de directorios a renderizar.
    prefix : str
        El prefijo de espaciado para la indentación.
    use_emoji : bool
        Si usar emojis para representar directorios y ficheros.
    """
    entries = list(tree.items())

    for i, (name, subtree) in enumerate(entries):
        is_last: bool = i == (len(entries) - 1)
        connector: str = "└── " if is_last else "├── "

        if isinstance(subtree, dict):
            icon: str = "📁 " if use_emoji else "[d] "
            name_with_meta = name
            if show_metadata and dir_map and metadata_map:
                # Buscar metadatos del directorio
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
            # Usar emoji específico para el tipo de archivo si está habilitado
            icon = _get_file_emoji(name) + " " if use_emoji else "[f] "

            name_with_meta = name
            if show_metadata and dir_map and metadata_map:
                # Buscar metadatos del archivo
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
    Punto de entrada principal para la herramienta de línea de comandos.

    Esta función configura el parser de argumentos, valida la ruta de entrada,
    construye el árbol de directorios y renderiza la salida en el formato solicitado.

    Returns
    -------
    None
        Esta función no retorna valor, imprime la salida directamente.

    Raises
    ------
    SystemExit
        Sale con código 1 si la ruta proporcionada no es un directorio válido.
    """
    # Configurar codificación UTF-8 para Windows solo si no estamos en tests
    if sys.platform == "win32":
        # Verificar si estamos en un test
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
                # Si no se puede configurar UTF-8, continuar sin cambios
                pass
    parser = argparse.ArgumentParser(
        description="Lista el contenido de un directorio con filtros avanzados."
    )
    parser.add_argument("path", nargs="?", default=".", help="La ruta al directorio a listar.")
    parser.add_argument(
        "--format",
        choices=["tree", "ascii", "json", "yaml", "flat"],
        default="tree",
        help="Formato de salida.",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        action="append",
        default=[],
        help="Patrón a excluir (ficheros y directorios).",
    )
    parser.add_argument(
        "-xd",
        "--exclude-dir",
        action="append",
        default=[],
        help="Patrón a excluir (solo directorios).",
    )
    parser.add_argument(
        "-xf",
        "--exclude-file",
        action="append",
        default=[],
        help="Patrón a excluir (solo ficheros).",
    )
    parser.add_argument(
        "-m",
        "--show-metadata",
        action="store_true",
        help="Mostrar metadatos (tamaño, fecha de modificación) para archivos y directorios.",
    )
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Desactivar emojis en el formato tree (usar caracteres ASCII en su lugar).",
    )

    args: argparse.Namespace = parser.parse_args()
    start_path: Path = Path(args.path).resolve()

    if not start_path.is_dir():
        print(
            f"Error: La ruta '{start_path}' no es un directorio válido.",
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
        # Para formatos que necesitan estructura completa, reconstruir el árbol
        tree_structure: Dict[str, Any] = {}
        dir_map: Dict[Path, Dict[str, Any]] = {start_path: tree_structure}
        dir_metadata_map: Dict[Path, DirectoryMetadata] = {}

        for dirpath, dirnames, filenames, metadata in tree_generator:
            current_level_tree = dir_map.get(dirpath, {})

            # Procesar subdirectorios
            for d_name in dirnames:
                current_level_tree[d_name] = {}
                dir_map[dirpath / d_name] = current_level_tree[d_name]

            # Procesar archivos
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
                    # Sin metadata: formato simple tradicional
                    current_level_tree[f_name] = None

            # Guardar metadatos del directorio
            if args.show_metadata and metadata and "directory" in metadata:
                dir_metadata_map[dirpath] = metadata["directory"]

        # Añadir metadatos de directorios a la estructura solo si se solicitan
        if args.show_metadata:
            for dirpath, tree_dict in dir_map.items():
                if dirpath in dir_metadata_map:
                    dir_meta = dir_metadata_map[dirpath]
                    # Convertir el directorio a un objeto con metadatos
                    if dirpath != start_path:
                        # Encontrar el directorio padre y reemplazar la referencia
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
                        # Directorio raíz
                        tree_structure["_metadata"] = {
                            "file_count": dir_meta.file_count,
                            "total_size": dir_meta.total_size,
                            "modified": dir_meta.modified.isoformat(),
                        }
        else:
            # Sin metadata: mantener estructura simple tradicional
            # Los archivos ya están como None, los directorios como {}
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
