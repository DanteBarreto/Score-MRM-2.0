# Score MRM 2.0

Reporte HTML de indicadores de riesgo de modelo del COE Model Risk Management. Toma información de archivos Excel, calcula un puntaje de 0 a 100 por indicador, driver y modelo, y genera una sola página interactiva con filtros.

> **Importante:** este repositorio es público y no incluye datos. Cada persona trabaja con los Excel de su carpeta local, que Git ignora. No subas esos archivos ni el reporte generado.

## Inicio rápido

Necesitas [Python 3.10 o superior](https://www.python.org/downloads/), [Visual Studio Code](https://code.visualstudio.com/) y los tres Excel de entrada en una carpeta de tu equipo.

1. Clona el repositorio y abre la carpeta en Visual Studio Code.
2. Abre `Terminal > Run Task…` y ejecuta **1. Preparar entorno** (solo la primera vez). Esto crea tu archivo `config.yaml`.
3. Abre `config.yaml` e indica en `carpeta_inputs` la carpeta de tus Excel. Si los nombres de tus archivos son otros, ajústalos en `archivos`.
4. Presiona `Ctrl+Shift+B` para generar el reporte. Se abrirá en tu navegador.

El reporte queda en `output/reporte_mrm.html`. Incluye los datos, así que compártelo solo con quien corresponda. Necesita internet al abrirse, porque carga los estilos desde un CDN.

La guía paso a paso, con la alternativa por terminal y la solución de errores frecuentes, está en [docs/guia_vscode.md](docs/guia_vscode.md).

## Qué muestra el reporte

| Sección | Contenido |
|---|---|
| **Reporte** | Indicadores de cabecera, evolutivo del score y tablero con los 16 indicadores |
| **Macro** | Mapas de calor por Model User y por Banca y Producto, e indicadores por modelo |
| **Seguimiento** | Cobertura de seguimiento, alertas, tiempos de atención (TTM) y mitigantes |
| **Validación** | Cobertura metodológica y de implementación, calificaciones y próximas descoberturas |
| **Observaciones** | Observaciones pendientes y vencidas, con su detalle y recomendación |
| **Implementación** | Ambientes de despliegue y data, ratios y plataformas |
| **Gobierno** | Flujo de información y explicación de cada puntuación |

## Cómo funciona

```mermaid
flowchart LR
    subgraph L[Carpeta local del usuario]
      A[Input principal]
      B[Reporte de observaciones]
      C[Tablón de coberturas]
    end
    A --> D[generar_reporte.py]
    B --> D
    C --> D
    T[Plantilla HTML] --> D
    D --> R[output/reporte_mrm.html]
```

Python lee y valida los Excel, une la información por ID de modelo y la inserta en la plantilla. Los indicadores se calculan en el navegador, para que se actualicen con cada filtro.

## Estructura del proyecto

```text
Score-MRM-2.0/
├── config.ejemplo.yaml  Plantilla de tu config.yaml local
├── requirements.txt   Dependencias de Python
├── docs/              Documentación
├── src/               Código del proceso
│   ├── generar_reporte.py
│   └── simular_historico.py
├── templates/         Plantilla del reporte: diseño e indicadores
├── tests/             Pruebas automáticas
├── .vscode/           Tareas y configuración de Visual Studio Code
├── config.yaml        Tu configuración local (no se sube a Git)
└── output/            Reporte generado (no se sube a Git)
```

## Documentación

| Documento | Para qué sirve |
|---|---|
| [Guía de Visual Studio Code](docs/guia_vscode.md) | Instalar, correr el proceso y resolver errores |
| [Proceso](docs/proceso.md) | Qué hace cada etapa, de los Excel al reporte |
| [Datos de entrada](docs/datos.md) | Carpeta local, archivos, columnas y controles de calidad |
| [Indicadores](docs/indicadores.md) | Cálculo de indicadores, drivers, score y puntos por definir |
| [Actualización mensual](docs/actualizacion_mensual.md) | Qué hacer cada mes para actualizar el reporte |

## Estado

Primer MVP. Las definiciones pendientes están en [docs/indicadores.md](docs/indicadores.md#puntos-por-definir).

## Tecnologías

Python, [openpyxl](https://openpyxl.readthedocs.io/), [PyYAML](https://pyyaml.org/) y [Tabler](https://tabler.io/) (licencia MIT).
