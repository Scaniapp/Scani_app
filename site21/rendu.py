# -*- coding: utf-8 -*-
# Rend l'ÉCRAN SEUL (393 × 852, sans coque, sans titre, sans photo posée) de chaque capture du banc,
# net (×3 = 1179 px) avec Chrome sans interface, puis WebP 900 px → img/<langue>/<clé>.webp.
#   python3 rendu.py [langues…]      (sans argument : en ja fr)
import os, re, subprocess, sys
from bs4 import BeautifulSoup

ICI = os.path.dirname(os.path.abspath(__file__))
BANC = os.path.expanduser('~/Developer/Scani/Scani_Data/bancs/captures-2026-09-30/')
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# La série à 10 (12/11), la même dans les 50 langues.
def numeros(L):
    return {'menu': '01', 'dish': '02', 'sign': '03', 'product': '04', 'appliance': '05', 'receipt': '06',
            'letter': '07', 'notice': '08', 'plant': '09', 'langs': '10'}

def run(*a, **k):
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **k)

def ecran_seul(L, nn, dst):
    s = BeautifulSoup(open(f'{BANC}sortie/{L}/{nn}.html', encoding='utf-8').read(), 'html.parser')
    ecran = s.find('div', style=re.compile(r'zoom:\.8041'))
    ecran['style'] = ecran['style'].replace('zoom:.8041;', '')
    s.body.clear(); s.body.append(ecran)
    s.body['style'] = 'margin:0;width:393px;height:852px;overflow:hidden;background:#F2F2F7'
    tmp_html = f'{ICI}/_rendu_{L}_{nn}.html'; tmp_png = f'{ICI}/_rendu_{L}_{nn}.png'
    open(tmp_html, 'w', encoding='utf-8').write(str(s))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=3",
                    "--allow-file-access-from-files", "--window-size=393,852", "--virtual-time-budget=4000",
                    "--screenshot=" + tmp_png, "file://" + tmp_html], capture_output=True, timeout=120)
    run('cwebp', '-q', '90', '-m', '6', '-resize', '900', '0', tmp_png, '-o', dst)
    os.remove(tmp_html); os.remove(tmp_png)

sys.path.insert(0, BANC)
from textes import TITRES
for L in (sys.argv[1:] or list(TITRES)):
    os.makedirs(f'{ICI}/img/{L}', exist_ok=True)
    CLES = [c for c in os.environ.get('CLES', '').split(',') if c]   # CLES=langs : seulement ces écrans
    for k, nn in numeros(L).items():
        if CLES and k not in CLES: continue
        ecran_seul(L, nn, f'{ICI}/img/{L}/{k}.webp')
        print(L, k, nn, flush=True)
