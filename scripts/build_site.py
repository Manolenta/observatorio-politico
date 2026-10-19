"""Empaqueta data/*.json en site/data.js (sin servidor: el sitio estático lee window.OBS)."""
import json, os
from common import DATA, BASE, now_iso

def load(n):
    p = os.path.join(DATA, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"estado": "pendiente"}

def main():
    boe = load("boe_normas.json")
    boe.pop("normas", None)  # el detalle norma a norma queda en data/ (demasiado grande para la web)
    obs = {"generado": now_iso(), "macro": load("macro.json"), "indices": load("indices.json"),
           "boe": boe, "cgpj": load("cgpj_corrupcion.json"), "manual": load("manual.json"),
           "institucional": {k: v for k, v in load("institucional.json").items() if k != "cache_elecciones"},
           "changelog": {k: v for k, v in load("changelog.json").items() if k in ("ultima_ejecucion", "ultima_actualizacion_datos")}}
    out = os.path.join(BASE, "site", "data.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("window.OBS = " + json.dumps(obs, ensure_ascii=False) + ";\n")
    print("generado", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()
