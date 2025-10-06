# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning (CalVer)](https://calver.org/).

## [25.10.5] - 2025-10-06

### Changed

- Translated all comments and docstrings to English for consistency
- Updated all test files to use English docstrings and comments
- Improved code readability and international accessibility

### Fixed

- Fixed mypy type checking errors in test_utils.py
- Corrected type annotations for _format_size function calls

## [25.10.4] - 2025-10-06

### Fixed

- Added missing `typing_extensions` dependency to fix `uvx trxd` execution
- Fixed ModuleNotFoundError when using `uvx` or installing from PyPI

## [25.10.3] - 2025-10-06

### Changed

- Updated all GitHub repository URLs to point to renamed `trxd` repository
- Updated git remote origin to use new repository location

## [25.10.2] - 2025-10-06

### Changed

- Completely renamed package from `ls_tree` to `trxd` for consistency
- Renamed source directory from `src/ls_tree/` to `src/trxd/`
- Updated all imports and references throughout codebase
- Updated CLI command from `ls-tree` to `trxd`
- Updated all documentation and tests to use `trxd`

## [25.10.1] - 2025-10-06

### Changed

- Updated documentation to use `trxd` instead of `ls-tree` for consistency
- Updated README.md, CHANGELOG.md, and test files
- Updated pyproject.toml script entry point

## [25.10.0] - 2025-10-06

### Added

- Initial release of trxd (formerly ls-tree)
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
- Comprehensive test suite with pytest
- CI/CD pipeline with GitHub Actions
- Automated PyPI publishing workflow

### Fixed

- Fixed metadata rendering in tree and ASCII formats - metadata now displays correctly when using `--show-metadata` flag
- Resolved Unicode encoding issues on Windows by setting UTF-8 encoding for stdout/stderr
- Fixed test compatibility issues with pytest by detecting test environment and avoiding global state modifications
- Fixed linting errors (E501, W293, F401, SIM117, B007) across codebase
- Fixed cross-platform test compatibility for case sensitivity
- Fixed CI/CD workflow dependencies and configuration

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
