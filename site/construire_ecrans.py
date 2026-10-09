# Transforme les captures App Store (sortie/<langue>/NN.html) en écrans ANIMÉS pour le site,
# dans chaque langue : l'ÉCRAN seul (393 × 852) — le titre, la coque et la photo posée à côté
# sont dessinés par la page, la même coque pour tous — et les cellules qui arrivent comme dans
# l'onboarding (250 ms, puis une toutes les 110 ms, 0,3 s en douceur, 8 px de montée).
# La page parente envoie « jouer » / « reset ».
#
#   python3 construire_ecrans.py      → ecrans/<langue>/NN.html + cartes.js + langues.js
import json, os, re, sys
from shutil import copy
from bs4 import BeautifulSoup

ICI = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.expanduser('~/Documents/Scani2.0/bancs/captures-2026-09-30/')
PHOTOS = BANC + 'photos/'
APP = os.path.expanduser('~/Developer/AppleOCRTest/AppleOCRTest/')
sys.path.insert(0, BANC); sys.path.insert(0, ICI)
from textes import TITRES          # les titres des captures, par langue
from site_textes import SITE       # les quelques phrases propres au site

CSS = """
/* AU REPOS, les cellules sont des FANTÔMES du vrai contenu (18 %) : un téléphone voisin n'est
   jamais blanc pendant qu'on fait défiler (2026-10-07) ; elles s'allument en arrivant au centre. */
html,body{background:transparent!important;overflow:hidden}
.a-cell{opacity:.18;translate:0 8px;transition:opacity .3s ease-out,translate .3s ease-out}
.a-cell.on{opacity:1;translate:0 0}
.a-fade{opacity:.18;transition:opacity .35s ease-out}
.a-fade.on{opacity:1}
/* la phrase au serveur : chaque morceau devient net, au rythme des cellules (pas de translate sur du texte en ligne) */
.a-mot{opacity:.18;filter:blur(6px);transition:opacity .45s cubic-bezier(.2,.8,.2,1),filter .45s cubic-bezier(.2,.8,.2,1)}
.a-mot.on{opacity:1;filter:blur(0)}
/* dans le bloc restaurant, la coque porte une barre d'état fixe : celle de l'écran s'efface */
.sans-etat .a-etat{visibility:hidden}
.a-voile{opacity:0;transition:opacity .4s ease-out}
.a-voile.on{opacity:1}
.a-sheet{translate:0 105%;transition:translate .5s cubic-bezier(.2,.9,.3,1)}
.a-sheet.on{translate:0 0}
@media (prefers-reduced-motion:reduce){.a-cell,.a-mot,.a-fade,.a-voile,.a-sheet{transition:none!important}.a-shutter{animation:none}}
"""

JS = """
(function () {
  const Q = s => [...document.querySelectorAll(s)];
  const tous = Q('.a-cell,.a-mot,.a-fade,.a-voile,.a-sheet');
  const calme = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let minuteurs = [];
  function montre(el, d) { minuteurs.push(setTimeout(() => el.classList.add('on'), d)); }
  function reset() {
    minuteurs.forEach(clearTimeout); minuteurs = [];
    tous.forEach(el => { el.style.transition = 'none'; el.classList.remove('on'); });
    document.body.offsetWidth;
    tous.forEach(el => el.style.transition = '');
  }
  function jouer() {
    reset();
    if (calme) { tous.forEach(el => el.classList.add('on')); return; }
    let t = 250;
    const avant = Q('.a-voile,.a-sheet');
    avant.forEach(el => montre(el, 120));
    if (avant.length) t += 380;
    Q('.a-cell').forEach((el, i) => montre(el, t + i * 110));
    t += Q('.a-cell').length * 110;
    Q('.a-mot').forEach((el, i) => montre(el, t + i * 160));
    t += Q('.a-mot').length * 160;
    Q('.a-fade').forEach((el, i) => montre(el, t + i * 320));
  }
  addEventListener('message', e => { if (e.data === 'jouer') jouer(); if (e.data === 'reset') reset(); });
  parent.postMessage({pret: location.pathname}, '*');
})();
"""

def classe(t, c):
    t['class'] = (t.get('class') or []) + [c]

def chaines(langue):
    """Localizable.strings de l'app → dict."""
    t = open(f"{APP}{langue}.lproj/Localizable.strings", encoding="utf-8").read()
    return {m.group(1): m.group(2).replace('\\"', '"') for m in re.finditer(r'^"(.+?)"\s*=\s*"(.*)";\s*$', t, re.M)}

NOMS = json.load(open(BANC + 'noms_langues.json'))
RTL = {'ar', 'he', 'ur'}
TYPES = ['menu', 'ticket', 'produit', 'document', 'panneau', 'instructions', 'cours', 'quiz', 'appareil']
# l'écran 4 (traductions sur la photo) n'est pas sur le site : la fonction n'est pas assez fiable
ECRANS = [1, 2, 3, 5, 6, 7, 8, 9, 10]

LANGUES = sorted(d for d in os.listdir(BANC + 'sortie') if os.path.isfile(f'{BANC}sortie/{d}/10.html'))
CARTES, TEXTES = {}, {}
for L in LANGUES:
    os.makedirs(f'{ICI}/ecrans/{L}', exist_ok=True)
    CARTES[L] = {}
    for n in ECRANS:
        nom = '%02d' % n
        s = BeautifulSoup(open(f'{BANC}sortie/{L}/{nom}.html').read().replace('file://' + PHOTOS, '../../img/'), 'html.parser')
        st = lambda t: t.get('style') or ''

        # L'écran seul, 393 × 852 : la coque est dessinée par la page, la même pour tous.
        ecran = s.find('div', style=re.compile(r'zoom:\.8041'))
        ecran['style'] = st(ecran).replace('zoom:.8041;', '')
        for c in ecran.find_all(recursive=False):
            if 'top:147px' in st(c) and 'flex-direction:column' in st(c) and n != 9:
                for x in c.find_all(recursive=False): classe(x, 'a-cell')           # les lignes
            if 'top:762px' in st(c) or 'top:750px' in st(c):
                classe(c, 'a-fade')                                                  # la pilule du bas
            if 'font-size:56px' in st(c):
                for x in c.find_all('span', recursive=False): classe(x, 'a-mot')     # la phrase au serveur
            if st(c).startswith('position:absolute;top:0;left:0;width:393px;height:54px'):
                classe(c, 'a-etat')                                                  # la barre d'état (le bloc pose la sienne, fixe)
            if 'top:663px' in st(c):
                classe(c, 'a-shutter')                                               # le déclencheur respire
            if 'rgba(0,0,0,.35)' in st(c):
                classe(c, 'a-voile')                                                 # le voile sous la feuille
            if 'top:337px' in st(c) or ('top:64px' in st(c) and 'border-radius:24px 24px 0 0' in st(c)):
                classe(c, 'a-sheet')                                                 # la feuille qui monte
                if 'top:337px' in st(c):
                    for x in c.find_all(recursive=False)[1].find_all(recursive=False): classe(x, 'a-cell')
                else:
                    for x in c.find_all(recursive=False)[2:]: classe(x, 'a-cell')

        # La photo scannée, posée de travers à côté du téléphone : elle passe dans la page
        # (cartes.js), en coordonnées de la coque (330 × 699, posée en 55 / 214 dans la capture).
        # Sur le site seulement, elle remonte pour finir 30 au-dessus du bas de la coque, sinon
        # elle tombe sur le bouton « Get Scani ». Les captures App Store ne bougent pas.
        carte = s.find('div', style=re.compile(r'border:5px solid'))
        if carte:
            img = carte.find('img')
            w = int(re.search(r'width:(\d+)px', st(carte)).group(1)); hh = int(re.search(r'height:(\d+)px', st(carte)).group(1))
            CARTES[L][nom] = {'src': img['src'].replace('../../', ''), 'x': int(re.search(r'left:(-?\d+)px', st(carte)).group(1)) - 55,
                              'y': 699 - 30 - hh, 'w': w, 'h': hh, 'rot': float(re.search(r'rotate\((-?[\d.]+)deg\)', st(carte)).group(1)),
                              'pos': (re.search(r'object-position:([^;"]+)', st(img)) or [None, 'center'])[1]}

        s.body.clear()
        s.body.append(ecran)
        style = s.new_tag('style'); style.string = CSS; s.find('head').append(style)
        script = s.new_tag('script'); script.string = JS; s.body.append(script)
        open(f'{ICI}/ecrans/{L}/{nom}.html', 'w').write(str(s))

    # Les textes de la page dans cette langue : titres des captures, phrases du site, les 9 types
    c = chaines(L)
    t = TITRES[L]
    TEXTES[L] = {
        'nom': NOMS[L][L][:1].upper() + NOMS[L][L][1:],      # NOMS[a][b] : la langue b écrite en a
        'anglais': NOMS['en'][L],                            # pour la recherche du premier écran
        'rtl': L in RTL,
        'legendes': {'01': [c['onb_camera_titre'], c['onb_camera_accent'], c['onb_camera_sous']],
                     **{'%02d' % n: list(t[n - 1]) for n in ECRANS if n != 1}},
        'site': SITE[L],
        # le haut du site : la page 3 de l'onboarding (déjà traduite et mesurée dans l'app)
        'promesse': [c['onb_promesse_titre'], c['onb_promesse_accent'], c['onb_promesse_sous']],
        'types': [[c['onb_type_' + k], c['onb_type_' + k + '_detail']] for k in TYPES],
    }
    print(L, len(CARTES[L]), 'photos')

open(ICI + '/cartes.js', 'w').write('// Généré par construire_ecrans.py — les photos posées à côté de la coque, par langue.\nconst CARTES = '
                                     + json.dumps(CARTES) + ';\n')
open(ICI + '/langues.js', 'w').write('// Généré par construire_ecrans.py — les textes de la page, par langue.\nconst LANGUES = '
                                      + json.dumps(TEXTES, ensure_ascii=False) + ';\n')

# les photos posées à côté du téléphone (la fiche japonaise montre les documents français)
for f in os.listdir(PHOTOS):
    if f.endswith('.jpg'):
        copy(PHOTOS + f, ICI + '/img/' + f)
