#!/bin/bash

# Script para configurar el repositorio ls-tree

echo "🚀 Configurando repositorio ls-tree..."

# Inicializar git si no está ya inicializado
if [ ! -d ".git" ]; then
    echo "📁 Inicializando git..."
    git init
fi

# Agregar todos los archivos
echo "📝 Agregando archivos al repositorio..."
git add .

# Crear primer commit
echo "💾 Creando primer commit..."
git commit -m "feat: initial release of ls-tree v2024.12.19

- Add modern directory listing tool with multiple output formats
- Support for tree, ASCII, flat, JSON, and YAML formats
- Advanced filtering with glob patterns
- Metadata support for file sizes and modification dates
- Memory-efficient generator-based processing
- File type-specific emojis with --no-emoji option
- Comprehensive CLI with multiple filtering options
- Support for Python 3.8+ with modern pathlib
- Type hints and NumPy-style documentation
- Cross-platform compatibility"

echo "✅ Repositorio local configurado!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Crear repositorio en GitHub: https://github.com/new"
echo "2. Nombre: ls-tree"
echo "3. Descripción: A modern Python command-line tool for listing directory contents with advanced filtering and metadata support"
echo "4. Marcar como público"
echo "5. NO inicializar con README, .gitignore o LICENSE (ya los tenemos)"
echo "6. Ejecutar los comandos que se muestran a continuación:"
echo ""
echo "git remote add origin https://github.com/alejandromarcoramos/ls-tree.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "🎉 ¡Después podrás publicar en PyPI!"
