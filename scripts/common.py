"""Utilidades comunes del Observatorio."""
import datetime, json, os, time
import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
UA = {"User-Agent": "ObservatorioCalidadPolitica/0.1 (datos abiertos; contacto en README)"}

def now_iso():
    from zoneinfo import ZoneInfo
    return datetime.datetime.now(ZoneInfo("Europe/Madrid")).isoformat(timespec="seconds")

def get(url, tries=4, timeout=120, **kw):
    last = None
    h = {**UA, **kw.pop("headers", {})}
    for i in range(tries):
        try:
            r = requests.get(url, headers=h, timeout=timeout, **kw)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa
            last = e
            time.sleep(2 * (i + 1))
    raise last

def save(name, obj):
    p = os.path.join(DATA, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("guardado", p)

# Legislaturas: fecha de sesión constitutiva del Congreso (fuente: congreso.es, "Legislaturas").
# Cada legislatura va de su sesión constitutiva a la siguiente (incluye periodo tras disolución).
LEGISLATURAS = [
    ("Constituyente", "1977-07-13", "Suárez (UCD)"),
    ("I", "1979-03-23", "Suárez / Calvo-Sotelo (UCD)"),
    ("II", "1982-11-18", "González (PSOE)"),
    ("III", "1986-07-15", "González (PSOE)"),
    ("IV", "1989-11-21", "González (PSOE)"),
    ("V", "1993-06-29", "González (PSOE)"),
    ("VI", "1996-03-27", "Aznar (PP)"),
    ("VII", "2000-04-05", "Aznar (PP)"),
    ("VIII", "2004-04-02", "Zapatero (PSOE)"),
    ("IX", "2008-04-01", "Zapatero (PSOE)"),
    ("X", "2011-12-13", "Rajoy (PP)"),
    ("XI", "2016-01-13", "Rajoy en funciones (PP)"),
    ("XII", "2016-07-19", "Rajoy (PP) / Sánchez (PSOE) desde 1-6-2018"),
    ("XIII", "2019-05-21", "Sánchez en funciones (PSOE)"),
    ("XIV", "2019-12-03", "Sánchez (PSOE-UP)"),
    ("XV", "2023-08-17", "Sánchez (PSOE-Sumar)"),
]
FIN_XV = "2026-10-06"  # disolución, RD 806/2026 (BOE-A-2026-20742)

def legislatura_de(fecha):
    """fecha 'YYYY-MM-DD' -> nombre legislatura o None."""
    if fecha < LEGISLATURAS[0][1]:
        return None
    nombre = None
    for n, ini, _ in LEGISLATURAS:
        if fecha >= ini:
            nombre = n
    return nombre
