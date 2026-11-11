"""Controles de calidad de datos de los archivos de entrada.

Hay dos grupos de controles:
  1. De estructura (validar_esquema): columnas, tipos de dato, vacíos, catálogos y duplicados,
     según lo definido en esquema.py.
  2. De coherencia (controles_cruzados): reglas entre campos y entre archivos.

Niveles:
  ERROR   El proceso se detiene: no se puede generar un reporte confiable.
  ALERTA  El reporte se genera, pero una cifra puede no ser correcta. Revisar en la fuente.
  AVISO   Tema de formato o completitud que el proceso ya resuelve o que no cambia las cifras.
"""
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime

ERROR, ALERTA, AVISO = "ERROR", "ALERTA", "AVISO"
FECHA_TEXTO = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")


@dataclass
class Hallazgo:
    archivo: str
    nivel: str
    control: str
    casos: int
    ejemplo: str = ""


def vacio(v):
    return v is None or (isinstance(v, str) and not v.strip())


def es_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def cumple_tipo(tipo, v):
    if tipo == "entero":
        return es_numero(v) and float(v).is_integer()
    if tipo == "decimal":
        return es_numero(v)
    if tipo == "decimal 0-1":
        return es_numero(v) and 0 <= v <= 1
    if tipo == "decimal 0-100":
        return es_numero(v) and 0 <= v <= 100
    if tipo == "fecha":
        return isinstance(v, (date, datetime)) and v.year >= 1990
    if tipo == "fecha texto":
        return isinstance(v, str) and bool(FECHA_TEXTO.match(v.strip()))
    if tipo == "id modelo":
        return (es_numero(v) and float(v).is_integer()) or bool(re.search(r"\d+\s*$", str(v)))
    if tipo == "monto o texto":
        return es_numero(v) or isinstance(v, str)
    if tipo == "lista de id":
        return True  # puede traer texto, como "Transversal"; lo revisa controles_cruzados
    return isinstance(v, str)  # texto y categoría


def ejemplos(valores, n=3):
    return ", ".join(repr(v) if isinstance(v, str) else str(v) for v in list(dict.fromkeys(valores))[:n])


def validar_esquema(arch, cabecera, filas):
    """Controles de estructura de un archivo. filas: valores tal como vienen del Excel."""
    h = []
    faltan = [c for c in arch.requeridos if c not in cabecera]
    if faltan:
        h.append(Hallazgo(arch.titulo, ERROR, "Faltan columnas que el reporte necesita", len(faltan), ", ".join(faltan)))
        return h
    informativas = [c for c in arch.nombres if c not in cabecera]
    if informativas:
        h.append(Hallazgo(arch.titulo, AVISO, "Faltan columnas informativas", len(informativas), ", ".join(informativas)))
    nuevas = [c for c in cabecera if c and c not in arch.nombres]
    if nuevas:
        h.append(Hallazgo(arch.titulo, AVISO, "Columnas que no están en el esquema (se ignoran)", len(nuevas), ", ".join(map(str, nuevas))))

    for campo in arch.campos:
        if campo.nombre not in cabecera:
            continue
        valores = [f[campo.nombre] for f in filas]
        con_dato = [v for v in valores if not vacio(v)]
        if filas and not con_dato:
            h.append(Hallazgo(arch.titulo, ALERTA if campo.requerido and not campo.nulos else AVISO,
                              f"{campo.nombre}: la columna está vacía en todas las filas", len(filas)))
            continue
        if not campo.nulos and len(con_dato) < len(valores):
            h.append(Hallazgo(arch.titulo, ALERTA, f"{campo.nombre}: vacíos en un campo obligatorio", len(valores) - len(con_dato)))
        tipo = "texto" if campo.categorias else campo.tipo
        malos = [v for v in con_dato if not cumple_tipo(tipo, v)]
        if malos:
            regla = "fechas con otro formato o anteriores a 1990 (relleno)" if tipo == "fecha" else f"valores que no cumplen el tipo «{tipo}»"
            h.append(Hallazgo(arch.titulo, ALERTA, f"{campo.nombre}: {regla}", len(malos), ejemplos(malos)))
        if campo.categorias:
            fuera = [v for v in con_dato if isinstance(v, str) and v.strip() not in campo.categorias]
            if fuera:
                h.append(Hallazgo(arch.titulo, ALERTA, f"{campo.nombre}: valores fuera del catálogo", len(fuera), ejemplos(fuera)))
        # Solo en valores cortos: los textos largos (observaciones) se limpian sin avisar
        espacios = [v for v in con_dato if isinstance(v, str) and len(v) < 80 and (v != v.strip() or "  " in v)]
        if espacios:
            h.append(Hallazgo(arch.titulo, AVISO, f"{campo.nombre}: textos con espacios sobrantes (se limpian)", len(espacios), ejemplos(espacios, 2)))
    return h


def controles_cruzados(d):
    """Controles de coherencia entre campos y entre archivos.

    d contiene las filas ya limpias de cada archivo (None si no se cargó), el histórico completo
    en d["hist"], los modelos del último mes en d["ultimo"] (por id) y la fecha de corte en d["corte"].
    """
    h = []

    def agrega(archivo, nivel, control, casos, ej=""):
        if casos:
            h.append(Hallazgo(archivo, nivel, control, casos, ej if isinstance(ej, str) else ejemplos(ej)))

    hist, ult, corte = d["hist"], d["ultimo"], d["corte"]
    T = "Input principal histórico"
    fechas = sorted({m["FECHA"] for m in hist})
    por_fecha = defaultdict(list)
    for m in hist:
        por_fecha[m["FECHA"]].append(m)

    # --- Histórico: estabilidad de la serie
    for antes, despues in zip(fechas, fechas[1:]):
        a, b = {m["ID_MODELO"] for m in por_fecha[antes]}, {m["ID_MODELO"] for m in por_fecha[despues]}
        if len(a ^ b) > 0.1 * len(a):
            agrega(T, ALERTA, f"Quiebre de la serie en {despues[:7]}: altas y bajas superan el 10% de los modelos",
                   len(a ^ b), f"{len(b - a)} altas y {len(a - b)} bajas")
    for campo in ("ESTADO_ALERTA", "ESTADO_SEGUIMIENTO", "AMBIENTE_DATA", "AMBIENTE_DESPLIEGUE", "PROCESO", "MODEL_DEVELOPER"):
        actuales = {m[campo] for m in ult.values()}
        previos = Counter(m[campo] for m in hist if m["FECHA"] != corte and m[campo] not in actuales)
        agrega(T, AVISO, f"{campo}: categorías que solo aparecen en meses anteriores", sum(previos.values()), list(previos))
    for campo in ("OBS_SBS_AI_PENDIENTES", "OBS_CRIT_RELE_MODE_PENDIENTES_VI"):
        en_cero = [f[:7] for f in fechas if not sum(m[campo] or 0 for m in por_fecha[f])]
        if 0 < len(en_cero) < len(fechas):
            agrega(T, ALERTA, f"{campo}: meses con total 0 entre meses con dato (distorsiona el evolutivo)", len(en_cero), ", ".join(en_cero))
    nombres = defaultdict(set)
    for m in hist:
        nombres[m["ID_MODELO"]].add(m["NOMBRE_MODELO"])
    agrega(T, AVISO, "Modelos cuyo nombre cambia entre meses", sum(len(v) > 1 for v in nombres.values()))
    repetidos = Counter(m["NOMBRE_MODELO"] for m in ult.values())
    agrega(T, AVISO, "Nombres de modelo usados por más de un ID en el último mes", sum(v > 1 for v in repetidos.values()),
           [k for k, v in repetidos.items() if v > 1])

    # --- Histórico: coherencia entre campos, en el último mes
    ms = list(ult.values())

    def n(f):
        return [m["ID_MODELO"] for m in ms if f(m)]

    def alerta(m):
        return m["ESTADO_ALERTA"] == "En alerta"

    def profundidad(m):
        return m["BBDD"] is not None

    for control, f, nivel in [
        ('Modelos "Sin Seguimiento" con nota de profundidad del seguimiento', lambda m: m["ESTADO_SEGUIMIENTO"] == "Sin Seguimiento" and profundidad(m), AVISO),
        ('Modelos "Con Seguimiento" sin nota de profundidad del seguimiento', lambda m: m["ESTADO_SEGUIMIENTO"] == "Con Seguimiento" and not profundidad(m), AVISO),
        ('Modelos "Sin Seguimiento" marcados "En alerta"', lambda m: m["ESTADO_SEGUIMIENTO"] == "Sin Seguimiento" and alerta(m), ALERTA),
        ("Modelos en alerta sin dato de mitigante", lambda m: alerta(m) and m["PRESENCIA_MITIGANTE"] is None, ALERTA),
        ("Modelos en alerta sin situación de TTM", lambda m: alerta(m) and m["EXCEDE_TTM"] is None, ALERTA),
        ("Modelos sin alerta con datos de alerta (TTM o mitigante)", lambda m: not alerta(m) and (m["EXCEDE_TTM"] or m["PRESENCIA_MITIGANTE"]), ALERTA),
        ('EXCEDE_TTM no coincide con el signo de EXCESO_MESES_TTM', lambda m: m["EXCESO_MESES_TTM"] is not None and (m["EXCEDE_TTM"] == "Excede TTM") != (m["EXCESO_MESES_TTM"] > 0), ALERTA),
        ('Mitigante "Si" cuya descripción empieza con "No aplica"', lambda m: m["PRESENCIA_MITIGANTE"] == "Si" and str(m["DESCRIPCION_MITIGANTE"] or "").startswith("No aplica"), AVISO),
        ("Ambiente de despliegue informado con plataforma sin información", lambda m: m["PLATAFORMA_IMPLEMENTACION"] == "Sin información" and m["AMBIENTE_DESPLIEGUE"] in ("PRODUCTIVO", "NO PRODUCTIVO", "MIXTO"), AVISO),
        ("NOTA_CALIDAD_DATOS igual a 0: confirmar si es nota real o modelo no evaluado", lambda m: m["NOTA_CALIDAD_DATOS"] == 0, ALERTA),
        ("Más observaciones vencidas que pendientes", lambda m: any((m[v] or 0) > (m[p] or 0) for v, p in (("OBS_CRIT_RELE_MODE_VENCIDAS_VI", "OBS_CRIT_RELE_MODE_PENDIENTES_VI"), ("OBS_SBS_AI_VENCIDAS", "OBS_SBS_AI_PENDIENTES"), ("OBS_AMB_TEC_VENCIDOS", "OBS_AMB_TEC_PENDIENTES"))), ALERTA),
        ("IMPACTO con texto en lugar de un monto", lambda m: isinstance(m["IMPACTO"], str) and m["IMPACTO"] not in ("No aplica", "Sin info"), AVISO),
    ]:
        casos = n(f)
        agrega(T, nivel, control, len(casos), casos)

    # --- Inventario
    inv = d.get("inventario")
    if inv is not None:
        T = "Inventario de modelos"
        I = {r["_id"]: r for r in inv}
        agrega(T, ERROR if len(I) < len(inv) else AVISO, "ID_MODELO repetido", len(inv) - len(I))
        faltan = [k for k in ult if k not in I]
        agrega(T, ALERTA, "Modelos del score que no están en el inventario", len(faltan), faltan)
        distinto = [k for k, m in ult.items() if k in I and I[k].get("ESTADO_MODELO") not in (None, m["ESTADO_MODELO"])]
        agrega(T, AVISO, "Estado distinto al del input principal (el reporte usa el del input)", len(distinto),
               [f"{k}: {I[k].get('ESTADO_MODELO')}" for k in distinto])
        agrega(T, ALERTA, "Modelos que se declaran como modelo input de sí mismos (se ignora)", sum(k in d["insumos_crudos"].get(k, []) for k in ult),
               [k for k in ult if k in d["insumos_crudos"].get(k, [])])
        sin_inv = sorted({i for k in ult for i in d["insumos_crudos"].get(k, []) if i not in I})
        agrega(T, ALERTA, "Modelos input que no existen en el inventario", len(sin_inv), sin_inv)
        agrega(T, AVISO, 'Modelos del score sin modelo input declarado (vacío o "No aplica")', sum(not d["insumos"].get(k) for k in ult if k in I))
        agrega(T, AVISO, "Modelos del score sin descripción", sum(1 for k in ult if k in I and I[k].get("DESCRIPCION") in (None, "Pendiente")))

    # --- TTM
    ttm = d.get("ttm")
    if ttm is not None:
        T = "TTM"
        por = {r["_id"]: r for r in ttm}
        en_alerta = [k for k, m in ult.items() if alerta(m)]
        agrega(T, ALERTA, "Modelos en alerta sin fila en el archivo TTM", sum(k not in por for k in en_alerta), [k for k in en_alerta if k not in por])
        agrega(T, ALERTA, "Filas de TTM de modelos que no están en alerta en el último mes", sum(k not in en_alerta for k in por), [k for k in por if k not in en_alerta])
        dif = [k for k, r in por.items() if k in ult and ult[k]["EXCESO_MESES_TTM"] is not None and r["HOLGURA_EXCESO_TTM"] is not None
               and abs(r["HOLGURA_EXCESO_TTM"] - ult[k]["EXCESO_MESES_TTM"]) > 0.02]
        agrega(T, ALERTA, "HOLGURA_EXCESO_TTM distinta de EXCESO_MESES_TTM del input principal", len(dif), dif)
        con_ttm = [k for k, r in por.items() if k in ult and ult[k]["EXCEDE_TTM"] == "No tiene TTM" and r["TTM_GOBIERNO_MESES"] is not None]
        agrega(T, ALERTA, 'Modelos "No tiene TTM" en el input principal pero con TTM de gobierno en este archivo', len(con_ttm), con_ttm)
        calc = [k for k, r in por.items() if r["TTM_GOBIERNO_MESES"] is not None and r["HOLGURA_EXCESO_TTM"] is not None
                and abs(r["TTM_REAL_HOY"] - r["TTM_GOBIERNO_MESES"] - r["HOLGURA_EXCESO_TTM"]) > 0.02]
        agrega(T, ALERTA, "La holgura no es igual a TTM real menos TTM de gobierno", len(calc), calc)
        agrega(T, AVISO, "DIAGNOSTICO y PLAN_ACCION son idénticos en todas las filas", len(ttm) if ttm and all(r["DIAGNOSTICO"] == r["PLAN_ACCION"] for r in ttm) else 0)

    # --- Observaciones de validación
    obs = d.get("observaciones")
    if obs is not None:
        T = "Reporte de observaciones"
        agrega(T, AVISO, "Filas repetidas de una misma observación y modelo (se cuenta una)", d["obs_meta"]["duplicadas"])
        agrega(T, AVISO, "Observaciones de modelos fuera del último mes del score (no se incluyen)", d["obs_meta"]["total"] - d["obs_meta"]["duplicadas"] - d["obs_meta"]["vinculadas"])
        crm = ("Crítico", "Relevante", "Moderado")
        pend = Counter(o["id_modelo"] for o in obs if o["criticidad"] in crm)
        venc = Counter(o["id_modelo"] for o in obs if o["criticidad"] in crm and o["vencimiento"] == "Vencido")
        tec = Counter(o["id_modelo"] for o in obs if o["ambito"] == "Entorno Tecnológico")
        for campo, cuenta, texto in (("OBS_CRIT_RELE_MODE_PENDIENTES_VI", pend, "críticas, relevantes y moderadas pendientes"),
                                     ("OBS_CRIT_RELE_MODE_VENCIDAS_VI", venc, "críticas, relevantes y moderadas vencidas"),
                                     ("OBS_AMB_TEC_PENDIENTES", tec, "de entorno tecnológico pendientes")):
            dif = [k for k, m in ult.items() if cuenta[k] != (m[campo] or 0)]
            agrega(T, ALERTA, f"Modelos donde las observaciones {texto} no cuadran con {campo}", len(dif),
                   f"detalle {sum(cuenta.values())} frente a input {sum(m[campo] or 0 for m in ult.values())}")

    # --- Observaciones SBS y auditoría interna
    sbs = d.get("sbs")
    if sbs is not None:
        T = "Observaciones SBS & AI"
        meta = d["sbs_meta"]
        agrega(T, AVISO, "Observaciones sin modelo (transversales u otro texto): se muestran aparte", meta["transversales"], meta["textos"])
        agrega(T, AVISO, "Celdas de ID_MODELO con varios modelos (se separan en una fila por modelo)", meta["multiples"])
        agrega(T, AVISO, "Pares observación–modelo de modelos fuera del último mes del score (no se incluyen)", meta["fuera"], meta["ids_fuera"])
        pend = Counter(o["id_modelo"] for o in sbs if o["id_modelo"] and o["estado"] == "Pendiente")
        venc = Counter(o["id_modelo"] for o in sbs if o["id_modelo"] and o["estado"] == "Pendiente" and o["vencimiento"] < corte)
        for campo, cuenta in (("OBS_SBS_AI_PENDIENTES", pend), ("OBS_SBS_AI_VENCIDAS", venc)):
            dif = [k for k, m in ult.items() if cuenta[k] != (m[campo] or 0)]
            agrega(T, ALERTA, f"Modelos donde las observaciones en estado Pendiente no cuadran con {campo}", len(dif),
                   [f"{k}: detalle {cuenta[k]}, input {ult[k][campo]}" for k in dif])

    # --- Nota de gobierno
    gob = d.get("gobierno")
    if gob is not None:
        T = "Nota de Gobierno"
        claves = Counter((g["po"], g["dev"]) for g in gob)
        agrega(T, ERROR, "PO usuario y model developer repetidos: no se puede asignar la nota", sum(v > 1 for v in claves.values()), [k for k, v in claves.items() if v > 1])
        sin_nota = [k for k in ult if k not in d["gob_de"]]
        agrega(T, ALERTA, "Modelos sin nota de gobierno: su PO y model developer no están en el archivo", len(sin_nota),
               sorted({f"{ult[k]['PO_USUARIO']} / {ult[k]['MODEL_DEVELOPER']}" for k in sin_nota}))
        usados = set(d["gob_de"].values())
        agrega(T, AVISO, "Filas de nota de gobierno sin modelos en el último mes", sum(i not in usados for i in range(len(gob))),
               [f"{g['po']} / {g['dev']}" for i, g in enumerate(gob) if i not in usados])
        dif = [k for k, i in d["gob_de"].items() if ult[k]["NOTA_GOBIERNO"] is not None and abs(gob[i]["nota"] / 100 - ult[k]["NOTA_GOBIERNO"]) > 0.006]
        agrega(T, ALERTA, "Modelos cuya NOTA_GOBIERNO del input principal difiere de la nota del archivo", len(dif),
               sorted({f"{gob[d['gob_de'][k]]['po']}: {gob[d['gob_de'][k]]['nota']:.1f} frente a {ult[k]['NOTA_GOBIERNO'] * 100:.1f}" for k in dif}))
        mal = [g["po"] for g in gob if [c for c in g["comp"] if c is not None] and abs(sum(c for c in g["comp"] if c is not None) / len([c for c in g["comp"] if c is not None]) - g["nota"]) > 0.05]
        agrega(T, ALERTA, "La nota no es el promedio de sus componentes con dato", len(mal), mal)

    # --- Calidad de datos
    cal = d.get("calidad")
    if cal is not None:
        T = "Calidad de Datos"
        agrega(T, AVISO, "Modelos evaluados que no están en el último mes del score (no se incluyen)", d["cal_meta"]["fuera"], d["cal_meta"]["ids_fuera"])
        suma = [c["id_modelo"] for c in cal if abs(sum(c["valores"]) - c["indicador"]) > 0.011]
        agrega(T, ALERTA, "El indicador no es la suma de sus criterios", len(suma), suma)

        def rango(v):
            return "<= a 50%" if v <= 0.5 else "50% a 70%" if v <= 0.7 else "> a 70%"

        agrega(T, ALERTA, "Rango de cumplimiento incoherente con el indicador", sum(rango(c["indicador"]) != c["rango"] for c in cal),
               [c["id_modelo"] for c in cal if rango(c["indicador"]) != c["rango"]])
        agrega(T, ALERTA, "Evaluaciones con todos los criterios en 0: confirmar si el modelo fue evaluado", sum(not any(c["valores"]) for c in cal))
        ids = {c["id_modelo"] for c in cal}
        dif = [c["id_modelo"] for c in cal if ult[c["id_modelo"]]["NOTA_CALIDAD_DATOS"] is None or abs(ult[c["id_modelo"]]["NOTA_CALIDAD_DATOS"] - c["indicador"]) > 0.006]
        agrega(T, ALERTA, "Indicador distinto de NOTA_CALIDAD_DATOS del input principal", len(dif), dif)
        agrega(T, ALERTA, "Modelos con NOTA_CALIDAD_DATOS en el input principal y sin detalle en este archivo",
               sum(1 for k, m in ult.items() if m["NOTA_CALIDAD_DATOS"] is not None and k not in ids))

    # --- Tablón de coberturas
    cob = d.get("coberturas")
    if cob is not None:
        T = "Tablón de coberturas"
        K = {c["Modelo_ID"]: c for c in cob}
        faltan = [k for k in ult if k not in K]
        agrega(T, ALERTA, "Modelos del score sin registro en el tablón", len(faltan), faltan)
        dif = [k for k, m in ult.items() if k in K and (m["VALIDACION_PERIODICA"] == "Coberturado") != (K[k]["Cobertura_Global"] == "Coberturado")]
        agrega(T, ALERTA, "VALIDACION_PERIODICA del input principal distinta de Cobertura_Global", len(dif), dif)
        for frente, col, fecha in (("metodológica", "Cobertura_Metodologia", "Fecha_descobertura_Met"), ("de implementación", "Cobertura_Implementación", "Fecha_descobertura_Imp")):
            vencida = [c["Modelo_ID"] for c in cob if c[col] == "Coberturado" and c[fecha] and c[fecha] < d["cob_meta"]["corte"]]
            agrega(T, ALERTA, f"Cobertura {frente} vigente con fecha de descobertura ya pasada", len(vencida), vencida)
    return h


def escribir(hallazgos, ruta, contexto):
    """Guarda el informe de control de calidad como texto."""
    orden = {ERROR: 0, ALERTA: 1, AVISO: 2}
    total = Counter(x.nivel for x in hallazgos)
    lineas = ["CONTROL DE CALIDAD DE DATOS · Score MRM", "=" * 40, *contexto, "",
              f"Resumen: {total[ERROR]} errores, {total[ALERTA]} alertas y {total[AVISO]} avisos.",
              "ERROR detiene el proceso · ALERTA puede afectar una cifra · AVISO es de formato o completitud.",
              "El detalle de cada control está en docs/calidad_datos.md.", ""]
    for archivo in dict.fromkeys(x.archivo for x in hallazgos):
        lineas += [archivo, "-" * len(archivo)]
        for x in sorted((x for x in hallazgos if x.archivo == archivo), key=lambda x: orden[x.nivel]):
            lineas.append(f"[{x.nivel}] {x.control}: {x.casos}" + (f"  ·  Ej.: {x.ejemplo}" if x.ejemplo else ""))
        lineas.append("")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(lineas), encoding="utf-8")
    return total
