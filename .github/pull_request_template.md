## 📝 Descripción

Descripción clara de los cambios realizados en este PR.

## 🔗 Issues Relacionados

- Closes #(issue number)
- Fixes #(issue number)
- Related to #(issue number)

## 🧪 Testing

- [ ] Tests unitarios añadidos/actualizados
- [ ] Tests de integración pasan
- [ ] Verificado manualmente en diferentes sistemas operativos
- [ ] Verificado con diferentes formatos de salida

### Comandos de Testing

```bash
# Ejecutar tests
uv run pytest

# Verificar calidad del código
uv run ruff check --fix .
uv run ruff format .
uv run mypy .

# Probar funcionalidad manualmente
uv run python -m trxd --help
uv run python -m trxd /path/to/test/directory
```

## 📚 Documentación

- [ ] README actualizado si es necesario
- [ ] Docstrings añadidos/actualizados
- [ ] Comentarios en código si es necesario
- [ ] CONTRIBUTING.md actualizado si es necesario

## 🎨 Cambios Visuales

Si hay cambios visuales, incluye capturas de pantalla o ejemplos:

### Antes
```
# Output anterior
```

### Después
```
# Output nuevo
```

## 🔧 Cambios Técnicos

### Archivos Modificados
- `archivo1.py` - Descripción del cambio
- `archivo2.py` - Descripción del cambio

### Nuevas Dependencias
- [ ] No se añadieron nuevas dependencias
- [ ] Se añadieron nuevas dependencias (especificar cuáles y por qué)

### Breaking Changes
- [ ] No hay breaking changes
- [ ] Hay breaking changes (describir cuáles y cómo migrar)

## 📊 Impacto en Rendimiento

- [ ] No hay impacto en rendimiento
- [ ] Mejora el rendimiento (describir)
- [ ] Puede afectar el rendimiento (describir y justificar)

## 🔍 Checklist

- [ ] Mi código sigue las convenciones del proyecto
- [ ] He realizado self-review de mi código
- [ ] He comentado mi código, especialmente en áreas difíciles de entender
- [ ] He hecho los cambios correspondientes en la documentación
- [ ] Mis cambios no generan warnings nuevos
- [ ] He añadido tests que prueban que mi fix es efectivo o que mi feature funciona
- [ ] Los tests nuevos y existentes pasan localmente con mis cambios
- [ ] Cualquier cambio dependiente ha sido mergeado y publicado

## 📝 Notas Adicionales

Cualquier información adicional que los reviewers deberían saber.

## 🎯 Tipo de Cambio

- [ ] Bug fix (cambio que corrige un problema)
- [ ] Nueva funcionalidad (cambio que añade funcionalidad)
- [ ] Breaking change (fix o feature que causaría que funcionalidad existente no funcione como se espera)
- [ ] Documentación (cambios solo en documentación)
- [ ] Refactoring (cambio de código que no corrige un bug ni añade funcionalidad)
- [ ] Performance (cambio que mejora el rendimiento)
- [ ] Test (añadir tests o corregir tests existentes)
- [ ] Chore (cambios en build process, herramientas auxiliares, etc.)

## 🚀 Screenshots/Videos

Si aplica, incluye screenshots o videos que demuestren los cambios.
