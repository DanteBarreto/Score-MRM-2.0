# Actualización mensual

Sigue estos pasos cada vez que haya información de un nuevo mes.

## Antes de empezar

Los archivos se actualizan en tu carpeta local, la de `carpeta_inputs` en `config.yaml`. El repositorio es público y no debe contener datos.

## Pasos

1. **Input principal:** agrega las filas del nuevo mes, sin borrar los meses anteriores. Mantén los nombres de las columnas.
2. **Reporte de observaciones:** reemplaza el archivo por el del nuevo mes.
3. **Tablón de coberturas:** reemplaza el archivo por el del nuevo mes.
4. **Configuración:** si algún archivo cambió de nombre, actualízalo en `archivos` de `config.yaml`.
5. **Generación:** presiona `Ctrl+Shift+B` en Visual Studio Code.
6. **Revisión:** lee los avisos de calidad en la terminal y revisa el reporte.

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
- [ ] `git status` no muestra Excel, `config.yaml` ni el reporte generado.
