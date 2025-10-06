# trxd

A modern Python command-line tool for listing directory contents with advanced filtering and metadata support. Similar to `tree` but with more features and better performance.

## Features

- **Multiple output formats**: Tree (with emojis), ASCII tree, flat list, JSON, YAML, and CSV
- **Advanced filtering**: Exclude files and directories using glob patterns
- **Metadata support**: File sizes, modification dates, and directory statistics
- **Memory efficient**: Uses generators for large directory structures
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Modern Python**: Built with pathlib and type hints

## Installation

### Using pip

```bash
pip install trxd
```

### From source

```bash
git clone https://github.com/alexmarco/trxd.git
cd trxd
pip install -e .
```

### Using uv (recommended)

```bash
uv add trxd
```

## Usage

### Basic usage

```bash
# List current directory in tree format
trxd

# List specific directory
trxd /path/to/directory

# List with emoji icons (default)
trxd --format tree

# List with ASCII characters (no emojis)
trxd --format tree --no-emoji

# List with ASCII format (same as --no-emoji)
trxd --format ascii
```

### Output formats

```bash
# Tree format with emojis (default)
trxd --format tree

# Tree format with ASCII characters
trxd --format ascii

# Flat list format
trxd --format flat

# JSON format
trxd --format json

# YAML format
trxd --format yaml

# CSV format
trxd --format csv
```

### Filtering options

```bash
# Exclude files and directories
trxd --exclude "*.pyc" --exclude "__pycache__"

# Exclude only directories
trxd --exclude-dir "node_modules" --exclude-dir ".git"

# Exclude only files
trxd --exclude-file "*.log" --exclude-file "*.tmp"

# Multiple exclusions
trxd -x "*.pyc" -x "*.pyo" -xd "__pycache__" -xd ".git"
```

### Metadata support

```bash
# Show file sizes and modification dates
trxd --show-metadata

# Combine with different formats
trxd --format flat --show-metadata
trxd --format json --show-metadata
```

## Examples

### Basic directory listing

```bash
$ trxd src/
📁 src/
├── 📁 components/
│   ├── 🐍 Button.py
│   └── 🐍 Header.py
├── 📁 utils/
│   └── 🐍 helpers.py
└── 🐍 main.py
```

### Tree format without emojis

```bash
$ trxd --format tree --no-emoji src/
[d] src/
├── [d] components/
│   ├── [f] Button.py
│   └── [f] Header.py
├── [d] utils/
│   └── [f] helpers.py
└── [f] main.py
```

### ASCII tree format

```bash
$ trxd --format ascii src/
[d] src/
├── [d] components/
│   ├── [f] Button.py
│   └── [f] Header.py
├── [d] utils/
│   └── [f] helpers.py
└── [f] main.py
```

### Tree format with metadata

```bash
$ trxd --format tree --show-metadata src/
📁 src/ [4 files, 2.1 KB]
├── 📁 components/ [2 files, 922 B]
│   ├── 🐍 Button.py [450 B, 2024-01-15 14:25]
│   └── 🐍 Header.py [472 B, 2024-01-15 14:20]
├── 📁 utils/ [1 file, 800 B]
│   └── 🐍 helpers.py [800 B, 2024-01-15 14:15]
└── 🐍 main.py [1.2 KB, 2024-01-15 14:30]
```

### Mixed file types with emojis

```bash
$ trxd project/
📁 project/
├── 📁 src/
│   ├── 🐍 main.py
│   ├── 🌐 index.html
│   ├── 🎨 styles.css
│   └── 📜 app.js
├── 📁 docs/
│   ├── 📝 README.md
│   └── 📄 manual.pdf
├── 📋 config.json
├── 🔐 .env
└── 🐳 Dockerfile
```

### Flat format (simple)

```bash
$ trxd --format flat src/
src
src/main.py
src/components
src/components/Button.py
src/components/Header.py
src/utils
src/utils/helpers.py
```

### Flat format with metadata

```bash
$ trxd --format flat --show-metadata src/
src [4 files, 2.1 KB]
src/main.py [1.2 KB, 2024-01-15 14:30]
src/components [2 files, 922 B]
src/components/Button.py [450 B, 2024-01-15 14:25]
src/components/Header.py [472 B, 2024-01-15 14:20]
src/utils [1 file, 800 B]
src/utils/helpers.py [800 B, 2024-01-15 14:15]
```

### JSON output (simple)

```bash
$ trxd --format json src/
{
  "src": {
    "main.py": null,
    "components": {
      "Button.py": null,
      "Header.py": null
    },
    "utils": {
      "helpers.py": null
    }
  }
}
```

### JSON output with metadata

```bash
$ trxd --format json --show-metadata
{
  "_metadata": {
    "file_count": 4,
    "total_size": 2156,
    "modified": "2024-01-15T14:30:00"
  },
  "src": {
    "type": "directory",
    "file_count": 4,
    "total_size": 2156,
    "modified": "2024-01-15T14:30:00",
    "contents": {
      "main.py": {
        "type": "file",
        "size": 1234,
        "modified": "2024-01-15T14:30:00"
      },
      "components": {
        "type": "directory",
        "file_count": 2,
        "total_size": 922,
        "modified": "2024-01-15T14:25:00",
        "contents": {
          "Button.py": {
            "type": "file",
            "size": 450,
            "modified": "2024-01-15T14:25:00"
          },
          "Header.py": {
            "type": "file",
            "size": 472,
            "modified": "2024-01-15T14:20:00"
          }
        }
      },
      "utils": {
        "type": "directory",
        "file_count": 1,
        "total_size": 800,
        "modified": "2024-01-15T14:15:00",
        "contents": {
          "helpers.py": {
            "type": "file",
            "size": 800,
            "modified": "2024-01-15T14:15:00"
          }
        }
      }
    }
  }
}
```

### YAML output (simple)

```bash
$ trxd --format yaml src/
src:
  main.py: null
  components:
    Button.py: null
    Header.py: null
  utils:
    helpers.py: null
```

### YAML output with metadata

```bash
$ trxd --format yaml --show-metadata src/
_metadata:
  file_count: 4
  total_size: 2156
  modified: '2024-01-15T14:30:00'
src:
  type: directory
  file_count: 4
  total_size: 2156
  modified: '2024-01-15T14:30:00'
  contents:
    main.py:
      type: file
      size: 1234
      modified: '2024-01-15T14:30:00'
    components:
      type: directory
      file_count: 2
      total_size: 922
      modified: '2024-01-15T14:25:00'
      contents:
        Button.py:
          type: file
          size: 450
          modified: '2024-01-15T14:25:00'
        Header.py:
          type: file
          size: 472
          modified: '2024-01-15T14:20:00'
    utils:
      type: directory
      file_count: 1
      total_size: 800
      modified: '2024-01-15T14:15:00'
      contents:
        helpers.py:
          type: file
          size: 800
          modified: '2024-01-15T14:15:00'
```

### CSV format

The CSV format provides a structured, tabular output that's perfect for data analysis and processing:

```bash
$ trxd --format csv src/
type,path,name,extension
directory,src,src,
file,src/main.py,main.py,py
directory,src/components,components,
file,src/components/Button.py,Button.py,py
file,src/components/Header.py,Header.py,py
directory,src/utils,utils,
file,src/utils/helpers.py,helpers.py,py
```

### CSV format with metadata

When using `--show-metadata` with CSV format, additional columns are included:

```bash
$ trxd --format csv --show-metadata src/
type,path,name,extension,size,modified,file_count,total_size
directory,src,src,,0,2024-01-15 14:30:00,4,2156
file,src/main.py,main.py,py,1234,2024-01-15 14:30:00,,
directory,src/components,components,,0,2024-01-15 14:25:00,2,922
file,src/components/Button.py,Button.py,py,450,2024-01-15 14:25:00,,
file,src/components/Header.py,Header.py,py,472,2024-01-15 14:20:00,,
directory,src/utils,utils,,0,2024-01-15 14:15:00,1,800
file,src/utils/helpers.py,helpers.py,py,800,2024-01-15 14:15:00,,
```

**CSV Columns:**

- `type`: "directory" or "file"
- `path`: Relative path from the starting directory
- `name`: File or directory name
- `extension`: File extension (empty for directories)
- `size`: File size in bytes (only with `--show-metadata`)
- `modified`: Last modification date (only with `--show-metadata`)
- `file_count`: Number of files in directory (only with `--show-metadata`)
- `total_size`: Total size of all files in directory (only with `--show-metadata`)

### ASCII format with metadata

```bash
$ trxd --format ascii --show-metadata src/
[d] src/ [4 files, 2.1 KB]
├── [d] components/ [2 files, 922 B]
│   ├── [f] Button.py [450 B, 2024-01-15 14:25]
│   └── [f] Header.py [472 B, 2024-01-15 14:20]
├── [d] utils/ [1 file, 800 B]
│   └── [f] helpers.py [800 B, 2024-01-15 14:15]
└── [f] main.py [1.2 KB, 2024-01-15 14:30]
```

### Filtering examples

```bash
# Exclude Python cache files
$ trxd --exclude "*.pyc" --exclude "__pycache__"

# Exclude common build directories
$ trxd --exclude-dir "node_modules" --exclude-dir ".git" --exclude-dir "dist"

# Show only source files
$ trxd --exclude-file "*.log" --exclude-file "*.tmp" --show-metadata

# Complex filtering example
$ trxd --exclude-dir "node_modules" --exclude-dir ".git" --exclude "*.pyc" --exclude "*.pyo" --show-metadata
```

### Real-world usage examples

```bash
# List a Python project structure
$ trxd --exclude-dir "__pycache__" --exclude-dir ".git" --exclude "*.pyc" --format tree

# Get directory size information
$ trxd --show-metadata --format flat | grep "\[.*files"

# Export project structure for documentation
$ trxd --format yaml --exclude-dir ".git" --exclude-dir "node_modules" > project-structure.yaml

# Generate JSON for API consumption
$ trxd --format json --show-metadata --exclude-dir ".git" > directory-info.json

# Quick file listing without directories
$ trxd --format flat --exclude-dir "*" src/
```

### Integration examples

```bash
# Use with other tools
$ trxd --format flat | grep "\.py$" | wc -l  # Count Python files
$ trxd --show-metadata --format json | jq '.src.contents | keys'  # Get directory contents with jq

# CSV data analysis
$ trxd --format csv --show-metadata | awk -F',' '$1=="file" {sum+=$5} END {print "Total file size:", sum}'  # Sum file sizes
$ trxd --format csv | grep "\.py$" | wc -l  # Count Python files using CSV
$ trxd --format csv --show-metadata | grep "directory" | awk -F',' '{print $3, $7}'  # Show directory file counts

# Generate reports
$ trxd --show-metadata --format json | jq '[.src.contents | to_entries[] | select(.value.type == "file") | {name: .key, size: .value.size}]'
$ trxd --format csv --show-metadata > directory-analysis.csv  # Export to CSV for Excel/analysis
```

## Command-line options

```txt
positional arguments:
  path                  Directory path to list (default: current directory)

options:
  -h, --help            Show help message and exit
  --format {tree,ascii,json,yaml,flat}
                        Output format (default: tree)
  -x, --exclude EXCLUDE
                        Pattern to exclude (files and directories)
  -xd, --exclude-dir EXCLUDE_DIR
                        Pattern to exclude (directories only)
  -xf, --exclude-file EXCLUDE_FILE
                        Pattern to exclude (files only)
  -m, --show-metadata   Show metadata (size, modification date)
  --no-emoji           Disable emojis in tree format (use ASCII characters)
```

## Performance

- **Memory efficient**: Uses generators to process large directory structures without loading everything into memory
- **Fast filtering**: Uses pathlib's efficient pattern matching
- **Lazy evaluation**: Metadata is only collected when requested

## Requirements

- Python 3.8+
- PyYAML (for YAML output)

## Development

### Setup development environment

```bash
git clone https://github.com/alexmarco/trxd.git
cd trxd
uv sync --dev
```

### Run tests

```bash
uv run pytest
```

### Run linting

```bash
uv run ruff check .
uv run ruff format .
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

### v1.0.0

- Initial release
- Basic tree listing functionality
- Multiple output formats (tree, ascii, flat, json, yaml)
- Advanced filtering options
- Metadata support (file sizes, modification dates)
- Memory-efficient generator-based processing
