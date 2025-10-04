# Guía de Publicación - ls-tree

## 📋 Checklist Completo

### ✅ Ya Completado

- [x] Código fuente completo con funcionalidades
- [x] Documentación en README.md
- [x] pyproject.toml configurado con CalVer (2024.12.19)
- [x] .gitignore apropiado
- [x] LICENSE (MIT)
- [x] CHANGELOG.md
- [x] GitHub Actions para CI/CD
- [x] Configuración de linting y testing

### 🚀 Pasos para Publicar

## 1. Configurar Git y GitHub

### Opción A: Usar el script automático

```bash
chmod +x setup_repo.sh
./setup_repo.sh
```

### Opción B: Manual

```bash
# Inicializar git
git init

# Agregar archivos
git add .

# Primer commit
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
```

### Crear repositorio en GitHub

1. Ve a <https://github.com/new>
2. **Nombre**: `ls-tree`
3. **Descripción**: `A modern Python command-line tool for listing directory contents with advanced filtering and metadata support`
4. **Visibilidad**: Público
5. **NO marcar**: README, .gitignore, o LICENSE (ya los tenemos)
6. Click "Create repository"

### Conectar repositorio local con GitHub

```bash
git remote add origin https://github.com/alejandromarcoramos/ls-tree.git
git branch -M main
git push -u origin main
```

## 2. Configurar PyPI

### Crear cuenta en PyPI

1. Ve a <https://pypi.org/account/register/>
2. Crea una cuenta (usa el mismo email que en pyproject.toml)

### Crear API Token

1. Ve a <https://pypi.org/manage/account/token/>
2. Click "Add API token"
3. **Token name**: `ls-tree-release`
4. **Scope**: Entire account (not recommended) o Project: ls-tree
5. **Copy the token** (solo se muestra una vez)

### Configurar GitHub Secrets

1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. **Name**: `PYPI_API_TOKEN`
5. **Secret**: Pega el token de PyPI

## 3. Crear Release

### Opción A: Automática (Recomendada)

```bash
# Crear y subir tag
git tag 2024.12.19
git push origin 2024.12.19
```

Esto activará automáticamente el workflow de release que publicará en PyPI.

### Opción B: Manual

```bash
# Instalar herramientas de desarrollo
pip install build twine

# Construir paquete
python -m build

# Verificar paquete
twine check dist/*

# Subir a PyPI
twine upload dist/*
```

## 4. Verificar Publicación

### Verificar en PyPI

- <https://pypi.org/project/ls-tree/>

### Instalar desde PyPI

```bash
pip install ls-tree
ls-tree --help
```

## 5. Configuraciones Adicionales

### GitHub Repository Settings

- [ ] Habilitar Issues
- [ ] Configurar branch protection rules
- [ ] Configurar CODEOWNERS (opcional)

### PyPI Project Settings

- [ ] Agregar descripción larga
- [ ] Configurar categorías
- [ ] Agregar keywords adicionales

## 🎯 Próximas Versiones

Para futuras versiones usando CalVer:

```bash
# Actualizar versión en pyproject.toml
# Ejemplo: 2024.12.20, 2024.12.21, etc.

# Crear tag y push
git tag 2024.12.20
git push origin 2024.12.20
```

## 📊 Métricas a Seguir

- [ ] Downloads en PyPI
- [ ] Stars en GitHub
- [ ] Issues y PRs
- [ ] Uso en otros proyectos

## 🔧 Troubleshooting

### Error de autenticación PyPI

- Verificar que el token esté correcto
- Verificar que el nombre del paquete no esté tomado

### Error de permisos GitHub

- Verificar que tengas permisos de write en el repositorio
- Verificar que el workflow tenga permisos de write

### Error de versión

- Verificar que la versión sea única
- No reutilizar versiones ya publicadas
