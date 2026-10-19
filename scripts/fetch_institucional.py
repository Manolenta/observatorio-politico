"""Cuadro 3 (ampliación): indicadores institucionales a partir del BOE y del Congreso.
- Años con Presupuestos Generales del Estado prorrogados (BOE: leyes de PGE).
- Días de Gobierno en funciones tras elecciones (BOE: RD de disolución -> fecha de elecciones; RD de nombramiento del Presidente).
- Retraso en la renovación del CGPJ (BOE: RD de nombramiento de Vocales).
- RDL tramitados como proyecto de ley en la XV Legislatura (datos abiertos del Congreso).
- TC: pendiente (ver motivo).
Los resultados de documentos inmutables (fechas de elecciones extraídas del texto o PDF del BOE) se guardan en caché
dentro de data/institucional.json para no tener que releer PDFs antiguos en cada ejecución.
"""
import re, html, json, os, datetime, subprocess, tempfile
from common import get, save, now_iso, DATA, legislatura_de
from fetch_boe import url_busqueda, resultados, MESES

OUT = os.path.join(DATA, "institucional.json")
NUM = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
       "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "dieciséis": 16, "diecisiete": 17, "dieciocho": 18,
       "diecinueve": 19, "veinte": 20, "veintiuno": 21, "veintidós": 22, "veintitrés": 23, "veinticuatro": 24, "veinticinco": 25,
       "veintiséis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29, "treinta": 30, "treinta y uno": 31}
DEC = {"setenta": 70, "ochenta": 80, "noventa": 90}

def año_palabras(s):
    m = re.match(r"mil novecientos (setenta|ochenta|noventa)(?: y (\w+))?", s)
    return 1900 + DEC[m.group(1)] + (NUM.get(m.group(2), 0) if m.group(2) else 0) if m else None

def texto_boe(ref, forzar_pdf=False):
    s = get(f"https://www.boe.es/diario_boe/txt.php?id={ref}").text
    m = re.search(r'<div id="textoxslt">(.*?)</div>\s*</div>', s, re.S)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))) if m else ""
    if forzar_pdf or "Texto no disponible" in t or len(t) < 200:  # documento antiguo: solo PDF
        d = get(f"https://www.boe.es/buscar/doc.php?id={ref}").text
        p = re.search(r'href="(/boe/dias/[^"]+\.pdf)"', d)
        if p:
            with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                f.write(get("https://www.boe.es" + p.group(1)).content); f.flush()
                t = re.sub(r"\s+", " ", subprocess.run(["pdftotext", f.name, "-"], capture_output=True, text=True).stdout)
    return t

def fecha_elecciones(t, año_rd):
    m = re.search(r"celebrar[áa]n el (?:día )?(?:domingo )?(\d{1,2}|[a-zéíú]+(?: y uno)?) de (\w+)(?: de (\d{4}|mil novecientos [a-z ]+?)(?:[.,]| Art))?", t)
    if not m or m.group(2) not in MESES:
        return None
    d = int(m.group(1)) if m.group(1).isdigit() else NUM.get(m.group(1))
    y = m.group(3)
    y = int(y) if y and y.isdigit() else (año_palabras(y.strip()) if y else None)
    if y is None:  # sin año explícito: el del RD, o el siguiente si el mes es anterior
        y = año_rd
    return f"{y}-{MESES[m.group(2)]:02d}-{d:02d}" if d else None

def presupuestos():
    u = url_busqueda(1, '"Presupuestos Generales del Estado para"', "1977-01-01", f"{datetime.date.today().year}-12-31")
    _, res = resultados(u)
    leyes = {}
    for r in res:
        m = re.match(r"^Ley (\d+/\d{4}), de (\d+) de (\w+), de Presupuestos Generales del Estado para (?:el (?:año|ejercicio) (?:de )?)?(\d{4})\.?$", r["titulo"])
        if m and r["dem"] == "Jefatura del Estado":
            y = int(m.group(4)); pub = datetime.datetime.strptime(r["pub"], "%d/%m/%Y").date().isoformat()
            leyes.setdefault(y, {"ley": "Ley " + m.group(1), "ref": r["ref"], "publicada": pub, "url": f"https://www.boe.es/buscar/doc.php?id={r['ref']}"})
    filas = []
    for y in range(1978, datetime.date.today().year + 1):
        l = leyes.get(y)
        if l:
            estado = "aprobados en plazo" if l["publicada"] <= f"{y}-01-01" else "prórroga parcial: ley publicada después del 1 de enero"
        else:
            estado = "prorrogados todo el año"
        filas.append({"año": y, "estado": estado, "legislatura": legislatura_de(f"{y}-01-01"), **(l or {})})
    return {"consulta": u, "años": filas}

def funciones(cache):
    elecciones = []
    for q in ('"disolución del Congreso"', '"disolución de las Cortes"'):
        u = url_busqueda(1, q, "1977-01-01", f"{datetime.date.today().year}-12-31")
        for r in resultados(u)[1]:
            if r["dem"] == "Jefatura del Estado" and r["titulo"].startswith("Real Decreto"):
                c = cache.get(r["ref"])
                if not c:
                    año_rd = int(re.search(r"/(\d{4}),", r["titulo"]).group(1))
                    f = fecha_elecciones(texto_boe(r["ref"]), año_rd) or fecha_elecciones(texto_boe(r["ref"], True), año_rd)
                    c = {"ref": r["ref"], "rd": r["titulo"].split(",")[0], "elecciones": f}
                    if f: cache[r["ref"]] = c
                elecciones.append(c)
    elecciones = sorted({e["ref"]: e for e in elecciones}.values(), key=lambda e: e["elecciones"] or "")
    u = url_busqueda(2, '"nombra Presidente del Gobierno"', "1977-01-01", f"{datetime.date.today().year}-12-31")
    nombr = []
    for r in resultados(u)[1]:
        m = re.match(r"^Real Decreto (\d+/\d{4}), de (\d+) de (\w+), por el que se nombra Presidente del Gobierno a (.+?)\.$", r["titulo"])
        if m:
            y = int(m.group(1).split("/")[1])
            nombr.append({"fecha": f"{y}-{MESES[m.group(3)]:02d}-{int(m.group(2)):02d}", "presidente": m.group(4), "ref": r["ref"], "rd": "Real Decreto " + m.group(1)})
    nombr.sort(key=lambda x: x["fecha"])
    periodos, hoy = [], datetime.date.today().isoformat()
    i = 0
    validas = [e for e in elecciones if e["elecciones"]]
    while i < len(validas):
        e = validas[i]
        if e["elecciones"] > hoy:
            break
        n = next((x for x in nombr if x["fecha"] > e["elecciones"]), None)
        grupo = [e]
        while n and i + 1 < len(validas) and validas[i + 1]["elecciones"] < n["fecha"]:  # repetición electoral sin investidura
            i += 1; grupo.append(validas[i])
        fin = n["fecha"] if n else hoy
        dias = (datetime.date.fromisoformat(fin) - datetime.date.fromisoformat(e["elecciones"])).days
        periodos.append({"desde_elecciones": e["elecciones"], "elecciones": [g["elecciones"] for g in grupo],
                         "rd_convocatoria": [{"rd": g["rd"], "url": f"https://www.boe.es/buscar/doc.php?id={g['ref']}"} for g in grupo],
                         "hasta_nombramiento": fin, "nombramiento": n and {"rd": n["rd"], "presidente": n["presidente"], "url": f"https://www.boe.es/buscar/doc.php?id={n['ref']}"},
                         "dias": dias, "en_curso": n is None})
        i += 1
    sin_fecha = [e["rd"] for e in elecciones if not e["elecciones"]]
    return {"periodos": periodos, "no_parseados": sin_fecha,
            "nota": "Días entre la jornada electoral (según el RD de convocatoria) y el RD de nombramiento del Presidente. No incluye la etapa en funciones tras una dimisión (1981) ni la moción de censura (2018, sin periodo en funciones)."}

# Renovaciones COMPLETAS del CGPJ (dos RD, Congreso y Senado, el mismo día). En 1989 y 1994 hubo
# nombramientos parciales por sustitución (el PDF del BOE nombra solo a algunos vocales), que no inician mandato nuevo.
PARCIALES_CGPJ = {"1989", "1994"}

def cgpj():
    u = url_busqueda(2, '"Vocales del Consejo General del Poder Judicial"', "1977-01-01", f"{datetime.date.today().year}-12-31")
    por_fecha = {}
    for r in resultados(u)[1]:
        m = re.match(r"^Real Decreto (\d+/\d{4}), de (\d+) de (\w+), por el que se nombran? Vocales del Consejo General del Poder Judicial,? a propuesta del (Congreso|Senado)", r["titulo"])
        if m:
            y = m.group(1).split("/")[1]
            f = f"{y}-{MESES[m.group(3)]:02d}-{int(m.group(2)):02d}"
            por_fecha.setdefault(f, []).append({"rd": "Real Decreto " + m.group(1), "camara": m.group(4), "url": f"https://www.boe.es/buscar/doc.php?id={r['ref']}"})
    completas = [(f, v) for f, v in sorted(por_fecha.items()) if {x["camara"] for x in v} == {"Congreso", "Senado"} and f[:4] not in PARCIALES_CGPJ]
    filas = []
    for k, (f, v) in enumerate(completas):
        fila = {"renovacion": f, "rds": v}
        if k > 0:
            prev = datetime.date.fromisoformat(completas[k - 1][0])
            vence = prev.replace(year=prev.year + 5)
            fila.update({"mandato_anterior_vence_aprox": vence.isoformat(), "dias_retraso_aprox": (datetime.date.fromisoformat(f) - vence).days})
        filas.append(fila)
    return {"consulta": u, "renovaciones": filas,
            "nota": "Mandato de 5 años (art. 568 LOPJ). Se aproxima con la fecha del RD de nombramiento; la constitución del Consejo es unos días posterior, así que el retraso real puede variar en ±10 días. La primera renovación de la serie (1985) es la primera con la LOPJ de 1985; el CGPJ de 1980 no figura con este título en el buscador."}

def rdl_proyecto_xv():
    page = get("https://www.congreso.es/es/opendata/iniciativas", headers={"User-Agent": "Mozilla/5.0 (Observatorio)"}).text
    m = re.search(r'href="(/webpublica/opendata/iniciativas/ProyectosDeLey__\d+\.json)"', page)
    url = "https://www.congreso.es" + m.group(1)
    d = get(url, headers={"User-Agent": "Mozilla/5.0 (Observatorio)"}).json()
    items = []
    for i in d:
        o = re.sub(r"\s+", " ", i.get("OBJETO") or "")
        mm = re.search(r"procedente del Real Decreto-ley (\d+/\d{4})", o)
        if mm:
            items.append({"expediente": i.get("NUMEXPEDIENTE"), "rdl": "Real Decreto-ley " + mm.group(1), "situacion": i.get("SITUACIONACTUAL"),
                          "resultado": (i.get("RESULTADOTRAMITACION") or "").split("\n")[0].strip()})
    leyes = sum(1 for x in items if x["resultado"].lower().startswith("aprobado"))
    return {"legislatura": sorted({i.get("LEGISLATURA") for i in d}), "fuente": url, "web": "https://www.congreso.es/es/opendata/iniciativas",
            "tramitados_como_proyecto": len(items), "terminados_como_ley": leyes,
            "caducados": sum(1 for x in items if "Caducado" in (x["situacion"] or "")), "detalle": items,
            "nota": "Los datos abiertos del Congreso solo cubren la legislatura en curso. Para legislaturas anteriores queda pendiente: los acuerdos de convalidación del BOE no indican si se acordó tramitar el RDL como proyecto de ley."}

def main():
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    cache = prev.get("cache_elecciones", {})
    out = {"extraido": now_iso(), "fuente": "https://www.boe.es/buscar/boe.php"}
    for k, f in (("presupuestos", presupuestos), ("cgpj", cgpj), ("rdl_proyecto_xv", rdl_proyecto_xv)):
        try:
            out[k] = f()
        except Exception as e:
            out[k] = dict(prev.get(k, {}), aviso=f"Fallo al actualizar; dato anterior: {str(e)[:120]}") if k in prev else {"estado": "pendiente", "error": str(e)[:200]}
    try:
        out["funciones"] = funciones(cache)
    except Exception as e:
        out["funciones"] = dict(prev.get("funciones", {}), aviso=str(e)[:120]) if "funciones" in prev else {"estado": "pendiente", "error": str(e)[:200]}
    out["tc"] = {"estado": "pendiente", "motivo": "El TC se renueva por tercios (Congreso, Senado, Gobierno y CGPJ) con mandatos de 9 años y sustituciones por vacantes; para calcular el retraso de cada tercio hay que asignar cada magistrado a su tercio y órgano proponente, dato que solo figura en el texto o PDF de cada RD. No se publica hasta tener una codificación verificada.",
                 "consulta": url_busqueda(2, '"Magistrado del Tribunal Constitucional"', "1977-01-01", "2026-12-31")}
    out["cache_elecciones"] = cache
    save("institucional.json", out)

if __name__ == "__main__":
    main()
