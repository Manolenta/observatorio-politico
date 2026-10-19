"""Genera capturas PNG del sitio servido localmente (python3 -m http.server 8765 dentro de site/).
Uso: .venv/bin/python scripts/capturas.py [url]"""
import sys, os
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/index.html"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "capturas")
os.makedirs(OUT, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1400, "height": 900}, device_scale_factor=1)
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(1500)
    pg.screenshot(path=f"{OUT}/pagina_completa.png", full_page=True)
    for sid, name in [("c1", "1_macro"), ("c2", "2_promesas"), ("c3", "3_calidad_democratica"), ("c4", "4_corrupcion")]:
        pg.locator(f"#{sid}").screenshot(path=f"{OUT}/{name}.png")
    pg.locator("header").screenshot(path=f"{OUT}/0_cabecera.png")
    errs = []
    b.close()
print("capturas en", OUT)
