# Recursos incrustados en el reporte

`src/generar_reporte.py` copia estos archivos dentro del HTML del reporte. Así el reporte no necesita internet y se ve igual en visores que bloquean recursos externos, como SharePoint, Outlook o Teams.

| Archivo | Origen | Versión | Licencia |
|---|---|---|---|
| `tabler.min.css`, `tabler.min.js` | [Tabler](https://github.com/tabler/tabler) | 1.4.0 | MIT |
| `tabler-icons.min.css`, `tabler-icons.woff2` | [Tabler Icons](https://github.com/tabler/tabler-icons) | 3.34.0 | MIT |
| `archivo.css`, `archivo-latin.woff2`, `archivo-latin-ext.woff2` | [Archivo](https://fonts.google.com/specimen/Archivo), de Omnibus-Type | Google Fonts v25 | SIL Open Font License 1.1 |

No los edites a mano. Para cambiar de versión, reemplaza los archivos y revisa que el reporte se vea bien.
