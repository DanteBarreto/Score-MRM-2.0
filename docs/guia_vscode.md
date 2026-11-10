# Guía de Visual Studio Code

Esta guía explica cómo correr el proceso desde cero en Visual Studio Code.

## 1. Requisitos

- [Python 3.10 o superior](https://www.python.org/downloads/). En Windows, marca **Add python.exe to PATH** durante la instalación.
- [Visual Studio Code](https://code.visualstudio.com/) con la extensión **Python** de Microsoft. Al abrir el proyecto, VS Code te la sugerirá.
- [Git](https://git-scm.com/downloads), para clonar el repositorio.
- Los Excel de entrada en una carpeta de tu equipo: el input principal histórico y, si los tienes, los siete archivos de detalle. El repositorio no los incluye; revisa [Datos de entrada](datos.md).

Para comprobar Python, abre una terminal y ejecuta:

```bash
python --version
```

## 2. Obtener el proyecto

En VS Code, abre la paleta con `Ctrl+Shift+P`, elige **Git: Clone** y pega esta dirección:

```text
https://github.com/DanteBarreto/Score-MRM-2.0.git
```

Elige una carpeta y, cuando VS Code lo pregunte, abre el proyecto. Evita carpetas con rutas muy largas: en Windows pueden causar errores.

## Opción rápida: ejecución guiada

Abre la terminal integrada y ejecuta:

```bash
python ejecutar.py
```

El script explica cada paso, prepara el entorno, te pide la carpeta de tus Excel y genera el reporte. También puedes abrir `ejecutar.py` y presionar **Run Python File**. Si prefieres hacerlo por tareas, sigue los pasos de abajo.

## 3. Preparar el entorno (solo la primera vez)

1. Abre `Terminal > Run Task…`.
2. Elige **1. Preparar entorno**.
3. Espera a que termine. Se creará la carpeta `.venv` con las dependencias y tu archivo `config.yaml`.

Si VS Code pregunta qué intérprete usar, elige el de `.venv`.

## 4. Indicar dónde están tus inputs

Abre `config.yaml` y cambia `carpeta_inputs` por la ruta de tu carpeta, entre comillas simples:

```yaml
carpeta_inputs: 'C:\Users\tu.usuario\Documents\Score MRM\Inputs'

archivos:
  input_principal: Input_principal_Score MRM_hist.xlsx
  inventario: Inventario de modelos.xlsx
  ttm: TTM.xlsx
  observaciones: Reporte de observaciones.xlsx
  observaciones_sbs_ai: Observaciones SBS & AI.xlsx
  nota_gobierno: Nota de Gobierno.xlsx
  calidad_datos: Calidad de Datos.xlsx
  coberturas: Tablón de coberturas.xlsx
```

Para copiar la ruta, abre la carpeta en el Explorador de archivos y haz clic en la barra de direcciones. Si tus archivos tienen otros nombres, cámbialos en `archivos`. Solo el input principal es obligatorio: si falta un archivo de detalle, su bloque no se muestra.

`config.yaml` es solo tuyo: Git lo ignora, así que tu ruta no se sube al repositorio.

## 5. Generar el reporte

Presiona `Ctrl+Shift+B`. Esto ejecuta la tarea **2. Generar y abrir reporte**, que:

1. Lee los Excel de tu carpeta local y revisa su calidad.
2. Crea `output/reporte_mrm.html` y `output/control_calidad.txt`.
3. Abre el reporte en tu navegador.
4. Muestra en la terminal los archivos leídos y el resumen de calidad.

La salida correcta se ve así, con las cifras de tus archivos:

```text
reporte_mrm.html: 9 meses (2026-01 a 2026-09), 312 modelos en el último mes
  - Input_principal_Score MRM_hist.xlsx: 2935 filas
  - Reporte de observaciones.xlsx: 995 filas
  ...
Calidad de datos: 22 alertas y 37 avisos. Detalle en output\control_calidad.txt
```

Si hay errores de calidad de datos, el proceso se detiene y los muestra. Qué significa cada control está en [calidad_datos.md](calidad_datos.md).

El reporte necesita internet al abrirse, porque carga los estilos desde un CDN. El archivo HTML incluye todos los datos, así que compártelo solo con quien corresponda.

## 6. Ejecutar las pruebas

En `Terminal > Run Task…`, elige **3. Ejecutar pruebas**. Usan Excel ficticios que crean y borran solas, así que no necesitan tus inputs. Conviene correrlas antes de subir cambios.

## 7. Depurar paso a paso

Abre el panel **Run and Debug** (`Ctrl+Shift+D`), elige **Generar reporte** y presiona `F5`. Puedes poner puntos de interrupción en `src/generar_reporte.py`.

## 8. Alternativa por terminal

Abre la terminal integrada (`Ctrl+Ñ` o `` Ctrl+` ``) y ejecuta estos comandos en PowerShell.

Crear el entorno e instalar dependencias:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\python -m pip install -r requirements.txt
```

Crear tu configuración y luego editarla como en el paso 4:

```bash
Copy-Item config.ejemplo.yaml config.yaml
```

Generar y abrir el reporte:

```bash
.venv\Scripts\python src/generar_reporte.py --abrir
```

Ejecutar las pruebas:

```bash
.venv\Scripts\python -m unittest discover -s tests
```

En macOS o Linux, usa `python3` para crear el entorno y `.venv/bin/python` en los demás comandos.

## 9. Errores frecuentes

| Mensaje o síntoma | Causa | Solución |
|---|---|---|
| `python` no se reconoce | Python no está instalado o no está en el PATH | Reinstálalo marcando **Add python.exe to PATH** y reinicia VS Code |
| `ModuleNotFoundError: yaml` u `openpyxl` | Falta preparar el entorno | Ejecuta la tarea **1. Preparar entorno** |
| `El sistema no puede encontrar la ruta` al usar `Ctrl+Shift+B` | No existe `.venv` | Ejecuta la tarea **1. Preparar entorno** |
| `No existe config.yaml` | Falta crear la configuración local | Ejecuta la tarea **1. Preparar entorno** |
| `No se encontró el Excel` | `carpeta_inputs` o el nombre del archivo no coinciden | Corrige la ruta y los nombres en `config.yaml` |
| `found unknown escape character` | La ruta está entre comillas dobles | Usa comillas simples en `carpeta_inputs` |
| `Faltan columnas en …` | El Excel cambió de estructura | Compáralo con [Datos de entrada](datos.md) |
| `Modelos repetidos en una misma FECHA` | Un ID aparece dos veces en una fecha | Corrige el input principal |
| `El proceso se detuvo por errores de calidad de datos` | Un archivo tiene un problema que impide un reporte confiable | Corrige lo indicado y revisa [calidad_datos.md](calidad_datos.md) |
| No aparecen los bloques de TTM, SBS & AI, Calidad de Datos, Inventario o Nota de Gobierno | Tu `config.yaml` es de la versión 1 y no lista esos archivos | Copia las secciones `archivos` y `homologacion` de `config.ejemplo.yaml` |
| Un bloque muestra "solo está disponible para…" | Elegiste un mes anterior al último | Selecciona el último mes en el filtro Fecha |
| `PermissionError` al guardar | El Excel está abierto | Ciérralo y vuelve a ejecutar |
| El reporte se ve sin estilos | No hay acceso al CDN | Revisa la conexión a internet o la red corporativa |
