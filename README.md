# Jake's Card Shop

A shop page for ready-to-play Riftbound decks, singles and other products, with the shop's meta tier list. It has three tabs: **Decks** (the main page), **Singles & more** and **Tier list**; each has its own address (`#decks`, `#cards`, `#tiers`), so the tier list can be shared as a link. Customers tap what they want, check their list and tap **Send order on LINE**: LINE opens a chat with the shop's LINE Official Account with the order already typed (items, copies, prices, total, plus their name and note), they send it, and payment and shipping are sorted out in the chat. On a computer, the order shows as a QR code to scan with a phone. The page is in Thai or English (it follows the phone's language; there is a switch at the top).

- **Shop:** https://atiabababa.github.io/riftbound-shop/
- **Tier list:** https://atiabababa.github.io/riftbound-shop/#tiers
- **Shopkeeper zone:** https://atiabababa.github.io/riftbound-shop/#keeper (nothing on the shop links to it; `#keeper/cards` and `#keeper/tiers` open its other tabs)

## One-time setup

Prices, stock and products are kept in the Supabase project that also holds the [Riftcheese](https://atiabababa.github.io/riftcheese/) accounts, so the shopkeeper signs in with a Riftcheese username and password.

1. Supabase → **SQL Editor → New query**: paste the contents of [`supabase/shop.sql`](supabase/shop.sql) and click **Run**. It adds the stock, product and tier list tables and a public bucket for product photos. Everyone can read them; only shopkeepers can change them. Safe to run again, and run it again whenever the file changes (the shopkeeper zone says so when the database is behind, e.g. before deck styles, tags and the tier list can be saved).
2. Open the shopkeeper zone and sign in. It says the account can't change stock yet and shows one line of SQL with your account in it: run that line in the SQL Editor too, then click *Check again*. Only accounts added this way can change the shop; nobody can add themselves from the website.

Orders go to the LINE account in `SHOP_CONFIG` at the top of the script in `index.html` (`lineOA` for an Official Account, or `lineId` for a personal ID). The shop name and currency are set there too.

## Adding things to sell

In the shopkeeper zone, changes are saved straight away and show in the shop for everyone; there is nothing to commit.

- **Cards:** search or filter for a card and tap it. Each row is one version of the card:
  - *Version*: leave blank for the normal card, or type e.g. `Foil`, `Alt art`, `Signed`. **+ Add a version** adds another row with its own price and quantity.
  - *Price*: per copy, e.g. `120`. Blank shows *Ask price*.
  - *Quantity*: how many you have. `0` shows *Sold out*; blank shows no number.
  - *Description*: anything customers should know, e.g. `Near mint, English, from a sealed booster`.

  Clear a whole row (or delete it) to take that version off sale.
- **Decks** (the Decks tab): tap **+ Add a deck** and fill in the name, price, quantity, description and photo, plus:
  - *Style*: Aggro, Midrange, Control or Combo, shown on the deck with a coloured dot. Customers can filter by it.
  - *Tags*: extra words, e.g. `#kennen #midrange #combo #highroll`. They show under the deck; tapping one shows every deck with that tag. Search finds them too. (Filtering by a style also finds decks tagged with it.)
  - *Deck list*: one card per line under headings (`Legend:`, `Champion:`, `Main Deck:`, `Battlefields:`, `Runes:`), e.g. `3 Falling Star [OGN-029]`. Customers see every card with its picture, the deck's card count, and the Legend as the deck's picture if you don't add a photo. The Legend also puts the deck under the Legend filter and links it with the tier list. The box under the list counts the cards and says if a line matches no card.

  The price puts the deck on a shelf: up to ฿1,000 is **Budget Starter** (a first deck for someone without one), ฿1,001–5,000 **Mid-Level** (can win games at events: cheaper takes on strong decks, or top lists that are nearly complete), above ฿5,000 **Tournament Winner** (tier 1 winning lists). A deck without a price shows under *Ask for price*. Change the limits in `deckLevels` in `SHOP_CONFIG`. For a tournament list, say where it won in the description (e.g. `1st place, Bangkok Regional Oct 2026`): it shows under the deck.
- **Other products** (booster boxes, packs, sleeves, playmats…): on the Singles & more tab, tap **+ Add a product** and fill in the name, price, quantity and description, and choose a photo (it's shrunk to 1200 px before uploading). Tap a product in the shop grid to change or delete it. The *Deck / Other product* switch at the top of the editor moves something between the two tabs.
- **Tier list** (the Tier list tab): tap **Edit tier list**. Each tier has a name (`Tier 1`, `S`…), and each deck in it has a Legend, a name, a style and an optional note for customers. ↑ ↓ change the order, the tier menu moves a deck to another tier, and the note at the top can say what the list is based on. Saving shows it straight away with today's date. Customers see the decks' Legend pictures and, when you sell decks with that Legend, a link to them; a deck's details also say where its Legend stands in the tier list. Empty tiers are hidden from customers.
- **Lots of cards at once:** *Download as CSV* gives every card with your current prices. Fill in `price`, `qty`, `note` and `description` in Excel or Google Sheets, save as CSV (in Excel, *CSV UTF-8*) and use *Import CSV*. A card's row left blank in the file takes that version off sale; cards missing from the file stay as they are. Products aren't in the CSV.

Customers see only what you've listed: anything with a price, quantity, version name or description. Something with quantity `0` stays in the shop as *Sold out*; to hide it, clear its row (cards) or delete it (products). In the shopkeeper zone every card shows, so you can find new ones to list; tick *Listed only* to see just yours. Set `showAllCards: true` in `SHOP_CONFIG` to let customers also ask about unlisted cards. The *Setup check* at the bottom of the shopkeeper zone shows which LINE account orders go to and where the stock is read from.

## Files

- `index.html` – the shop and its shopkeeper zone (everything is in this one page).
- `supabase/shop.sql` – the stock, product, tier list (`shop_docs`) and shopkeeper tables, the photo bucket and who may change what.
- `stock.csv` – a fallback price list, read only until `supabase/shop.sql` has been run or when the cloud can't be reached. `python scripts/make_stock_csv.py` writes it (one row per card) and adds rows for new cards while keeping what's filled in.
- `cards/` – card data (`cards.json`) and picture sheets, copied from Riftcheese. Copy them again when new sets are added there.

## Credits

Card data from [Riftcodex](https://riftcodex.com) and the official [Riftbound card gallery](https://riftbound.leagueoflegends.com/en-us/card-gallery/). Riftbound, its cards and card images are the property of Riot Games. This shop is not affiliated with Riot Games.
