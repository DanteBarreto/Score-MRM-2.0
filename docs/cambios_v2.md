# Cambios de la versión 2

La versión 2 incorpora el input principal histórico y siete archivos de detalle, agrega controles de calidad de datos, crea la sección Inventario, amplía Gobierno y suma el simulador y los umbrales por Tier. El cálculo del score no cambia: sigue usando solo el input principal.

## Datos de entrada

| Antes | Ahora |
|---|---|
| Input principal de un mes, con meses simulados | Input principal histórico (enero a setiembre de 2026). Se retira la simulación |
| 3 archivos | 8 archivos: input principal, Inventario, TTM, Reporte de observaciones, Observaciones SBS & AI, Nota de Gobierno, Calidad de Datos y Tablón de coberturas |
| Todos los archivos obligatorios | Solo el input principal es obligatorio. Si falta uno de detalle, su bloque no se muestra |
| ID del modelo en un solo formato | Se acepta número o código (`MOD-BCP-21122`, `MOBA-BCP-0000177`) |
| Sin equivalencias de catálogos | Sección `homologacion` en `config.yaml` |

## Calidad de datos

- **Esquema único:** `src/esquema.py` define los campos de cada archivo, su tipo de dato y su uso.
- **Controles automáticos:** `src/calidad.py` revisa la estructura y la coherencia, con niveles ERROR, ALERTA y AVISO.
- **Informe:** cada corrida crea `output/control_calidad.txt`. Si hay errores, el proceso se detiene.
- **Diccionario de datos:** `docs/referencia/Diccionario_de_datos.xlsx`, con una hoja por archivo, generado desde el esquema.
- **Documentación:** el proceso y los controles están en [calidad_datos.md](calidad_datos.md).

## Reporte

| Sección | Cambio |
|---|---|
| Todas | Los evolutivos muestran 9 meses reales. Desaparecen la línea punteada y la nota de dato simulado |
| Filtro Fecha | Setiembre se muestra como "Set" |
| Seguimiento | Nuevo gráfico de tiempo de atención por modelo: TTM real frente al TTM de gobierno. El detalle de alertas suma fecha de alerta, plan de acción, TTM, ampliación y comentarios |
| Observaciones | Nuevo bloque de SBS y auditoría interna: indicadores, gráficos por origen y riesgo, detalle y observaciones transversales. El evolutivo suma las vencidas de SBS y auditoría |
| Implementación | Nuevo bloque de calidad de datos: cumplimiento por criterio, cobertura por Tier y detalle por modelo |
| Inventario | Sección nueva: modelos con modelo input, explorador, mapa por proceso (incluye los modelos sin modelo input) y altas y bajas del último mes frente al anterior |
| Gobierno | Flujos interactivos del gobierno de modelos, matriz de aprobaciones, jerarquía de comités, aplicabilidad por perímetro, definición de indicadores, mapa normativo desplegable, flujo de información con owners y recurrencias, y nota de gobierno por PO usuario |
| Reporte | Simulador en el tablero de indicadores: se cambia el valor de un indicador y se recalculan puntuación, score y semáforo. Se retiran el botón de impresión y el gráfico de nota dinámica |
| Filtros | Selección múltiple en todos, salvo Fecha. Se retira el filtro Modelo. Se agregan Entidad (columna nueva `ENTIDAD_MODELO` del input principal, opcional) y Tipo de riesgo |
| Validación | Evolutivo de la cobertura de validación (% de modelos validados o coberturados) junto al evolutivo de modelos sin validación |
| Simulador | Recalcula en cascada los indicadores que dependen del que se cambia y explica los efectos |
| Semáforo | Umbrales según los Tier elegidos: Tier I 85/90, II 80/85, III 75/80, IV 60/75; solo Tier I y II 81/86; otras combinaciones según el Tier más crítico; sin filtro 70/80 |
| Todas las tablas | Muestran el código completo del modelo (`MOD-BCP-XXXX`) |

**Regla del último mes:** todo lo que viene de los archivos de detalle se muestra solo con el último mes del input principal seleccionado. En meses anteriores aparece un aviso y se mantienen los evolutivos.

## Reglas de negocio

| Tema | Regla |
|---|---|
| Observaciones SBS & AI pendientes | Solo el estado "Pendiente". "En Proceso" e "Implementada Por Verificar" se muestran, pero no cuentan |
| Observaciones SBS & AI vencidas | Pendientes con fecha de vencimiento anterior al corte del input principal |
| Nota de Gobierno | Se asigna por PO usuario y model developer. Si un PO tiene una sola fila, se usa esa fila aunque el developer no coincida |
| Inventario | Aporta los modelos input, el código del modelo y las fechas de inicio y retiro. El estado y los demás datos del modelo salen del input principal |
| Modelo input "No aplica" | Los modelos input llamados "No aplica" o "Pendiente" se tratan como sin modelo input |
| Alerta de salud | "Saludable" y "Aceptable" cuentan como modelos sin alerta, igual que "Sin alerta" |
| Calidad de datos por criterio | Puntos obtenidos sobre el peso del criterio. Los pesos se infirieron del archivo y suman 100% |

## Archivos del proyecto

| Archivo | Cambio |
|---|---|
| `src/esquema.py` | Nuevo |
| `src/calidad.py` | Nuevo |
| `src/generar_diccionario.py` | Nuevo |
| `src/generar_reporte.py` | Lee los ocho archivos, valida y une |
| `src/simular_historico.py` | Eliminado |
| `templates/plantilla_reporte.html` | Bloques y secciones nuevos, simulador, filtros múltiples y umbrales por Tier |
| `config.ejemplo.yaml` | Ocho archivos y homologación |
| `contenido/gobierno_modelos.yaml` | Nuevo: contenido de la sección Gobierno |
| `ejecutar.py` | Revisa el input principal y avisa qué archivos de detalle faltan |
| `tests/test_reporte.py` | 16 pruebas con los ocho archivos y el contenido de Gobierno |
| `docs/` | Nuevos `calidad_datos.md`, `cambios_v2.md` y diccionario de datos; guías actualizadas |

## Para actualizar desde la versión 1

1. Copia la nueva sección `archivos` y `homologacion` de `config.ejemplo.yaml` a tu `config.yaml`.
2. Borra la sección `simulacion` de tu `config.yaml`; ya no se usa.
3. Guarda los ocho Excel en tu carpeta de inputs y genera el reporte. El contenido de Gobierno ya viene en el repositorio (`contenido/gobierno_modelos.yaml`); si tu `config.yaml` tiene la línea `gobierno_contenido`, puedes borrarla.

## Pendiente de confirmar

- Pesos de los criterios del indicador de calidad de datos.
- Significado de `MODELOELIMINADO` en el inventario.
- Si las diferencias entre el detalle de observaciones y los conteos del input principal se corrigen en la fuente.
