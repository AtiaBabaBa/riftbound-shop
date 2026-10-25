# Jake's Card Shop

A shop page for ready-to-play Riftbound decks, singles and other products, with the shop's meta tier list. It has four tabs: **Home** (the main page: a promotion slider, for now the budget decks, then why Chinese-print cards), **Decks**, **Singles & more** and **Tier list**; each has its own address (`#home`, `#decks`, `#cards`, `#tiers`), so the tier list can be shared as a link. Customers tap what they want (the count then sits on the card's picture, with − and + and a box to type a number), check their list, add a promo code if they have one, and tap **Send order on LINE**: LINE opens a chat with the shop's LINE Official Account with the order already typed (items, copies, prices, promo code, shipping, total, plus their name and note), they send it, and payment is sorted out in the chat. On a computer, the order shows as a QR code to scan with a phone. The page is in Thai or English (it follows the phone's language; there is a switch at the top).

- **Shop:** https://atiabababa.github.io/riftbound-shop/
- **Tier list:** https://atiabababa.github.io/riftbound-shop/#tiers
- **Shopkeeper zone:** https://atiabababa.github.io/riftbound-shop/#keeper (nothing on the shop links to it; `#keeper/cards` and `#keeper/tiers` open its other tabs)

## One-time setup

Prices, stock and products are kept in the Supabase project that also holds the [Riftcheese](https://atiabababa.github.io/riftcheese/) accounts, so the shopkeeper signs in with a Riftcheese username and password.

1. Supabase → **SQL Editor → New query**: paste the contents of [`supabase/shop.sql`](supabase/shop.sql) and click **Run**. It adds the stock, product and tier list tables and a public bucket for product photos. Everyone can read them; only shopkeepers can change them. Safe to run again, and run it again whenever the file changes (the shopkeeper zone says so when the database is behind, e.g. before deck styles, tags and the tier list can be saved).
2. Open the shopkeeper zone and sign in. It says the account can't change stock yet and shows one line of SQL with your account in it: run that line in the SQL Editor too, then click *Check again*. Only accounts added this way can change the shop; nobody can add themselves from the website.

Orders go to the LINE account in `SHOP_CONFIG` at the top of the script in `index.html` (`lineOA` for an Official Account, or `lineId` for a personal ID). The shop name and currency are set there too.

## Shipping, returns and promo codes

- **Shipping:** `shipping` in `SHOP_CONFIG` (now ฿50) is added once to every order, in the list, the order check and the LINE message. `0` makes shipping free.
- **Return policy:** shown in the order check (*Shipping and returns*) and from the link at the bottom of the page. Its text is `policy` in `LANG` in `index.html`, in English and Thai. It says in-stock orders ship within 2 days of payment, every single is Near Mint, which tournament rules allow Chinese-print cards (with a link to Riot's rules), and that wrong or damaged cards are replaced or refunded if reported within 7 days with photos. Single-card details also say *Condition: Near Mint (NM)* (`condNM` in `LANG`). Change them to match how you work.
- **Facebook:** put the page's address in `facebook` in `SHOP_CONFIG` and a link to it shows at the bottom of the page. Empty hides it.
- **Promo codes:** customers type a code in their list, above the subtotal. Codes live in the `shop_promos` table (added by `supabase/shop.sql`; run it again once). Add a row in Supabase → **Table Editor → shop_promos** for each code: `code` in capitals, then `percent_off` (10 = 10% off) or `amount_off` (100 = ฿100 off), and/or `free_shipping`; `min_order` is the smallest order before shipping it works on; `starts_at` / `ends_at` limit the dates (empty = no limit) and unticking `active` turns it off. The discount shows in the total and the code is in the LINE message, so check it there before you take payment. Customers can't list the codes: the shop asks about one code at a time. There is no limit on how many times a code can be used.

## Card fonts

Card names, cost and stats use **Beaufort for LOL Bold**, card types and groups (ELITE, SPIDER, YETI…) **Univers 59**, and card text **Univers 55**, as on the printed cards. These fonts aren't free, so the page doesn't include them: visitors who have them installed see them, and everyone else sees stand-ins (Marcellus, Barlow Condensed and Barlow). If you have a licence to use them on a website, put the `.woff2` files in a `fonts/` folder and their paths in `cardFonts` in `SHOP_CONFIG`.

## Finding cards

The Singles & more tab's filters work like [Rift Atlas](https://riftatlas.com/cards): a search box (name, number or card text), then a **type** menu (tick several: Champion Unit, Unit, Spell, Signature, Gear, Rune, Battlefield, Legend, Other products), the six **domains** plus Colorless (tap several), **cost** (0 to 7+), **sort** (set, name, cost, might, type, domain, price) with a button to reverse it, **grid or list** view (remembered on that device), **EN | 中文** for the card pictures (English or the Chinese print, also remembered), and **All filters** for set, rarity, group and might (and, in the shopkeeper zone, the *Show* menu and price range). Search also finds Chinese names and text.

## Printings and Chinese cards

Every printing of a card is a card of its own in the shop, with its own picture, price and stock: alternate art (`UNL-116a`), overnumbered (`OGN-299`), signature (`OGN-299*`), showcase (`RAD-sp1`), rune art from later sets, starter-deck Legends, and the prints sold only in China (T1 and Arcane bundles, Chinese promos and signatures). A printing shows its version on the tile (e.g. *Alt Art*), in the details and in the LINE message, and is compared with that exact printing on TCGplayer; a Chinese-only print has no comparison.

Every card also has its Chinese print: the Chinese name and card text in the details, and the Chinese picture when **中文** is picked.

They come from `cards/printings.json` and its picture sheets (`cards/v*.webp` for the English printings, `cards/z*.webp` for the Chinese pictures), made by `python scripts/make_printings.py` from the official [card gallery](https://riftbound.leagueoflegends.com/en-us/card-gallery/) and the official Chinese site [playloltcg.com](https://playloltcg.com/card.html). Run it again when a new set comes out (after copying the new `cards/` from Riftcheese); it keeps its downloads in `.cache/`, so only new pictures are fetched. The big pictures in the details load from those two sites. Without the file the shop works as before, with just the cards.

## Adding things to sell

In the shopkeeper zone, changes are saved straight away and show in the shop for everyone; there is nothing to commit.

- **Cards:** the Singles & more tab in the shopkeeper zone shows only the cards you've listed. Tap **+ Add a card** to find any card or printing (search by name, number or Chinese name; pick a version such as *Alt Art*, *Overnumbered*, *Signature* or *Chinese-only prints*, and a set) and tap it; tap a card in your list to change it. The editor shows the card's other printings, to price them too. Each row is one version of that printing:
  - *Version*: leave blank for the card as pictured, or type e.g. `Foil`, `Signed`. **+ Add a version** adds another row with its own price and quantity. (Alternate art, overnumbered and signature cards have their own entries now, with their own pictures; older listings with `Alt Art` as the version still work.)
  - *Price*: per copy, e.g. `120`. Blank shows *Ask price*.
  - *Quantity*: how many you have. `0` shows *Sold out*; blank shows no number.
  - *Description*: anything customers should know, e.g. `Near mint, English, from a sealed booster`.

  Clear a whole row (or delete it) to take that version off sale.
- **Decks** (the Decks tab): tap **+ Add a deck** and fill in the name, price, quantity, description and photo, plus:
  - *Style*: Aggro, Midrange, Control or Combo, shown on the deck with a coloured dot. Customers can filter by it.
  - *Tags*: extra words, e.g. `#kennen #midrange #combo #highroll`. They show under the deck; tapping one shows every deck with that tag. Search finds them too. (Filtering by a style also finds decks tagged with it.)
  - *Deck list*: one card per line under headings (`Legend:`, `Champion:`, `Main Deck:`, `Battlefields:`, `Runes:`), e.g. `3 Falling Star [OGN-029]`. Customers see every card with its picture, the deck's card count, and the Legend as the deck's picture if you don't add a photo. The Legend also puts the deck under the Legend filter and links it with the tier list. The box under the list counts the cards and says if a line matches no card.

  In a deck's details, *See the whole deck on one page* shows every card with its count on the Legend's colours (as in Riftcheese), with the price and add button, and *Save as image* makes a PNG with the shop's name to post or share.

  The Home tab, under the promotion slider, explains why Chinese-print cards are a good buy (tournament legal in identical opaque sleeves, cheaper, 100% genuine from a certified shop, cards shown in English). Its text is `whyTitle` and `why1`–`why4` in `LANG` in `index.html`, in English and Thai.

  The price puts the deck on a shelf: up to ฿1,000 is **Budget Starter** (a first deck for someone without one), ฿1,001–5,000 **Mid-Level** (can win games at events: cheaper takes on strong decks, or top lists that are nearly complete), above ฿5,000 **Tournament Winner** (tier 1 winning lists). A deck without a price shows under *Ask for price*. Change the limits in `deckLevels` in `SHOP_CONFIG`. For a tournament list, say where it won in the description (e.g. `1st place, Bangkok Regional Oct 2026`): it shows under the deck.
- **Other products** (booster boxes, packs, sleeves, playmats…): on the Singles & more tab, tap **+ Add a product** and fill in the name, price, quantity and description, and choose a photo (it's shrunk to 1200 px before uploading). Tap a product in the shop grid to change or delete it. The *Deck / Other product* switch at the top of the editor moves something between the two tabs.
- **Tier list** (the Tier list tab): tap **Edit tier list**, or click a deck in the list to open the editor on it. Drag a Legend's picture from the bottom of the editor onto a tier to add a deck (on a phone: hold the picture, then drag). Drag a deck to reorder it or move it to another tier, or back to the Legends to take it off. Click a deck to give it a name (it's named after its champion until then), a style and an optional note for customers; decks with a note show a dot. Each tier has a name (`Tier 1`, `S`…) and ↑ ↓ to change the order, and the note at the top can say what the list is based on. Saving shows it straight away with today's date. Customers see the decks' Legend pictures and, when you sell decks with that Legend, a link to them; a deck's details also say where its Legend stands in the tier list. Empty tiers are hidden from customers.
- **Lots of cards at once:** *Download as CSV* gives every card with your current prices. Fill in `price`, `qty`, `note` and `description` in Excel or Google Sheets, save as CSV (in Excel, *CSV UTF-8*) and use *Import CSV*. A card's row left blank in the file takes that version off sale; cards missing from the file stay as they are. Products aren't in the CSV.

Customers see only what you've listed: anything with a price, quantity, version name or description. Something with quantity `0` stays in the shop as *Sold out*; to hide it, clear its row (cards) or delete it (products). The shopkeeper zone shows the same listed cards; new ones are found with *+ Add a card*. To organize your listings, the Singles & more tab has, under *All filters*, a *Show* menu (all cards, listed only, shown to customers, hidden because they're not cheaper than TCGplayer, no TCGplayer price, no price), each with how many cards it holds; a *Min ฿ – Max ฿* price range; and the sort *Price vs TCGplayer*, which puts the cards furthest above TCGplayer on top. Hidden cards say how far above TCGplayer they are, e.g. *Hidden · 24% above*. Set `showAllCards: true` in `SHOP_CONFIG` to let customers also ask about unlisted cards. The *Setup check* at the bottom of the shopkeeper zone shows which LINE account orders go to and where the stock is read from.

## TCGplayer price comparison

Cards and decks show what the same cards cost on TCGplayer, in baht, so customers can see the shop is cheaper:

- **Tiles:** under the price, e.g. `TCGplayer ฿6,465 · Save 26%`, shown where the shop is cheaper. In the shopkeeper zone every tile shows its TCGplayer price, as a pricing guide.
- **Details:** the TCGplayer price, what the customer saves, the date of the prices and the exchange rate used.
- **The list:** "You save ฿… compared with TCGplayer" for everything in it that has a price on both.
- **Shopkeeper editors:** the card editor shows the card's TCGplayer price (normal, alternate art, overnumbered…), and the deck editor shows the TCGplayer value of the pasted list.

Singles that cost the same or more here than on TCGplayer are hidden from customers (`hideNotCheaper` in `SHOP_CONFIG`; `false` shows them again). A *Save X%* chip shows only when the saving is at least `minSave` percent (10); smaller savings show just the TCGplayer price. The shopkeeper zone still shows them, marked *Hidden: not cheaper*. TCGplayer prices change daily, so a card comes back by itself once it's cheaper here again, or when you lower its price. Cards TCGplayer has no price for (e.g. Chinese-only alt arts) and decks are always shown.

A card is compared with its own printing: the version name picks it (`Alt Art` → TCGplayer's Alternate Art, also `Overnumbered`, `Signature`, `Metal`; `Normal`, `Foil` or blank → the plain card, foil price for `Foil`). A version TCGplayer doesn't sell (e.g. a Chinese-only alt art) shows no comparison. A deck counts every card in its list at that card's cheapest printing on TCGplayer.

Prices are TCGplayer market prices in US dollars with the dollar-to-baht rate, from [Riftcheese's `cards/prices.json`](https://atiabababa.github.io/riftcheese/cards/prices.json), which a GitHub Action there refreshes every day (`tcgPrices` in `SHOP_CONFIG`; empty turns the comparison off). If that file can't be read, the shop works as before without it.

## Files

- `index.html` – the shop and its shopkeeper zone (everything is in this one page).
- `supabase/shop.sql` – the stock, product, tier list (`shop_docs`) and shopkeeper tables, the photo bucket and who may change what.
- `stock.csv` – a fallback price list, read only until `supabase/shop.sql` has been run or when the cloud can't be reached. `python scripts/make_stock_csv.py` writes it (one row per card) and adds rows for new cards while keeping what's filled in.
- `cards/` – card data (`cards.json`) and picture sheets, copied from Riftcheese. Copy them again when new sets are added there. `printings.json` with the `v*.webp` and `z*.webp` sheets holds the other printings and the Chinese cards (`scripts/make_printings.py`).
- `og.png` – the picture LINE, Facebook and X show when the shop link is shared (the `og:` tags at the top of `index.html`). `python scripts/make_og_image.py` draws it again. If the shop moves to its own domain, change the two addresses in those tags.

## Credits

Card data from [Riftcodex](https://riftcodex.com) and the official [Riftbound card gallery](https://riftbound.leagueoflegends.com/en-us/card-gallery/); Chinese cards from the official Chinese site [playloltcg.com](https://playloltcg.com/card.html). Riftbound, its cards and card images are the property of Riot Games. This shop is not affiliated with Riot Games.
