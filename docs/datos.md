# Datos de entrada

## Carpeta local

El repositorio no contiene inputs. Cada persona guarda los tres Excel en una carpeta de su equipo y la indica en `carpeta_inputs` de su `config.yaml`. Git ignora `config.yaml`, los Excel y el reporte generado.

El proceso lee la primera hoja de cada Excel, con los títulos en la primera fila.

## Archivos

| Archivo | Contenido | Identificador | Periodicidad |
|---|---|---|---|
| Input principal | Inventario y campos de cada indicador | `ID_MODELO` | Una fila por modelo y `FECHA` |
| Reporte de observaciones | Detalle de observaciones pendientes | `ID_Model` | Solo última fecha |
| Tablón de coberturas | Cobertura por frente de validación | `Modelo_ID` | Solo última fecha |

Los nombres de los archivos se definen en `archivos` de `config.yaml`.

`docs/referencia/Indicadores.xlsx` documenta las medidas de Power BI (DAX) y no se lee en el proceso: las reglas están programadas en la plantilla. Si cambia una regla, hay que actualizar la plantilla y [Indicadores](indicadores.md).

## Input principal

| Grupo | Columnas |
|---|---|
| Identificación | `FECHA`, `ID_MODELO`, `NOMBRE_MODELO`, `TIER_MODELO`, `ESTADO_MODELO`, `TIPO_RIESGO` |
| Clasificación | `PRODUCTO`, `SUB_PRODUCTO`, `BANCA`, `PROCESO` |
| Responsables | `MODEL_DEVELOPER`, `RESPONSABLE_MONITORING`, `RESPONSABLE_DEVELOPER`, `PO_USUARIO`, `MODEL_USER` |
| Seguimiento | `ESTADO_SEGUIMIENTO`, `ESTADO_ALERTA`, `EXCESO_MESES_TTM`, `EXCEDE_TTM`, `IMPACTO`, `PRESENCIA_MITIGANTE`, `DESCRIPCION_MITIGANTE` |
| Completitud de seguimiento | `BBDD`, `GOB`, `PRECISION_DISCRIMINACION`, `GRANULARIDAD`, `UNIVARIADA` |
| Validación | `VALIDACION_COMPLETA`, `VALIDACION_PERIODICA`, `NOTA_DINAMICA_VALIDACION` |
| Observaciones | `OBS_CRIT_RELE_MODE_PENDIENTES_VI`, `OBS_CRIT_RELE_MODE_VENCIDAS_VI`, `OBS_SBS_AI_PENDIENTES`, `OBS_SBS_AI_VENCIDAS`, `OBS_AMB_TEC_PENDIENTES`, `OBS_AMB_TEC_VENCIDOS` |
| Implementación | `PLATAFORMA_IMPLEMENTACION`, `AMBIENTE_DESPLIEGUE`, `RATIO_IMPLEMENTACION`, `PLATAFORMA_DATA`, `AMBIENTE_DATA`, `RATIO_DATA`, `NOTA_CALIDAD_DATOS` |
| Gobierno y desarrollo | `NUM_INCIDENTES`, `NOTA_GOBIERNO`, `NOTA_10_LINEAMIENTOS` |

Las notas y ratios van de 0 a 1. La columna opcional `SIMULADO` marca con 1 las filas simuladas.

## Reporte de observaciones

| Grupo | Columnas |
|---|---|
| Identificación | `ID_Obs`, `ID_Model`, `FECHA_PROCESO` |
| Contenido | `Observación`, `Recomendación`, `Criticidad_observacion`, `Ambito_observacion`, `Tipo_revisión` |
| Plazos | `Estado_Vencimiento`, `# Ampliaciones`, `Fecha estimada`, `Fecha ampliada` |
| Responsables | `Nombre_proyecto`, `Area homologada`, `Manager_nombre`, `Validador_nombre`, `Propietario_nombre` |

Los días vencidos se calculan entre el compromiso vigente (`Fecha ampliada` si existe, si no `Fecha estimada`) y `FECHA_PROCESO`. No se usa `Diferencia_dias`, porque siempre parte de la fecha estimada original.

## Tablón de coberturas

| Grupo | Columnas |
|---|---|
| Identificación | `Modelo_ID`, `Fecha` |
| Cobertura actual | `Cobertura_Metodologia`, `Cobertura_Implementación`, `Cobertura_Global` |
| Cobertura proyectada | `Proy_Cobertura_Met`, `Proy_Cobertura_Imp`, `Proy_Cobertura_Global` |
| Fechas | `Met_Fecha_fin`, `Imp_Fecha_fin`, `Fecha_descobertura_Met`, `Fecha_descobertura_Imp` |
| Última validación | `Met_Tipo_revision`, `Imp_Tipo_revision`, `Met_Alcance`, `Imp_Alcance`, `Met_Manager`, `Imp_Manager`, `Met_Validador`, `Imp_Validador`, `Calificación_Metodología`, `Calificación_Implementación` |

`Fecha_descobertura_Met` y `Fecha_descobertura_Imp` van en formato `dd/mm/aaaa`.

## Controles de calidad

Al generar el reporte, la consola lista avisos que no detienen el proceso:

- Modelos "Sin Seguimiento" con nota de completitud, o "Con Seguimiento" sin ella.
- Modelos "Sin Seguimiento" marcados "En alerta".
- Modelos en alerta sin dato de mitigante, o sin alerta con ese dato.
- Mitigante "Si" con descripción "No aplica".
- Ambiente informado con plataforma sin información.
- `NOTA_CALIDAD_DATOS` igual a 0.
- Más observaciones vencidas que pendientes.
- Filas repetidas en observaciones.
- Modelos sin registro en el tablón.
- Observaciones y coberturas de modelos fuera del inventario.

## Diferencias conocidas entre fuentes

En la base de desarrollo de agosto de 2026 se encontró lo siguiente. Conviene revisarlo con los datos reales:

| Dato | Input principal | Archivo de detalle |
|---|---|---|
| Críticas, relevantes y moderadas pendientes | 151 | 163 |
| Críticas, relevantes y moderadas vencidas | 121 | 127 |
| Observaciones de entorno tecnológico pendientes | 11 | 9 |
| `VALIDACION_PERIODICA` frente a `Cobertura_Global` | 20 modelos con estado distinto | |

El score y la cabecera usan el input principal.
