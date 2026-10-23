"""Make og.png, the picture LINE, Facebook and others show when the shop link is shared.

Run from the repo root:  python scripts/make_og_image.py
Needs Pillow and the Windows fonts Georgia and Segoe UI (change FONTS for other systems).
"""
import json
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
BG, INK, MUTED, TEAL, GOLD = (16, 19, 26), (236, 239, 243), (160, 170, 186), (70, 195, 199), (217, 168, 76)
FONTS = {'title': 'C:/Windows/Fonts/georgiab.ttf', 'body': 'C:/Windows/Fonts/segoeui.ttf', 'bold': 'C:/Windows/Fonts/segoeuib.ttf'}
LEGENDS = ['Lux - Lady of Luminosity', 'Ahri - Nine-Tailed Fox', "Kai'Sa - Daughter of the Void", 'Jinx - Loose Cannon', 'Akali - Rogue Assassin']

data = json.load(open('cards/cards.json', encoding='utf-8'))
cards = {c['n']: c for c in data['cards']}


def card_picture(name):
    sheet_i, cell = cards[name]['im']
    s = data['sheets'][sheet_i]
    x, y = cell % s['c'] * s['w'], cell // s['c'] * s['h']
    return Image.open(s['f']).convert('RGBA').crop((x, y, x + s['w'], y + s['h']))


def rounded(im, r=12):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r, fill=255)
    im.putalpha(mask)
    return im


img = Image.new('RGB', (W, H), BG)
glow = Image.new('RGB', (W, H), BG)
ImageDraw.Draw(glow).ellipse((700, 40, 1260, 600), fill=(24, 52, 60))
img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(120)), 1)

# a fan of Legend cards on the right, the middle one on top
centre, step = 870, 88
order = [0, 4, 1, 3, 2]
for i in order:
    off = i - 2
    card = rounded(card_picture(LEGENDS[i]).resize((220, 307), Image.LANCZOS))
    card = card.rotate(-off * 7, resample=Image.BICUBIC, expand=True)
    shadow = Image.new('RGBA', card.size, (0, 0, 0, 0))
    shadow.putalpha(card.getchannel('A').point(lambda a: a * 0.55))
    x, y = centre + off * step - card.width // 2, 160 + abs(off) * 18
    img.paste(Image.new('RGB', card.size, (0, 0, 0)), (x + 6, y + 12), shadow.getchannel('A').filter(ImageFilter.GaussianBlur(10)))
    img.paste(card, (x, y), card)

d = ImageDraw.Draw(img)
font = lambda k, size: ImageFont.truetype(FONTS[k], size)

# the shop's hexagon mark
hx, hy, r = 92, 118, 30
hexagon = [(hx, hy - r), (hx + r * .87, hy - r / 2), (hx + r * .87, hy + r / 2), (hx, hy + r), (hx - r * .87, hy + r / 2), (hx - r * .87, hy - r / 2)]
d.polygon(hexagon, outline=TEAL, width=4)
d.line([(hx, hy - 15), (hx, hy + 15)], fill=GOLD, width=4)

d.text((140, 96), 'RIFTBOUND', font=font('bold', 30), fill=TEAL)
d.text((60, 170), "Jake's", font=font('title', 84), fill=INK)
d.text((60, 262), 'Card Shop', font=font('title', 84), fill=INK)
lines = ['Ready-to-play decks, singles', 'and the meta tier list']
for i, line in enumerate(lines):
    d.text((62, 392 + i * 46), line, font=font('body', 36), fill=MUTED)
d.rounded_rectangle((60, 510, 420, 568), 29, fill=GOLD)
d.text((240, 539), 'Order on LINE', font=font('bold', 30), fill=BG, anchor='mm')

img.save('og.png', optimize=True)
print('wrote og.png', img.size)
