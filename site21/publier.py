# -*- coding: utf-8 -*-
"""Publie le site 2.1 (cet atelier, Scani_Site/site21/) dans docs/ — la vitrine servie par GitHub Pages
sous scaniapp.com. À lancer QUAND APPLE A VALIDÉ LA 2.1 (Mathias, 12/11), pas avant.

    python3 publier.py --essai             tout dans un dossier temporaire, rien ne touche docs/ (pour vérifier)
    python3 publier.py                     écrit dans docs/ (puis : relire, commit, push — avec l'accord de Mathias)
    python3 publier.py --version 2.1       en plus : docs/version.json « latest » → 2.1 (l'app propose la mise à
                                           jour aux versions plus anciennes, sans l'imposer). SEULEMENT une fois la
                                           2.1 en ligne sur l'App Store, sinon l'app proposerait une version introuvable.

Ce qu'il fait :
- index.html : « noindex » retiré, et la page ANGLAISE posée en dur dans <main> (Google la lit sans JavaScript ;
  le script la remplace ensuite par la langue du visiteur) — rendue par Chrome sans interface ;
- copie textes.js, favicon.png, apple-touch-icon.png, img/ (logo, img/p, img/<langue>/ : seulement les 10 écrans) ;
- retire de docs/ ce qui n'appartient qu'à l'ancien site : langues.js, cartes.js, ecrans/ ;
- garde intacts dans docs/ : CNAME, app-ads.txt, version.json, privacy.html, support.html.
"""
import json, os, re, shutil, subprocess, sys, tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(os.path.dirname(ICI), "docs")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GARDER = ["CNAME", "app-ads.txt", "version.json", "privacy.html", "support.html"]
ANCIENS = ["langues.js", "cartes.js", "ecrans"]
ECRANS = {"menu", "dish", "sign", "product", "appliance", "receipt", "letter", "notice", "plant", "langs"}

essai = "--essai" in sys.argv
version = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else None

if essai:
    dst = tempfile.mkdtemp(prefix="scani-docs-")
    for f in os.listdir(DOCS):
        s = os.path.join(DOCS, f)
        (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, os.path.join(dst, f))
else:
    dst = DOCS
for f in GARDER:
    assert os.path.exists(os.path.join(dst, f)), f"docs/{f} manque : rien n'est publié"

# 1. La page anglaise rendue par Chrome, posée en dur dans <main>.
src = open(os.path.join(ICI, "index.html"), encoding="utf-8").read()
rendu = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                        "--window-size=393,852", "--virtual-time-budget=1500", "--dump-dom",
                        "file://" + os.path.join(ICI, "index.html") + "?l=en"],
                       capture_output=True, text=True, timeout=120).stdout
m = re.search(r'<main id="main">(.*?)</main>', rendu, re.S)
assert m and "apps.apple.com/app/id6761646868" in m.group(1), "la page anglaise n'a pas été rendue"
# seulement ce que le script ajoute en marchant (pas style="--n:10" des vignettes, dont la grille a besoin)
statique = re.sub(r'\sdata-coupe="[^"]*"|\sstyle="font-size:[^"]*"', "", m.group(1))
assert 'style="--n:' in statique
statique = statique.replace(' class="on part"', ' class="on"').replace(" entre", "")
# Un visiteur non anglais ne doit pas télécharger les images anglaises : dans la page en dur, seules l'icône et
# les deux premières images (photo + écran du menu) partent ; les autres attendent (data-src), le script refait
# de toute façon la page dans la langue du visiteur.
statique = re.sub(r'<img (?![^>]*class="(?:icone|it on)")((?:[^>]*?\s)?)src="', r'<img \1data-src="', statique)
assert statique.count(' src="img/') == 3, statique.count(' src="img/')
out = src.replace('<meta name="robots" content="noindex, nofollow">\n', "")
assert "noindex" not in out
out = out.replace('<main id="main"></main>', '<main id="main">' + statique + "</main>", 1)
open(os.path.join(dst, "index.html"), "w", encoding="utf-8").write(out)

# 2. Les fichiers du site.
for f in ["textes.js", "favicon.png", "apple-touch-icon.png", "og.png"]:
    shutil.copy2(os.path.join(ICI, f), os.path.join(dst, f))
img = os.path.join(dst, "img")
if os.path.exists(img):
    shutil.rmtree(img)
os.makedirs(img)
shutil.copy2(os.path.join(ICI, "img", "logo.png"), img)
nb = 0
for d in sorted(os.listdir(os.path.join(ICI, "img"))):
    s = os.path.join(ICI, "img", d)
    if not os.path.isdir(s):
        continue
    os.makedirs(os.path.join(img, d))
    for f in os.listdir(s):
        if d == "p" or f.split(".")[0] in ECRANS:
            if f.endswith(".webp"):
                shutil.copy2(os.path.join(s, f), os.path.join(img, d, f)); nb += 1

# 3. Ce qui n'appartient qu'à l'ancien site.
for f in ANCIENS:
    p = os.path.join(dst, f)
    if os.path.isdir(p):
        shutil.rmtree(p)
    elif os.path.exists(p):
        os.remove(p)

# 4. La version annoncée à l'app.
if version:
    v = json.load(open(os.path.join(dst, "version.json")))
    v["latest"] = version
    json.dump(v, open(os.path.join(dst, "version.json"), "w"))

print(("ESSAI dans " if essai else "publié dans ") + dst, "—", nb, "images,", len(out), "octets d'index.html",
      "— version.json :", open(os.path.join(dst, "version.json")).read().strip())
