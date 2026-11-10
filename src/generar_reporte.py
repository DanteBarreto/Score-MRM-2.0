"""Genera el reporte HTML del Score MRM a partir de los Excel de insumos.

Los Excel se leen de la carpeta local indicada en config.yaml, que cada usuario crea a partir de
config.ejemplo.yaml. Uso:  python src/generar_reporte.py [--config config.yaml] [--abrir]

El input principal es obligatorio y guarda el historial mensual. Los demás archivos son de detalle,
corresponden solo al último mes del input y son opcionales: si falta uno, su bloque no se muestra.
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

import calidad
from esquema import ARCHIVOS, COMPONENTES_GOBIERNO, CRITERIOS_CALIDAD

RAIZ = Path(__file__).resolve().parents[1]
PLANTILLA = RAIZ / "templates" / "plantilla_reporte.html"
MARCA = "/*__DATOS__*/null"
SIN_INSUMO = ("no aplica", "pendiente")  # nombres del inventario que significan "sin modelo insumo"

COLUMNAS = ARCHIVOS["input_principal"].nombres
COLS_COBERTURA = ARCHIVOS["coberturas"].requeridos
# Columna del reporte de observaciones -> campo usado en el HTML
COLS_OBSERVACION = {
    "ID_Obs": "id", "ID_Model": "id_modelo", "Observación": "observacion", "Recomendación": "recomendacion",
    "Criticidad_observacion": "criticidad", "Ambito_observacion": "ambito", "Estado_Vencimiento": "vencimiento",
    "# Ampliaciones": "ampliaciones", "Fecha ampliada": "fecha_ampliada", "Fecha estimada": "fecha_estimada",
    "Nombre_proyecto": "proyecto", "Tipo_revisión": "tipo_revision", "Area homologada": "area",
    "Manager_nombre": "manager", "Validador_nombre": "validador", "Propietario_nombre": "propietario",
}
# Columna de Observaciones SBS & AI -> campo usado en el HTML. No se incluye el correo.
COLS_SBS = {
    "ID": "id", "CodigoProyecto": "codigo", "NombreProyecto/Visita Inspección": "proyecto", "TituloObs": "titulo",
    "Observación": "observacion", "Recomendación": "recomendacion", "Estado": "estado", "Riesgo": "riesgo",
    "Fecha de Vencimiento": "vencimiento", "Propietario": "propietario", "Unidad Responsable": "unidad",
    "Número de ampliaciones": "ampliaciones", "Tipo": "tipo",
}
COLS_TTM = {
    "FECH_ALERTA": "fecha_alerta", "DIAGNOSTICO": "diagnostico", "PLAN_ACCION": "plan", "TTM_GOBIERNO_MESES": "ttm_gobierno",
    "TTM_REAL_HOY": "ttm_real", "HOLGURA_EXCESO_TTM": "holgura", "SOLICITO_AMPLIACION": "ampliacion",
    "NUEVA_FECH_SUBSANACION": "nueva_fecha", "COMENTARIOS": "comentarios",
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


def num_id(v):
    """Número del modelo, venga como 21122, "MOD-BCP-21122" o "MOD-BCP-0000177"."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v) if float(v).is_integer() else None
    m = re.search(r"(\d+)\s*$", str(v))
    return int(m.group(1)) if m else None


def lista_ids(v):
    """Números de modelo de una celda que puede traer varios: 246, "246;245" o "21045, 18578"."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return [int(v)]
    return [int(x) for x in re.findall(r"\d+", str(v or ""))]


def leer_crudo(ruta, arch):
    """Devuelve la cabecera y las filas tal como vienen del Excel, para validar los tipos de dato."""
    hoja = load_workbook(ruta, read_only=True, data_only=True).worksheets[0]
    filas = hoja.iter_rows(values_only=True)
    cab = [limpiar(c) for c in next(filas)]
    faltan = [c for c in arch.requeridos if c not in cab]
    if faltan:
        sys.exit(f"Faltan columnas en {Path(ruta).name}: {', '.join(faltan)}")
    return cab, [dict(zip(cab, f)) for f in filas if any(c is not None for c in f)]


class Lector:
    """Lee los archivos de config.yaml, valida su estructura y acumula los hallazgos de calidad."""

    def __init__(self, cfg):
        self.carpeta = Path(cfg["carpeta_inputs"])
        self.nombres = cfg.get("archivos") or {}
        self.homologacion = cfg.get("homologacion") or {}
        self.hallazgos = []
        self.leidos = {}

    def leer(self, clave, obligatorio=False):
        """Filas limpias del archivo, o None si es opcional y no está."""
        arch, nombre = ARCHIVOS[clave], self.nombres.get(clave)
        ruta = self.carpeta / nombre if nombre else None
        if not ruta or not ruta.exists():
            if obligatorio:
                sys.exit(f"No se encontró el Excel: {ruta}\nRevisa carpeta_inputs y archivos en config.yaml")
            motivo = f"no se encontró {nombre}" if nombre else "no está en config.yaml"
            self.hallazgos.append(calidad.Hallazgo(arch.titulo, calidad.ALERTA, f"Archivo no cargado ({motivo}): su bloque no se muestra", 1))
            return None
        cab, crudas = leer_crudo(ruta, arch)
        self.hallazgos += calidad.validar_esquema(arch, cab, crudas)
        cambios = self.homologacion.get(clave) or {}
        filas = [{c: limpiar(v) for c, v in f.items()} for f in crudas]
        for columna, mapa in cambios.items():
            for f in filas:
                f[columna] = mapa.get(f.get(columna), f.get(columna))
        self.leidos[clave] = f"{nombre}: {len(filas)} filas"
        return filas


def leer_observaciones(filas, ids):
    """Une por ID_Model con el inventario; quita filas repetidas de una misma observación y modelo."""
    unicas = {(f["ID_Obs"], num_id(f["ID_Model"])): f for f in filas}
    vinculadas = [f for (_, modelo), f in unicas.items() if modelo in ids]
    meta = {"corte": max(f["FECHA_PROCESO"] for f in filas), "total": len(filas), "duplicadas": len(filas) - len(unicas),
            "vinculadas": len(vinculadas)}
    return [{d: (num_id(f[c]) if d == "id_modelo" else f[c]) for c, d in COLS_OBSERVACION.items()} for f in vinculadas], meta


def leer_coberturas(filas, ids):
    """Une por Modelo_ID con el inventario."""
    vinculadas = [{c: f[c] for c in COLS_COBERTURA} for f in filas if num_id(f["Modelo_ID"]) in ids]
    for f in vinculadas:
        f["Modelo_ID"] = num_id(f["Modelo_ID"])
        f["Fecha_descobertura_Met"] = fecha_iso(f["Fecha_descobertura_Met"])
        f["Fecha_descobertura_Imp"] = fecha_iso(f["Fecha_descobertura_Imp"])
    return vinculadas, {"corte": max(f["Fecha"] for f in filas), "total": len(filas), "vinculadas": len(vinculadas)}


def leer_ttm(filas, ids):
    return [{"id_modelo": num_id(f["ID_MODELO"]), **{d: f[c] for c, d in COLS_TTM.items()}} for f in filas if num_id(f["ID_MODELO"]) in ids]


def leer_sbs(filas, ids):
    """Una fila por observación y modelo. Las que no traen modelo (transversales) quedan con id_modelo vacío."""
    salida, meta = [], {"total": len(filas), "multiples": 0, "transversales": 0, "fuera": 0, "textos": [], "ids_fuera": []}
    for f in filas:
        base = {d: f[c] for c, d in COLS_SBS.items()}
        base["emision"] = fecha_iso(f["Fecha Emisión"])
        modelos = lista_ids(f["ID_MODELO"])
        meta["multiples"] += len(modelos) > 1
        if not modelos:
            meta["transversales"] += 1
            meta["textos"].append(f["ID_MODELO"] or "vacío")
            salida.append({**base, "id_modelo": None, "alcance": f["ID_MODELO"] or "Sin modelo"})
        for modelo in modelos:
            if modelo in ids:
                salida.append({**base, "id_modelo": modelo})
            else:
                meta["fuera"] += 1
                meta["ids_fuera"].append(modelo)
    meta["textos"] = sorted(set(meta["textos"]))
    meta["ids_fuera"] = sorted(set(meta["ids_fuera"]))
    return salida, meta


def leer_gobierno(filas, ultimo):
    """La nota se asigna por PO usuario y model developer; si el PO tiene una sola fila, por PO."""
    gob = [{"po": f["PO_USUARIO"], "dev": f["MODELO_DEVELOPER"], "user": f["MODEL_USER"], "nota": f["NOTA_GOBIERNO"],
            "comp": [f[c] for c, _ in COMPONENTES_GOBIERNO]} for f in filas]
    por_clave = {(g["po"], g["dev"]): i for i, g in enumerate(gob)}
    por_po = Counter(g["po"] for g in gob)
    unico = {g["po"]: i for i, g in enumerate(gob) if por_po[g["po"]] == 1}
    asignada = {}
    for k, m in ultimo.items():
        i = por_clave.get((m["PO_USUARIO"], m["MODEL_DEVELOPER"]), unico.get(m["PO_USUARIO"]))
        if i is not None:
            asignada[k] = i
    return gob, asignada


def leer_calidad(filas, ids):
    todas = [{"id_modelo": num_id(f["ID"]), "valores": [f[c] or 0 for c, _, _ in CRITERIOS_CALIDAD],
              "indicador": f["Indicador de Calidad de datos"], "rango": f["Rango de cumplimiento"]} for f in filas]
    fuera = sorted(c["id_modelo"] for c in todas if c["id_modelo"] not in ids)
    return [c for c in todas if c["id_modelo"] in ids], {"total": len(todas), "fuera": len(fuera), "ids_fuera": fuera}


def leer_inventario(filas, ids):
    """Modelos insumo de cada modelo del score y nombres de esos insumos."""
    for f in filas:
        f["_id"] = num_id(f["ID_MODELO"])
    por_id = {f["_id"]: f for f in filas}

    def es_real(i):
        return i in por_id and str(por_id[i]["NOMBRE_MODELO"]).strip().lower() not in SIN_INSUMO

    crudos = {k: lista_ids(por_id[k]["ID_MODELO_INPUT"]) for k in ids if k in por_id}
    insumos = {k: [i for i in dict.fromkeys(v) if i != k and es_real(i)] for k, v in crudos.items()}
    nombres = {i: {"n": por_id[i]["NOMBRE_MODELO"], "p": por_id[i]["PERIMETRO_MODELO"]} for v in insumos.values() for i in v}
    modelos = [{"id_modelo": k, "tipo": por_id[k]["TIPO_MODELO"], "perimetro": por_id[k]["PERIMETRO_MODELO"], "insumos": v} for k, v in insumos.items()]
    return modelos, nombres, crudos, insumos


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
    salida = RAIZ / cfg["salida"]
    lector = Lector(cfg)

    filas = lector.leer("input_principal", obligatorio=True)
    for f in filas:
        f["CODIGO_MODELO"], f["ID_MODELO"] = f["ID_MODELO"], num_id(f["ID_MODELO"])
    sin_id = sum(f["ID_MODELO"] is None for f in filas)
    if sin_id:
        sys.exit(f"{sin_id} filas del input principal no tienen un ID_MODELO con número")
    fechas = sorted({f["FECHA"] for f in filas})
    repetidos = [k for k, v in Counter((m["FECHA"], m["ID_MODELO"]) for m in filas).items() if v > 1]
    if repetidos:
        sys.exit(f"Modelos repetidos en una misma FECHA: {repetidos[:10]}")

    # Los archivos de detalle solo corresponden a la última fecha del input
    corte = fechas[-1]
    ultimo = {f["ID_MODELO"]: f for f in filas if f["FECHA"] == corte}
    ids = set(ultimo)
    control = {"hist": filas, "ultimo": ultimo, "corte": corte}
    datos = {"fechas": fechas, "modelos": [{c: m[c] for c in [*COLUMNAS, "CODIGO_MODELO"]} for m in filas], "corte": corte}

    obs = lector.leer("observaciones")
    datos["observaciones"], datos["obs_meta"] = leer_observaciones(obs, ids) if obs else ([], None)
    cob = lector.leer("coberturas")
    datos["coberturas"], datos["cob_meta"] = leer_coberturas(cob, ids) if cob else ([], None)
    ttm = lector.leer("ttm")
    datos["ttm"] = leer_ttm(ttm, ids) if ttm else None
    sbs = lector.leer("observaciones_sbs_ai")
    datos["sbs"], sbs_meta = leer_sbs(sbs, ids) if sbs else (None, None)
    gob = lector.leer("nota_gobierno")
    datos["gobierno"], datos["gob_de"] = leer_gobierno(gob, ultimo) if gob else (None, {})
    datos["gob_componentes"] = [t for _, t in COMPONENTES_GOBIERNO]
    cal = lector.leer("calidad_datos")
    datos["calidad"], cal_meta = leer_calidad(cal, ids) if cal else (None, None)
    datos["cal_criterios"] = [{"t": t, "peso": p} for _, t, p in CRITERIOS_CALIDAD]
    inv = lector.leer("inventario")
    datos["inventario"], datos["inv_nombres"], crudos, insumos = leer_inventario(inv, ids) if inv else (None, {}, {}, {})

    control.update(
        observaciones=datos["observaciones"] if obs else None, obs_meta=datos["obs_meta"],
        coberturas=datos["coberturas"] if cob else None, cob_meta=datos["cob_meta"],
        ttm=[{**t, "_id": t["id_modelo"], **{c: t[d] for c, d in COLS_TTM.items()}} for t in datos["ttm"]] if ttm else None,
        sbs=datos["sbs"], sbs_meta=sbs_meta, gobierno=datos["gobierno"], gob_de=datos["gob_de"],
        calidad=datos["calidad"], cal_meta=cal_meta, inventario=inv, insumos_crudos=crudos, insumos=insumos)
    lector.hallazgos += calidad.controles_cruzados(control)
    errores = [x for x in lector.hallazgos if x.nivel == calidad.ERROR]

    ruta_control = salida.parent / "control_calidad.txt"
    contexto = [f"Generado: {datetime.now():%d/%m/%Y %H:%M}", f"Último mes del input principal: {corte}", f"Modelos en el último mes: {len(ids)}",
                "Archivos leídos:", *[f"  - {v}" for v in lector.leidos.values()]]
    total = calidad.escribir(lector.hallazgos, ruta_control, contexto)
    if errores:
        sys.exit("El proceso se detuvo por errores de calidad de datos:\n" + "\n".join(f"  - {x.archivo}: {x.control} ({x.ejemplo})" for x in errores))

    plantilla = PLANTILLA.read_text(encoding="utf-8")
    if MARCA not in plantilla:
        sys.exit(f"La plantilla no contiene la marca {MARCA}")
    json_datos = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(plantilla.replace(MARCA, json_datos), encoding="utf-8")
    print(f"{salida.name}: {len(fechas)} meses ({fechas[0][:7]} a {corte[:7]}), {len(ids)} modelos en el último mes")
    for linea in lector.leidos.values():
        print(f"  - {linea}")
    print(f"Calidad de datos: {total[calidad.ALERTA]} alertas y {total[calidad.AVISO]} avisos. Detalle en {ruta_control.relative_to(RAIZ) if ruta_control.is_relative_to(RAIZ) else ruta_control}")
    if args.abrir:
        webbrowser.open(salida.resolve().as_uri())


if __name__ == "__main__":
    main()
