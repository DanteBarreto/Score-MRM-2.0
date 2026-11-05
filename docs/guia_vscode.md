# Guía de Visual Studio Code

Esta guía explica cómo correr el proceso desde cero en Visual Studio Code.

## 1. Requisitos

- [Python 3.10 o superior](https://www.python.org/downloads/). En Windows, marca **Add python.exe to PATH** durante la instalación.
- [Visual Studio Code](https://code.visualstudio.com/) con la extensión **Python** de Microsoft. Al abrir el proyecto, VS Code te la sugerirá.
- [Git](https://git-scm.com/downloads), para clonar el repositorio.

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

## 3. Preparar el entorno (solo la primera vez)

1. Abre `Terminal > Run Task…`.
2. Elige **1. Preparar entorno**.
3. Espera a que termine. Se creará la carpeta `.venv` con las dependencias.

Si VS Code pregunta qué intérprete usar, elige el de `.venv`.

## 4. Generar el reporte

Presiona `Ctrl+Shift+B`. Esto ejecuta la tarea **2. Generar y abrir reporte**, que:

1. Lee los Excel definidos en `config.yaml`.
2. Crea `output/reporte_mrm.html`.
3. Lo abre en tu navegador.
4. Muestra en el panel de la terminal los avisos de calidad de datos.

La salida correcta se ve así:

```text
reporte_mrm.html: 1227 filas, fechas [...], 343 observaciones, 309 coberturas
Avisos de calidad de datos:
  - 10 modelos "Sin Seguimiento" con nota de profundidad de seguimiento
  ...
```

El reporte necesita internet al abrirse, porque carga los estilos desde un CDN. También puedes compartir el archivo HTML: incluye todos los datos.

## 5. Ejecutar las pruebas

En `Terminal > Run Task…`, elige **3. Ejecutar pruebas**. Comprueban que el proceso funcione de principio a fin. Conviene correrlas antes de subir cambios.

## 6. Depurar paso a paso

Abre el panel **Run and Debug** (`Ctrl+Shift+D`), elige **Generar reporte** y presiona `F5`. Puedes poner puntos de interrupción en `src/generar_reporte.py`.

## 7. Alternativa por terminal

Abre la terminal integrada (`Ctrl+Ñ` o `` Ctrl+` ``) y ejecuta estos comandos en PowerShell.

Crear el entorno e instalar dependencias:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\python -m pip install -r requirements.txt
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

## 8. Errores frecuentes

| Mensaje o síntoma | Causa | Solución |
|---|---|---|
| `python` no se reconoce | Python no está instalado o no está en el PATH | Reinstálalo marcando **Add python.exe to PATH** y reinicia VS Code |
| `ModuleNotFoundError: yaml` u `openpyxl` | Falta preparar el entorno | Ejecuta la tarea **1. Preparar entorno** |
| `El sistema no puede encontrar la ruta` al usar `Ctrl+Shift+B` | No existe `.venv` | Ejecuta la tarea **1. Preparar entorno** |
| `No se encontró el Excel` | La ruta de `config.yaml` no coincide con el archivo | Corrige el nombre en `config.yaml` |
| `Faltan columnas en …` | El Excel cambió de estructura | Compáralo con [Datos de entrada](datos.md) |
| `Modelos repetidos en una misma FECHA` | Un ID aparece dos veces en una fecha | Corrige el input principal |
| `El input ya tiene varias fechas` | El input trae historial y la simulación sigue activa | Cambia `simulacion.activa` a `false` en `config.yaml` |
| `PermissionError` al guardar | El Excel está abierto | Ciérralo y vuelve a ejecutar |
| El reporte se ve sin estilos | No hay acceso al CDN | Revisa la conexión a internet o la red corporativa |
