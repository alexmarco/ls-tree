"""Tests para funciones de filtrado."""

import argparse
from pathlib import Path

import pytest

from ls_tree import is_excluded


class TestIsExcluded:
    """Tests para la función is_excluded."""

    def test_no_exclusions(self) -> None:
        """Test que sin exclusiones, nada se excluye."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=[]
        )
        
        assert not is_excluded(Path("file.txt"), args)
        assert not is_excluded(Path("directory"), args)

    def test_exclude_patterns(self) -> None:
        """Test patrones de exclusión generales."""
        args = argparse.Namespace(
            exclude=["*.pyc", "*.tmp"],
            exclude_dir=[],
            exclude_file=[]
        )
        
        # Archivos que deben ser excluidos
        assert is_excluded(Path("script.pyc"), args)
        assert is_excluded(Path("temp.tmp"), args)
        assert is_excluded(Path("src/script.pyc"), args)
        
        # Archivos que NO deben ser excluidos
        assert not is_excluded(Path("script.py"), args)
        assert not is_excluded(Path("file.txt"), args)

    def test_exclude_dir_patterns(self) -> None:
        """Test patrones de exclusión específicos para directorios."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=["__pycache__", "node_modules", ".git"],
            exclude_file=[]
        )
        
        # Crear objetos Path que simulen directorios usando mock
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
        
        # Directorios que deben ser excluidos
        assert is_excluded(cache_dir, args)
        assert is_excluded(node_dir, args)
        assert is_excluded(git_dir, args)
        
        # Archivos con nombres similares NO deben ser excluidos
        assert not is_excluded(Path("__pycache__.txt"), args)
        assert not is_excluded(Path("node_modules.zip"), args)
        
        # Directorios que NO deben ser excluidos
        assert not is_excluded(Path("src"), args)
        assert not is_excluded(Path("docs"), args)

    def test_exclude_file_patterns(self) -> None:
        """Test patrones de exclusión específicos para archivos."""
        args = argparse.Namespace(
            exclude=[],
            exclude_dir=[],
            exclude_file=["*.log", "*.tmp", "*.bak"]
        )
        
        # Crear objetos Path que simulen archivos usando mock
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
        
        # Archivos que deben ser excluidos
        assert is_excluded(log_file, args)
        assert is_excluded(tmp_file, args)
        assert is_excluded(bak_file, args)
        
        # Directorios con nombres similares NO deben ser excluidos
        assert not is_excluded(Path("logs"), args)  # directorio
        assert not is_excluded(Path("temp"), args)  # directorio
        
        # Archivos que NO deben ser excluidos
        assert not is_excluded(Path("script.py"), args)
        assert not is_excluded(Path("readme.md"), args)

    def test_combined_exclusions(self) -> None:
        """Test combinación de diferentes tipos de exclusiones."""
        args = argparse.Namespace(
            exclude=["*.pyc", "*.pyo"],
            exclude_dir=["__pycache__", "node_modules"],
            exclude_file=["*.log", "*.tmp"]
        )
        
        # Archivos excluidos por patrones generales
        assert is_excluded(Path("script.pyc"), args)
        assert is_excluded(Path("module.pyo"), args)
        
        # Crear objetos Path que simulen directorios usando mock
        from unittest.mock import Mock
        cache_dir = Mock(spec=Path)
        cache_dir.match.return_value = True
        cache_dir.is_dir.return_value = True
        
        node_dir = Mock(spec=Path)
        node_dir.match.return_value = True
        node_dir.is_dir.return_value = True
        
        # Directorios excluidos por patrones de directorio
        assert is_excluded(cache_dir, args)
        assert is_excluded(node_dir, args)
        
        # Crear objetos Path que simulen archivos usando mock
        from unittest.mock import Mock
        log_file = Mock(spec=Path)
        log_file.match.return_value = True
        log_file.is_file.return_value = True
        
        tmp_file = Mock(spec=Path)
        tmp_file.match.return_value = True
        tmp_file.is_file.return_value = True
        
        # Archivos excluidos por patrones de archivo
        assert is_excluded(log_file, args)
        assert is_excluded(tmp_file, args)
        
        # Archivos que NO deben ser excluidos
        assert not is_excluded(Path("script.py"), args)
        assert not is_excluded(Path("readme.md"), args)
        assert not is_excluded(Path("src"), args)

    def test_wildcard_patterns(self) -> None:
        """Test patrones con wildcards."""
        args = argparse.Namespace(
            exclude=["test_*", "*_test.py"],
            exclude_dir=[],
            exclude_file=[]
        )
        
        # Archivos que coinciden con patrones
        assert is_excluded(Path("test_file.py"), args)
        assert is_excluded(Path("unit_test.py"), args)
        assert is_excluded(Path("integration_test.py"), args)
        
        # Archivos que NO coinciden
        assert not is_excluded(Path("main.py"), args)
        assert not is_excluded(Path("helper.py"), args)

    def test_hidden_files_and_dirs(self) -> None:
        """Test archivos y directorios ocultos."""
        args = argparse.Namespace(
            exclude=[".*"],
            exclude_dir=[],
            exclude_file=[]
        )
        
        # Archivos y directorios ocultos
        assert is_excluded(Path(".gitignore"), args)
        assert is_excluded(Path(".env"), args)
        assert is_excluded(Path(".git"), args)
        assert is_excluded(Path(".vscode"), args)
        
        # Archivos normales
        assert not is_excluded(Path("readme.md"), args)
        assert not is_excluded(Path("src"), args)

    def test_case_sensitivity(self) -> None:
        """Test sensibilidad a mayúsculas/minúsculas."""
        args = argparse.Namespace(
            exclude=["*.PYC"],
            exclude_dir=[],
            exclude_file=[]
        )
        
        # En Windows, pathlib es case-insensitive por defecto
        # Por lo tanto, ambos deberían coincidir
        assert is_excluded(Path("script.pyc"), args)  # minúsculas
        assert is_excluded(Path("script.PYC"), args)     # mayúsculas

    def test_nested_paths(self) -> None:
        """Test rutas anidadas."""
        args = argparse.Namespace(
            exclude=["src/*.pyc"],
            exclude_dir=[],
            exclude_file=[]
        )
        
        # Archivos en subdirectorios
        assert is_excluded(Path("src/script.pyc"), args)
        # El patrón "src/*.pyc" no coincide con "src/utils/helper.pyc" porque * no incluye /
        # assert is_excluded(Path("src/utils/helper.pyc"), args)
        
        # Archivos en otros directorios
        assert not is_excluded(Path("docs/script.pyc"), args)
        assert not is_excluded(Path("script.pyc"), args)

    def test_empty_patterns(self) -> None:
        """Test con patrones vacíos."""
        args = argparse.Namespace(
            exclude=[""],
            exclude_dir=[""],
            exclude_file=[""]
        )
        
        # Patrones vacíos no deberían excluir nada
        assert not is_excluded(Path("file.txt"), args)
        assert not is_excluded(Path("directory"), args)

    def test_multiple_matches(self) -> None:
        """Test cuando un archivo coincide con múltiples patrones."""
        args = argparse.Namespace(
            exclude=["*.pyc", "*.tmp"],
            exclude_dir=[],
            exclude_file=["*.log"]
        )
        
        # Archivo que coincide con patrón general
        assert is_excluded(Path("script.pyc"), args)
        
        # Crear objeto Path que simule archivo usando mock
        from unittest.mock import Mock
        log_file = Mock(spec=Path)
        log_file.match.return_value = True
        log_file.is_file.return_value = True
        
        # Archivo que coincide con patrón de archivo
        assert is_excluded(log_file, args)
        
        # Archivo que no coincide con ningún patrón
        assert not is_excluded(Path("script.py"), args)
