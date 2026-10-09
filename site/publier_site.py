# Copie l'accueil 2.0 (site/) dans docs/ (scaniapp.com) : noindex retiré,
# textes anglais posés EN DUR dans le HTML (Google les lit sans JavaScript ; le
# script les remplace ensuite par la langue du visiteur). privacy/support,
# CNAME, app-ads.txt, version.json de docs/ : intacts.
import html, json, re, shutil, os

# L'atelier (site/) et la vitrine (docs/, servie par GitHub Pages) vivent dans le même dépôt Scani_Site.
SRC = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(SRC), "docs")

src = open(f"{SRC}/index.html", encoding="utf-8").read()
js = open(f"{SRC}/langues.js", encoding="utf-8").read()
m = re.search(r"const LANGUES = (\{.*?\});\s*$", js, re.S | re.M)
LANGUES = json.loads(m.group(1))
en = LANGUES["en"]
e = html.escape

def titre(a, b, s, balise):
    return f'<{balise} class="h"><span>{e(a)}</span><span class="acc">{e(b)}</span></{balise}><p class="sous">{e(s)}</p>'

out = src.replace('<meta name="robots" content="noindex, nofollow">\n', "")
assert "noindex" not in out
p = en["promesse"]
l1 = en["legendes"]["01"]
out = out.replace('id="entree"><div class="txt"></div>', f'id="entree"><div class="txt">{titre(l1[0], l1[1], p[0] + " " + p[1], "h1")}</div>', 1)
for nn in ["02", "03", "09", "05", "06", "07", "08"]:
    a, b, s = en["legendes"][nn]
    avant = f'id="s{nn}"><div class="txt"></div>'
    assert avant in out, nn
    out = out.replace(avant, f'id="s{nn}"><div class="txt">{titre(a, b, s, "h2")}</div>', 1)
open(f"{DST}/index.html", "w", encoding="utf-8").write(out)

for f in ["langues.js", "cartes.js", "favicon.png", "apple-touch-icon.png"]:
    shutil.copy2(f"{SRC}/{f}", f"{DST}/{f}")
for d in ["ecrans", "img"]:
    if os.path.exists(f"{DST}/{d}"):
        shutil.rmtree(f"{DST}/{d}")
    shutil.copytree(f"{SRC}/{d}", f"{DST}/{d}", ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "icon-1024.png"))   # l'icône App Store n'est pas pour le site
print("ok", len(out))
