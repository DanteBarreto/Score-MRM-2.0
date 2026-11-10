"""Pruebas del proceso con Excel ficticios. Ejecutar con:  python -m unittest discover -s tests"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import yaml
from openpyxl import Workbook

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from calidad import ALERTA, ERROR, cumple_tipo, validar_esquema  # noqa: E402
from esquema import ARCHIVOS, CRITERIOS_CALIDAD  # noqa: E402
from generar_reporte import fecha_iso, limpiar, lista_ids, num_id  # noqa: E402


def excel(ruta, columnas, filas):
    libro = Workbook()
    hoja = libro.active
    hoja.append(columnas)
    for fila in filas:
        hoja.append([fila.get(c) for c in columnas])
    libro.save(ruta)


class Limpieza(unittest.TestCase):
    def test_texto(self):
        self.assertEqual(limpiar("Sin  validación "), "Sin validación")
        self.assertEqual(limpiar("linea_x000D_\nsiguiente"), "linea siguiente")
        self.assertIsNone(limpiar("   "))

    def test_fecha(self):
        self.assertEqual(fecha_iso("31/08/2026"), "2026-08-31")
        self.assertEqual(fecha_iso("1/05/2019"), "2019-05-01")
        self.assertIsNone(fecha_iso(None))

    def test_id_modelo(self):
        self.assertEqual([num_id(v) for v in (21122, "MOD-BCP-21122", "MOBA-BCP-0000177", "Transversal", None)], [21122, 21122, 177, None, None])
        self.assertEqual(lista_ids("21045, 18578"), [21045, 18578])
        self.assertEqual(lista_ids("246;245"), [246, 245])
        self.assertEqual(lista_ids("Transversal"), [])


class Esquema(unittest.TestCase):
    def test_tipos(self):
        self.assertTrue(cumple_tipo("decimal 0-1", 0.5))
        self.assertFalse(cumple_tipo("decimal 0-1", -0.2))
        self.assertFalse(cumple_tipo("entero", "0"))
        self.assertFalse(cumple_tipo("fecha", datetime(1900, 1, 1)))
        self.assertTrue(cumple_tipo("fecha texto", "1/05/2019"))

    def test_columna_faltante_es_error(self):
        arch = ARCHIVOS["ttm"]
        hallazgos = validar_esquema(arch, ["ID_MODELO"], [{"ID_MODELO": 1}])
        self.assertEqual(hallazgos[0].nivel, ERROR)

    def test_catalogo_y_vacios(self):
        arch = ARCHIVOS["ttm"]
        fila = {c: None for c in arch.nombres} | {"ID_MODELO": 1, "FECH_ALERTA": datetime(2026, 9, 30), "TTM_REAL_HOY": 1, "SOLICITO_AMPLIACION": "Quizás"}
        controles = {h.control: h.nivel for h in validar_esquema(arch, arch.nombres, [fila])}
        self.assertEqual(controles["SOLICITO_AMPLIACION: valores fuera del catálogo"], ALERTA)


class Generacion(unittest.TestCase):
    """Dos meses de historial y siete archivos de detalle con tres modelos: 1, 2 y 3 (solo en el último mes)."""

    def setUp(self):
        directorio = tempfile.TemporaryDirectory()
        self.addCleanup(directorio.cleanup)
        self.tmp = Path(directorio.name)
        self.inputs = self.tmp / "inputs"
        self.inputs.mkdir()
        cols = {k: a.nombres for k, a in ARCHIVOS.items()}
        base = {"ESTADO_ALERTA": "Sin alerta", "ESTADO_SEGUIMIENTO": "Con Seguimiento", "PO_USUARIO": "Ana", "MODEL_DEVELOPER": "COE IRM",
                "NOMBRE_MODELO": "Modelo", "PROCESO": "Cobranza", "TIER_MODELO": "I"}
        base.update({c: 0 for c in cols["input_principal"] if c.startswith("OBS_")})
        ago, sep = datetime(2026, 8, 31), datetime(2026, 9, 30)
        alerta = {"ESTADO_ALERTA": "En alerta", "EXCEDE_TTM": "Excede TTM", "EXCESO_MESES_TTM": 2.0, "PRESENCIA_MITIGANTE": "No"}
        excel(self.inputs / "hist.xlsx", cols["input_principal"], [
            {**base, "FECHA": ago, "ID_MODELO": "MOD-BCP-1"}, {**base, "FECHA": ago, "ID_MODELO": "MOD-BCP-2"},
            {**base, **alerta, "FECHA": sep, "ID_MODELO": "MOD-BCP-1"}, {**base, "FECHA": sep, "ID_MODELO": "MOD-BCP-2", "PO_USUARIO": "Luis"},
            {**base, "FECHA": sep, "ID_MODELO": "MOBA-BCP-0003", "MODEL_DEVELOPER": "GGR"}])
        obs = {"FECHA_PROCESO": datetime(2026, 10, 5), "ID_Obs": 10, "ID_Model": 1}
        excel(self.inputs / "obs.xlsx", cols["observaciones"], [obs, obs, {**obs, "ID_Obs": 11, "ID_Model": 99}])
        excel(self.inputs / "cob.xlsx", cols["coberturas"], [{"Modelo_ID": 1, "Fecha": datetime(2026, 10, 5), "Fecha_descobertura_Met": "31/12/2026"}])
        excel(self.inputs / "ttm.xlsx", cols["ttm"], [{"ID_MODELO": "MOD-BCP-1", "FECH_ALERTA": ago, "TTM_GOBIERNO_MESES": 3, "TTM_REAL_HOY": 5, "HOLGURA_EXCESO_TTM": 2}])
        sbs = {"Estado": "Pendiente", "Tipo": "SBS", "Fecha Emisión": "01/02/2026", "Fecha de Vencimiento": datetime(2026, 6, 30)}
        excel(self.inputs / "sbs.xlsx", cols["observaciones_sbs_ai"], [
            {**sbs, "ID": 1, "ID_MODELO": "1, 2", "Correo": "persona@ejemplo.com"}, {**sbs, "ID": 2, "ID_MODELO": "Transversal"}, {**sbs, "ID": 3, "ID_MODELO": 99}])
        nota = {"MODEL_USER": "Riesgos", "NOTA_GOBIERNO": 90, "NOTA_POLITICAS": 90}
        excel(self.inputs / "gob.xlsx", cols["nota_gobierno"], [
            {**nota, "PO_USUARIO": "Ana", "MODELO_DEVELOPER": "MMGR"}, {**nota, "PO_USUARIO": "Ana", "MODELO_DEVELOPER": "GGR", "NOTA_GOBIERNO": 70},
            {**nota, "PO_USUARIO": "Luis", "MODELO_DEVELOPER": "Otro"}])
        excel(self.inputs / "cal.xlsx", cols["calidad_datos"], [
            {"ID": 2, **{c: 0.05 for c, _, _ in CRITERIOS_CALIDAD}, "Indicador de Calidad de datos": 0.35, "Rango de cumplimiento": "<= a 50%"}])
        excel(self.inputs / "inv.xlsx", cols["inventario"], [
            {"ID_MODELO": 1, "NOMBRE_MODELO": "Modelo", "ID_MODELO_INPUT": "2;50;1;900"}, {"ID_MODELO": 2, "NOMBRE_MODELO": "Modelo", "ID_MODELO_INPUT": 900},
            {"ID_MODELO": 3, "NOMBRE_MODELO": "Modelo"}, {"ID_MODELO": 50, "NOMBRE_MODELO": "Módulo", "PERIMETRO_MODELO": "Módulo"},
            {"ID_MODELO": 900, "NOMBRE_MODELO": "No aplica"}])
        self.cfg = {
            "carpeta_inputs": str(self.inputs), "salida": str(self.tmp / "reporte.html"),
            "archivos": {"input_principal": "hist.xlsx", "observaciones": "obs.xlsx", "coberturas": "cob.xlsx", "ttm": "ttm.xlsx",
                         "observaciones_sbs_ai": "sbs.xlsx", "nota_gobierno": "gob.xlsx", "calidad_datos": "cal.xlsx", "inventario": "inv.xlsx"},
            "homologacion": {"nota_gobierno": {"MODELO_DEVELOPER": {"MMGR": "COE IRM"}}},
        }

    def generar(self):
        ruta = self.tmp / "config.yaml"
        ruta.write_text(yaml.safe_dump(self.cfg, allow_unicode=True), encoding="utf-8")
        return self.ejecutar(ruta)

    def ejecutar(self, config):
        return subprocess.run([sys.executable, str(RAIZ / "src" / "generar_reporte.py"), "--config", str(config)],
                              capture_output=True, text=True, encoding="utf-8")

    def datos(self):
        r = self.generar()
        self.assertEqual(r.returncode, 0, r.stderr)
        html = (self.tmp / "reporte.html").read_text(encoding="utf-8")
        self.assertNotIn("/*__DATOS__*/null", html)
        return json.loads(re.search(r"const DATOS = (\{.*?\});\n", html, re.S).group(1))

    def test_historico_e_id_normalizado(self):
        d = self.datos()
        self.assertEqual(d["fechas"], ["2026-08-31", "2026-09-30"])
        self.assertEqual(sorted(m["ID_MODELO"] for m in d["modelos"] if m["FECHA"] == d["corte"]), [1, 2, 3])
        self.assertEqual({m["CODIGO_MODELO"] for m in d["modelos"] if m["ID_MODELO"] == 3}, {"MOBA-BCP-0003"})

    def test_detalle_solo_del_ultimo_mes(self):
        d = self.datos()
        # Quita la fila repetida y la observación de un modelo fuera del inventario
        self.assertEqual([o["id_modelo"] for o in d["observaciones"]], [1])
        self.assertEqual(d["coberturas"][0]["Fecha_descobertura_Met"], "2026-12-31")
        self.assertEqual([(t["id_modelo"], t["holgura"]) for t in d["ttm"]], [(1, 2)])
        self.assertEqual([c["id_modelo"] for c in d["calidad"]], [2])

    def test_sbs_una_fila_por_modelo_y_sin_correo(self):
        sbs = self.datos()["sbs"]
        # "1, 2" se separa en dos filas, la transversal queda sin modelo y la del modelo 99 se excluye
        self.assertEqual(sorted((o["id"], o["id_modelo"]) for o in sbs if o["id_modelo"]), [(1, 1), (1, 2)])
        self.assertEqual([o["alcance"] for o in sbs if not o["id_modelo"]], ["Transversal"])
        self.assertNotIn("persona@ejemplo.com", json.dumps(sbs))

    def test_nota_de_gobierno_por_po_y_developer(self):
        d = self.datos()
        nota = {k: d["gobierno"][i]["nota"] for k, i in d["gob_de"].items()}
        # Ana tiene dos filas: se elige por model developer. Luis tiene una sola: se usa aunque el developer no coincida.
        self.assertEqual(nota, {"1": 90, "2": 90, "3": 70})

    def test_insumos_sin_marcador_ni_autorreferencia(self):
        d = self.datos()
        insumos = {i["id_modelo"]: i["insumos"] for i in d["inventario"]}
        self.assertEqual(insumos, {1: [2, 50], 2: [], 3: []})
        self.assertEqual(d["inv_nombres"]["50"], {"n": "Módulo", "p": "Módulo"})

    def test_control_de_calidad(self):
        self.generar()
        texto = (self.tmp / "control_calidad.txt").read_text(encoding="utf-8")
        self.assertIn("Modelos que se declaran como insumo de sí mismos", texto)
        self.assertIn("Observaciones sin modelo", texto)

    def test_archivo_de_detalle_opcional(self):
        self.cfg["archivos"].pop("ttm")
        self.cfg["archivos"]["inventario"] = "no_existe.xlsx"
        d = self.datos()
        self.assertIsNone(d["ttm"])
        self.assertIsNone(d["inventario"])
        self.assertIn("Archivo no cargado", (self.tmp / "control_calidad.txt").read_text(encoding="utf-8"))

    def test_input_principal_faltante(self):
        self.cfg["archivos"]["input_principal"] = "no_existe.xlsx"
        r = self.generar()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("No se encontró", r.stderr)
        self.assertIn("carpeta_inputs", r.stderr)

    def test_sin_config(self):
        r = self.ejecutar(self.tmp / "no_existe.yaml")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("config.ejemplo.yaml", r.stderr)


if __name__ == "__main__":
    unittest.main()
