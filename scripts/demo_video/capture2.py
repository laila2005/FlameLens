"""Capture the scenes for the narrated demo (v2) from the live site: 1920x1080 viewport at 2x pixels, plus element rects.

Usage: capture2.py <out_dir> [url]
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
URL = sys.argv[2] if len(sys.argv) > 2 else "https://flamelens-steel.vercel.app"
meta = {}
RECT_JS = """(sels) => { const o = {}; for (const [k, s] of Object.entries(sels)) {
  const e = document.querySelector(s); if (!e) { o[k] = null; continue; }
  const r = e.getBoundingClientRect(); o[k] = [r.x, r.y, r.width, r.height]; } return o; }"""


def shot(page, name, sels):
    page.wait_for_timeout(450)
    page.screenshot(path=str(OUT / f"{name}.png"))
    meta[name] = page.evaluate(RECT_JS, sels)
    print(name, json.dumps(meta[name]))


def scroll_to(page, sel, offset):
    page.evaluate("([s,o]) => { const e=document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - o); }", [sel, offset])
    page.wait_for_timeout(800)


def preset(page, pid, wait=3500):
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
    page.add_style_tag(content="html{scroll-behavior:auto!important} ::-webkit-scrollbar{display:none} .jumpbar{position:static!important}")

    top = {"rover": '.pre[data-id="pressurized-rover"]', "iss": '.pre[data-id="iss-cabin"]', "verdict": "#verdict",
           "controls": ".controls", "habitat": ".habitat", "pp": ".pp", "chip": "#datachip", "brief": "#briefbtn"}
    preset(page, "pressurized-rover")
    page.evaluate("window.scrollTo(0,0)")
    shot(page, "a_top_rover", top)

    preset(page, "iss-cabin")
    scroll_to(page, "#strengthmeter", 150)
    shot(page, "b_meter_iss", {"meter": "#strengthmeter", "conditions": "#conditions", "wholes": "#wholes", "chip": "#datachip"})

    preset(page, "pressurized-rover", 4500)
    scroll_to(page, "#evidence-case", 30)
    shot(page, "c_case_rover", {"meter": "#strengthmeter", "conditions": "#conditions", "why": ".sm-why",
                                "o2": "#conditions .cond:nth-child(1)", "psi": "#conditions .cond:nth-child(2)"})
    meta["case_text"] = page.inner_text("#conditions")[:500]

    scroll_to(page, "#verdict", 30)
    shot(page, "d_verdict_rover", {"verdict": "#verdict", "closest": "#closest"})
    scroll_to(page, ".cllimits", 60)
    shot(page, "e_limits_rover", {"limits": ".cllimits", "row1": ".cllimits .clbrows li"})
    meta["limits_text"] = page.inner_text(".cllimits")[:600]

    scroll_to(page, "#explainbox", 30)
    shot(page, "f_explain", {"explain": "#explainbox", "claim1": "#claims li", "run1": "#claims .runlink", "removed": "#removed"})
    page.click("#claims .runlink")
    page.wait_for_timeout(2000)
    shot(page, "g_drawer", {"drawer": "#drawer", "run1": "#claims .runlink"})
    page.click("#drawerclose")
    page.wait_for_timeout(400)

    scroll_to(page, "#campaign", 30)
    page.click('#cmpn [data-n="3"]'); page.wait_for_timeout(2500)
    shot(page, "h_campaign_n3", {"panel": "#campaign", "n3": '#cmpn [data-n="3"]', "list": "#cmplist", "habs": "#cmphabs", "sum": "#cmpsum"})

    scroll_to(page, "#asknasa", 30)
    page.select_option("#asksel", "PSI-25")
    page.wait_for_timeout(1500)
    page.fill("#askq", "How did airflow affect flame spread or extinction?")
    shot(page, "i_ask_q", {"panel": "#asknasa", "btn": "#askbtn", "q": "#askq"})
    page.click("#askbtn")
    page.wait_for_function("document.querySelector('#askout .askquote') || document.querySelector('#askout') && document.querySelector('#askout').innerText.includes('passages')", timeout=90000)
    page.wait_for_timeout(1500)
    scroll_to(page, "#asknasa", 30)
    shot(page, "j_ask_answer", {"panel": "#asknasa", "out": "#askout", "quote": "#askout .askquote"})
    meta["ask_text"] = page.inner_text("#askout")[:700]
    b.close()

(OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
print("done")
