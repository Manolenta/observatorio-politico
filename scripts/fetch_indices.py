"""Cuadros 3 y 4: índices internacionales de calidad democrática y corrupción.
- Banco Mundial WGI (API): voz y rendición de cuentas, estado de derecho, control de la corrupción, eficacia del gobierno.
- V-Dem y Freedom House y TI-CPI vía Our World in Data (CSV redistribuible; origen citado).
- EIU Democracy Index: OWID no permite redistribuirlo -> 'pendiente' (consulta manual).
"""
import csv, io
from common import get, save, now_iso, DATA
import json as _json, os as _os

PAISES = {"Spain", "Germany", "France", "Italy", "Portugal"}

def owid(slug):
    url = f"https://ourworldindata.org/grapher/{slug}.csv"
    rows = list(csv.reader(io.StringIO(get(url).text)))
    head = rows[0]; series = {}
    for r in rows[1:]:
        if r[0] in PAISES and len(r) > 3 and r[3] != "":
            series.setdefault(r[0], {})[r[2]] = float(r[3])
    return {"url": url, "web": f"https://ourworldindata.org/grapher/{slug}", "columna": head[3], "series": series}

def wgi(code):
    url = f"https://api.worldbank.org/v2/country/ESP;DEU;FRA;ITA;PRT/indicator/GOV_WGI_{code}.EST?format=json&per_page=2000"
    meta, rows = get(url).json()
    s = {}
    for r in rows or []:
        if r["value"] is not None:
            s.setdefault(r["country"]["value"], {})[r["date"]] = round(r["value"], 3)
    return {"url": url, "web": "https://www.worldbank.org/en/publication/worldwide-governance-indicators", "series": s,
            "actualizado_fuente": meta.get("lastupdated")}

IND = [
    ("vdem_electoral", "V-Dem: índice de democracia electoral (0-1)", "V-Dem (vía OWID)", "democracia", lambda: owid("electoral-democracy-index")),
    ("vdem_liberal", "V-Dem: índice de democracia liberal (0-1)", "V-Dem (vía OWID)", "democracia", lambda: owid("liberal-democracy-index")),
    ("vdem_rule_of_law", "V-Dem: estado de derecho (0-1)", "V-Dem (vía OWID)", "democracia", lambda: owid("rule-of-law-index")),
    ("vdem_judicial", "V-Dem: control judicial del ejecutivo (0-1)", "V-Dem (vía OWID)", "democracia", lambda: owid("judicial-constraints-on-the-executive-index")),
    ("fh_derechos_politicos", "Freedom House: derechos políticos (0-40)", "Freedom House (vía OWID)", "democracia", lambda: owid("political-rights-score-fh")),
    ("fh_libertades_civiles", "Freedom House: libertades civiles (0-60)", "Freedom House (vía OWID)", "democracia", lambda: owid("civil-liberties-score-fh")),
    ("wgi_voz", "WGI: voz y rendición de cuentas (-2,5 a 2,5)", "Banco Mundial WGI", "democracia", lambda: wgi("VA")),
    ("wgi_estado_derecho", "WGI: estado de derecho (-2,5 a 2,5)", "Banco Mundial WGI", "democracia", lambda: wgi("RL")),
    ("wgi_eficacia", "WGI: eficacia del gobierno (-2,5 a 2,5)", "Banco Mundial WGI", "democracia", lambda: wgi("GE")),
    ("ti_cpi", "TI: Índice de Percepción de la Corrupción (0-100)", "Transparency International (vía OWID)", "corrupcion", lambda: owid("ti-corruption-perception-index")),
    ("wgi_corrupcion", "WGI: control de la corrupción (-2,5 a 2,5)", "Banco Mundial WGI", "corrupcion", lambda: wgi("CC")),
    ("vdem_corrupcion", "V-Dem: índice de corrupción política (0-1, más = peor)", "V-Dem (vía OWID)", "corrupcion", lambda: owid("political-corruption-index")),
]

def main():
    out = {"extraido": now_iso(), "indicadores": []}
    nombre = "macro.json" if "macro" in __file__ else "indices.json"
    prev = {}
    if _os.path.exists(_os.path.join(DATA, nombre)):
        prev = {i["id"]: i for i in _json.load(open(_os.path.join(DATA, nombre), encoding="utf-8"))["indicadores"] if i.get("estado") == "ok"}
    for k, n, f, cuadro, fn in IND:
        try:
            r = fn(); r.update({"id": k, "nombre": n, "fuente": f, "cuadro": cuadro, "estado": "ok"})
        except Exception as e:
            r = dict(prev[k], estado="ok", aviso="Fallo al actualizar; se conserva el dato anterior: " + str(e)[:120]) if k in prev else {"id": k, "nombre": n, "fuente": f, "cuadro": cuadro, "estado": "pendiente", "error": str(e)[:200]}
        print(k, r["estado"]); out["indicadores"].append(r)
    out["indicadores"].append({"id": "eiu", "nombre": "EIU Democracy Index (0-10)", "fuente": "Economist Intelligence Unit",
        "cuadro": "democracia", "estado": "pendiente", "web": "https://www.eiu.com/n/campaigns/democracy-index-2024/",
        "error": "Licencia no redistribuible (OWID devuelve 403). Requiere consulta manual del informe anual."})
    save("indices.json", out)

if __name__ == "__main__":
    main()
