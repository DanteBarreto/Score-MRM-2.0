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

from generar_reporte import COLS_COBERTURA, COLS_OBSERVACION, COLUMNAS, fecha_iso, limpiar  # noqa: E402


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
        self.assertIsNone(fecha_iso(None))


class Generacion(unittest.TestCase):
    def setUp(self):
        directorio = tempfile.TemporaryDirectory()
        self.addCleanup(directorio.cleanup)
        self.tmp = Path(directorio.name)
        self.inputs = self.tmp / "inputs"
        self.inputs.mkdir()
        modelo = {"FECHA": datetime(2026, 8, 31), "ESTADO_ALERTA": "Sin alerta", "ESTADO_SEGUIMIENTO": "Con Seguimiento"}
        modelo.update({c: 0 for c in COLUMNAS if c.startswith("OBS_")})
        excel(self.inputs / "input.xlsx", COLUMNAS, [{**modelo, "ID_MODELO": 1}, {**modelo, "ID_MODELO": 2}])
        obs = {"FECHA_PROCESO": datetime(2026, 10, 22), "ID_Obs": 10, "ID_Model": 1}
        excel(self.inputs / "obs.xlsx", [*COLS_OBSERVACION, "FECHA_PROCESO"],
              [obs, obs, {**obs, "ID_Obs": 11, "ID_Model": 99}])
        excel(self.inputs / "cob.xlsx", [*COLS_COBERTURA, "Fecha"],
              [{"Modelo_ID": 1, "Fecha": datetime(2026, 10, 5), "Fecha_descobertura_Met": "31/12/2026"}])
        self.cfg = {
            "carpeta_inputs": str(self.inputs),
            "archivos": {"input_principal": "input.xlsx", "observaciones": "obs.xlsx", "coberturas": "cob.xlsx"},
            "salida": str(self.tmp / "reporte.html"),
            "simulacion": {"activa": False, "salida": str(self.tmp / "simulado.xlsx")},
        }

    def generar(self):
        ruta = self.tmp / "config.yaml"
        ruta.write_text(yaml.safe_dump(self.cfg, allow_unicode=True), encoding="utf-8")
        return self.ejecutar(ruta)

    def ejecutar(self, config):
        return subprocess.run([sys.executable, str(RAIZ / "src" / "generar_reporte.py"), "--config", str(config)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_reporte_con_inputs_locales(self):
        r = self.generar()
        self.assertEqual(r.returncode, 0, r.stderr)
        html = (self.tmp / "reporte.html").read_text(encoding="utf-8")
        self.assertNotIn("/*__DATOS__*/null", html)
        datos = json.loads(re.search(r"const DATOS = (\{.*?\});\n", html, re.S).group(1))
        self.assertEqual(datos["fechas"], ["2026-08-31"])
        self.assertEqual(datos["fechas_simuladas"], [])
        self.assertEqual(len(datos["modelos"]), 2)
        # Quita la fila repetida y la observación de un modelo fuera del inventario
        self.assertEqual([o["id_modelo"] for o in datos["observaciones"]], [1])
        self.assertEqual(datos["coberturas"][0]["Fecha_descobertura_Met"], "2026-12-31")

    def test_archivo_faltante(self):
        self.cfg["archivos"]["observaciones"] = "no_existe.xlsx"
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
