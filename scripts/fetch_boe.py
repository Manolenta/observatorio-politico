"""Cuenta en el BOE (Sección I y III) leyes, leyes orgánicas, reales decretos-leyes,
RDL derogados (no convalidados) por el Congreso e indultos, por año y legislatura.
Fuente: buscador oficial https://www.boe.es/buscar/boe.php (consulta por título y fecha de publicación).
"""
import re, html, datetime, urllib.parse, sys
from collections import Counter, defaultdict
from common import get, save, now_iso, legislatura_de, LEGISLATURAS, FIN_XV

MESES = {m: i + 1 for i, m in enumerate("enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split())}
SEARCH = "https://www.boe.es/buscar/boe.php"

def url_busqueda(seccion, titulo, desde, hasta):
    p = [("campo[0]", "ORIS"), (f"dato[0][{seccion}]", str(seccion)), ("operador[0]", "and"),
         ("campo[1]", "TITULOS"), ("dato[1]", titulo), ("operador[1]", "and"),
         ("operador[6]", "and"), ("campo[6]", "FPU"), ("dato[6][0]", desde), ("dato[6][1]", hasta),
         ("page_hits", "2000"), ("sort_field[0]", "FPU"), ("sort_order[0]", "asc"), ("accion", "Buscar")]
    return SEARCH + "?" + urllib.parse.urlencode(p)

def resultados(url):
    s = get(url).text
    m = re.search(r"Resultados 1 a ([\d.]+) de ([\d.]+)", s)
    total = int(m.group(2).replace(".", "")) if m else 0
    mostrados = int(m.group(1).replace(".", "")) if m else 0
    out = []
    for b in s.split('class="resultado-busqueda"')[1:]:
        dem = re.search(r'class="linea-dem">(.*?)</p>', b, re.S)
        tit = re.search(r'<p>(.*?)</p>', b.split('linea-pub')[1] if 'linea-pub' in b else b, re.S)
        ref = re.search(r'id=(BOE-[A-Z]-\d{4}-\d+)', b)
        pub = re.search(r'de (\d\d/\d\d/\d{4})', b)
        out.append({"dem": html.unescape(dem.group(1).strip()) if dem else "",
                    "titulo": html.unescape(re.sub(r"\s+", " ", tit.group(1)).strip()) if tit else "",
                    "ref": ref.group(1) if ref else "", "pub": pub.group(1) if pub else ""})
    if mostrados < total:
        print(f"AVISO: truncado {mostrados}/{total} en {url}", file=sys.stderr)
    return total, out

RX_NORMA = re.compile(r"^(Ley Orgánica|Ley|Real Decreto-ley) (\d+)/(\d{4}), de (\d+) de ([a-z]+)")
RX_DEROG = re.compile(r"acuerdo de derogaci[oó]n del Real Decreto-ley (\d+)/(\d{4}), de (\d+) de ([a-z]+)", re.I)
RX_CONVAL = re.compile(r"acuerdo de convalidaci[oó]n del Real Decreto-ley (\d+)/(\d{4}), de (\d+) de ([a-z]+)", re.I)

def main(y0=1977, y1=None):
    y1 = y1 or datetime.date.today().year
    normas, derogados, convalidados, indultos, consultas = {}, {}, {}, [], []
    for y in range(y0, y1 + 1):
        u = url_busqueda(1, "ley", f"{y}-01-01", f"{y}-12-31")
        tot, res = resultados(u); consultas.append({"año": y, "tipo": "normas", "url": u, "resultados": tot})
        for r in res:
            t = r["titulo"]
            m = RX_NORMA.match(t)
            if m and r["dem"] == "Jefatura del Estado":
                tipo, num, anio, d, mes = m.groups()
                if mes not in MESES: continue
                fecha = f"{anio}-{MESES[mes]:02d}-{int(d):02d}"
                key = f"{tipo} {num}/{anio}"
                normas.setdefault(key, {"tipo": tipo, "num": int(num), "fecha": fecha, "ref": r["ref"], "titulo": t[:200]})
            m3 = RX_CONVAL.search(t)
            if m3 and m3.group(4) in MESES:
                num, anio, d, mes = m3.groups()
                convalidados[f"Real Decreto-ley {num}/{anio}"] = {"fecha": f"{anio}-{MESES[mes]:02d}-{int(d):02d}", "ref_acuerdo": r["ref"]}
            m2 = RX_DEROG.search(t)
            if m2:
                num, anio, d, mes = m2.groups()
                if mes in MESES:
                    derogados[f"Real Decreto-ley {num}/{anio}"] = {"fecha": f"{anio}-{MESES[mes]:02d}-{int(d):02d}", "ref_acuerdo": r["ref"]}
        ui = url_busqueda(3, '"se indulta"', f"{y}-01-01", f"{y}-12-31")
        tot_i, res_i = resultados(ui); consultas.append({"año": y, "tipo": "indultos", "url": ui, "resultados": tot_i})
        n_ind = sum(1 for r in res_i if "se indulta" in r["titulo"] and r["titulo"].startswith("Real Decreto"))
        indultos.append({"año": y, "indultos": n_ind})
        print(y, len(normas), n_ind, flush=True)
    # Complemento: API de legislación consolidada (rellena huecos de títulos con formato atípico)
    for codigo, tipo in (("1290", "Ley Orgánica"), ("1300", "Ley"), ("1320", "Real Decreto-ley")):
        try:
            q = urllib.parse.quote('{"query":{"query_string":{"query":"rango@codigo:%s"}}}' % codigo)
            api = get(f"https://www.boe.es/datosabiertos/api/legislacion-consolidada?limit=-1&query={q}", headers={"Accept": "application/json"}).json()["data"]
            for x in api:
                x["departamento"] = x.get("departamento") or {"texto": ""}
                if x["ambito"]["codigo"] != "1" or x["departamento"]["texto"] != "Jefatura del Estado" or "/" not in (x.get("numero_oficial") or ""):
                    continue
                f = x["fecha_disposicion"]; fecha = f"{f[:4]}-{f[4:6]}-{f[6:8]}"
                key = f"{tipo} {int(x['numero_oficial'].split('/')[0])}/{x['numero_oficial'].split('/')[1]}"
                if key not in normas:
                    normas[key] = {"tipo": tipo, "num": int(x["numero_oficial"].split("/")[0]), "fecha": fecha, "ref": x["identificador"], "titulo": x["titulo"][:200], "via": "api_consolidada"}
        except Exception as e:
            print("AVISO API consolidada:", e, file=sys.stderr)
    # agregados
    por_anio = defaultdict(Counter); por_leg = defaultdict(Counter)
    for k, v in normas.items():
        if v["fecha"] < LEGISLATURAS[0][1]: continue
        por_anio[v["fecha"][:4]][v["tipo"]] += 1
        por_leg[legislatura_de(v["fecha"])][v["tipo"]] += 1
    for k, v in derogados.items():
        if LEGISLATURAS[0][1] <= v["fecha"]:
            por_leg[legislatura_de(v["fecha"])]["RDL derogados"] += 1
            por_anio[v["fecha"][:4]]["RDL derogados"] += 1
    for k, v in convalidados.items():
        if LEGISLATURAS[0][1] <= v["fecha"]:
            por_leg[legislatura_de(v["fecha"])]["RDL convalidados"] += 1
    leg_rows = []
    for i, (n, ini, gob) in enumerate(LEGISLATURAS):
        fin = LEGISLATURAS[i + 1][1] if i + 1 < len(LEGISLATURAS) else datetime.date.today().isoformat()
        dias = (datetime.date.fromisoformat(fin) - datetime.date.fromisoformat(ini)).days
        c = por_leg[n]; leyes = c["Ley"] + c["Ley Orgánica"]
        leg_rows.append({"legislatura": n, "inicio": ini, "fin": fin, "gobierno": gob, "años": round(dias / 365.25, 2),
                         "leyes_ordinarias": c["Ley"], "leyes_organicas": c["Ley Orgánica"], "rdl": c["Real Decreto-ley"],
                         "rdl_derogados": c["RDL derogados"], "rdl_convalidados_publicados": c["RDL convalidados"],
                         "rdl_por_año": round(c["Real Decreto-ley"] / (dias / 365.25), 1),
                         "leyes_por_año": round(leyes / (dias / 365.25), 1),
                         "ratio_rdl_leyes": round(c["Real Decreto-ley"] / leyes, 2) if leyes else None})
    save("boe_normas.json", {"extraido": now_iso(), "fuente": SEARCH,
        "nota": "Normas de la Jefatura del Estado en Sección I del BOE cuyo título empieza por 'Ley', 'Ley Orgánica' o 'Real Decreto-ley'; asignadas por fecha de la disposición. RDL derogados = 'Acuerdo de derogación' publicado por el Congreso (no convalidados).",
        "por_legislatura": leg_rows, "por_año": {k: dict(v) for k, v in sorted(por_anio.items())},
        "indultos_por_año": indultos, "consultas": consultas, "normas": normas, "rdl_derogados": derogados, "rdl_convalidados": convalidados,
        "nota_xv": f"La XV Legislatura se cuenta hasta hoy: Cortes disueltas el {FIN_XV} (RD 806/2026); siguen publicándose normas aprobadas antes de la disolución y RDL que convalida la Diputación Permanente."})

if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:]))
