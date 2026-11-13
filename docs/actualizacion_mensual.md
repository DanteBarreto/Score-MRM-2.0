# Actualización mensual

Sigue estos pasos cada vez que haya información de un nuevo mes.

## Antes de empezar

Los archivos se actualizan en tu carpeta local, la de `carpeta_inputs` en `config.yaml`. El repositorio es público y no debe contener datos.

## Pasos

1. **Input principal histórico:** agrega las filas del nuevo mes, sin borrar los meses anteriores. Mantén los nombres de las columnas y completa `ENTIDAD_MODELO`, que alimenta el filtro Entidad.
2. **Archivos de detalle:** reemplaza los siete por los del nuevo mes: Inventario, TTM, Reporte de observaciones, Observaciones SBS & AI, Nota de Gobierno, Calidad de Datos y Tablón de coberturas. Deben corresponder al mismo mes que acabas de agregar al input principal. El contenido de Gobierno (`contenido/gobierno_modelos.yaml`) no se cambia cada mes: está en el repositorio y solo se edita cuando cambian la norma, los flujos o las fuentes.
3. **Configuración:** si algún archivo cambió de nombre, actualízalo en `archivos` de `config.yaml`.
4. **Generación:** presiona `Ctrl+Shift+B` en Visual Studio Code, o ejecuta `python ejecutar.py`.
5. **Calidad de datos:** abre `output/control_calidad.txt`. Revisa primero las alertas y consulta su significado en [calidad_datos.md](calidad_datos.md).
6. **Revisión:** recorre el reporte con el nuevo mes seleccionado.

## Qué cambia en el reporte

- La nueva fecha aparece en el filtro **Fecha** y queda seleccionada por defecto.
- Los evolutivos suman un punto.
- Los bloques de los archivos de detalle pasan a mostrar el nuevo mes. Para fechas anteriores muestran un aviso.

## Lista de control

- [ ] El proceso terminó sin errores.
- [ ] La terminal lista los ocho archivos leídos.
- [ ] El número de modelos del último mes es el esperado.
- [ ] Revisé las alertas de `output/control_calidad.txt`.
- [ ] Si apareció una categoría nueva escrita distinto, la agregué a `homologacion` en `config.yaml`.
- [ ] Los filtros responden y el semáforo cambia de umbrales al elegir un Tier.
- [ ] Seguimiento, Validación, Observaciones, Implementación, Inventario y Gobierno muestran datos del nuevo mes.
- [ ] `git status` no muestra Excel, `config.yaml` ni el reporte generado.
