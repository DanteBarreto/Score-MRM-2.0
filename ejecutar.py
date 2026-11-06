"""Ejecuta el Score MRM paso a paso, explicando qué hace cada etapa.

En Visual Studio Code, abre este archivo y presiona Run, o escribe en la terminal:
    python ejecutar.py
Solo usa la biblioteca estándar de Python, porque corre antes de instalar las dependencias.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENV = RAIZ / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
CONFIG = RAIZ / "config.yaml"


def paso(numero, titulo, explicacion):
    print(f"\n[Paso {numero} de 5] {titulo}\n  {explicacion}")


def correr(*comando):
    if subprocess.run(comando, cwd=RAIZ).returncode != 0:
        sys.exit("\nEl paso falló. Revisa el mensaje anterior o docs/guia_vscode.md.")


def carpeta_configurada():
    return re.search(r"^carpeta_inputs:\s*'?(.*?)'?\s*$", CONFIG.read_text(encoding="utf-8"), re.M).group(1)


def pedir_carpeta():
    while True:
        carpeta = input("  Pega la ruta de la carpeta con tus Excel: ").strip().strip("'\"")
        if Path(carpeta).is_dir():
            return carpeta
        print("  Esa carpeta no existe. Inténtalo de nuevo.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("Score MRM: generación guiada del reporte")

    paso(1, "Revisar Python", "El proceso necesita Python 3.10 o superior.")
    if sys.version_info < (3, 10):
        sys.exit(f"  Tienes Python {sys.version.split()[0]}. Instala una versión más reciente.")
    print(f"  Correcto: Python {sys.version.split()[0]}.")

    paso(2, "Preparar el entorno", "Crea .venv, una instalación de Python solo para este proyecto.")
    if PYTHON.exists():
        print("  El entorno ya existe.")
    else:
        correr(sys.executable, "-m", "venv", str(VENV))
        print("  Entorno creado.")

    paso(3, "Instalar dependencias", "Instala las librerías para leer los Excel y la configuración.")
    correr(str(PYTHON), "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", "requirements.txt")
    print("  Dependencias listas.")

    paso(4, "Configurar tus inputs", "config.yaml guarda la carpeta de tus Excel y no se sube a Git.")
    if not CONFIG.exists():
        shutil.copy(RAIZ / "config.ejemplo.yaml", CONFIG)
        print("  Se creó config.yaml.")
    if Path(carpeta_configurada()).is_dir():
        print(f"  Carpeta de inputs: {carpeta_configurada()}")
    else:
        carpeta = pedir_carpeta().replace("'", "''")
        texto = re.sub(r"^carpeta_inputs:.*$", lambda _: f"carpeta_inputs: '{carpeta}'",
                       CONFIG.read_text(encoding="utf-8"), flags=re.M)
        CONFIG.write_text(texto, encoding="utf-8")
        print("  Carpeta guardada. Si tus archivos tienen otros nombres, ajústalos en config.yaml.")

    paso(5, "Generar el reporte", "Lee los Excel, los une por ID de modelo y abre el reporte en el navegador.")
    correr(str(PYTHON), "src/generar_reporte.py", "--abrir")
    print("\nListo. El reporte está en output/reporte_mrm.html. La próxima vez, vuelve a ejecutar este archivo.")


if __name__ == "__main__":
    main()
