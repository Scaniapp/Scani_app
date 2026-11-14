# -*- coding: utf-8 -*-
# Construit le site4 par langue : img/<langue>/*.webp (écrans 2.1 recadrés au ras de la coque),
# img/p/*.webp (les photos d'origine, communes) et textes.js (les textes des 50 langues).
#   python3 construire.py
import json, os, re, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.expanduser('~/Developer/Scani/Scani_Data/bancs/captures-2026-09-30/')
SITE_DIR = os.path.expanduser('~/Developer/Scani/Scani_Site/site/')
sys.path.insert(0, BANC); sys.path.insert(0, SITE_DIR)
from textes import TITRES            # titres des captures, 50 langues (index 1..10, nouvelle numérotation)
from site_textes import SITE         # phrases du site, 50 langues

s = open(SITE_DIR + 'langues.js', encoding='utf-8').read()
ANCIEN = json.loads(s[s.index('{'):s.rindex('}') + 1])   # nom, rtl, legendes 01, promesse, types

# Les deux phrases nouvelles du site (à relire par un natif).
VOIR = {
 'en': ('You see this', 'Scani tells you'), 'ja': ('あなたが見るもの', 'Scani が伝えること'),
 'fr': ('Ce que vous voyez', 'Ce que Scani vous dit'), 'es': ('Lo que ves', 'Lo que Scani te dice'),
 'de': ('Das siehst du', 'Das sagt dir Scani'), 'ko': ('당신이 보는 것', 'Scani가 알려주는 것'),
 'it': ('Quello che vedi', 'Quello che Scani ti dice'), 'pt-BR': ('O que você vê', 'O que o Scani diz'),
 'pt-PT': ('O que vê', 'O que o Scani lhe diz'), 'nl': ('Dit zie je', 'Dit vertelt Scani'),
 'ca': ('El que veus', 'El que et diu Scani'), 'da': ('Det ser du', 'Det fortæller Scani'),
 'sv': ('Det du ser', 'Det Scani berättar'), 'nb': ('Det du ser', 'Det Scani forteller'),
 'fi': ('Näet tämän', 'Scani kertoo'), 'pl': ('To widzisz', 'To mówi Scani'),
 'cs': ('Tohle vidíte', 'Tohle vám řekne Scani'), 'sk': ('Toto vidíte', 'Toto vám povie Scani'),
 'hr': ('Ovo vidite', 'Ovo vam kaže Scani'), 'ro': ('Ce vezi', 'Ce îți spune Scani'),
 'hu': ('Ezt látod', 'Ezt mondja a Scani'), 'el': ('Αυτό βλέπεις', 'Αυτό σου λέει το Scani'),
 'ru': ('Вы видите это', 'Scani объясняет'), 'uk': ('Ви бачите це', 'Scani пояснює'),
 'tr': ('Gördüğünüz', 'Scani’nin söylediği'), 'id': ('Yang Anda lihat', 'Yang Scani jelaskan'),
 'ms': ('Apa yang anda lihat', 'Apa yang Scani terangkan'), 'vi': ('Bạn thấy gì', 'Scani giải thích'),
 'th': ('สิ่งที่คุณเห็น', 'สิ่งที่ Scani บอก'), 'hi': ('आप यह देखते हैं', 'Scani यह बताता है'),
 'ar': ('ما تراه', 'ما يخبرك به Scani'), 'he': ('מה שאתם רואים', 'מה ש‑Scani מסביר'),
 'sl': ('To vidite', 'To vam pove Scani'), 'bn': ('আপনি যা দেখেন', 'Scani যা বলে'),
 'gu': ('તમે જે જુઓ છો', 'Scani જે કહે છે'), 'kn': ('ನೀವು ನೋಡುವುದು', 'Scani ಹೇಳುವುದು'),
 'ml': ('നിങ്ങൾ കാണുന്നത്', 'Scani പറയുന്നത്'), 'mr': ('तुम्ही जे पाहता', 'Scani जे सांगते'),
 'or': ('ଆପଣ ଯାହା ଦେଖନ୍ତି', 'Scani ଯାହା କହେ'), 'pa': ('ਜੋ ਤੁਸੀਂ ਦੇਖਦੇ ਹੋ', 'ਜੋ Scani ਦੱਸਦਾ ਹੈ'),
 'ta': ('நீங்கள் பார்ப்பது', 'Scani சொல்வது'), 'te': ('మీరు చూసేది', 'Scani చెప్పేది'),
 'ur': ('جو آپ دیکھتے ہیں', 'جو Scani بتاتا ہے'), 'zh-Hans': ('你看到的', 'Scani 告诉你的'),
 'zh-Hant': ('你看到的', 'Scani 告訴你的'), 'bg': ('Това виждате', 'Това казва Scani'),
 'kk': ('Сіз көресіз', 'Scani түсіндіреді'), 'lt': ('Tai matote', 'Tai pasako Scani'),
 'my': ('သင်မြင်သည်', 'Scani ပြောသည်'), 'ne': ('तपाईंले देख्नुहुन्छ', 'Scani ले बताउँछ'),
}

# La série à 10 (12/11), la même dans les 50 langues.
def numeros(L):
    return {'menu': '01', 'dish': '02', 'sign': '03', 'product': '04', 'appliance': '05', 'receipt': '06',
            'letter': '07', 'notice': '08', 'plant': '09', 'langs': '10'}

# Les titres des captures (TITRES : la série à 10, index 0..9).
IDX = {'menu': 0, 'dish': 1, 'sign': 2, 'product': 3, 'appliance': 4, 'receipt': 5,
       'letter': 6, 'notice': 7, 'plant': 8, 'langs': 9}

# La photo d'origine de chaque écran : documents japonais partout, français pour la fiche japonaise.
PHOTO = {'menu': 'menu', 'receipt': 'ticket', 'sign': 'panneau', 'product': 'produit', 'dish': 'photo',
         'appliance': 'appareil', 'langs': 'menu', 'letter': 'lettre', 'notice': 'notice', 'plant': 'plante'}
# Pour la fiche japonaise, l'original change là où il était japonais (lettre allemande, notice coréenne : non).
AUTRE_JA = ('menu', 'receipt', 'sign', 'product', 'appliance', 'dish', 'langs')
def photo_de(L, k):
    """L'original montré : jamais dans la langue du lecteur (ja : français ; de : lettre japonaise ; ko : notice japonaise)."""
    if L == 'ja' and k in AUTRE_JA: return PHOTO[k] + '_fr'
    if (L, k) in (('de', 'letter'), ('ko', 'notice')): return PHOTO[k] + '_jp'
    return PHOTO[k]

def run(*a):
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def ecran(L, nn, dst):
    """Capture 1320×2868 → coque seule (x 164..1150, y 640..2729) → 600 px de large → WebP."""
    if os.path.exists(dst): return
    tmp = dst + '.png'
    run('cp', f'{BANC}sortie/{L}/{nn}.png', tmp)
    run('sips', '--cropOffset', '640', '164', '-c', '2089', '986', tmp, '--out', tmp)
    run('sips', '-Z', '600', tmp, '--out', tmp)
    run('cwebp', '-q', '82', '-m', '6', tmp, '-o', dst)
    os.remove(tmp)

def photo(nom, dst):
    if os.path.exists(dst): return
    tmp = dst + '.jpg'
    run('sips', '-s', 'format', 'jpeg', '-Z', '1000', f'{BANC}photos/{nom}.jpg', '--out', tmp)
    run('cwebp', '-q', '78', '-m', '6', tmp, '-o', dst)
    os.remove(tmp)

os.makedirs(f'{ICI}/img/p', exist_ok=True)
for p in ['menu', 'ticket', 'panneau', 'produit', 'appareil', 'photo']:
    photo(p, f'{ICI}/img/p/{p}.webp')
    photo(p + '_fr', f'{ICI}/img/p/{p}_fr.webp')
for p in ['lettre', 'notice', 'plante', 'lettre_jp', 'notice_jp']:
    photo(p, f'{ICI}/img/p/{p}.webp')

# Le nom des vignettes de la fin pour le plat et la plante (le type de l'app dit « Photo » pour les deux).
PLAT_PLANTE = {
 'en': ('Food', 'Plant'), 'ja': ('料理', '植物'), 'fr': ('Plat', 'Plante'), 'es': ('Plato', 'Planta'),
 'de': ('Gericht', 'Pflanze'), 'ko': ('음식', '식물'), 'it': ('Piatto', 'Pianta'), 'pt-BR': ('Prato', 'Planta'),
 'pt-PT': ('Prato', 'Planta'), 'nl': ('Gerecht', 'Plant'), 'ca': ('Plat', 'Planta'), 'da': ('Ret', 'Plante'),
 'sv': ('Maträtt', 'Växt'), 'nb': ('Rett', 'Plante'), 'fi': ('Ruoka', 'Kasvi'), 'pl': ('Danie', 'Roślina'),
 'cs': ('Jídlo', 'Rostlina'), 'sk': ('Jedlo', 'Rastlina'), 'hr': ('Jelo', 'Biljka'), 'ro': ('Mâncare', 'Plantă'),
 'hu': ('Étel', 'Növény'), 'el': ('Φαγητό', 'Φυτό'), 'ru': ('Блюдо', 'Растение'), 'uk': ('Страва', 'Рослина'),
 'tr': ('Yemek', 'Bitki'), 'id': ('Makanan', 'Tanaman'), 'ms': ('Makanan', 'Tumbuhan'), 'vi': ('Món ăn', 'Cây'),
 'th': ('อาหาร', 'พืช'), 'hi': ('खाना', 'पौधा'), 'ar': ('طبق', 'نبتة'), 'he': ('מנה', 'צמח'),
 'sl': ('Jed', 'Rastlina'), 'bn': ('খাবার', 'গাছ'), 'gu': ('વાનગી', 'છોડ'), 'kn': ('ಖಾದ್ಯ', 'ಸಸ್ಯ'),
 'ml': ('വിഭവം', 'ചെടി'), 'mr': ('पदार्थ', 'वनस्पती'), 'or': ('ଖାଦ୍ୟ', 'ଗଛ'), 'pa': ('ਪਕਵਾਨ', 'ਪੌਦਾ'),
 'ta': ('உணவு', 'செடி'), 'te': ('వంటకం', 'మొక్క'), 'ur': ('کھانا', 'پودا'), 'zh-Hans': ('菜品', '植物'),
 'zh-Hant': ('菜餚', '植物'), 'bg': ('Ястие', 'Растение'), 'kk': ('Тағам', 'Өсімдік'), 'lt': ('Patiekalas', 'Augalas'),
 'my': ('ဟင်းလျာ', 'အပင်'), 'ne': ('परिकार', 'बिरुवा'),
}

LANGUES = sys.argv[1:] or list(TITRES)   # sans argument : les 50
T = {}
for L in LANGUES:
    nums = numeros(L)
    os.makedirs(f'{ICI}/img/{L}', exist_ok=True)
    for k, nn in nums.items():
        ecran(L, nn, f'{ICI}/img/{L}/{k}.webp')
    A, S, TT = ANCIEN[L], SITE[L], TITRES[L]
    source = 'FR' if L == 'ja' else 'JA'
    titres = {k: list(TT[IDX[k]]) for k in nums}
    T[L] = {
        'nom': A['nom'], 'rtl': A['rtl'], 'source': source,
        'h1': A['legendes']['01'][:2], 'lead': A['legendes']['01'][2],
        'promesse': A['promesse'], 'voir': VOIR[L],
        'types1': S['types1'], 'types2': S['types2'], 'types_sous': S['types_sous'],
        'get': S['get'], 'choisir': S['choisir'], 'langs': TT[IDX['langs']][0],
        'labels': {'menu': A['types'][0][0], 'overlay': A['types'][0][0], 'receipt': A['types'][1][0], 'product': A['types'][2][0],
                   'sign': A['types'][4][0], 'appliance': A['types'][8][0], 'dish': PLAT_PLANTE[L][0],
                   'letter': A['types'][3][0], 'notice': A['types'][5][0], 'plant': PLAT_PLANTE[L][1], 'langs': TT[IDX['langs']][0].rstrip('.。।۔')},
        'titres': titres,
        'ecrans': {k: f'img/{L}/{k}.webp' for k in nums},
        'photos': {k: f"img/p/{photo_de(L, k)}.webp" for k in nums},
    }
    print(L, len(nums), 'écrans', flush=True)

js = '// Généré par construire.py — textes et images du site, par langue.\nconst TEXTES = ' + json.dumps(T, ensure_ascii=False, separators=(',', ':')) + ';\n'
open(f'{ICI}/textes.js', 'w', encoding='utf-8').write(js)
print('textes.js', len(js), 'octets')
