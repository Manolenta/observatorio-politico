#!/usr/bin/env bash
# Regenera todos los datos y el sitio. Uso: bash scripts/update_all.sh
set -u
cd "$(dirname "$0")"
python3 fetch_macro.py   || echo "AVISO: macro falló (se conservan datos previos)"
python3 fetch_indices.py || echo "AVISO: índices falló"
python3 fetch_boe.py     || echo "AVISO: BOE falló"
python3 fetch_cgpj.py    || echo "AVISO: CGPJ falló"
python3 build_site.py
