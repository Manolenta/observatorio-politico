"""Cuadro 1: indicadores macro de Eurostat, Banco Mundial y FMI (APIs públicas sin clave)."""
import itertools
from common import get, save, now_iso, DATA
import json as _json, os as _os

ES = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
GEOS = ["ES", "EU27_2020", "EA20", "DE", "FR", "IT", "PT"]

def eurostat(ds, filtros, geos=GEOS):
    q = "&".join(f"{k}={v}" for k, v in filtros.items()) + "".join(f"&geo={g}" for g in geos)
    url = f"{ES}{ds}?{q}"
    d = get(url).json()
    dims = d["id"]; size = d["size"]
    cats = [sorted(d["dimension"][k]["category"]["index"].items(), key=lambda x: x[1]) for k in dims]
    series = {}
    for flat, combo in enumerate(itertools.product(*cats)):
        v = d["value"].get(str(flat))
        if v is None: continue
        c = {dims[i]: combo[i][0] for i in range(len(dims))}
        series.setdefault(c["geo"], {})[c["time"]] = v
    return {"url": url, "web": f"https://ec.europa.eu/eurostat/databrowser/view/{ds}/default/table",
            "actualizado_fuente": d.get("updated"), "series": series}

def worldbank(ind, paises="ESP;EUU;DEU;FRA;ITA;PRT"):
    url = f"https://api.worldbank.org/v2/country/{paises}/indicator/{ind}?format=json&per_page=20000"
    meta, rows = get(url).json()
    series = {}
    for r in rows or []:
        if r["value"] is not None:
            series.setdefault(r["countryiso3code"] or r["country"]["id"], {})[r["date"]] = r["value"]
    return {"url": url, "web": f"https://data.worldbank.org/indicator/{ind}?locations=ES",
            "actualizado_fuente": meta.get("lastupdated"), "series": series}

def imf(ind, paises=("ESP", "DEU", "FRA", "ITA", "PRT")):
    url = f"https://www.imf.org/external/datamapper/api/v1/{ind}/{'/'.join(paises)}"
    d = get(url).json()
    return {"url": url, "web": f"https://www.imf.org/external/datamapper/{ind}@WEO/ESP",
            "series": {k: v for k, v in d.get("values", {}).get(ind, {}).items() if k in paises}, "nota": "WEO: incluye estimaciones y proyecciones para los años recientes/futuros"}

INDICADORES = [
    ("pib_crecimiento", "Crecimiento real del PIB (%)", "Eurostat", lambda: eurostat("tec00115", {"unit": "CLV_PCH_PRE", "na_item": "B1GQ"})),
    ("pib_pc_pps", "PIB per cápita en PPA (UE27=100)", "Eurostat", lambda: eurostat("tec00114", {"indic_ppp": "VI_PPS_EU27_2020_HAB"}, ["ES", "EU27_2020", "DE", "FR", "IT", "PT"])),
    ("pib_pc_ppa_usd", "PIB per cápita PPA ($ int. constantes 2021)", "Banco Mundial", lambda: worldbank("NY.GDP.PCAP.PP.KD")),
    ("paro", "Tasa de paro 15-74 (%)", "Eurostat", lambda: eurostat("une_rt_a", {"age": "Y15-74", "sex": "T", "unit": "PC_ACT"})),
    ("paro_juvenil", "Paro juvenil 15-24 (%)", "Eurostat", lambda: eurostat("une_rt_a", {"age": "Y15-24", "sex": "T", "unit": "PC_ACT"})),
    ("deuda", "Deuda pública (% PIB, PDE)", "Eurostat", lambda: eurostat("gov_10dd_edpt1", {"na_item": "GD", "sector": "S13", "unit": "PC_GDP"})),
    ("deficit", "Déficit (-)/superávit público (% PIB)", "Eurostat", lambda: eurostat("gov_10dd_edpt1", {"na_item": "B9", "sector": "S13", "unit": "PC_GDP"})),
    ("inflacion", "Inflación IPCA (media anual, %)", "Eurostat", lambda: eurostat("prc_hicp_aind", {"coicop": "CP00", "unit": "RCH_A_AVG"})),
    ("productividad_hora", "Productividad por hora trabajada (UE27=100, PPS)", "Eurostat", lambda: eurostat("tesem160", {"na_item": "NLPR_HW"})),
    ("paro_largo_fmi", "Paro (%), serie larga desde 1980", "FMI WEO", lambda: imf("LUR")),
    ("deuda_larga_fmi", "Deuda bruta AAPP (% PIB), serie larga", "FMI WEO", lambda: imf("GGXWDG_NGDP")),
    ("deficit_largo_fmi", "Saldo AAPP (% PIB), serie larga", "FMI WEO", lambda: imf("GGXCNL_NGDP")),
    ("pib_crec_largo_fmi", "Crecimiento real PIB (%), serie larga", "FMI WEO", lambda: imf("NGDP_RPCH")),
    ("inflacion_larga_fmi", "Inflación IPC media (%), serie larga", "FMI WEO", lambda: imf("PCPIPCH")),
]

def main():
    out = {"extraido": now_iso(), "indicadores": []}
    nombre = "macro.json" if "macro" in __file__ else "indices.json"
    prev = {}
    if _os.path.exists(_os.path.join(DATA, nombre)):
        prev = {i["id"]: i for i in _json.load(open(_os.path.join(DATA, nombre), encoding="utf-8"))["indicadores"] if i.get("estado") == "ok"}
    for k, nombre, fuente, f in INDICADORES:
        try:
            r = f(); r.update({"id": k, "nombre": nombre, "fuente": fuente, "estado": "ok"})
        except Exception as e:
            r = dict(prev[k], estado="ok", aviso="Fallo al actualizar; se conserva el dato anterior: " + str(e)[:120]) if k in prev else {"id": k, "nombre": nombre, "fuente": fuente, "estado": "pendiente", "error": str(e)[:200]}
        print(k, r["estado"]); out["indicadores"].append(r)
    save("macro.json", out)

if __name__ == "__main__":
    main()
