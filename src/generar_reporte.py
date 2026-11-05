"""Genera el reporte HTML del Score MRM a partir de los Excel de insumos.

Los Excel se leen de la carpeta local indicada en config.yaml, que cada usuario crea a partir de
config.ejemplo.yaml. Uso:  python src/generar_reporte.py [--config config.yaml] [--abrir]
"""
import argparse
import json
import re
import sys
import webbrowser
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import yaml
from openpyxl import load_workbook

from simular_historico import simular

RAIZ = Path(__file__).resolve().parents[1]
PLANTILLA = RAIZ / "templates" / "plantilla_reporte.html"
MARCA = "/*__DATOS__*/null"

COLUMNAS = """FECHA ID_MODELO NOMBRE_MODELO TIER_MODELO ESTADO_MODELO TIPO_RIESGO PRODUCTO SUB_PRODUCTO BANCA PROCESO
ESTADO_SEGUIMIENTO ESTADO_ALERTA EXCESO_MESES_TTM EXCEDE_TTM IMPACTO PRESENCIA_MITIGANTE DESCRIPCION_MITIGANTE
VALIDACION_COMPLETA VALIDACION_PERIODICA NOTA_DINAMICA_VALIDACION OBS_CRIT_RELE_MODE_PENDIENTES_VI
OBS_CRIT_RELE_MODE_VENCIDAS_VI OBS_SBS_AI_PENDIENTES OBS_SBS_AI_VENCIDAS PLATAFORMA_IMPLEMENTACION AMBIENTE_DESPLIEGUE
PLATAFORMA_DATA AMBIENTE_DATA RATIO_IMPLEMENTACION RATIO_DATA OBS_AMB_TEC_PENDIENTES OBS_AMB_TEC_VENCIDOS BBDD GOB
PRECISION_DISCRIMINACION GRANULARIDAD UNIVARIADA NUM_INCIDENTES NOTA_GOBIERNO NOTA_10_LINEAMIENTOS NOTA_CALIDAD_DATOS
MODEL_DEVELOPER RESPONSABLE_MONITORING RESPONSABLE_DEVELOPER PO_USUARIO MODEL_USER""".split()

# Campos del tablón de coberturas que usa la sección Validación
COLS_COBERTURA = """Modelo_ID Cobertura_Metodologia Cobertura_Implementación Cobertura_Global Proy_Cobertura_Met Proy_Cobertura_Imp
Proy_Cobertura_Global Fecha_descobertura_Met Fecha_descobertura_Imp Met_Fecha_fin Imp_Fecha_fin Met_Tipo_revision
Imp_Tipo_revision Met_Alcance Imp_Alcance Met_Manager Imp_Manager Met_Validador Imp_Validador Calificación_Metodología
Calificación_Implementación""".split()

# Columna del reporte de observaciones -> campo usado en el HTML
COLS_OBSERVACION = {
    "ID_Obs": "id", "ID_Model": "id_modelo", "Observación": "observacion", "Recomendación": "recomendacion",
    "Criticidad_observacion": "criticidad", "Ambito_observacion": "ambito", "Estado_Vencimiento": "vencimiento",
    "# Ampliaciones": "ampliaciones", "Fecha ampliada": "fecha_ampliada", "Fecha estimada": "fecha_estimada",
    "Nombre_proyecto": "proyecto", "Tipo_revisión": "tipo_revision", "Area homologada": "area",
    "Manager_nombre": "manager", "Validador_nombre": "validador", "Propietario_nombre": "propietario",
}


def limpiar(v):
    if isinstance(v, str):
        v = re.sub(r"_x000D_|[​‌﻿]", " ", v)
        return re.sub(r"\s+", " ", v).strip() or None
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    return v


def fecha_iso(texto):
    return datetime.strptime(texto, "%d/%m/%Y").strftime("%Y-%m-%d") if texto else None


def leer(ruta, columnas=COLUMNAS):
    if not Path(ruta).exists():
        sys.exit(f"No se encontró el Excel: {ruta}\nRevisa carpeta_inputs y archivos en config.yaml")
    hoja = load_workbook(ruta, read_only=True, data_only=True).worksheets[0]
    filas = hoja.iter_rows(values_only=True)
    cab = [limpiar(c) for c in next(filas)]
    faltan = [c for c in columnas if c not in cab]
    if faltan:
        sys.exit(f"Faltan columnas en {Path(ruta).name}: {', '.join(faltan)}")
    return [dict(zip(cab, map(limpiar, f))) for f in filas if any(c is not None for c in f)]


def avisos_calidad(ms):
    """Cruces entre campos que conviene revisar en la fuente; no alteran el cálculo."""
    def n(f):
        return sum(1 for m in ms if f(m))

    def alerta(m):
        return m["ESTADO_ALERTA"] == "En alerta"

    pares = [
        (n(lambda m: m["ESTADO_SEGUIMIENTO"] == "Sin Seguimiento" and m["BBDD"] is not None),
         'modelos "Sin Seguimiento" con nota de profundidad de seguimiento'),
        (n(lambda m: m["ESTADO_SEGUIMIENTO"] == "Con Seguimiento" and m["BBDD"] is None),
         'modelos "Con Seguimiento" sin nota de profundidad de seguimiento'),
        (n(lambda m: m["ESTADO_SEGUIMIENTO"] == "Sin Seguimiento" and alerta(m)),
         'modelos "Sin Seguimiento" marcados "En alerta"'),
        (n(lambda m: alerta(m) and m["PRESENCIA_MITIGANTE"] is None), "modelos en alerta sin dato de mitigante"),
        (n(lambda m: not alerta(m) and m["PRESENCIA_MITIGANTE"] is not None), "modelos sin alerta con dato de mitigante"),
        (n(lambda m: str(m["DESCRIPCION_MITIGANTE"] or "").startswith("No aplica") and m["PRESENCIA_MITIGANTE"] == "Si"),
         'modelos con mitigante "Si" cuya descripción es "No aplica"'),
        (n(lambda m: m["PLATAFORMA_IMPLEMENTACION"] == "Sin información"
           and m["AMBIENTE_DESPLIEGUE"] in ("PRODUCTIVO", "NO PRODUCTIVO", "MIXTO")),
         "modelos con ambiente de despliegue informado y plataforma sin información"),
        (n(lambda m: m["NOTA_CALIDAD_DATOS"] == 0), "modelos con NOTA_CALIDAD_DATOS = 0 (¿nota real o dato faltante?)"),
        (n(lambda m: m["OBS_CRIT_RELE_MODE_VENCIDAS_VI"] > m["OBS_CRIT_RELE_MODE_PENDIENTES_VI"]
           or m["OBS_SBS_AI_VENCIDAS"] > m["OBS_SBS_AI_PENDIENTES"]), "modelos con más observaciones vencidas que pendientes"),
    ]
    return [f"{c} {t}" for c, t in pares if c]


def leer_observaciones(ruta, ids):
    """Une por ID_Model con el inventario; quita filas repetidas de una misma observación y modelo."""
    filas = leer(ruta, [*COLS_OBSERVACION, "FECHA_PROCESO"])
    unicas = {(f["ID_Obs"], f["ID_Model"]): f for f in filas}
    vinculadas = [f for f in unicas.values() if f["ID_Model"] in ids]
    meta = {"corte": max(f["FECHA_PROCESO"] for f in filas), "total": len(filas), "duplicadas": len(filas) - len(unicas),
            "vinculadas": len(vinculadas)}
    return [{d: f[c] for c, d in COLS_OBSERVACION.items()} for f in vinculadas], meta


def leer_coberturas(ruta, ids):
    """Une por Modelo_ID con el inventario."""
    filas = leer(ruta, [*COLS_COBERTURA, "Fecha"])
    vinculadas = [{c: f[c] for c in COLS_COBERTURA} for f in filas if f["Modelo_ID"] in ids]
    for f in vinculadas:
        f["Fecha_descobertura_Met"] = fecha_iso(f["Fecha_descobertura_Met"])
        f["Fecha_descobertura_Imp"] = fecha_iso(f["Fecha_descobertura_Imp"])
    return vinculadas, {"corte": max(f["Fecha"] for f in filas), "total": len(filas), "vinculadas": len(vinculadas)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--config", default=RAIZ / "config.yaml")
    args.add_argument("--abrir", action="store_true", help="abre el reporte en el navegador al terminar")
    args = args.parse_args()
    if not Path(args.config).exists():
        sys.exit("No existe config.yaml: copia config.ejemplo.yaml como config.yaml e indica la carpeta de tus inputs")
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    carpeta = Path(cfg["carpeta_inputs"])
    salida = RAIZ / cfg["salida"]

    ruta = carpeta / cfg["archivos"]["input_principal"]
    if cfg["simulacion"]["activa"]:
        ruta = simular(ruta, RAIZ / cfg["simulacion"]["salida"])
    filas = leer(ruta)
    fechas = sorted({f["FECHA"] for f in filas})
    repetidos = [k for k, v in Counter((m["FECHA"], m["ID_MODELO"]) for m in filas).items() if v > 1]
    if repetidos:
        sys.exit(f"Modelos repetidos en una misma FECHA: {repetidos[:10]}")

    corte = fechas[-1]
    actuales = [f for f in filas if f["FECHA"] == corte]
    # Observaciones y coberturas solo corresponden a la última fecha del input
    ids = {f["ID_MODELO"] for f in actuales}
    observaciones, obs_meta = leer_observaciones(carpeta / cfg["archivos"]["observaciones"], ids)
    coberturas, cob_meta = leer_coberturas(carpeta / cfg["archivos"]["coberturas"], ids)
    sin_tablon = len(ids - {c["Modelo_ID"] for c in coberturas})
    avisos = avisos_calidad(actuales)
    if obs_meta["duplicadas"]:
        avisos.append(f"{obs_meta['duplicadas']} filas repetidas en el reporte de observaciones (se cuenta una)")
    if sin_tablon:
        avisos.append(f"{sin_tablon} modelos del inventario sin registro en el tablón de coberturas")
    avisos.append(f"{obs_meta['total'] - obs_meta['duplicadas'] - obs_meta['vinculadas']} observaciones y "
                  f"{cob_meta['total'] - cob_meta['vinculadas']} coberturas son de modelos fuera del inventario y no se incluyen")
    datos = {
        "fechas": fechas, "modelos": [{c: m[c] for c in COLUMNAS} for m in filas],
        "fechas_simuladas": sorted({f["FECHA"] for f in filas if f.get("SIMULADO")}),
        "observaciones": observaciones, "obs_meta": obs_meta, "coberturas": coberturas, "cob_meta": cob_meta,
    }
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    if MARCA not in plantilla:
        sys.exit(f"La plantilla no contiene la marca {MARCA}")
    json_datos = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(plantilla.replace(MARCA, json_datos), encoding="utf-8")
    print(f"{salida.name}: {len(filas)} filas, fechas {fechas}, {len(observaciones)} observaciones, "
          f"{len(coberturas)} coberturas")
    print("Avisos de calidad de datos:")
    for aviso in avisos:
        print(f"  - {aviso}")
    if args.abrir:
        webbrowser.open(salida.resolve().as_uri())


if __name__ == "__main__":
    main()
