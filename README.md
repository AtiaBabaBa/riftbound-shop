# Jake's Card Shop

A shop page for Riftbound singles and other products. Customers tap what they want, check their list and tap **Send order on LINE**: LINE opens a chat with the shop's LINE Official Account with the order already typed (items, copies, prices, total, plus their name and note), they send it, and payment and shipping are sorted out in the chat. On a computer, the order shows as a QR code to scan with a phone. The page is in Thai or English (it follows the phone's language; there is a switch at the top).

- **Shop:** https://atiabababa.github.io/riftbound-shop/
- **Shopkeeper zone:** https://atiabababa.github.io/riftbound-shop/#keeper (nothing on the shop links to it)

## One-time setup

Prices, stock and products are kept in the Supabase project that also holds the [Riftcheese](https://atiabababa.github.io/riftcheese/) accounts, so the shopkeeper signs in with a Riftcheese username and password.

1. Supabase → **SQL Editor → New query**: paste the contents of [`supabase/shop.sql`](supabase/shop.sql) and click **Run**. It adds the stock and product tables and a public bucket for product photos. Everyone can read them; only shopkeepers can change them. Safe to run again.
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
- **Other products** (booster boxes, packs, sleeves, playmats…): tap **+ Add a product** and fill in the name, price, quantity and description, and choose a photo (it's shrunk to 1200 px before uploading). Tap a product in the shop grid to change or delete it.
- **Lots of cards at once:** *Download as CSV* gives every card with your current prices. Fill in `price`, `qty`, `note` and `description` in Excel or Google Sheets, save as CSV (in Excel, *CSV UTF-8*) and use *Import CSV*. A card's row left blank in the file takes that version off sale; cards missing from the file stay as they are. Products aren't in the CSV.

Customers see only what you've listed: anything with a price, quantity, version name or description. Something with quantity `0` stays in the shop as *Sold out*; to hide it, clear its row (cards) or delete it (products). In the shopkeeper zone every card shows, so you can find new ones to list; tick *Listed only* to see just yours. Set `showAllCards: true` in `SHOP_CONFIG` to let customers also ask about unlisted cards. The *Setup check* at the bottom of the shopkeeper zone shows which LINE account orders go to and where the stock is read from.

## Files

- `index.html` – the shop and its shopkeeper zone (everything is in this one page).
- `supabase/shop.sql` – the stock, product and shopkeeper tables, the photo bucket and who may change what.
- `stock.csv` – a fallback price list, read only until `supabase/shop.sql` has been run or when the cloud can't be reached. `python scripts/make_stock_csv.py` writes it (one row per card) and adds rows for new cards while keeping what's filled in.
- `cards/` – card data (`cards.json`) and picture sheets, copied from Riftcheese. Copy them again when new sets are added there.

## Credits

Card data from [Riftcodex](https://riftcodex.com) and the official [Riftbound card gallery](https://riftbound.leagueoflegends.com/en-us/card-gallery/). Riftbound, its cards and card images are the property of Riot Games. This shop is not affiliated with Riot Games.
