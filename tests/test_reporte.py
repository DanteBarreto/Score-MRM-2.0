"""Pruebas del proceso. Ejecutar con:  python -m unittest discover -s tests"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from generar_reporte import fecha_iso, limpiar  # noqa: E402


class Limpieza(unittest.TestCase):
    def test_texto(self):
        self.assertEqual(limpiar("Sin  validación "), "Sin validación")
        self.assertEqual(limpiar("linea_x000D_\nsiguiente"), "linea siguiente")
        self.assertIsNone(limpiar("   "))

    def test_fecha(self):
        self.assertEqual(fecha_iso("31/08/2026"), "2026-08-31")
        self.assertIsNone(fecha_iso(None))


class Generacion(unittest.TestCase):
    def generar(self, cambios=None):
        cfg = yaml.safe_load((RAIZ / "config.yaml").read_text(encoding="utf-8"))
        tmp = Path(self.dir.name)
        cfg["rutas"]["salida"] = str(tmp / "reporte.html")
        cfg["simulacion"]["salida"] = str(tmp / "input.xlsx")
        cfg["rutas"].update(cambios or {})
        ruta = tmp / "config.yaml"
        ruta.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        return subprocess.run([sys.executable, str(RAIZ / "src" / "generar_reporte.py"), "--config", str(ruta)],
                              capture_output=True, text=True, encoding="utf-8")

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

    def test_reporte_completo(self):
        r = self.generar()
        self.assertEqual(r.returncode, 0, r.stderr)
        html = (Path(self.dir.name) / "reporte.html").read_text(encoding="utf-8")
        self.assertNotIn("/*__DATOS__*/null", html)
        datos = json.loads(re.search(r"const DATOS = (\{.*?\});\n", html, re.S).group(1))
        self.assertEqual(len(datos["fechas"]), 4)
        ultima = [m for m in datos["modelos"] if m["FECHA"] == datos["fechas"][-1]]
        ids = {m["ID_MODELO"] for m in ultima}
        self.assertTrue(all(o["id_modelo"] in ids for o in datos["observaciones"]))
        self.assertTrue(all(c["Modelo_ID"] in ids for c in datos["coberturas"]))

    def test_archivo_faltante(self):
        r = self.generar({"observaciones": "data/no_existe.xlsx"})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("No se encontró", r.stderr)


if __name__ == "__main__":
    unittest.main()
