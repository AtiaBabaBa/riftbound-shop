"""Write stock.csv: the fallback price list for the shop (index.html), one row per card.

The shop reads its stock from the cloud (the shopkeeper zone, #keeper) once supabase/shop.sql has been run; this file
is only read until then, or when the cloud can't be reached. The shopkeeper zone's Download as CSV and Import CSV use
the same columns, so this file can also be filled in and imported there.

Open it in Excel or Google Sheets and fill in, for each card you sell:
  price  price per copy, a plain number (120). Blank = the shop shows "Ask price".
  qty    how many copies you have. Blank = no limit shown; 0 = sold out.
  note   optional, shown on the card (Foil, Alt art, Signed, Played...).
  description  optional, the shop's own words about this copy (condition, language...).
To sell two versions of one card (normal and foil), copy its row and give each copy a different note.
The id and name columns say which card a row is; set and rarity are only there to help sorting and filtering.
Save it as CSV (in Excel, "CSV UTF-8" keeps Thai text readable).

Running this again keeps your prices, quantities, notes and descriptions and adds rows for cards that are new in
cards/cards.json. Run from the repository root:  python scripts/make_stock_csv.py
"""
import csv
import json
import re
from pathlib import Path

OUT = Path('stock.csv')
COLS = ['id', 'name', 'set', 'rarity', 'price', 'qty', 'note', 'description']
SET_ORDER = ['rad', 'ven', 'unl', 'sfd', 'ogn', 'ogs', 'opp']  # newest first, by the set in a card's number, as the shop sorts


def card_key(s):
    # Same as cardKey in the pages: "Akali, Deadly Weapon" and "akali - deadly weapon" are one card.
    s = re.sub(r'\s*\([^)]*\)\s*$', '', str(s or ''))
    return re.sub(r'\s+', ' ', re.sub(r',\s+', ' - ', s).strip()).lower()


def rank(card_id):
    s, n = (card_id.split('-') + ['', ''])[:2]
    m = re.match(r'\d+', n)
    return (SET_ORDER.index(s) if s in SET_ORDER else len(SET_ORDER), int(m.group()) if m else 0, card_id)


def read_existing():
    if not OUT.exists():
        return []
    raw = OUT.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp874')  # Excel's plain "CSV" on Thai Windows
    first = text.splitlines()[0] if text else ''
    delim = max([',', ';', '\t'], key=first.count)
    rows = list(csv.DictReader(text.splitlines(), delimiter=delim))
    return [{(k or '').strip().lower(): (v or '').strip() for k, v in r.items()} for r in rows]


cards = json.loads(Path('cards/cards.json').read_text(encoding='utf-8'))['cards']
# Some Legends are listed twice, by title only ("Matriarch of War") and in full ("Ambessa - Matriarch of War"); keep the full one.
legends = [c for c in cards if c['t'] == 'Legend']
alias = {c['k'] for c in legends if ' - ' not in c['k'] and any(x['k'].endswith(' - ' + c['k']) for x in legends)}
cards = [c for c in cards if c['k'] not in alias]
by_id = {c['id']: c for c in cards}
by_name = {c['k']: c for c in cards}

kept, unmatched = {}, []
for r in read_existing():
    if not (r.get('price') or r.get('qty') or r.get('note') or r.get('description')):
        continue
    cid = re.sub(r'[\s/]+', '-', r.get('id', '').lower())
    c = by_id.get(cid) or by_name.get(card_key(r.get('name')))
    if not c:
        unmatched.append(r)
        continue
    kept.setdefault(c['id'], []).append(r)

rows = []
for c in sorted(cards, key=lambda c: rank(c['id'])):
    base = {'id': c['id'], 'name': c['n'], 'set': c['id'].split('-')[0].upper(), 'rarity': c['r']}
    for r in kept.get(c['id']) or [{}]:
        rows.append({**base, 'price': r.get('price', ''), 'qty': r.get('qty', ''), 'note': r.get('note', ''), 'description': r.get('description', '')})
rows += [{k: r.get(k, '') for k in COLS} for r in unmatched]  # never drop what the seller typed

with OUT.open('w', encoding='utf-8-sig', newline='') as f:  # the BOM makes Excel read it as UTF-8
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(f'{OUT} written: {len(rows)} rows, {sum(len(v) for v in kept.values())} with a price, quantity or note kept')
for r in unmatched:
    print(f"  kept at the end, no card matches: {r.get('id') or ''} {r.get('name') or ''}".rstrip())
