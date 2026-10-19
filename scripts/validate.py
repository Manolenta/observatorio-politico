"""Validación previa a la publicación. Sale con código 1 si hay ERRORES (el workflow no publica).
Los enlaces rotos son solo AVISOS. Escribe el informe en data/validacion.md.
Uso: python3 validate.py [--sin-enlaces]"""
import json, os, re, sys, collections, concurrent.futures as cf
import requests
from common import DATA, UA

# Huecos de numeración ya conocidos y revisados (números que el BOE no publica como Ley/LO/RDL de Jefatura del Estado
# o asignados a disposiciones con otra rúbrica). Cualquier hueco nuevo se trata como error de extracción.
HUECOS_CONOCIDOS = {"Ley 18/1977", "Ley 25/1977", "Ley 45/1977", "Ley 16/1978", "Ley 21/1978", "Ley 57/1978", "Ley 58/1978",
    "Ley 78/1978", "Ley 79/1978", "Ley 90/1978", "Ley 20/1979", "Ley 21/1979", "Ley 22/1979", "Ley 23/1979", "Ley 24/1979",
    "Ley 25/1979", "Ley 42/1980", "Ley 8/1981", "Ley 38/1983", "Ley 8/1985", "Ley 12/1988", "Ley 13/2001", "Ley 15/2001",
    "Ley Orgánica 9/1991", "Real Decreto-ley 27/1977", "Real Decreto-ley 28/1977", "Real Decreto-ley 38/1977",
    "Real Decreto-ley 13/1978", "Real Decreto-ley 17/1978", "Real Decreto-ley 26/1978", "Real Decreto-ley 40/1978",
    "Real Decreto-ley 47/1978", "Real Decreto-ley 17/1979", "Real Decreto-ley 5/2001", "Real Decreto-ley 6/2004"}
CAMPOS_CGPJ = ["personas_fisicas", "procedimientos", "cond_conformidad", "cond_sin_conformidad", "absolutorias"]
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}")
errores, avisos, urls = [], [], set()

def load(n):
    p = os.path.join(DATA, n)
    if not os.path.exists(p):
        errores.append(f"Falta {n}"); return {}
    return json.load(open(p, encoding="utf-8"))

def boe():
    n = load("boe_normas.json").get("normas", {})
    if not n: errores.append("boe_normas.json sin normas"); return
    g = collections.defaultdict(set)
    for v in n.values():
        if v["fecha"] >= "1977": g[(v["tipo"], v["fecha"][:4])].add(v["num"])
    huecos = {f"{t} {i}/{y}" for (t, y), s in g.items() for i in range(1, max(s) + 1) if i not in s}
    for h in sorted(huecos - HUECOS_CONOCIDOS): errores.append(f"BOE: hueco de numeración nuevo: {h}")
    for h in sorted(HUECOS_CONOCIDOS - huecos): avisos.append(f"BOE: el hueco conocido {h} ya no aparece (¿se ha recuperado la norma?)")

def cgpj():
    a = load("cgpj_corrupcion.json").get("anual", {})
    años = sorted(y for y, v in a.items() if v.get("trimestres") == 4)
    if len(años) < 5: errores.append("CGPJ: menos de 5 años completos"); return
    for c in CAMPOS_CGPJ:
        for y0, y1 in zip(años, años[1:]):
            v0, v1 = a[y0].get(c), a[y1].get(c)
            if v0 is None or v1 is None or v1 < 0: errores.append(f"CGPJ {y1} {c}: valor ausente o negativo"); continue
            base = max(v0, 10)
            if v1 > 4 * base or (v0 >= 20 and v1 < v0 / 4):
                errores.append(f"CGPJ {y1} {c}: salto anómalo {v0} → {v1} (×4 o más)")
            elif v1 > 2.5 * base or (v0 >= 20 and v1 < v0 / 2.5):
                avisos.append(f"CGPJ {y1} {c}: variación grande {v0} → {v1}")
    for y, v in a.items():
        if v.get("trimestres", 0) < 4 and y not in (max(a), min(a)): errores.append(f"CGPJ {y}: año pasado incompleto ({v.get('trimestres')} trimestres)")

def manual():
    m = load("manual.json")
    general = m.get("consultado")
    if not (general and FECHA.match(general)): errores.append("manual.json: falta 'consultado' (fecha) general")
    def chk(nombre, e, campo_fecha=("consultado", "fecha_dato")):
        if not e.get("url", "").startswith("http"): errores.append(f"manual.json: {nombre} sin URL")
        else: urls.add(e["url"])
        if not any(FECHA.match(str(e.get(k, ""))) for k in campo_fecha) and not general:
            errores.append(f"manual.json: {nombre} sin fecha")
    chk("pactocheck", m.get("pactocheck", {}))
    if not FECHA.match(str(m.get("pactocheck", {}).get("fecha_dato", ""))): errores.append("manual.json: pactocheck sin fecha_dato")
    for k in ("promesas", "manuales_democracia", "manuales_corrupcion"):
        for i, e in enumerate(m.get(k, [])): chk(f"{k}[{i}] {e.get('promesa') or e.get('nombre')}", e)

def institucional():
    d = load("institucional.json")
    for k in ("presupuestos", "funciones", "cgpj", "rdl_proyecto_xv"):
        if d.get(k, {}).get("estado") == "pendiente": avisos.append(f"institucional: {k} pendiente ({d[k].get('error', '')[:80]})")
        elif d.get(k, {}).get("aviso"): avisos.append(f"institucional: {k}: {d[k]['aviso']}")
    for p in d.get("funciones", {}).get("periodos", []):
        if not (0 <= p["dias"] < 400) and not p.get("en_curso"): errores.append(f"funciones: duración anómala {p}")
    if d.get("funciones", {}).get("no_parseados"): avisos.append(f"funciones: RD sin fecha de elecciones: {d['funciones']['no_parseados']}")

def recoger_urls():
    for n in ("macro.json", "indices.json"):
        for i in load(n).get("indicadores", []):
            for k in ("web",): 
                if i.get(k): urls.add(i[k])
    urls.update({"https://www.boe.es/buscar/boe.php", "https://www.congreso.es/es/opendata/iniciativas"})

def enlace(u):
    try:
        r = requests.head(u, headers=UA, timeout=25, allow_redirects=True)
        if r.status_code >= 400 and r.status_code not in (403, 405, 429):
            r = requests.get(u, headers=UA, timeout=25, stream=True)
        return u, r.status_code
    except Exception as e:
        return u, type(e).__name__

def main():
    boe(); cgpj(); manual(); institucional(); recoger_urls()
    if "--sin-enlaces" not in sys.argv:
        with cf.ThreadPoolExecutor(8) as ex:
            for u, st in ex.map(enlace, sorted(urls)):
                if not (isinstance(st, int) and st < 400): avisos.append(f"Enlace no responde ({st}): {u}")
    rep = ["# Validación", "", f"Errores: {len(errores)} · Avisos: {len(avisos)} · Enlaces comprobados: {len(urls)}", ""]
    rep += ["## Errores"] + [f"- {e}" for e in errores] + ["", "## Avisos"] + [f"- {a}" for a in avisos]
    open(os.path.join(DATA, "validacion.md"), "w", encoding="utf-8").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    sys.exit(1 if errores else 0)

if __name__ == "__main__":
    main()
