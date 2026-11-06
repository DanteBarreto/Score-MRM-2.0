# Guía de Visual Studio Code

Esta guía explica cómo correr el proceso desde cero en Visual Studio Code.

## 1. Requisitos

- [Python 3.10 o superior](https://www.python.org/downloads/). En Windows, marca **Add python.exe to PATH** durante la instalación.
- [Visual Studio Code](https://code.visualstudio.com/) con la extensión **Python** de Microsoft. Al abrir el proyecto, VS Code te la sugerirá.
- [Git](https://git-scm.com/downloads), para clonar el repositorio.
- Los tres Excel de entrada en una carpeta de tu equipo. El repositorio no los incluye; revisa [Datos de entrada](datos.md).

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
  input_principal: Input_principal_Score MRM.xlsx
  observaciones: Reporte de observaciones.xlsx
  coberturas: Tablón de coberturas.xlsx
```

Para copiar la ruta, abre la carpeta en el Explorador de archivos y haz clic en la barra de direcciones. Si tus archivos tienen otros nombres, cámbialos en `archivos`.

`config.yaml` es solo tuyo: Git lo ignora, así que tu ruta no se sube al repositorio.

## 5. Generar el reporte

Presiona `Ctrl+Shift+B`. Esto ejecuta la tarea **2. Generar y abrir reporte**, que:

1. Lee los Excel de tu carpeta local.
2. Crea `output/reporte_mrm.html`.
3. Lo abre en tu navegador.
4. Muestra en el panel de la terminal los avisos de calidad de datos.

La salida correcta se ve así, con las cifras de tus archivos:

```text
reporte_mrm.html: 314 filas, fechas ['2026-08-31'], 343 observaciones, 309 coberturas
Avisos de calidad de datos:
  - 10 modelos "Sin Seguimiento" con nota de profundidad de seguimiento
  ...
```

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
| `El input ya tiene varias fechas` | El input trae historial y activaste la simulación | Cambia `simulacion.activa` a `false` en `config.yaml` |
| `PermissionError` al guardar | El Excel está abierto | Ciérralo y vuelve a ejecutar |
| El reporte se ve sin estilos | No hay acceso al CDN | Revisa la conexión a internet o la red corporativa |
