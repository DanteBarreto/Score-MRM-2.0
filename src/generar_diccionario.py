"""Crea docs/referencia/Diccionario_de_datos.xlsx a partir de esquema.py.

Tiene una hoja resumen y una hoja por archivo de entrada, con cada campo, su tipo de dato,
si admite vacíos y cómo lo usa el reporte. Vuelve a ejecutarlo cuando cambie esquema.py:
    python src/generar_diccionario.py
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from esquema import ARCHIVOS

SALIDA = Path(__file__).resolve().parents[1] / "docs" / "referencia" / "Diccionario_de_datos.xlsx"
HOJAS = {"input_principal": "Input principal", "inventario": "Inventario", "ttm": "TTM", "observaciones": "Observaciones",
         "observaciones_sbs_ai": "Obs SBS y AI", "nota_gobierno": "Nota de Gobierno", "calidad_datos": "Calidad de Datos",
         "coberturas": "Tablón de coberturas"}


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


def main():
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
    print(f"{SALIDA.name}: {len(ARCHIVOS)} archivos y {sum(len(a.campos) for a in ARCHIVOS.values())} campos")


if __name__ == "__main__":
    main()
