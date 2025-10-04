# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning (CalVer)](https://calver.org/).

## [2024.12.19] - 2024-12-19

### Added

- Initial release of ls-tree
- Multiple output formats: tree (with emojis), ASCII tree, flat list, JSON, and YAML
- Advanced filtering with glob patterns for files and directories
- Metadata support showing file sizes, modification dates, and directory statistics
- Memory-efficient generator-based processing for large directory structures
- File type-specific emojis for better visual identification
- Option to disable emojis (`--no-emoji`) for compatibility
- Comprehensive command-line interface with multiple filtering options
- Support for Python 3.8+ with modern pathlib usage
- Type hints and NumPy-style documentation throughout
- Cross-platform compatibility (Windows, macOS, Linux)

### Features

- **Tree formats**: Default emoji tree, ASCII tree, and emoji-disabled tree
- **Data formats**: JSON and YAML with integrated metadata structures
- **Filtering**: Exclude files, directories, or both using glob patterns
- **Metadata**: File sizes, modification dates, directory statistics
- **Performance**: Lazy evaluation and memory-efficient processing
- **Extensibility**: Clean architecture with separated concerns

### Technical Details

- Built with modern Python using pathlib.Path.walk()
- Generator-based architecture for memory efficiency
- Comprehensive type annotations with mypy support
- Ruff for fast linting and formatting
- Hatchling build system for packaging
- MIT license for maximum compatibility
