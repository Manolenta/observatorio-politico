"""Cuadro 4: Repositorio de datos sobre procesos por corrupción del CGPJ (resumen nacional trimestral).
https://www.poderjudicial.es/cgpj/es/Temas/Transparencia/Repositorio-de-datos-sobre-procesos-por-corrupcion/
Se extrae, por trimestre: personas acusadas/procesadas (auto de apertura de juicio oral o procesamiento),
nº de procedimientos, y forma de terminación (condenatorias con/sin conformidad, parcialmente condenatorias,
absolutorias, 'por otras causas' = resoluciones que terminan el asunto sin sentencia, p.ej. sobreseimiento/prescripción;
el repositorio NO desglosa el motivo)."""
import re, html, datetime, sys
from common import get, save, now_iso

URL = "https://www.poderjudicial.es/cgpj/es/Temas/Transparencia/Repositorio-de-datos-sobre-procesos-por-corrupcion/ch.Consulta-de-datos.formato1/?anio={a}&tipo=RN&trimestre={t}"

def texto(u):
    s = get(u, headers={"User-Agent": "Mozilla/5.0 (Observatorio)"}).text
    s = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))

def trimestre(a, t):
    u = URL.format(a=a, t=t); s = texto(u)
    i = s.find("PERSONAS Y PROCEDIMENTOS")
    if i < 0:
        return None
    s = s[i: s.find("Compartir", i)]
    m = re.search(r"CC\.AA\. (?:\d+ ){7}\d+ Total ((?:\d+ ){7}\d+)", s)
    sent = re.findall(r"Total (\d+) (\d+) (\d+) (\d+) (\d+)", s)
    if not m or not sent:
        return None
    p = [int(x) for x in m.group(1).split()]
    c = [int(x) for x in sent[-1]]
    return {"año": a, "trimestre": t, "url": u, "personas_fisicas": sum(p[:6]), "personas_juridicas": p[6],
            "procedimientos": p[7], "cond_conformidad": c[0], "cond_sin_conformidad": c[1], "parc_condenatorias": c[2],
            "absolutorias": c[3], "otras_causas": c[4]}

def main(a0=2013):
    filas = []
    for a in range(a0, datetime.date.today().year + 1):
        for t in range(1, 5):
            try:
                r = trimestre(a, t)
            except Exception as e:
                print("error", a, t, e, file=sys.stderr); r = None
            if r and (r["personas_fisicas"] + r["procedimientos"] + r["absolutorias"] + r["cond_conformidad"] > 0 or a >= 2015):
                filas.append(r); print(a, t, r["personas_fisicas"], r["cond_conformidad"] + r["cond_sin_conformidad"] + r["parc_condenatorias"], r["absolutorias"], flush=True)
    anual = {}
    for r in filas:
        x = anual.setdefault(r["año"], {"trimestres": 0})
        x["trimestres"] += 1
        for k in ("personas_fisicas", "personas_juridicas", "procedimientos", "cond_conformidad", "cond_sin_conformidad", "parc_condenatorias", "absolutorias", "otras_causas"):
            x[k] = x.get(k, 0) + r[k]
    save("cgpj_corrupcion.json", {"extraido": now_iso(), "fuente": "https://www.poderjudicial.es/cgpj/es/Temas/Transparencia/Repositorio-de-datos-sobre-procesos-por-corrupcion/",
          "nota": "Suma de los cuatro trimestres del 'Resumen nacional'. Solo corrupción pública (cargos y funcionarios con afectación de dinero público). Años incompletos marcados por nº de trimestres.",
          "trimestral": filas, "anual": anual})

if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:]))
