"""Compara las cifras clave con la instantánea anterior y anota los cambios en data/changelog.json y CHANGELOG.md.
Se ejecuta en update_all.sh después de las descargas y antes de build_site.py."""
import json, os
from common import DATA, BASE, now_iso

def L(n):
    p = os.path.join(DATA, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}

def cifras():
    c = {}
    for i in L("macro.json").get("indicadores", []):
        s = (i.get("series") or {}).get("ES") or {}
        if s:
            y = max(s); c[f"macro · {i.get('nombre')} · {y}"] = s[y]
    for r in L("boe_normas.json").get("por_legislatura", []):
        for k in ("leyes_ordinarias", "leyes_organicas", "rdl", "rdl_convalidados_publicados", "rdl_derogados"):
            c[f"BOE · {r['legislatura']} · {k}"] = r.get(k)
    for r in L("boe_normas.json").get("indultos_por_año", []):
        c[f"BOE · indultos · {r['año']}"] = r["indultos"]
    for y, v in L("cgpj_corrupcion.json").get("anual", {}).items():
        for k in ("personas_fisicas", "procedimientos"):
            c[f"CGPJ · {y} · {k}"] = v.get(k)
    d = L("institucional.json")
    for a in d.get("presupuestos", {}).get("años", []):
        c[f"Presupuestos · {a['año']}"] = a["estado"]
    for p in d.get("funciones", {}).get("periodos", []):
        c[f"Días en funciones · elecciones {p['desde_elecciones']}"] = p["dias"]
    for r in d.get("cgpj", {}).get("renovaciones", []):
        if "dias_retraso_aprox" in r: c[f"Retraso CGPJ · renovación {r['renovacion']}"] = r["dias_retraso_aprox"]
    x = d.get("rdl_proyecto_xv", {})
    if "tramitados_como_proyecto" in x:
        c["RDL tramitados como PL · XV"] = x["tramitados_como_proyecto"]; c["RDL tramitados como PL · XV · ley"] = x["terminados_como_ley"]
    return {k: v for k, v in c.items() if v is not None}

def main():
    p = os.path.join(DATA, "changelog.json")
    log = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"entradas": [], "instantanea": {}}
    ant, act = log.get("instantanea", {}), cifras()
    cambios = [{"cifra": k, "antes": ant.get(k), "ahora": v} for k, v in sorted(act.items()) if ant.get(k) != v]
    cambios += [{"cifra": k, "antes": ant[k], "ahora": None} for k in sorted(set(ant) - set(act))]
    ts = now_iso()
    log["ultima_ejecucion"] = ts
    if cambios:
        primera = not ant
        log["entradas"].insert(0, {"fecha": ts, "n_cambios": len(cambios),
                                   "cambios": [] if primera else cambios[:300],
                                   "nota": "Instantánea inicial de las cifras (sin comparación previa)." if primera else ""})
        log["ultima_actualizacion_datos"] = ts
    log["entradas"] = log["entradas"][:200]
    log["instantanea"] = act
    json.dump(log, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# Registro de cambios de datos", "", "Generado automáticamente por `scripts/changelog.py` en cada actualización: solo se anotan las cifras que cambian.",
          "Los cambios de código y metodología están en el historial de git.", ""]
    for e in log["entradas"]:
        md.append(f"## {e['fecha'][:16].replace('T', ' ')} (hora de Madrid) · {e['n_cambios']} cifras")
        if e.get("nota"): md.append(e["nota"])
        md += [f"- {c['cifra']}: {c['antes']} → {c['ahora']}" for c in e["cambios"][:100]]
        md.append("")
    open(os.path.join(BASE, "CHANGELOG.md"), "w", encoding="utf-8").write("\n".join(md))
    print(f"changelog: {len(cambios)} cambios")

if __name__ == "__main__":
    main()
