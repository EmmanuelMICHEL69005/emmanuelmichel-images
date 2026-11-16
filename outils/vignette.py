import json, sys, subprocess, html, pathlib, os, re
from PIL import Image

# ---- Polices (Inter Tight pour le titre, Jost pour le pied de page) -------------
FONTS = pathlib.Path(os.environ.get("EM_FONTS", pathlib.Path.home() / "em-fonts"))
need = [("jost", "500"), ("inter-tight", "700"), ("inter-tight", "800")]
def fpath(name, w):
    return FONTS / "node_modules" / "@fontsource" / name / "files" / f"{name}-latin-{w}-normal.woff2"
if not all(fpath(n, w).exists() for n, w in need):
    FONTS.mkdir(parents=True, exist_ok=True)
    subprocess.run("npm init -y >/dev/null 2>&1; npm i @fontsource/jost @fontsource/inter-tight >/dev/null 2>&1",
                   shell=True, cwd=FONTS)
ok_fonts = all(fpath(n, w).exists() for n, w in need)
face = "".join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('{fpath(n, w).resolve().as_uri()}') format('woff2')}}"
    for fam, n, w in [("TitleF", "inter-tight", "800"), ("TitleF", "inter-tight", "700"), ("FootF", "jost", "500")]
) if ok_fonts else ""
TITLE_FONT = "'TitleF','Inter Display','Inter',sans-serif"
FOOT_FONT = "'FootF','Jost','Inter',sans-serif"

d = json.load(open(sys.argv[1])); out = sys.argv[2]
e = html.escape
mode = d.get("mode", "table")
cat = d["categorie"]

def bar(w, c="#d4dfdb", h=12):
    return f'<i class="bar" style="width:{w}px;height:{h}px;background:{c}"></i>'

def card_table():
    rows = ""
    pats = [(70, 96, 40), (80, 46, 56), (86, 56, 50), (50, 44, 70), (40, 64, 74)]
    for i, (a, b, c) in enumerate(pats, 1):
        rows += (f'<div class="tr"><span class="n">{i}</span><span class="td">{bar(a,"#d4dfdb")}</span>'
                 f'<span class="td">{bar(b,"#d4dfdb" if i%2 else "#e4ebe8")}</span>'
                 f'<span class="td">{bar(c,"#e4ebe8" if i%2 else "#d4dfdb")}</span></div>')
    return (f'<div class="card light"><div class="head"><span class="doc"></span>{e(d.get("header","donnees.csv"))}</div>'
            f'<div class="tr hd"><span class="n"></span><span class="td">A</span><span class="td">B</span><span class="td">C</span></div>{rows}</div>')

def card_serp():
    return (f'<div class="card light serp"><div class="search"><span class="ring"></span>{bar(190,"#d4dfdb",10)}</div>'
            f'<div class="hit"><div>{bar(80,"#cfe0da",9)}</div><b>{e(d.get("highlight","Votre page en 1re position"))}</b>{bar(200,"#e4ebe8",9)}</div>'
            f'<div class="res">{bar(240,"#d4dfdb",10)}{bar(290,"#e4ebe8",10)}</div>'
            f'<div class="res">{bar(200,"#d4dfdb",10)}{bar(230,"#e4ebe8",10)}</div></div>')

def card_ai():
    txt = e(d.get("ai_text", "D'après *votre site*, la réponse est…"))
    txt = re.sub(r"\*(.+?)\*", r'<mark>\1</mark>', txt)
    chips = "".join(f'<span class="chip">{e(c)}</span>' for c in d.get("chips", ["Source 1", "Source 2"])[:3])
    return (f'<div class="card dark"><div class="ah"><span class="ic">✦</span>{e(d.get("header","Assistant IA"))}</div>'
            f'<div class="ln" style="width:100%"></div><div class="ln" style="width:84%"></div>'
            f'<p>{txt}</p><div class="chips">{chips}</div></div>')

card = {"table": card_table, "serp": card_serp, "ai": card_ai}[mode]()
title = re.sub(r"\s+([:;!?»])", "&nbsp;\\1", e(d["titre"]).replace("« ", "«&nbsp;"))

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
{face}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1200px;height:675px;overflow:hidden;position:relative;background:#e8eeec;
background-image:radial-gradient(circle,rgba(47,107,87,.08) 1.4px,transparent 1.6px);background-size:30px 30px;background-position:15px 15px}}
.pill{{position:absolute;left:70px;top:72px;height:35px;padding:0 18px;border-radius:999px;background:#2f6b57;color:#fff;
font:700 17px/35px {TITLE_FONT};letter-spacing:.01em}}
h1{{position:absolute;left:70px;top:138px;width:600px;font:800 53px/1.04 {TITLE_FONT};letter-spacing:-.012em;color:#111;text-wrap:balance}}
.foot{{position:absolute;left:70px;top:567px;height:38px;display:flex;align-items:center;gap:12px;font:500 20px/1 {FOOT_FONT};color:#1c2b26}}
.av{{width:38px;height:38px;border-radius:50%;background:#2f6b57;color:#fff;font:800 14px/38px {TITLE_FONT};text-align:center}}
.card{{position:absolute;left:710px;width:420px;top:50%;transform:translateY(-50%);border-radius:22px;
box-shadow:0 22px 55px rgba(20,45,38,.16),0 2px 6px rgba(20,45,38,.06)}}
.light{{background:#fff;overflow:hidden}}
.bar{{display:block;border-radius:8px}}
.head{{height:44px;background:#2f6557;color:#fff;font:600 16px/44px 'Inter','Inter Display',sans-serif;padding:0 16px;display:flex;align-items:center;gap:10px}}
.doc{{width:18px;height:22px;background:#fff;border-radius:3px}}
.tr{{display:flex;height:40px;border-top:1px solid #e8eeec;align-items:center}}
.tr.hd{{height:36px;background:#f4f8f7;border-top:0;color:#6c807a;font:600 14px 'Inter',sans-serif}}
.n{{width:30px;text-align:center;color:#6c807a;font:600 14px 'Inter',sans-serif}}
.td{{flex:1;padding:0 14px;border-left:1px solid #e8eeec;height:100%;display:flex;align-items:center;color:#6c807a;font:600 14px 'Inter',sans-serif}}
.td:not(:has(.bar)){{justify-content:center}}
.tr.hd .td{{justify-content:center}}
.serp{{padding:24px 24px 28px;display:flex;flex-direction:column;gap:16px}}
.search{{height:48px;border:2px solid #cfe0da;border-radius:24px;display:flex;align-items:center;gap:12px;padding:0 16px}}
.ring{{width:14px;height:14px;border:3px solid #2f6b57;border-radius:50%}}
.hit{{background:#f2fefc;border:1px solid #d9efe8;border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:10px}}
.hit b{{font:700 20px/1.1 'Inter','Inter Display',sans-serif;color:#2a6b57;letter-spacing:-.01em}}
.res{{display:flex;flex-direction:column;gap:9px;padding:0 4px}}
.dark{{background:#111;color:#fff;padding:22px 22px 24px}}
.ah{{display:flex;align-items:center;gap:10px;font:700 17px 'Inter',sans-serif;color:#a8e6cf;margin-bottom:16px}}
.ic{{width:26px;height:26px;border-radius:7px;background:#2f8f72;color:#fff;font-size:15px;line-height:26px;text-align:center}}
.ln{{height:10px;border-radius:6px;background:#3a3a3a;margin-bottom:9px}}
.dark p{{font:700 19px/1.3 'Inter',sans-serif;margin:16px 0 14px}} .dark mark{{background:none;color:#f5b82e}}
.chips{{display:flex;gap:8px}} .chip{{background:#2b2b2b;color:#a8c2b9;font:600 13px 'Inter',sans-serif;padding:7px 12px;border-radius:8px}}
</style></head><body>
<div class="pill">{e(cat)}</div><h1>{title}</h1>
{card}
<div class="foot"><span class="av">EM</span>emmanuelmichel.fr · Consultant SEO à Lyon</div>
</body></html>"""

p = pathlib.Path("t2.html"); p.write_text(page, encoding="utf-8")
subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                "--window-size=1200,675", "--screenshot=t2.png", p.resolve().as_uri()], check=True, capture_output=True)
im = Image.open("t2.png").convert("RGB"); assert im.size == (1200, 675), im.size
im.save(out, "WEBP", quality=88, method=6); im.save("t2_preview.png")
print(out, pathlib.Path(out).stat().st_size, "fonts_ok=", ok_fonts)
