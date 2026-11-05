# Actualización mensual

Sigue estos pasos cada vez que haya información de un nuevo mes.

## Antes de empezar

Este repositorio es público. Si los archivos contienen información real, no los subas aquí: usa un repositorio privado o déjalos solo en tu equipo.

## Pasos

1. **Input principal:** agrega al archivo de `data/` las filas del nuevo mes, sin borrar los meses anteriores. Mantén el nombre y el orden de las columnas.
2. **Reporte de observaciones:** reemplaza el archivo por el del nuevo mes.
3. **Tablón de coberturas:** reemplaza el archivo por el del nuevo mes.
4. **Configuración:** si algún archivo cambió de nombre, actualiza su ruta en `config.yaml`. Por ejemplo, el tablón lleva la fecha en el nombre.
5. **Generación:** presiona `Ctrl+Shift+B` en Visual Studio Code.
6. **Revisión:** lee los avisos de calidad en la terminal y revisa el reporte.
7. **Versionado:** guarda los cambios en Git, si corresponde.

Como el input tendrá más de una fecha, antes de la primera actualización real cambia esto en `config.yaml`:

```yaml
simulacion:
  activa: false
```

Con eso, los evolutivos usan solo datos reales y desaparecen la línea punteada y el punto hueco.

## Qué cambia en el reporte

- La nueva fecha aparece en el filtro **Fecha** y queda seleccionada por defecto.
- Los evolutivos suman un punto.
- Validación y Observaciones pasan a mostrar el nuevo mes. Para fechas anteriores solo muestran el evolutivo y un aviso.

## Lista de control

- [ ] El proceso terminó sin errores.
- [ ] El número de modelos es el esperado.
- [ ] Revisé los avisos de calidad de datos.
- [ ] Los filtros Fecha, Tier y Modelo responden.
- [ ] Validación y Observaciones muestran datos del nuevo mes.
- [ ] No hay datos reales en un repositorio público.
