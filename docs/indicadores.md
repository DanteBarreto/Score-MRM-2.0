# Indicadores

Este documento describe la lógica programada en el reporte. Las medidas originales en DAX están en `data/Indicadores.xlsx`, hoja `Medidas`.

## Cómo se construye el score

1. **Indicador:** cada uno tiene un valor y una puntuación de 0 a 100.
2. **Driver:** promedio de sus indicadores que aplican.
3. **Score:** promedio de los drivers que aplican, con igual peso.

Las medidas se recalculan sobre los modelos filtrados. El score de un modelo es la misma medida evaluada solo para ese modelo. Por eso el score del portafolio (71,6 en agosto) no es el promedio de los scores de los modelos (82,2).

Lo marcado como "No aplica" se muestra en gris y no entra al promedio.

## Semáforo

| Color | Puntaje |
|---|---|
| Rojo | Menor que 70 |
| Ámbar | De 70 a 80 |
| Verde | Mayor que 80 |

## Indicadores por driver

"Total" es el número de modelos filtrados.

### Seguimiento

| Indicador | Valor | Puntuación |
|---|---|---|
| Modelos sin seguimiento | Modelos con `ESTADO_SEGUIMIENTO` = "Sin Seguimiento" | 1 − valor / total |
| Modelos con alerta de salud | Modelos con `ESTADO_ALERTA` = "En alerta" | 1 − valor / total |
| Modelos que exceden el tiempo máximo de atención | Modelos con `EXCEDE_TTM` = "Excede TTM" | 1 − valor / modelos en alerta |
| Modelos con alerta sin mitigante temporal | Modelos en alerta con `PRESENCIA_MITIGANTE` = "No" | 1 − valor / modelos en alerta |
| Completitud de seguimiento (%) | Promedio de `BBDD`, `GOB`, `PRECISION_DISCRIMINACION`, `GRANULARIDAD` y `UNIVARIADA` | El mismo promedio |

Los dos indicadores de alerta son "No aplica" si no hay modelos en alerta.

### Validación

| Indicador | Valor | Puntuación |
|---|---|---|
| Modelos sin validación de primera vez | Modelos con `VALIDACION_COMPLETA` = "Sin validación" | 1 − valor / total |
| Modelos que incumplen la validación periódica | Modelos con `VALIDACION_PERIODICA` = "Descoberturado" | 1 − valor / total |
| Nota dinámica de validación (%) | Promedio de `NOTA_DINAMICA_VALIDACION` | El mismo promedio |

### Observaciones

| Indicador | Valor | Puntuación |
|---|---|---|
| Observaciones vencidas de validación (críticas, relevantes y moderadas) | Suma de `OBS_CRIT_RELE_MODE_VENCIDAS_VI` | 1 − vencidas / `OBS_CRIT_RELE_MODE_PENDIENTES_VI` |
| Observaciones vencidas del regulador y auditoría | Suma de `OBS_SBS_AI_VENCIDAS` | 1 − vencidas / `OBS_SBS_AI_PENDIENTES` |

Son "No aplica" si no hay observaciones pendientes.

### Implementación

| Indicador | Valor | Puntuación |
|---|---|---|
| Modelos en ambientes no productivos en el despliegue | Modelos con `AMBIENTE_DESPLIEGUE` = "NO PRODUCTIVO" o "MIXTO" | Promedio de `RATIO_IMPLEMENTACION` |
| Modelos en ambientes no productivos en la data | Modelos con `AMBIENTE_DATA` = "NO PRODUCTIVO" o "MIXTO" | Promedio de `RATIO_DATA` |
| Cumplimiento de la calidad de datos (%) | Promedio de `NOTA_CALIDAD_DATOS` | El mismo promedio |

"EN REVISIÓN" y "Sin información" no cuentan en el valor.

### Gobierno

| Indicador | Valor | Puntuación |
|---|---|---|
| Incidentes en el inventario | Suma de `NUM_INCIDENTES` | 1 − valor / total, con mínimo 0 |
| Nota de documentación (%) | Promedio de `NOTA_GOBIERNO` | El mismo promedio |

### Desarrollo

| Indicador | Valor | Puntuación |
|---|---|---|
| Cumplimiento de 10 lineamientos (%) | Promedio de `NOTA_10_LINEAMIENTOS` | El mismo promedio |

## Interpretaciones aplicadas

- **Seguimiento:** la definición escrita citaba `ESTADO_MODELO`, pero el valor "Sin Seguimiento" está en `ESTADO_SEGUIMIENTO`.
- **Incidentes:** se suma `NUM_INCIDENTES`, porque contar filas daría el total de modelos.
- **Promedios:** ignoran los vacíos y son "No aplica" solo si todos están vacíos.
- **Textos:** se normalizan los espacios dobles, como "Sin  validación".
- **Driver y score:** no están definidos en la documentación, así que se usa promedio simple.

## Puntos por definir

| Tema | Situación actual | Decisión pendiente |
|---|---|---|
| Observaciones sin pendientes en un modelo | El reporte da "No aplica". La medida DAX `Ratio 07 obs cri` da 100 | Definir cuál regla aplica. Cambia el score por modelo, no el del portafolio |
| Fuente de las observaciones del score | Usa los conteos del input | Definir si se calcula desde el reporte de observaciones |
| Denominador de TTM | Incluye 6 modelos que no tienen TTM | Dividir solo entre 21 modelos con TTM bajaría el indicador de 55,6 a 42,9 |
| Denominador de seguimiento y alerta | Incluye "No aplica" y "Sin información" | Definir si se usan solo modelos evaluables |
| `NOTA_CALIDAD_DATOS` en 0 | 24 de 43 notas son 0 | Confirmar si es nota real. Si es dato faltante, el indicador sube de 24,3 a 54,9 |
| Score oficial | Portafolio: 71,6. Promedio de modelos: 82,2 | Definir cuál se reporta |
| Faltas graves | 4 de 18 modelos sin seguimiento están en verde | Evaluar un tope de score |
| "Sin información" | Se excluye igual que "No aplica" | Evaluar penalizarlo |
| Umbrales | 70 y 80 | El reporte anterior usaba 69 y 79 |
| Peso de los drivers | Igual para todos, aunque Calidad cubre 43 modelos y Lineamientos 52 | Evaluar ponderar por cobertura |
| Cobertura proyectada | Se interpreta `Proy_` como cobertura esperada | Confirmar su significado |
| Nombres de plataforma | "SAS GUIDE" y "SAS Enterprise Guide" se muestran por separado | Definir si se agrupan |
