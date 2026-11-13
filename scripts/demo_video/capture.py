"""Capture FlameLens live-site scenes at a 1920x1080 viewport (2x pixels) plus element rects (CSS px)."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://flamelens-steel.vercel.app"
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
meta = {}
RECT_JS = """(sels) => { const o = {}; for (const [k, s] of Object.entries(sels)) {
  const e = document.querySelector(s); if (!e) { o[k] = null; continue; }
  const r = e.getBoundingClientRect(); o[k] = [r.x, r.y, r.width, r.height]; } return o; }"""


def shot(page, name, sels):
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / f"{name}.png"))
    meta[name] = page.evaluate(RECT_JS, sels)
    print(name, json.dumps(meta[name]))


def scroll_to(page, sel, offset):
    page.evaluate("([s,o]) => { const e=document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - o); }", [sel, offset])
    page.wait_for_timeout(700)


def preset(page, pid, wait=3000):
    page.click(f'#presets .pre[data-id="{pid}"]')
    page.wait_for_timeout(wait)


with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    ctx = b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=2, color_scheme="light")
    page = ctx.new_page()
    page.set_default_timeout(90000)
    page.goto(URL, wait_until="load", timeout=120000)
    page.wait_for_function("document.getElementById('datachip').textContent.includes('real runs')", timeout=120000)
    page.wait_for_function("document.querySelectorAll('#claims li').length > 0", timeout=120000)
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(2500)
    page.add_style_tag(content="html{scroll-behavior:auto!important} ::-webkit-scrollbar{display:none}")
    top = {"rover": '.pre[data-id="pressurized-rover"]', "iss": '.pre[data-id="iss-cabin"]', "verdict": "#verdict",
           "controls": ".controls", "habitat": ".habitat", "pp": ".pp", "chip": "#datachip", "brief": "#briefbtn"}
    preset(page, "pressurized-rover")
    page.evaluate("window.scrollTo(0,0)")
    shot(page, "s1_top_rover", top)
    preset(page, "iss-cabin")
    page.evaluate("window.scrollTo(0,0)")
    shot(page, "s2_top_iss", top)
    scroll_to(page, "#strengthmeter", 150)
    shot(page, "s2_meter_iss", {"meter": "#strengthmeter", "conditions": "#conditions", "wholes": "#wholes"})
    meta["iss_meter_text"] = page.inner_text("#strengthmeter")[:300]

    preset(page, "pressurized-rover", 4000)
    scroll_to(page, "#verdict", 40)
    shot(page, "s3_closest", {"verdict": "#verdict", "closest": "#closest", "cta": "#clgo"})
    meta["closest_text"] = page.inner_text("#closest")[:600]

    scroll_to(page, "#explainbox", 40)
    shot(page, "s4_explain", {"explain": "#explainbox", "claim1": "#claims li", "run1": "#claims .runlink", "removed": "#removed"})
    page.click("#claims .runlink")
    page.wait_for_timeout(2000)
    shot(page, "s4_drawer", {"drawer": "#drawer", "run1": "#claims .runlink"})
    meta["drawer_text"] = page.inner_text("#drawer")[:600]
    page.click("#drawerclose")
    page.wait_for_timeout(400)

    scroll_to(page, "#campaign", 40)
    page.click('#cmpn [data-n="1"]'); page.wait_for_timeout(2000)
    shot(page, "s5_campaign_n1", {"panel": "#campaign", "n1": '#cmpn [data-n="1"]', "n3": '#cmpn [data-n="3"]', "list": "#cmplist", "habs": "#cmphabs"})
    page.click('#cmpn [data-n="3"]'); page.wait_for_timeout(2500)
    shot(page, "s5_campaign_n3", {"panel": "#campaign", "n3": '#cmpn [data-n="3"]', "list": "#cmplist", "habs": "#cmphabs", "sum": "#cmpsum"})
    meta["campaign_text"] = page.inner_text("#campaign")[:900]

    page.evaluate("window.scrollTo(0, 0)")
    scroll_to(page, "main.layout", 10)
    tabs = {t: f'.lenses .tab[data-lens="{t}"]' for t in ["coverage", "spread", "coolflame", "aerosol"]}
    for t in ["spread", "coolflame", "aerosol"]:
        page.click(tabs[t]); page.wait_for_timeout(1800)
        shot(page, f"s6_{t}", {**tabs, "lens": "section.lenses", "chart": "#chart"})

    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(400)
    page.click("#briefbtn"); page.wait_for_timeout(4000)
    shot(page, "s7_brief_top", {"btn": "#briefbtn", "paper": "#brief", "print": "#briefprint"})
    page.evaluate("document.getElementById('briefwrap').scrollTop = 900")
    shot(page, "s7_brief_mid", {"paper": "#brief"})
    b.close()

(OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
print("done")
