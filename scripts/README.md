# Scripts del Observatorio

Requisitos: Python ≥ 3.10 y `requests`. Para las capturas: `playwright` y Chrome/Chromium.

| Script | Qué hace | Salida |
|---|---|---|
| `fetch_macro.py` | Eurostat (JSON-stat), Banco Mundial (API v2) y FMI WEO (DataMapper): PIB, PIB pc PPA, paro, deuda, déficit, IPCA, productividad | `data/macro.json` |
| `fetch_indices.py` | V-Dem, Freedom House y TI-CPI (CSV de Our World in Data) + WGI del Banco Mundial | `data/indices.json` |
| `fetch_boe.py [año_ini año_fin]` | Buscador del BOE: leyes, leyes orgánicas, RDL, RDL derogados/convalidados (Sección I) e indultos (Sección III), 1977-hoy; complemento con la API de legislación consolidada | `data/boe_normas.json` (norma a norma con ref. BOE y URL de cada consulta) |
| `fetch_cgpj.py [año_ini]` | Repositorio de corrupción del CGPJ, resumen nacional trimestral | `data/cgpj_corrupcion.json` |
| `build_site.py` | Empaqueta los JSON en `site/data.js` | `site/data.js` |
| `capturas.py` | Capturas PNG del sitio servido en local | `capturas/*.png` |
| `update_all.sh` | Ejecuta todo en orden | — |

Datos manuales (sin API): `data/manual.json`, con promesas, PactoCheck, TI-CPI 2025 y la lista de pendientes. Hay que editarlo a mano, con fuente y fecha.

## Regenerar

```bash
cd /workspace/observatorio
bash scripts/update_all.sh            # ~3-4 min (BOE ≈ 2,5 min, CGPJ ≈ 1 min)
cd site && python3 -m http.server 8765 --bind 127.0.0.1 &   # ver en http://127.0.0.1:8765
cd .. && .venv/bin/python scripts/capturas.py
```

Si una fuente falla, `fetch_macro.py` y `fetch_indices.py` conservan el dato anterior y lo marcan con `aviso`.
Validación del BOE: comprobar que la numeración anual es continua (hay un ejemplo en el informe de METODOLOGIA.md, §3.1).
