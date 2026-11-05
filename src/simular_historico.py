"""Simula los meses previos al input principal para probar los evolutivos del reporte.

Crea un Excel con el mes real y los meses previos, generados en cadena del más reciente al más antiguo.
Las filas simuladas llevan SIMULADO = 1. Se ejecuta desde generar_reporte.py si config.yaml lo indica.
"""
import random
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

# Del mes más cercano al input hacia atrás: (fecha simulada, modelos dados de alta el mes siguiente)
MESES = [(datetime(2026, 7, 31), 6), (datetime(2026, 6, 30), 4), (datetime(2026, 5, 31), 3)]
SEMILLA = 20260731
NOTAS = ["NOTA_DINAMICA_VALIDACION", "BBDD", "GOB", "PRECISION_DISCRIMINACION", "GRANULARIDAD", "UNIVARIADA",
         "NOTA_GOBIERNO", "NOTA_10_LINEAMIENTOS", "NOTA_CALIDAD_DATOS"]


def simular_fila(base, fecha, r):
    m = dict(base)
    m["FECHA"] = fecha

    # Notas: la mayoría sin cambio y el resto con una variación pequeña
    for k in NOTAS:
        if m[k] is not None and r.random() < 0.25:
            m[k] = round(min(1, max(0, m[k] + r.uniform(-0.05, 0.05))), 4)

    # Validación periódica: parte de los descoberturados venció recién en agosto
    if m["VALIDACION_PERIODICA"] == "Descoberturado" and r.random() < 0.12:
        m["VALIDACION_PERIODICA"] = "Coberturado"
    elif m["VALIDACION_PERIODICA"] == "Coberturado" and r.random() < 0.03:
        m["VALIDACION_PERIODICA"] = "Descoberturado"

    # Seguimiento
    if m["ESTADO_SEGUIMIENTO"] == "Sin Seguimiento" and r.random() < 0.15:
        m["ESTADO_SEGUIMIENTO"] = "Con Seguimiento"
    elif m["ESTADO_SEGUIMIENTO"] == "Con Seguimiento" and r.random() < 0.02:
        m["ESTADO_SEGUIMIENTO"] = "Sin Seguimiento"

    # Alertas: un mes menos de exceso de TTM y algunas alertas abiertas o cerradas en agosto
    if m["ESTADO_ALERTA"] == "En alerta":
        if r.random() < 0.15:
            m.update(ESTADO_ALERTA="Sin alerta", EXCESO_MESES_TTM=None, EXCEDE_TTM=None, IMPACTO=None,
                     PRESENCIA_MITIGANTE=None, DESCRIPCION_MITIGANTE=None)
        elif m["EXCESO_MESES_TTM"] is not None:
            m["EXCESO_MESES_TTM"] = round(m["EXCESO_MESES_TTM"] - 1, 2)
            m["EXCEDE_TTM"] = "Excede TTM" if m["EXCESO_MESES_TTM"] > 0 else "No excede"
    elif m["ESTADO_ALERTA"] == "Sin alerta" and r.random() < 0.02:
        m.update(ESTADO_ALERTA="En alerta", EXCESO_MESES_TTM=round(r.uniform(-6, 6), 2), IMPACTO="Sin info",
                 PRESENCIA_MITIGANTE="No", DESCRIPCION_MITIGANTE="Sin Mitigante Temporal")
        m["EXCEDE_TTM"] = "Excede TTM" if m["EXCESO_MESES_TTM"] > 0 else "No excede"

    # Observaciones: unas aún no vencían y otras se cerraron en agosto
    for pend, venc in (("OBS_CRIT_RELE_MODE_PENDIENTES_VI", "OBS_CRIT_RELE_MODE_VENCIDAS_VI"),
                       ("OBS_SBS_AI_PENDIENTES", "OBS_SBS_AI_VENCIDAS"),
                       ("OBS_AMB_TEC_PENDIENTES", "OBS_AMB_TEC_VENCIDOS")):
        if m[venc] and r.random() < 0.2:
            m[venc] -= 1
        if m[pend] and r.random() < 0.2:
            m[pend] += 1
            if r.random() < 0.5:
                m[venc] += 1

    # Ambientes: pocos modelos migraron a productivo en agosto
    for amb, rat in (("AMBIENTE_DESPLIEGUE", "RATIO_IMPLEMENTACION"), ("AMBIENTE_DATA", "RATIO_DATA")):
        if m[amb] == "MIXTO" and r.random() < 0.05:
            m.update({amb: "NO PRODUCTIVO", rat: 0})
        elif m[amb] == "PRODUCTIVO" and r.random() < 0.03:
            m.update({amb: "MIXTO", rat: 0.5})

    if r.random() < 0.02:
        m["NUM_INCIDENTES"] = 1 - (m["NUM_INCIDENTES"] or 0)
    return m


def simular(ruta, salida):
    filas = load_workbook(ruta, read_only=True, data_only=True).worksheets[0].iter_rows(values_only=True)
    cab = list(next(filas))
    agosto = [dict(zip(cab, f)) for f in filas if any(c is not None for c in f)]
    if len({m["FECHA"] for m in agosto}) > 1:
        sys.exit("El input ya tiene varias fechas: cambia simulacion.activa a false en config.yaml")

    r = random.Random(SEMILLA)
    meses, base = [], agosto
    for fecha, altas in MESES:
        altas_mes = set(sorted(m["ID_MODELO"] for m in base)[-altas:])  # no existían el mes previo
        base = [simular_fila(m, fecha, r) for m in base if m["ID_MODELO"] not in altas_mes]
        meses.append(base)

    libro = Workbook()
    hoja = libro.active
    hoja.append(cab + ["SIMULADO"])
    for m in agosto:
        hoja.append([m[c] for c in cab] + [0])
    for mes in meses:
        for m in mes:
            hoja.append([m[c] for c in cab] + [1])
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    libro.save(salida)
    print(f"{salida.name}: {len(agosto)} filas reales y simuladas {[len(mes) for mes in meses]}")
    return salida
