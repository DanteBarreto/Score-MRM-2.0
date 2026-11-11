"""Crea el diccionario de datos a partir de esquema.py, en dos formatos:

- docs/referencia/Diccionario_de_datos.xlsx: una hoja resumen y una hoja por archivo de entrada.
- El anexo "Archivos de entrada" de docs/guia_vscode.md, entre las marcas ARCHIVOS:INICIO y ARCHIVOS:FIN.

Vuelve a ejecutarlo cuando cambie esquema.py:
    python src/generar_diccionario.py
"""
import re
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from esquema import ARCHIVOS

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "docs" / "referencia" / "Diccionario_de_datos.xlsx"
GUIA = RAIZ / "docs" / "guia_vscode.md"
HOJAS = {"input_principal": "Input principal", "inventario": "Inventario", "ttm": "TTM", "observaciones": "Observaciones",
         "observaciones_sbs_ai": "Obs SBS y AI", "nota_gobierno": "Nota de Gobierno", "calidad_datos": "Calidad de Datos",
         "coberturas": "Tablón de coberturas"}
TIPOS = [
    ("entero", "Número sin decimales", "`12`"),
    ("decimal", "Número; puede ser negativo", "`-1.5`"),
    ("decimal 0-1", "Número entre 0 y 1 (porcentaje en formato decimal)", "`0.85`"),
    ("decimal 0-100", "Número entre 0 y 100", "`72.5`"),
    ("fecha", "Celda con formato de fecha de Excel, desde 1990", "`30/09/2026`"),
    ("fecha texto", "Texto con formato `d/mm/aaaa`", "`5/03/2027`"),
    ("id modelo", "Número del modelo o código que termina en ese número", "`21122` o `MOD-BCP-21122`"),
    ("lista de id", "Uno o varios ID separados por punto y coma", "`21122; 4189`"),
    ("monto o texto", "Número o texto", "`15000` o `Sin monto`"),
    ("texto", "Texto libre", "`Banca Minorista`"),
    ("categoría", "Solo uno de los valores indicados, escrito igual", "`Coberturado`"),
]


def escribir(hoja, cabecera, filas, anchos):
    hoja.append(cabecera)
    for celda in hoja[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="096AAD")
    for fila in filas:
        hoja.append(fila)
    for columna, ancho in zip("ABCDEFG", anchos):
        hoja.column_dimensions[columna].width = ancho
    for fila in hoja.iter_rows(min_row=2):
        for celda in fila:
            celda.alignment = Alignment(wrap_text=True, vertical="top")
    hoja.freeze_panes = "A2"


def excel():
    libro = Workbook()
    resumen = libro.active
    resumen.title = "Archivos"
    escribir(resumen, ["ARCHIVO", "CLAVE EN CONFIG.YAML", "OBLIGATORIO", "GRANULARIDAD", "LLAVE DEL MODELO", "COLUMNA DE FECHA", "SECCIÓN DEL REPORTE"],
             [[a.titulo, a.clave, "Sí" if a.clave == "input_principal" else "No", a.granularidad, a.id_modelo or "PO_USUARIO y MODELO_DEVELOPER",
               a.fecha or "No tiene", a.seccion] for a in ARCHIVOS.values()], [28, 24, 14, 44, 32, 20, 22])
    for clave, arch in ARCHIVOS.items():
        hoja = libro.create_sheet(HOJAS[clave])
        escribir(hoja, ["VARIABLE", "TIPO", "ADMITE VACÍOS", "USO EN EL REPORTE", "DESCRIPCIÓN"],
                 [[c.nombre, c.tipo, "Sí" if c.nulos else "No", "Requerido" if c.requerido else "Informativo", c.descripcion] for c in arch.campos],
                 [44, 44, 16, 20, 70])
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    libro.save(SALIDA)


def md(texto):
    return str(texto).replace("|", "\\|")


def tipo_md(tipo):
    if tipo.startswith("categoría:"):
        return "categoría: " + ", ".join(f"`{v.strip()}`" for v in tipo.split(":", 1)[1].split(";"))
    return tipo


def anexo():
    """Texto del anexo de la guía: archivos, tipos de dato y campos de cada archivo."""
    nombres = (yaml.safe_load((RAIZ / "config.ejemplo.yaml").read_text(encoding="utf-8")) or {}).get("archivos", {})
    l = ["## Anexo: archivos de entrada", "",
         "Esta sección se genera desde `src/esquema.py` con `python src/generar_diccionario.py`; no la edites a mano. "
         "La misma información está en el [diccionario de datos](referencia/Diccionario_de_datos.xlsx).", "",
         "### Archivos que necesita el proceso", "",
         "Todos van en la carpeta de `carpeta_inputs`. El proceso lee la **primera hoja** de cada Excel, con los nombres de las columnas en la **primera fila**.", "",
         "| Archivo | Nombre por defecto | Clave en `config.yaml` | Obligatorio | Una fila por | Llave del modelo | Columna de fecha | Sección |",
         "|---|---|---|---|---|---|---|---|"]
    for a in ARCHIVOS.values():
        l.append(f"| {a.titulo} | `{nombres.get(a.clave, '-')}` | `{a.clave}` | {'Sí' if a.clave == 'input_principal' else 'No'} | "
                 f"{md(a.granularidad.removeprefix('Una fila por ').removeprefix('Una fila '))} | `{a.id_modelo or 'PO_USUARIO y MODELO_DEVELOPER'}` | "
                 f"{f'`{a.fecha}`' if a.fecha else 'No tiene'} | {a.seccion} |")
    l += ["", "- **Gobierno:** su contenido no es un input; viene en el repositorio, en `contenido/gobierno_modelos.yaml`.",
          "- **Obligatorio:** sin el input principal el proceso no corre. Si falta otro archivo, su bloque del reporte no se muestra.",
          "- **Último mes:** los archivos de detalle deben corresponder a la última fecha del input principal.",
          "- **Columnas requeridas:** si falta una, el proceso se detiene. Si falta una informativa o sobra una columna, solo se avisa.", "",
          "### Tipos de dato", "", "| Tipo | Qué se espera | Ejemplo |", "|---|---|---|"]
    l += [f"| {t} | {d} | {e} |" for t, d, e in TIPOS]
    l += ["", "**Admite vacíos:** si dice No y la celda viene vacía, el control de calidad lo reporta.", "",
          "### Campos de cada archivo", "", "Haz clic en un archivo para ver sus campos.", ""]
    for a in ARCHIVOS.values():
        req = sum(c.requerido for c in a.campos)
        l += ["<details>", f"<summary><b>{a.titulo}</b> · {len(a.campos)} campos, {req} requeridos</summary>", "",
              "| Campo | Tipo | Admite vacíos | Uso | Descripción |", "|---|---|---|---|---|"]
        l += [f"| `{c.nombre}` | {md(tipo_md(c.tipo))} | {'Sí' if c.nulos else 'No'} | {'Requerido' if c.requerido else 'Informativo'} | {md(c.descripcion)} |"
              for c in a.campos]
        l += ["", "</details>", ""]
    return "\n".join(l).rstrip() + "\n"


def guia():
    texto = GUIA.read_text(encoding="utf-8")
    nuevo, n = re.subn(r"<!-- ARCHIVOS:INICIO -->.*?<!-- ARCHIVOS:FIN -->",
                       lambda _: f"<!-- ARCHIVOS:INICIO -->\n{anexo()}<!-- ARCHIVOS:FIN -->", texto, flags=re.S)
    if n != 1:
        raise SystemExit(f"{GUIA.name} debe tener una sola vez las marcas ARCHIVOS:INICIO y ARCHIVOS:FIN")
    GUIA.write_text(nuevo, encoding="utf-8")


def main():
    excel()
    guia()
    print(f"{SALIDA.name} y anexo de {GUIA.name}: {len(ARCHIVOS)} archivos y {sum(len(a.campos) for a in ARCHIVOS.values())} campos")


if __name__ == "__main__":
    main()
