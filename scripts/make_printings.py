"""Write cards/printings.json and its picture sheets: the other printings of the cards in cards/cards.json
(alternate art, overnumbered, signature, showcase, runes from later sets) and the Chinese version of every card.

- English printings come from the official card gallery (riftbound.leagueoflegends.com/en-us/card-gallery/), which
  lists every printing with its picture. A printing is linked to its card by name; one with no card in cards.json
  (a new card, a showcase card, a token) is kept with its own card details.
- Chinese names, text and pictures come from playloltcg.com, the official Chinese Riftbound site. A Chinese card is
  matched by its number ("UNL-089/219" is unl-089-219, "RAD·173*/167" the signature rad-173-star-167); Chinese-only
  printings (T1 and Arcane bundles, Chinese promos…) are linked by their Chinese name to a card matched that way.

Thumbnails go in sprite sheets next to cards.json, like the ones copied from Riftcheese: cards/v*.webp for English
printings and cards/z*.webp for the Chinese pictures (vl*/zl* for landscape battlefields). The big pictures in the
shop's card details load from the two sites. Downloads are kept in .cache/ so running it again only fetches new cards.
Run from the repository root:  python scripts/make_printings.py
"""
import hashlib
import io
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from PIL import Image

GALLERY = 'https://riftbound.leagueoflegends.com/en-us/card-gallery/'
CN_API = 'https://lol-api.playloltcg.com/xcx/card/searchCardCraftWeb'
CACHE = Path('.cache/printings')
OUT = Path('cards/printings.json')
PORTRAIT, LANDSCAPE = (200, 279), (279, 200)  # thumbnail size, as in the Riftcheese sheets
GRID = {PORTRAIT: (10, 10), LANDSCAPE: (8, 8)}  # columns, rows per sheet
HEADERS = {'User-Agent': 'Mozilla/5.0 (riftbound-shop printings; +https://github.com/AtiaBabaBa/riftbound-shop)'}
# Chinese rarity of a printing ("extendRarityName") → its version in the shop
CN_VERSION = {'异画': 'Alt Art', '超编': 'Overnumbered', '签名超编': 'Signature'}


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={**HEADERS, **({'Content-Type': 'application/json'} if data else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def cached(url):
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest() + '.img')
    if not f.exists():
        f.write_bytes(get(url))
    return f.read_bytes()


def card_key(s):
    # cardKey() in index.html: "Jinx, Loose Cannon" and "Jinx - Loose Cannon" are both "jinx - loose cannon"
    s = re.sub(r'\s*\([^)]*\)\s*$', '', s)
    return re.sub(r'\s+', ' ', re.sub(r',\s+', ' - ', s)).strip().lower()


def plain(html):
    s = re.sub(r'<br\s*/?>', '\n', html or '')
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'").strip()


def gallery():
    html = get(GALLERY).decode('utf-8')
    data = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))
    for blade in data['props']['pageProps']['page']['blades']:
        items = (blade.get('cards') or {}).get('items')
        if items:
            return items
    sys.exit('No cards found in the card gallery page; its layout may have changed.')


def chinese():
    out, page = [], 1
    while True:
        body = json.dumps({'pageNum': page, 'pageSize': 200, 'searchContent': '', 'cardCategoryList': [],
                           'cardColorList': [], 'rarityList': [], 'productCodeList': []}).encode()
        res = json.loads(get(CN_API, body))['result']
        out += res['list']
        if not res['list'] or len(out) >= res['total']:
            return out
        page += 1


def version(gid, total):
    # What a printing's id says it is: unl-116a-219 alternate art, sfd-227-star-221 signature, rad-sp1-005 showcase…
    rest = gid.split('-')[1:]
    if 'star' in rest:
        return 'Signature'
    n = rest[0]
    if re.fullmatch(r'sp\d+', n):
        return 'Showcase'
    if re.fullmatch(r't\d+', n):
        return 'Token'
    if re.fullmatch(r'r\d+[a-z]', n) or re.fullmatch(r'\d+[a-z]', n):
        return 'Alt Art'
    if re.fullmatch(r'r\d+', n):
        return 'Rune art'
    if n.isdigit() and total and int(n) > total:
        return 'Overnumbered'
    return ''


def main():
    sys.stdout.reconfigure(encoding='utf-8')  # Chinese card names in the messages
    base = json.loads(Path('cards/cards.json').read_text(encoding='utf-8'))
    img_base = base['imgBase']
    cards = base['cards']
    by_id, by_key = {}, {}
    for c in cards:  # a Legend is listed by title and in full; keep the full one ("Ambessa - Matriarch of War")
        if c['id'] not in by_id or ' - ' in c['k']:
            by_id[c['id']] = c
        by_key.setdefault(c['k'], c)

    # ---------- English printings ----------
    prints = []
    for g in gallery():
        gid = g['id']
        if gid in by_id:
            continue
        name = g['name'] + (' - ' + g['subtitle'] if g.get('subtitle') else '')
        total = int(gid.rsplit('-', 1)[1]) if re.fullmatch(r'\d+', gid.rsplit('-', 1)[1]) else 0
        s = gid.split('-')[0].upper()
        u = g['cardImage']['url'].split('?')[0].replace(img_base, '')
        p = {'id': gid, 'v': version(gid, total), 'r': g['rarity']['value']['label'], 's': [s], 'u': u}
        types = [t['label'] for t in g['cardType']['type']]
        # Legends go by their title alone ("Nine-Tailed Fox" is Ahri - Nine-Tailed Fox)
        legend = lambda t: next((c for k, c in by_key.items() if c['t'] == 'Legend' and k.endswith(' - ' + card_key(t))), None)
        of = by_key.get(card_key(name)) or legend(name) or legend(g['name'])
        if of and of['t'] in types:
            p['of'] = of['id']
            p['v'] = p['v'] or g.get('subtitle') if of['k'] != card_key(name) else p['v']  # "Starter" for the starter-deck Legends
        else:  # no card for it in cards.json: keep its own details
            tags = (g.get('tags') or {}).get('tags') or []
            p.update({'k': card_key(name), 'n': name, 't': types[-1] if types else 'Other', 'd': [d['label'] for d in g['domain']['values']],
                      'x': plain((g.get('text') or {}).get('richText', {}).get('body')), 'g': tags})
            if len(types) > 1:
                p['st'] = types[0]
            for f, k in (('energy', 'e'), ('might', 'm'), ('power', 'p')):
                if g.get(f):
                    p[k] = g[f]['value']['id']
        prints.append(p)
    known = set(by_id) | {p['id'] for p in prints}
    root = lambda i: next((p.get('of') for p in prints if p['id'] == i), None) or i

    # ---------- Chinese ----------
    zh, cn_only, by_cn_name = {}, [], {}
    cn = chinese()
    for c in cn:
        no = c['cardNo'].replace('·', '-').lower()
        m = re.fullmatch(r'([a-z0-9]+)-((?:sp|[rt])?\d+[a-z]?)(\*?)(?:/(\d+))?', no)
        gid = None
        if m:
            s, n, star, total = m.groups()
            cand = [f'{s}-{n}-star-{total}' if star else f'{s}-{n}-{total}'] if total else \
                [i for i in known if i.startswith(f'{s}-{n}-' if not star else f'{s}-{n}-star-') or i == f'{s}-{n}']
            gid = next((i for i in cand if i in known), None)
        entry = {'n': c['cardName'] + (' · ' + c['subTitle'] if c.get('subTitle') else ''), 'x': (c.get('cardEffect') or '').strip(), 'z': c['frontImage']}
        if gid:
            zh[gid] = entry
            by_cn_name.setdefault((c['cardName'], c.get('subTitle') or ''), root(gid))
        else:
            cn_only.append((c, entry))
    for c, entry in cn_only:  # Chinese-only printings, linked by name
        of = by_cn_name.get((c['cardName'], c.get('subTitle') or ''))
        if not of:
            print(f"  no English card for {c['cardNo']} {c['cardName']} {c.get('subTitle') or ''}")
            continue
        pid = 'zh-' + re.sub(r'[^a-z0-9]+', '-', c['cardNo'].replace('*', ' star ').lower()).strip('-')
        s = re.split(r'[·\-]', c['cardNo'])[0].upper()
        prints.append({'id': pid, 'of': of, 'v': CN_VERSION.get(c.get('extendRarityName'), s + ' print'), 'r': 'Showcase' if c.get('extendRarityName') in CN_VERSION else '',
                       's': [s], 'u': '', 'cn': 1})
        zh[pid] = entry

    # ---------- pictures ----------
    CACHE.mkdir(parents=True, exist_ok=True)
    jobs = [('v', p['id'], f"{img_base}{p['u']}?w=300&fm=webp") for p in prints if p['u']] + [('z', i, e['z']) for i, e in zh.items()]
    print(f'{len(prints)} printings, {len(zh)} Chinese cards; fetching {len(jobs)} pictures…')

    def thumb(job):
        try:
            im = Image.open(io.BytesIO(cached(job[2]))).convert('RGBA').convert('RGB')
        except Exception as e:
            print(f'  no picture for {job[1]}: {e}')
            return None
        size = LANDSCAPE if im.width > im.height else PORTRAIT
        return job, im.resize(size, Image.LANCZOS)
    with ThreadPoolExecutor(16) as ex:
        thumbs = [r for r in ex.map(thumb, jobs) if r]

    sheets, place = [], {}
    for kind in ('v', 'z'):
        for size in (PORTRAIT, LANDSCAPE):
            group = [(job, im) for job, im in thumbs if job[0] == kind and im.size == size]
            cols, rows = GRID[size]
            for n, start in enumerate(range(0, len(group), cols * rows)):
                part = group[start:start + cols * rows]
                r = (len(part) + cols - 1) // cols
                name = f"cards/{kind}{'l' if size == LANDSCAPE else ''}{n}.webp"
                sheet = Image.new('RGB', (size[0] * cols, size[1] * r))
                for i, (job, im) in enumerate(part):
                    sheet.paste(im, ((i % cols) * size[0], (i // cols) * size[1]))
                    place[(job[0], job[1])] = [len(sheets), i]
                sheet.save(name, 'WEBP', quality=80, method=6)
                sheets.append({'f': name, 'w': size[0], 'h': size[1], 'c': cols, 'r': r})
    for old in Path('cards').glob('[vz]*.webp'):  # sheets left over from a run with more pictures
        if old.as_posix() not in {s['f'] for s in sheets}:
            old.unlink()

    for p in prints:
        p['im'] = place.get(('v', p['id'])) or place.get(('z', p['id']))
    prints = [p for p in prints if p['im']]
    for i, e in zh.items():
        e['im'] = place.get(('z', i))
    out = {'source': 'Official card gallery (riftbound.leagueoflegends.com) and playloltcg.com (Chinese)', 'fetched': date.today().isoformat(),
           'sheets': sheets, 'prints': prints, 'zh': zh}
    body = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
    OUT.write_text(body + '\n', encoding='utf-8', newline='\n')
    print(f'{OUT} written: {len(prints)} printings ({sum(1 for p in prints if "of" not in p)} without a card in cards.json), '
          f'{len(zh)} Chinese cards, {len(sheets)} sheets')


if __name__ == '__main__':
    main()
