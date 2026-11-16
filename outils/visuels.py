#!/usr/bin/env python3
"""Visuels d'article pour emmanuelmichel.fr (schémas, tableaux, graphiques), style des schémas du site.
Usage : python3 visuels.py data.json sortie.webp
Types : steps | compare | bars | timeline | annotated  (voir README-visuels.md)"""
import json, sys, subprocess, html, pathlib, os, re, tempfile
from PIL import Image

FONTS = pathlib.Path(os.environ.get("EM_FONTS", pathlib.Path.home() / "em-fonts"))
need = [("jost", "400"), ("jost", "500"), ("inter-tight", "700"), ("inter-tight", "800")]
def fpath(n, w): return FONTS / "node_modules" / "@fontsource" / n / "files" / f"{n}-latin-{w}-normal.woff2"
if not all(fpath(n, w).exists() for n, w in need):
    FONTS.mkdir(parents=True, exist_ok=True)
    subprocess.run("npm init -y >/dev/null 2>&1; npm i @fontsource/jost @fontsource/inter-tight >/dev/null 2>&1", shell=True, cwd=FONTS)
fonts_ok = all(fpath(n, w).exists() for n, w in need)
face = "".join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{fpath(n, w).resolve().as_uri()}') format('woff2')}}"
               for fam, n, w in [("TitleF", "inter-tight", "800"), ("TitleF", "inter-tight", "700"),
                                 ("BodyF", "jost", "400"), ("BodyF", "jost", "500")]) if fonts_ok else ""

d = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
kind = d.get("type", "steps")

def e(s):
    s = html.escape(str(s))
    s = re.sub(r"\s+([:;!?»])", "&nbsp;\\1", s.replace("« ", "«&nbsp;"))
    s = re.sub(r"(\d) (?=\d)", "\\1&nbsp;", s)  # 3 200 reste groupé
    s = re.sub(r"(\d) (mots|Ko|Mo|€|%|h|min|jours|pages|URL)\b", "\\1&nbsp;\\2", s)
    return re.sub(r"\*(.+?)\*", r"<b>\1</b>", s)

def tags(lst, cls="tag"): return "".join(f'<span class="{cls}">{e(t)}</span>' for t in lst or [])

def head():
    sub = f'<p class="sub">{e(d["sous_titre"])}</p>' if d.get("sous_titre") else ""
    return f'<div class="pill">{e(d.get("pastille","SEO"))}</div><h1>{e(d["titre"])}</h1>{sub}'

def steps():
    items = d["items"]; n = len(items); h = ""
    for i, it in enumerate(items, 1):
        badge = f'<span class="badge">{e(it["badge"])}</span>' if it.get("badge") else ""
        txt = f'<p>{e(it["texte"])}</p>' if it.get("texte") else ""
        dark = " dark" if (i == n and n > 2 and d.get("dernier_noir", True)) else ""
        h += (f'<div class="card step"><span class="num{dark}">{i}</span><div><h3>{e(it["titre"])}{badge}</h3>{txt}'
              f'<div class="tags">{tags(it.get("tags"))}</div></div></div>')
    return h

def compare():
    cols = d["colonnes"]; hi = d.get("colonne_mise_en_avant")
    th = "".join(f'<th class="{"hi" if j == hi else ""}">{e(c)}</th>' for j, c in enumerate(cols))
    rows = ""
    for r in d["lignes"]:
        rows += "<tr>" + "".join(f'<{"th" if j == 0 else "td"} class="{"hi" if j == hi else ""}">{e(c)}</{"th" if j == 0 else "td"}>'
                                for j, c in enumerate(r)) + "</tr>"
    return f'<div class="card tbl"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>'

def bars():
    vals = [float(b["valeur"]) for b in d["barres"]]; mx = float(d.get("max", max(vals)))
    unit = d.get("unite", ""); h = ""
    for b, v in zip(d["barres"], vals):
        num = f'{int(v):,}'.replace(",", "\u202f") if v == int(v) else f'{v:g}'.replace(".", ",")
        shown = b.get("affichage") or (num + (f'\u00a0{unit}' if unit else ""))
        note = f'<p>{e(b["note"])}</p>' if b.get("note") else ""
        cls = " alt" if b.get("couleur") == "noir" else (" warn" if b.get("couleur") == "jaune" else "")
        h += (f'<div class="card bar"><div class="row"><h3>{e(b["label"])}</h3><span class="val">{e(shown)}</span></div>'
              f'<div class="track"><i class="fill{cls}" style="width:{max(2, v / mx * 100):.1f}%"></i></div>{note}</div>')
    return h

def timeline():
    h = '<div class="tl">'
    for ev in d["evenements"]:
        badge = f'<span class="badge">{e(ev["badge"])}</span>' if ev.get("badge") else ""
        txt = f'<p>{e(ev["texte"])}</p>' if ev.get("texte") else ""
        h += (f'<div class="ev"><span class="dot"></span><div class="card"><span class="date">{e(ev["date"])}</span>'
              f'<h3>{e(ev["titre"])}{badge}</h3>{txt}<div class="tags">{tags(ev.get("tags"))}</div></div></div>')
    return h + "</div>"

def annotated():
    w = d["fenetre"]; dark = w.get("style", "clair") == "sombre"
    lines = ""
    for l in w["lignes"]:
        mark = f'<span class="rep">{l["repere"]}</span>' if l.get("repere") else ""
        cls = "ln hl" if l.get("surligne") else "ln"
        lines += f'<div class="{cls}"><span>{e(l["texte"])}</span>{mark}</div>'
    win = (f'<div class="card win{" dk" if dark else ""}"><div class="wh">{e(w.get("titre",""))}</div>{lines}'
           f'<div class="tags">{tags(w.get("puces"), "chip")}</div></div>')
    cards = "".join(f'<div class="card step"><span class="num">{r["n"]}</span><div><h3>{e(r["titre"])}</h3>'
                    f'<p>{e(r.get("texte",""))}</p></div></div>' for r in d["reperes"])
    return win + cards

body = {"steps": steps, "compare": compare, "bars": bars, "timeline": timeline, "annotated": annotated}[kind]()
foot = f'<div class="foot"><span>{e(d["source"]) if d.get("source") else ""}</span><span>emmanuelmichel.fr</span></div>'
H = "'TitleF','Inter Tight','Inter',sans-serif"; B = "'BodyF','Jost','Inter',sans-serif"
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{face}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#e8eeec}}
body{{width:450px;padding:22px 20px 14px;font:400 18px/1.32 {B};color:#1c2b26;
background-image:radial-gradient(circle,rgba(47,107,87,.08) 1.1px,transparent 1.3px);background-size:22px 22px}}
.pill{{display:inline-block;height:32px;padding:0 15px;border-radius:999px;background:#2f6b57;color:#fff;font:700 16px/32px {H}}}
h1{{font:800 29px/1.13 {H};letter-spacing:-.012em;color:#111;margin:16px 0 6px;text-wrap:balance}}
.sub{{font:400 17px/1.3 {B};color:#40524c;margin-bottom:14px}}
.card{{background:#fff;border-radius:16px;box-shadow:0 8px 22px rgba(20,45,38,.09),0 1px 3px rgba(20,45,38,.06);padding:14px 16px;margin-bottom:11px}}
h3{{font:800 20px/1.18 {H};letter-spacing:-.008em;color:#111}}
.card p{{font:400 18px/1.3 {B};color:#40524c;margin-top:5px}} .card p b,td b{{font-weight:500;color:#111}}
.step{{display:flex;gap:12px;align-items:flex-start}}
.num{{flex:0 0 32px;height:32px;border-radius:9px;background:#2f6b57;color:#fff;font:800 17px/32px {H};text-align:center}}
.num.dark{{background:#111}}
.badge{{display:inline-block;margin-left:9px;padding:2px 9px;border-radius:999px;background:#f5b82e;color:#2b2208;font:700 14px/20px {H};vertical-align:2px;white-space:nowrap}}
.tags{{display:flex;gap:7px;flex-wrap:wrap}} .tags:not(:empty){{margin-top:9px}}
.tag{{padding:2px 10px;border-radius:8px;background:#f2fefc;border:1px solid #cfe6de;font:500 15px/20px {B};color:#1c2b26}}
.chip{{padding:5px 11px;border-radius:8px;background:#2b2b2b;color:#a8c2b9;font:500 15px {B}}}
.tbl{{padding:0;overflow:hidden}} table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:11px 12px;border-top:1px solid #e8eeec;font:400 17px/1.25 {B};vertical-align:top}}
thead th{{background:#2f6557;color:#fff;font:700 16px/1.2 {H};border-top:0}} thead th.hi{{background:#111}}
tbody th{{font:800 17px/1.25 {H};color:#111;width:34%}} td.hi{{background:#f2fefc;font-weight:500;color:#111}}
.bar .row{{display:flex;justify-content:space-between;align-items:baseline;gap:12px}}
.val{{font:800 20px {H};color:#2f6b57;white-space:nowrap}}
.track{{height:14px;border-radius:8px;background:#e4ebe8;margin-top:9px;overflow:hidden}}
.fill{{display:block;height:100%;border-radius:7px;background:#2f6b57}} .fill.alt{{background:#111}} .fill.warn{{background:#f5b82e}}
.tl{{position:relative;padding-left:26px}} .tl:before{{content:"";position:absolute;left:7px;top:10px;bottom:20px;width:2px;background:#bfd3cb}}
.ev{{position:relative}} .dot{{position:absolute;left:-26px;top:16px;width:16px;height:16px;border-radius:50%;background:#2f6b57;border:3px solid #e8eeec}}
.date{{display:block;font:700 14px/1 {H};color:#2f6b57;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px}}
.win{{padding:0;overflow:hidden}} .wh{{background:#f4f8f7;padding:11px 16px;font:700 16px {H};color:#2f6b57;border-bottom:1px solid #e8eeec}}
.ln{{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 16px;border-top:1px solid #f0f4f2;font:400 18px/1.3 {B}}}
.ln.hl{{background:#f2fefc}} .ln.hl span:first-child{{font-weight:500;color:#111}}
.rep{{flex:0 0 28px;height:28px;border-radius:50%;background:#2f6b57;color:#fff;font:800 15px/28px {H};text-align:center}}
.win .tags{{padding:0 16px 14px}} .win .tags:empty{{display:none}}
.win.dk{{background:#111}} .dk .wh{{background:#1b1b1b;color:#a8e6cf;border-color:#2b2b2b}} .dk .ln{{border-color:#242424;color:#e6efeb}}
.dk .ln.hl{{background:#1f2a26}} .dk .ln.hl span:first-child{{color:#f5b82e}}
.foot{{display:flex;justify-content:space-between;gap:12px;margin-top:4px;font:400 14px/1.3 {B};color:#6c807a}}
.foot span:last-child{{white-space:nowrap}}
</style></head><body><div id="c">{head()}{body}{foot}</div>
<script>document.fonts.ready.then(()=>{{document.body.dataset.h=Math.ceil(document.querySelector('.foot').getBoundingClientRect().bottom+16)}})</script></body></html>"""

tmp = pathlib.Path(tempfile.mkdtemp()); f = tmp / "v.html"; f.write_text(page, encoding="utf-8")
chrome = ["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=3"]
dom = subprocess.run(chrome + ["--window-size=450,900", "--virtual-time-budget=4000", "--dump-dom", f.as_uri()],
                     capture_output=True, text=True, check=True).stdout
hgt = int(re.search(r'data-h="(\d+)"', dom).group(1))
png = tmp / "v.png"
subprocess.run(chrome + [f"--window-size=450,{hgt}", f"--screenshot={png}", f.as_uri()], check=True, capture_output=True)
im = Image.open(png).convert("RGB"); assert im.width == 1350, im.size
im.save(out, "WEBP", quality=88, method=6); im.save(pathlib.Path(out).with_suffix(".preview.png"))
# Aperçu à la taille réelle d'un téléphone (300 px de large) : le texte doit y rester lisible
im.resize((300, round(im.height * 300 / im.width)), Image.LANCZOS).save(pathlib.Path(out).with_suffix(".mobile.png"))
print(out, im.size, pathlib.Path(out).stat().st_size, "octets", "fonts_ok=", fonts_ok)
