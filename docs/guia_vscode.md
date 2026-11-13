# Manual de ejecución en Visual Studio Code

Este manual explica qué archivos necesita el proceso y cómo instalarlo y ejecutarlo en Visual Studio Code, desde cero y en cada actualización mensual. El detalle de cada archivo (campos, tipos de dato y si admiten vacíos) está en el [anexo](#anexo-archivos-de-entrada).

## Resumen

| Cuándo | Qué hacer |
|---|---|
| Solo la primera vez | Instalar los requisitos, clonar el repositorio, preparar el entorno y configurar `config.yaml` (pasos 1 a 4) |
| Cada mes | Actualizar los inputs de tu carpeta y presionar `Ctrl+Shift+B` (paso 5). El detalle está en [Actualización mensual](actualizacion_mensual.md) |
| Antes de subir cambios al código | Ejecutar las pruebas (paso 7) |

## 1. Requisitos

- [Python 3.10 o superior](https://www.python.org/downloads/). En Windows, marca **Add python.exe to PATH** durante la instalación.
- [Visual Studio Code](https://code.visualstudio.com/) con la extensión **Python** de Microsoft. Al abrir el proyecto, VS Code te la sugerirá.
- [Git](https://git-scm.com/downloads), para clonar el repositorio y recibir las actualizaciones.
- Una carpeta de tu equipo con los inputs. El repositorio no los incluye. Los nombres, los campos y el tipo de dato de cada uno están en el [anexo de esta guía](#anexo-archivos-de-entrada):
  - el input principal histórico (obligatorio);
  - los siete Excel de detalle: Inventario de modelos, TTM, Reporte de observaciones, Observaciones SBS & AI, Nota de Gobierno, Calidad de Datos y Tablón de coberturas.

  El contenido de la sección Gobierno viene incluido en el repositorio, en `contenido/gobierno_modelos.yaml`; no tienes que copiarlo.

Para comprobar Python, abre una terminal y ejecuta:

```bash
python --version
```

## 2. Obtener el proyecto

En VS Code, abre la paleta con `Ctrl+Shift+P`, elige **Git: Clone** y pega esta dirección:

```text
https://github.com/DanteBarreto/Score-MRM-2.0.git
```

Elige una carpeta y, cuando VS Code lo pregunte, abre el proyecto. Evita carpetas con rutas muy largas: en Windows pueden causar errores. Si VS Code pregunta si confías en los autores de la carpeta, elige **Yes, I trust the authors** para que funcionen las tareas.

Si ya tenías el proyecto, actualízalo con `Ctrl+Shift+P` > **Git: Pull** antes de generar el reporte.

## Opción rápida: ejecución guiada

Abre la terminal integrada (`Ctrl+Ñ` o `` Ctrl+` ``) y ejecuta:

```bash
python ejecutar.py
```

El script explica cada paso, prepara el entorno, te pide la carpeta de tus inputs, avisa qué archivos faltan y genera el reporte. También puedes abrir `ejecutar.py` y presionar **Run Python File**, el triángulo de arriba a la derecha. Si prefieres hacerlo por tareas, sigue los pasos 3 a 5.

## 3. Preparar el entorno (solo la primera vez)

1. Abre `Terminal > Run Task…`.
2. Elige **1. Preparar entorno**.
3. Espera a que termine. Se creará la carpeta `.venv` con las dependencias y tu archivo `config.yaml`.

Si VS Code pregunta qué intérprete usar, elige el de `.venv`. También puedes elegirlo con `Ctrl+Shift+P` > **Python: Select Interpreter**.

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

Para copiar la ruta, abre la carpeta en el Explorador de archivos y haz clic en la barra de direcciones. Si tus archivos tienen otros nombres, cámbialos en `archivos`. Solo el input principal es obligatorio: si falta otro archivo, su bloque no se muestra.

`config.yaml` es solo tuyo: Git lo ignora, así que tu ruta no se sube al repositorio.

## 5. Generar el reporte

Presiona `Ctrl+Shift+B`. Esto ejecuta la tarea **2. Generar y abrir reporte**, que:

1. Lee los inputs de tu carpeta local y revisa su calidad.
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

El reporte es un solo archivo autocontenido: lleva dentro los estilos, los íconos y la fuente, así que no necesita internet y se puede compartir por correo, Teams o SharePoint. Incluye todos los datos, así que compártelo solo con quien corresponda.

## 6. Revisar el reporte

Con el reporte abierto en el navegador:

- **Filtros**, en la barra lateral: Fecha es de selección única. Entidad, Tipo de riesgo, Tier, PO / Usuario responsable, Model user, Model developer, Proceso, Banca y Producto permiten elegir varios valores. Entidad sale de la columna `ENTIDAD_MODELO` del input principal; si no la trae, los modelos aparecen como «Sin información». Los umbrales del semáforo cambian según los Tier elegidos.
- **Simulador**, en el tablero de indicadores de la sección Reporte: sube o baja el valor de un indicador para ver cómo cambian su puntuación, el score y el semáforo. Los indicadores que dependen de él se recalculan en cascada y el recuadro **Efectos de tu simulación** explica qué cambió. **Valores iniciales** deshace la simulación. Simular no modifica ningún archivo. Las reglas están en [Indicadores](indicadores.md#simulador).
- **Exportar CSV**: descarga los indicadores de los modelos filtrados.
- Los bloques que vienen de los Excel de detalle solo se muestran con el **último mes** seleccionado.

## 7. Ejecutar las pruebas

En `Terminal > Run Task…`, elige **3. Ejecutar pruebas**. Usan Excel ficticios que crean y borran solas, así que no necesitan tus inputs. También puedes correrlas desde el panel **Testing**, el ícono del matraz. Conviene correrlas antes de subir cambios.

## 8. Depurar paso a paso

Abre el panel **Run and Debug** (`Ctrl+Shift+D`), elige **Generar reporte** y presiona `F5`. Puedes poner puntos de interrupción en `src/generar_reporte.py`.

## 9. Alternativa por terminal

Abre la terminal integrada y ejecuta estos comandos en PowerShell.

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

Generar el reporte con otra configuración, por ejemplo para una prueba:

```bash
.venv\Scripts\python src/generar_reporte.py --config otra_config.yaml --abrir
```

Ejecutar las pruebas:

```bash
.venv\Scripts\python -m unittest discover -s tests
```

En macOS o Linux, usa `python3` para crear el entorno y `.venv/bin/python` en los demás comandos.

## 10. Errores frecuentes

| Mensaje o síntoma | Causa | Solución |
|---|---|---|
| `python` no se reconoce | Python no está instalado o no está en el PATH | Reinstálalo marcando **Add python.exe to PATH** y reinicia VS Code |
| `ModuleNotFoundError: yaml` u `openpyxl` | Falta preparar el entorno | Ejecuta la tarea **1. Preparar entorno** |
| `El sistema no puede encontrar la ruta` al usar `Ctrl+Shift+B` | No existe `.venv` | Ejecuta la tarea **1. Preparar entorno** |
| Las tareas no aparecen en `Run Task…` | La carpeta está en modo restringido | Abre `Ctrl+Shift+P` > **Workspaces: Manage Workspace Trust** y confía en la carpeta |
| `No existe config.yaml` | Falta crear la configuración local | Ejecuta la tarea **1. Preparar entorno** |
| `No se encontró el Excel` | `carpeta_inputs` o el nombre del archivo no coinciden | Corrige la ruta y los nombres en `config.yaml` |
| `found unknown escape character` | La ruta está entre comillas dobles | Usa comillas simples en `carpeta_inputs` |
| `Faltan columnas en …` | El Excel cambió de estructura | Compáralo con el [anexo de archivos de entrada](#anexo-archivos-de-entrada) |
| `Modelos repetidos en una misma FECHA` | Un ID aparece dos veces en una fecha | Corrige el input principal |
| `El proceso se detuvo por errores de calidad de datos` | Un archivo tiene un problema que impide un reporte confiable | Corrige lo indicado y revisa [calidad_datos.md](calidad_datos.md) |
| Gobierno no muestra los últimos cambios | El repositorio de tu equipo está desactualizado | Haz **Git: Pull**, vuelve a generar el reporte y recarga el navegador con `Ctrl+F5` |
| `No se encontró contenido/gobierno_modelos.yaml` | Falta el archivo en tu copia del repositorio | Haz **Git: Pull** |
| `gobierno_modelos.yaml no es un YAML válido` | El archivo se editó y quedó mal formado | Revisa la línea indicada: sangría con espacios, y textos con comas o dos puntos entre comillas |
| No aparecen los bloques de TTM, SBS & AI, Calidad de Datos, Inventario o Nota de Gobierno | Tu `config.yaml` es de la versión 1 y no lista esos archivos | Copia las secciones `archivos` y `homologacion` de `config.ejemplo.yaml` |
| Un bloque muestra "solo está disponible para…" | Elegiste un mes anterior al último | Selecciona el último mes en el filtro Fecha |
| `PermissionError` al guardar | El Excel está abierto | Ciérralo y vuelve a ejecutar |
| El reporte se ve sin estilos o deformado | Se generó con una versión anterior al 11/11/2026, que cargaba los estilos de internet | Haz **Git: Pull**, vuelve a generar el reporte y comparte el archivo nuevo |
| Al abrirlo desde SharePoint se descarga o se ve el código | SharePoint no muestra páginas HTML en el navegador | Descárgalo y ábrelo con doble clic |

<!-- ARCHIVOS:INICIO -->
## Anexo: archivos de entrada

Esta sección se genera desde `src/esquema.py` con `python src/generar_diccionario.py`; no la edites a mano. La misma información está en el [diccionario de datos](referencia/Diccionario_de_datos.xlsx).

### Archivos que necesita el proceso

Todos van en la carpeta de `carpeta_inputs`. El proceso lee la **primera hoja** de cada Excel, con los nombres de las columnas en la **primera fila**.

| Archivo | Nombre por defecto | Clave en `config.yaml` | Obligatorio | Una fila por | Llave del modelo | Columna de fecha | Sección |
|---|---|---|---|---|---|---|---|
| Input principal histórico | `Input_principal_Score MRM_hist.xlsx` | `input_principal` | Sí | modelo y fecha de corte | `ID_MODELO` | `FECHA` | Todas |
| Inventario de modelos | `Inventario de modelos.xlsx` | `inventario` | No | modelo | `ID_MODELO` | No tiene | Inventario |
| TTM | `TTM.xlsx` | `ttm` | No | modelo en alerta | `ID_MODELO` | No tiene | Seguimiento |
| Reporte de observaciones | `Reporte de observaciones.xlsx` | `observaciones` | No | observación de validación pendiente | `ID_Model` | `FECHA_PROCESO` | Observaciones |
| Observaciones SBS & AI | `Observaciones SBS & AI.xlsx` | `observaciones_sbs_ai` | No | observación de SBS o auditoría interna | `ID_MODELO` | No tiene | Observaciones |
| Nota de Gobierno | `Nota de Gobierno.xlsx` | `nota_gobierno` | No | PO usuario y model developer | `PO_USUARIO y MODELO_DEVELOPER` | No tiene | Gobierno |
| Calidad de Datos | `Calidad de Datos.xlsx` | `calidad_datos` | No | modelo evaluado | `ID` | No tiene | Implementación |
| Tablón de coberturas | `Tablón de coberturas.xlsx` | `coberturas` | No | modelo | `Modelo_ID` | `Fecha` | Validación |

- **Gobierno:** su contenido no es un input; viene en el repositorio, en `contenido/gobierno_modelos.yaml`.
- **Obligatorio:** sin el input principal el proceso no corre. Si falta otro archivo, su bloque del reporte no se muestra.
- **Último mes:** los archivos de detalle deben corresponder a la última fecha del input principal.
- **Columnas requeridas:** si falta una, el proceso se detiene. Si falta una informativa o sobra una columna, solo se avisa.

### Tipos de dato

| Tipo | Qué se espera | Ejemplo |
|---|---|---|
| entero | Número sin decimales | `12` |
| decimal | Número; puede ser negativo | `-1.5` |
| decimal 0-1 | Número entre 0 y 1 (porcentaje en formato decimal) | `0.85` |
| decimal 0-100 | Número entre 0 y 100 | `72.5` |
| fecha | Celda con formato de fecha de Excel, desde 1990 | `30/09/2026` |
| fecha texto | Texto con formato `d/mm/aaaa` | `5/03/2027` |
| id modelo | Número del modelo o código que termina en ese número | `21122` o `MOD-BCP-21122` |
| lista de id | Uno o varios ID separados por punto y coma | `21122; 4189` |
| monto o texto | Número o texto | `15000` o `Sin monto` |
| texto | Texto libre | `Banca Minorista` |
| categoría | Solo uno de los valores indicados, escrito igual | `Coberturado` |

**Admite vacíos:** si dice No y la celda viene vacía, el control de calidad lo reporta.

### Campos de cada archivo

Haz clic en un archivo para ver sus campos.

<details>
<summary><b>Input principal histórico</b> · 47 campos, 46 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `FECHA` | fecha | No | Requerido | Fecha de corte, fin de mes |
| `ID_MODELO` | id modelo | No | Requerido | Identificador del modelo. Llave de unión con los demás archivos |
| `NOMBRE_MODELO` | texto | No | Requerido | Nombre del modelo |
| `TIER_MODELO` | categoría: `I`, `II`, `III`, `IV` | No | Requerido | Nivel de materialidad |
| `ENTIDAD_MODELO` | texto | Sí | Informativo | Entidad dueña del modelo (filtro Entidad). Si falta, se muestra como Sin información |
| `ESTADO_MODELO` | texto | No | Requerido | Estado del modelo a la fecha de corte |
| `TIPO_RIESGO` | texto | No | Requerido | Tipo de riesgo |
| `PRODUCTO` | texto | No | Requerido | Producto |
| `SUB_PRODUCTO` | texto | No | Requerido | Sub producto |
| `BANCA` | texto | No | Requerido | Banca |
| `PROCESO` | texto | No | Requerido | Proceso en el que se usa el modelo |
| `ESTADO_SEGUIMIENTO` | categoría: `Con Seguimiento`, `Sin Seguimiento`, `No aplica`, `Sin información` | No | Requerido | Situación del seguimiento |
| `ESTADO_ALERTA` | categoría: `En alerta`, `Sin alerta`, `Saludable`, `Aceptable`, `No aplica`, `Sin información` | No | Requerido | Alerta de salud del modelo |
| `EXCESO_MESES_TTM` | decimal | Sí | Requerido | Meses de exceso sobre el tiempo máximo de atención; negativo si aún está en plazo |
| `EXCEDE_TTM` | categoría: `Excede TTM`, `No excede`, `No tiene TTM` | Sí | Requerido | Situación frente al tiempo máximo de atención |
| `IMPACTO` | monto o texto | Sí | Requerido | Impacto estimado de la alerta: un monto o un texto como "Sin info" |
| `PRESENCIA_MITIGANTE` | categoría: `Si`, `No` | Sí | Requerido | Indica si la alerta tiene mitigante temporal |
| `DESCRIPCION_MITIGANTE` | texto | Sí | Requerido | Descripción del mitigante |
| `VALIDACION_COMPLETA` | categoría: `Con validación`, `Sin validación` | No | Requerido | Validación de primera vez |
| `VALIDACION_PERIODICA` | categoría: `Coberturado`, `Descoberturado` | No | Requerido | Vigencia de la validación periódica |
| `NOTA_DINAMICA_VALIDACION` | decimal 0-1 | Sí | Requerido | Nota dinámica de validación |
| `OBS_CRIT_RELE_MODE_PENDIENTES_VI` | entero | No | Requerido | Observaciones de validación críticas, relevantes y moderadas pendientes |
| `OBS_CRIT_RELE_MODE_VENCIDAS_VI` | entero | No | Requerido | Observaciones de validación críticas, relevantes y moderadas vencidas |
| `OBS_SBS_AI_PENDIENTES` | entero | No | Requerido | Observaciones de SBS y auditoría interna pendientes |
| `OBS_SBS_AI_VENCIDAS` | entero | No | Requerido | Observaciones de SBS y auditoría interna vencidas |
| `PLATAFORMA_IMPLEMENTACION` | texto | No | Requerido | Plataformas de implementación, separadas por coma |
| `AMBIENTE_DESPLIEGUE` | categoría: `PRODUCTIVO`, `NO PRODUCTIVO`, `MIXTO`, `EN REVISIÓN`, `Sin información` | No | Requerido | Ambiente del despliegue |
| `PLATAFORMA_DATA` | texto | No | Requerido | Plataformas de data, separadas por coma |
| `AMBIENTE_DATA` | categoría: `PRODUCTIVO`, `NO PRODUCTIVO`, `MIXTO`, `EN REVISIÓN`, `Sin información` | No | Requerido | Ambiente de la data |
| `RATIO_IMPLEMENTACION` | decimal 0-1 | Sí | Requerido | Parte del despliegue en ambiente productivo |
| `RATIO_DATA` | decimal 0-1 | Sí | Requerido | Parte de la data en ambiente productivo |
| `OBS_AMB_TEC_PENDIENTES` | entero | No | Requerido | Observaciones de entorno tecnológico pendientes |
| `OBS_AMB_TEC_VENCIDOS` | entero | No | Requerido | Observaciones de entorno tecnológico vencidas |
| `BBDD` | decimal 0-1 | Sí | Requerido | Completitud de seguimiento: base de datos |
| `GOB` | decimal 0-1 | Sí | Requerido | Completitud de seguimiento: gobierno |
| `PRECISION_DISCRIMINACION` | decimal 0-1 | Sí | Requerido | Completitud de seguimiento: precisión y discriminación |
| `GRANULARIDAD` | decimal 0-1 | Sí | Requerido | Completitud de seguimiento: granularidad |
| `UNIVARIADA` | decimal 0-1 | Sí | Requerido | Completitud de seguimiento: análisis univariado |
| `NUM_INCIDENTES` | entero | No | Requerido | Incidentes en el inventario |
| `NOTA_GOBIERNO` | decimal 0-1 | Sí | Requerido | Nota de documentación y gobierno |
| `NOTA_10_LINEAMIENTOS` | decimal 0-1 | Sí | Requerido | Cumplimiento de los 10 lineamientos de desarrollo |
| `NOTA_CALIDAD_DATOS` | decimal 0-1 | Sí | Requerido | Indicador de calidad de datos |
| `MODEL_DEVELOPER` | texto | No | Requerido | Área desarrolladora |
| `RESPONSABLE_MONITORING` | texto | No | Requerido | Responsable del seguimiento |
| `RESPONSABLE_DEVELOPER` | texto | No | Requerido | Responsable del desarrollo |
| `PO_USUARIO` | texto | No | Requerido | PO o usuario responsable |
| `MODEL_USER` | texto | No | Requerido | Área usuaria |

</details>

<details>
<summary><b>Inventario de modelos</b> · 28 campos, 5 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `ID_MODELO` | id modelo | No | Requerido | Identificador del modelo |
| `CODIGO_MODELO` | texto | No | Informativo | Código del modelo |
| `NOMBRE_MODELO` | texto | No | Requerido | Nombre del modelo |
| `PERIMETRO_MODELO` | texto | No | Requerido | Perímetro: modelo, módulo, proceso, etc. |
| `ESTADO_MODELO` | texto | Sí | Informativo | Estado en el inventario. El reporte usa el estado del input principal |
| `TIER_MODELO` | texto | Sí | Informativo | Nivel de materialidad |
| `ENTIDAD_MODELO` | texto | No | Informativo | Entidad dueña del modelo |
| `CLASE_MODELO` | texto | Sí | Informativo | Clase de riesgo |
| `TIPO_MODELO` | texto | Sí | Requerido | Tipo de modelo |
| `USO_GENERICO_MODELO` | texto | Sí | Informativo | Uso genérico |
| `USO_ESPECIFICO_1` | texto | Sí | Informativo | Uso específico principal |
| `USO_ESPECIFICO_2` | texto | Sí | Informativo | Uso específico secundario |
| `BANCA` | texto | Sí | Informativo | Banca |
| `LINEA_PRODUCTO` | texto | Sí | Informativo | Línea de producto |
| `ID_MODELO_INPUT` | lista de id | Sí | Requerido | Modelos input que usa este modelo, separados por punto y coma |
| `COD_NOMBRE_MODELO_INPUT` | texto | Sí | Informativo | Código y nombre de los modelos input |
| `ID_VERSION_ANTERIOR` | id modelo | Sí | Informativo | Versión anterior del modelo |
| `CODIGO_MODELO_VERSION_ANTERIOR` | texto | Sí | Informativo | Código de la versión anterior |
| `NOMBRE_MODELO_VERSION_ANTERIOR` | texto | Sí | Informativo | Nombre de la versión anterior |
| `MODEL_IMPLEMENTER` | texto | Sí | Informativo | Área implementadora |
| `MODEL_USER` | texto | Sí | Informativo | Área usuaria |
| `MODEL_DEVELOPER` | texto | Sí | Informativo | Área desarrolladora |
| `MODEL_VALIDATOR` | texto | Sí | Informativo | Área validadora |
| `MODEL_DATA_PROVIDER` | texto | Sí | Informativo | Área proveedora de datos |
| `MODELOELIMINADO` | entero | No | Informativo | Marca de eliminación. Su significado está por confirmar |
| `DESCRIPCION` | texto | Sí | Informativo | Descripción del modelo |
| `FECHA_INICIO_USO` | fecha | Sí | Informativo | Fecha de inicio de uso |
| `FECHA_RETIRO_USO` | fecha | Sí | Informativo | Fecha de retiro |

</details>

<details>
<summary><b>TTM</b> · 13 campos, 10 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `ID_MODELO` | id modelo | No | Requerido | Identificador del modelo |
| `NOMBRE_MODELO` | texto | No | Informativo | Nombre del modelo |
| `TIER` | texto | No | Informativo | Nivel de materialidad |
| `FECH_ALERTA` | fecha | No | Requerido | Fecha en que se levantó la alerta |
| `DIAGNOSTICO` | texto | Sí | Requerido | Diagnóstico de la alerta |
| `PLAN_ACCION` | texto | Sí | Requerido | Plan de acción |
| `MITIGANTE` | texto | Sí | Informativo | Mitigante temporal |
| `TTM_GOBIERNO_MESES` | decimal | Sí | Requerido | Tiempo máximo de atención definido por gobierno, en meses |
| `TTM_REAL_HOY` | decimal | No | Requerido | Tiempo transcurrido, en meses |
| `HOLGURA_EXCESO_TTM` | decimal | Sí | Requerido | TTM real menos TTM de gobierno; positivo si excede |
| `SOLICITO_AMPLIACION` | categoría: `Si`, `No` | No | Requerido | Indica si se pidió ampliar el plazo |
| `NUEVA_FECH_SUBSANACION` | fecha | Sí | Requerido | Nueva fecha comprometida |
| `COMENTARIOS` | texto | Sí | Requerido | Comentarios |

</details>

<details>
<summary><b>Reporte de observaciones</b> · 26 campos, 17 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `FECHA_PROCESO` | fecha | No | Requerido | Fecha del archivo |
| `ID_Obs` | entero | No | Requerido | Identificador de la observación |
| `Observación` | texto | No | Requerido | Texto de la observación |
| `Recomendación` | texto | No | Requerido | Recomendación |
| `Criticidad_observacion` | categoría: `Crítico`, `Relevante`, `Moderado`, `Bajo`, `Potencial`, `Nulo` | No | Requerido | Criticidad |
| `Ambito_observacion` | texto | No | Requerido | Ámbito |
| `Estado_observacion` | texto | No | Informativo | Estado de la observación |
| `Estado_Vencimiento` | categoría: `Vencido`, `Por vencer < 15 días`, `Por vencer < 30 días`, `Por vencer > 30 días` | No | Requerido | Situación del plazo |
| `# Ampliaciones` | entero | No | Requerido | Número de ampliaciones de plazo |
| `Fecha ampliada` | fecha | Sí | Requerido | Nuevo compromiso tras una ampliación |
| `Fecha cierre` | fecha | Sí | Informativo | Fecha de cierre |
| `Fecha estimada` | fecha | No | Requerido | Compromiso original |
| `Codigo_proyecto` | texto | No | Informativo | Código del proyecto de validación |
| `Nombre_proyecto` | texto | No | Requerido | Proyecto de validación |
| `Estado_proyecto` | texto | No | Informativo | Estado del proyecto |
| `Tipo_revisión` | texto | No | Requerido | Tipo de revisión |
| `ID_Model` | id modelo | No | Requerido | Identificador del modelo |
| `Codigo_modelo` | texto | No | Informativo | Código del modelo |
| `Nombre_modelo` | texto | No | Informativo | Nombre del modelo |
| `Tier` | texto | No | Informativo | Nivel de materialidad |
| `Area homologada` | texto | No | Requerido | Área responsable |
| `Manager_nombre` | texto | No | Requerido | Manager de validación |
| `Validador_nombre` | texto | No | Requerido | Validador |
| `Propietario_nombre` | texto | No | Requerido | Propietario de la observación |
| `Diferencia_dias` | entero | Sí | Informativo | Días desde el compromiso original |
| `Observaciones_PA_createdon` | fecha | No | Informativo | Fecha de registro |

</details>

<details>
<summary><b>Observaciones SBS & AI</b> · 17 campos, 15 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `ID` | entero | No | Requerido | Identificador de la observación |
| `CodigoProyecto` | texto | No | Requerido | Código del proyecto u oficio |
| `NombreProyecto/Visita Inspección` | texto | No | Requerido | Proyecto o visita de inspección |
| `TituloObs` | texto | No | Requerido | Título de la observación |
| `Observación` | texto | No | Requerido | Texto de la observación |
| `Recomendación` | texto | No | Requerido | Recomendación |
| `Estado` | categoría: `Pendiente`, `En Proceso`, `Implementada Por Verificar` | No | Requerido | Estado. Solo "Pendiente" cuenta como pendiente |
| `Riesgo` | texto | No | Requerido | Nivel de riesgo. SBS y auditoría interna usan escalas distintas |
| `Fecha Emisión` | fecha texto | No | Requerido | Fecha de emisión, como dd/mm/aaaa |
| `Fecha de Vencimiento` | fecha | No | Requerido | Fecha de vencimiento |
| `Propietario` | texto | No | Requerido | Propietario |
| `Unidad Responsable` | texto | No | Requerido | Unidad responsable |
| `Número de ampliaciones` | entero | No | Requerido | Ampliaciones de plazo |
| `Tipo` | categoría: `SBS`, `A. Interna` | No | Requerido | Origen de la observación |
| `Correo` | texto | Sí | Informativo | Correo del propietario. No se incluye en el reporte |
| `ID_MODELO` | lista de id | Sí | Requerido | Modelos a los que aplica; texto si es transversal |
| `NOMBRE_MODELO` | texto | Sí | Informativo | Nombre del modelo |

</details>

<details>
<summary><b>Nota de Gobierno</b> · 10 campos, 10 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `MODELO_DEVELOPER` | texto | No | Requerido | Área desarrolladora |
| `MODEL_USER` | texto | No | Requerido | Área usuaria |
| `PO_USUARIO` | texto | No | Requerido | PO o usuario responsable. Llave de unión, junto con el model developer |
| `NOTA_GOBIERNO` | decimal 0-100 | No | Requerido | Nota de gobierno: promedio de los componentes con dato |
| `NOTA_POLITICAS` | decimal 0-100 | Sí | Requerido | Componente: políticas |
| `NOTA_ESTANDARES` | decimal 0-100 | Sí | Requerido | Componente: estándares |
| `NOTA_DESARROLLO` | decimal 0-100 | Sí | Requerido | Componente: desarrollo |
| `NOTA_VALIDACION` | decimal 0-100 | Sí | Requerido | Componente: validación |
| `WAIVERS` | decimal 0-100 | Sí | Requerido | Componente: waivers |
| `NOTA_CUMPL_CALCULADORA_VALIZACION` | decimal 0-100 | Sí | Requerido | Componente: uso de la calculadora de valorización |

</details>

<details>
<summary><b>Calidad de Datos</b> · 13 campos, 10 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `ID` | id modelo | No | Requerido | Identificador del modelo |
| `Owner` | texto | No | Informativo | Área dueña |
| `Modelo` | texto | No | Informativo | Nombre del modelo |
| `Tier` | texto | No | Informativo | Nivel de materialidad |
| `Documentación de incidencias por alertas` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Gobierno formal de calidad de datos y umbrales definidos para alertas` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Roles definidos y atención a alertas en calidad de datos` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Notificación de alertas al usuario` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Controles sobre variables insumo del modelo` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Controles sobre variables salida del modelo` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Monitoreo automático o reportes adhoc` | decimal 0-1 | No | Requerido | Criterio del indicador |
| `Indicador de Calidad de datos` | decimal 0-1 | No | Requerido | Suma de los siete criterios |
| `Rango de cumplimiento` | categoría: `<= a 50%`, `50% a 70%`, `> a 70%` | No | Requerido | Rango del indicador |

</details>

<details>
<summary><b>Tablón de coberturas</b> · 35 campos, 22 requeridos</summary>

| Campo | Tipo | Admite vacíos | Uso | Descripción |
|---|---|---|---|---|
| `Fecha` | fecha | No | Requerido | Fecha del archivo |
| `Modelo_ID` | id modelo | No | Requerido | Identificador del modelo |
| `Nombre_Modelo` | texto | No | Informativo | Nombre del modelo |
| `Codigo_Modelo` | texto | No | Informativo | Código del modelo |
| `Estado_Modelo` | texto | No | Informativo | Estado del modelo |
| `Perímetro` | texto | No | Informativo | Perímetro |
| `Tier` | texto | No | Informativo | Nivel de materialidad |
| `Imp_Codigo_proyecto` | texto | Sí | Informativo | Último proyecto de validación de implementación: código |
| `Imp_Nombre_proyecto` | texto | Sí | Informativo | Último proyecto de validación de implementación: nombre |
| `Imp_Fecha_fin` | fecha | Sí | Requerido | Fecha fin del proyecto de implementación |
| `Imp_Estado_proyecto` | texto | No | Informativo | Estado del proyecto de implementación |
| `Imp_Tipo_revision` | texto | No | Requerido | Tipo de revisión de implementación |
| `Imp_Manager` | texto | Sí | Requerido | Manager de la validación de implementación |
| `Imp_Validador` | texto | Sí | Requerido | Validador de implementación |
| `Imp_Alcance` | texto | Sí | Requerido | Alcance de la validación de implementación |
| `Met_Codigo_proyecto` | texto | Sí | Informativo | Último proyecto de validación metodológica: código |
| `Met_Nombre_proyecto` | texto | Sí | Informativo | Último proyecto de validación metodológica: nombre |
| `Met_Fecha_fin` | fecha | Sí | Requerido | Fecha fin del proyecto metodológico |
| `Met_Estado_proyecto` | texto | No | Informativo | Estado del proyecto metodológico |
| `Met_Tipo_revision` | texto | No | Requerido | Tipo de revisión metodológica |
| `Cobertura_Metodologia` | categoría: `Coberturado`, `No Coberturado` | No | Requerido | Cobertura del frente metodológico |
| `Cobertura_Implementación` | categoría: `Coberturado`, `No Coberturado` | No | Requerido | Cobertura del frente de implementación |
| `Cobertura_Global` | categoría: `Coberturado`, `Descoberturado` | No | Requerido | Coberturado solo si ambos frentes lo están |
| `Met_Manager` | texto | Sí | Requerido | Manager de la validación metodológica |
| `Met_Validador` | texto | Sí | Requerido | Validador metodológico |
| `Met_Alcance` | texto | Sí | Requerido | Alcance de la validación metodológica |
| `Fecha_descobertura_Met` | fecha texto | Sí | Requerido | Fecha en que vence la cobertura metodológica, como dd/mm/aaaa |
| `Proy_Cobertura_Met` | categoría: `Coberturado`, `No Coberturado` | No | Requerido | Cobertura metodológica proyectada |
| `Fecha_descobertura_Imp` | fecha texto | Sí | Requerido | Fecha en que vence la cobertura de implementación, como dd/mm/aaaa |
| `Proy_Cobertura_Imp` | categoría: `Coberturado`, `No Coberturado` | No | Requerido | Cobertura de implementación proyectada |
| `Proy_Cobertura_Global` | categoría: `Coberturado`, `Descoberturado` | No | Requerido | Cobertura global proyectada |
| `Modelos_Cobertura_Perimetro_Q` | texto | Sí | Informativo | Perímetro considerado en la proyección |
| `Modelos_Cobertura_Tier_Q_1` | texto | Sí | Informativo | Tier considerado en la proyección |
| `Calificación_Metodología` | categoría: `Satisfactorio`, `Aceptable`, `Regular`, `Deficiente` | Sí | Requerido | Calificación de la última validación metodológica |
| `Calificación_Implementación` | categoría: `Satisfactorio`, `Aceptable`, `Regular`, `Deficiente` | Sí | Requerido | Calificación de la última validación de implementación |

</details>
<!-- ARCHIVOS:FIN -->
