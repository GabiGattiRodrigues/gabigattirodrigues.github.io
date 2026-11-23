"""Gera as páginas-ponte /projetos/<id>/ a partir dos cards do index.html do portfólio.

Uso: python gerar.py <index.html do site> <pasta de saída> <pasta com os GIFs de prévia>
Cada página tem resumo, prévia, botão pro app, aviso de hibernação com print e links pro portfólio.
"""
import html
import json
import os
import sys

from bs4 import BeautifulSoup
from PIL import Image

SITE = "https://gabigattirodrigues.github.io"
idx_path, out_dir, gif_dir = sys.argv[1:4]

soup = BeautifulSoup(open(idx_path, encoding="utf-8").read(), "html.parser")
cards = soup.select("article.pc")
n_proj = len(cards)


def attr(s):
    return html.escape(s, quote=True)


def bi(tag, pt, en, cls="", extra=""):
    """Elemento bilíngue no mesmo padrão do site (data-pt / data-en)."""
    c = f' class="{cls}"' if cls else ""
    return f'<{tag}{c}{extra} data-pt="{attr(pt)}" data-en="{attr(en)}">{pt}</{tag}>'


TEMPLATE = open(os.path.join(os.path.dirname(__file__), "template.html"), encoding="utf-8").read()
feitos = []

for a in cards:
    pid = a["id"]
    app = next((x["href"] for x in a.select(".links a") if "streamlit.app" in x.get("href", "")), None)
    if not app:  # Alexandria e Argos já são páginas estáticas, não hibernam
        continue
    gh = next((x["href"] for x in a.select(".links a") if "github.com" in x.get("href", "")), "")
    name = a.select_one("h3").get_text(strip=True)
    pn = a.select_one(".p-name")
    q = a.select_one(".q")
    prob = a.select_one(".case-txt p")
    pv_src = a.select_one(".pv img")["src"].split("?")[0]

    # Imagem de prévia pros links no WhatsApp/LinkedIn: 1º quadro do GIF em JPG
    gif = Image.open(os.path.join(gif_dir, os.path.basename(pv_src)))
    gif.seek(0)
    os.makedirs(os.path.join(out_dir, "previews", "og"), exist_ok=True)
    gif.convert("RGB").save(os.path.join(out_dir, "previews", "og", f"{pid}.jpg"), quality=85)

    page = TEMPLATE
    rep = {
        "{{TITULO_PT_JS}}": json.dumps(f"{name} · {pn['data-pt']} — Gabriela Gatti Rodrigues", ensure_ascii=False).replace("</", "<\\/"),
        "{{TITULO_EN_JS}}": json.dumps(f"{name} · {pn['data-en']} — Gabriela Gatti Rodrigues", ensure_ascii=False).replace("</", "<\\/"),
        "{{ID}}": pid,
        "{{NOME}}": html.escape(name),
        "{{TITULO_PT}}": attr(f"{name} · {pn['data-pt']} — Gabriela Gatti Rodrigues"),
        "{{TITULO_EN}}": attr(f"{name} · {pn['data-en']} — Gabriela Gatti Rodrigues"),
        "{{OG_DESC}}": attr(html.unescape(q["data-pt"])),
        "{{OG_IMG}}": f"{SITE}/previews/og/{pid}.jpg",
        "{{URL}}": f"{SITE}/projetos/{pid}/",
        "{{ICONE}}": str(a.select_one(".p-icon")),
        "{{P_NAME}}": str(pn),
        "{{STATUS}}": str(a.select_one(".status") or ""),
        "{{AREAS}}": str(a.select_one(".areas")),
        "{{GANCHO}}": bi("p", q["data-pt"], q["data-en"], "gancho"),
        "{{PROBLEMA}}": bi("p", prob["data-pt"], prob["data-en"], "problema") if prob else "",
        "{{KPI}}": str(a.select_one(".kpi") or ""),
        "{{STACK}}": str(a.select_one(".stack-chips") or ""),
        "{{APP}}": app,
        "{{GH}}": gh,
        "{{PREVIEW}}": f"../../{pv_src}",
        "{{N_PROJ}}": str(n_proj),
    }
    for k, v in rep.items():
        page = page.replace(k, v)
    os.makedirs(os.path.join(out_dir, "projetos", pid), exist_ok=True)
    with open(os.path.join(out_dir, "projetos", pid, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    feitos.append((pid, app))

for pid, app in feitos:
    print(f"{SITE}/projetos/{pid}/  ->  {app}")
print(len(feitos), "páginas")
