-- Riftbound shop (index.html): prices, stock, products (decks included) and the meta tier list, edited in the shopkeeper zone (#keeper).
-- Run once in Supabase → SQL Editor → New query → paste → Run. Safe to run again.
-- Then make your account the shopkeeper with the line at the bottom (the shopkeeper zone shows it filled in).

-- Cards on sale: one row per card version. note is '' for the normal version, or e.g. 'Foil' for another one.
-- price null = "Ask price"; qty null = no number shown, 0 = sold out; descr = the shop's own description.
create table if not exists public.shop_stock (
  card_id    text not null check (char_length(card_id) between 3 and 40),
  note       text not null default '' check (char_length(note) <= 40),
  price      numeric(10, 2) check (price >= 0),
  qty        integer check (qty >= 0),
  updated_at timestamptz not null default now(),
  primary key (card_id, note)
);
alter table public.shop_stock add column if not exists descr text not null default '' check (char_length(descr) <= 1000);

-- The shopkeeper's own products (decks, booster boxes, packs, sleeves…). image is a path in the "shop" storage bucket, or ''.
create table if not exists public.shop_products (
  id         uuid primary key default gen_random_uuid(),
  name       text not null check (char_length(name) between 1 and 80),
  price      numeric(10, 2) check (price >= 0),
  qty        integer check (qty >= 0),
  descr      text not null default '' check (char_length(descr) <= 1000),
  image      text not null default '' check (char_length(image) <= 200),
  sort       integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
-- For decks: the deck list, one card per line ("3 Falling Star [OGN-029]" under "Legend:", "Main Deck:"… headings).
alter table public.shop_products add column if not exists deck text not null default '' check (char_length(deck) <= 4000);
-- Decks (the Decks tab): kind 'deck' marks a deck without a deck list (a list makes a product a deck anyway); style is how
-- it plays ('aggro', 'midrange', 'control', 'combo'); tags are extra words customers can tap, like 'kennen highroll'.
alter table public.shop_products add column if not exists kind text not null default '' check (char_length(kind) <= 20);
alter table public.shop_products add column if not exists style text not null default '' check (char_length(style) <= 20);
alter table public.shop_products add column if not exists tags text not null default '' check (char_length(tags) <= 300);

-- Pages the shopkeeper edits as a whole. 'tierlist' is the meta tier list (the Tier list tab):
-- { note, tiers: [{ name, decks: [{ name, legend, style, note }] }] }, top tier first.
create table if not exists public.shop_docs (
  id         text primary key check (char_length(id) between 1 and 40),
  data       jsonb not null default '{}'::jsonb check (pg_column_size(data) <= 200000),
  updated_at timestamptz not null default now()
);

-- Accounts allowed to change the shop. Nobody can add themselves: rows are added here in the SQL Editor.
create table if not exists public.shop_keepers (
  user_id uuid primary key references auth.users (id) on delete cascade
);

alter table public.shop_stock enable row level security;
alter table public.shop_products enable row level security;
alter table public.shop_keepers enable row level security;
alter table public.shop_docs enable row level security;
grant select on public.shop_stock, public.shop_products, public.shop_docs to anon, authenticated;
grant insert, update, delete on public.shop_stock, public.shop_products, public.shop_docs to authenticated;
grant select on public.shop_keepers to authenticated;

-- Is the signed-in account a shopkeeper?
create or replace function public.is_shop_keeper() returns boolean
language sql stable security invoker set search_path = public as $$
  select exists (select 1 from public.shop_keepers k where k.user_id = auth.uid());
$$;
grant execute on function public.is_shop_keeper() to authenticated;

-- Everyone (the shop's customers) can read the stock and products; only shopkeepers can change them.
drop policy if exists "shop_stock read" on public.shop_stock;
drop policy if exists "shop_stock keeper insert" on public.shop_stock;
drop policy if exists "shop_stock keeper update" on public.shop_stock;
drop policy if exists "shop_stock keeper delete" on public.shop_stock;
create policy "shop_stock read" on public.shop_stock for select to anon, authenticated using (true);
create policy "shop_stock keeper insert" on public.shop_stock for insert to authenticated with check (public.is_shop_keeper());
create policy "shop_stock keeper update" on public.shop_stock for update to authenticated using (public.is_shop_keeper()) with check (public.is_shop_keeper());
create policy "shop_stock keeper delete" on public.shop_stock for delete to authenticated using (public.is_shop_keeper());

drop policy if exists "shop_products read" on public.shop_products;
drop policy if exists "shop_products keeper insert" on public.shop_products;
drop policy if exists "shop_products keeper update" on public.shop_products;
drop policy if exists "shop_products keeper delete" on public.shop_products;
create policy "shop_products read" on public.shop_products for select to anon, authenticated using (true);
create policy "shop_products keeper insert" on public.shop_products for insert to authenticated with check (public.is_shop_keeper());
create policy "shop_products keeper update" on public.shop_products for update to authenticated using (public.is_shop_keeper()) with check (public.is_shop_keeper());
create policy "shop_products keeper delete" on public.shop_products for delete to authenticated using (public.is_shop_keeper());

drop policy if exists "shop_docs read" on public.shop_docs;
drop policy if exists "shop_docs keeper insert" on public.shop_docs;
drop policy if exists "shop_docs keeper update" on public.shop_docs;
drop policy if exists "shop_docs keeper delete" on public.shop_docs;
create policy "shop_docs read" on public.shop_docs for select to anon, authenticated using (true);
create policy "shop_docs keeper insert" on public.shop_docs for insert to authenticated with check (public.is_shop_keeper());
create policy "shop_docs keeper update" on public.shop_docs for update to authenticated using (public.is_shop_keeper()) with check (public.is_shop_keeper());
create policy "shop_docs keeper delete" on public.shop_docs for delete to authenticated using (public.is_shop_keeper());

-- A signed-in account can see whether it is a shopkeeper (the zone checks this), and nothing more.
drop policy if exists "shop_keepers own select" on public.shop_keepers;
create policy "shop_keepers own select" on public.shop_keepers for select to authenticated using (user_id = auth.uid());

-- Saves several card changes at once: removes the (card_id, note) rows in `removed`, then adds or updates the rows in
-- `changes`. It runs with the caller's rights, so the rules above still decide who may change what.
create or replace function public.shop_stock_save(changes jsonb, removed jsonb default '[]'::jsonb)
returns void language plpgsql security invoker set search_path = public as $$
begin
  delete from public.shop_stock s
    using jsonb_to_recordset(removed) as r(card_id text, note text)
    where s.card_id = r.card_id and s.note = coalesce(r.note, '');
  insert into public.shop_stock (card_id, note, price, qty, descr, updated_at)
    select r.card_id, coalesce(r.note, ''), r.price, r.qty, coalesce(r.descr, ''), now()
    from jsonb_to_recordset(changes) as r(card_id text, note text, price numeric, qty integer, descr text)
  on conflict (card_id, note) do update set price = excluded.price, qty = excluded.qty, descr = excluded.descr, updated_at = now();
end $$;
revoke all on function public.shop_stock_save(jsonb, jsonb) from public, anon;
grant execute on function public.shop_stock_save(jsonb, jsonb) to authenticated;

-- Product photos: a public bucket (anyone can view a photo by its address), 5 MB per file, images only.
-- Only shopkeepers can add, replace or delete them.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('shop', 'shop', true, 5242880, array['image/jpeg', 'image/png', 'image/webp'])
on conflict (id) do update set public = true, file_size_limit = 5242880, allowed_mime_types = array['image/jpeg', 'image/png', 'image/webp'];
drop policy if exists "shop photos keeper select" on storage.objects;
drop policy if exists "shop photos keeper insert" on storage.objects;
drop policy if exists "shop photos keeper update" on storage.objects;
drop policy if exists "shop photos keeper delete" on storage.objects;
create policy "shop photos keeper select" on storage.objects for select to authenticated using (bucket_id = 'shop' and public.is_shop_keeper());  -- needed to replace or delete
create policy "shop photos keeper insert" on storage.objects for insert to authenticated with check (bucket_id = 'shop' and public.is_shop_keeper());
create policy "shop photos keeper update" on storage.objects for update to authenticated using (bucket_id = 'shop' and public.is_shop_keeper());
create policy "shop photos keeper delete" on storage.objects for delete to authenticated using (bucket_id = 'shop' and public.is_shop_keeper());

-- Make an account the shopkeeper (put its username in place of YOURNAME and run this line):
-- insert into public.shop_keepers (user_id) select id from auth.users where email = 'YOURNAME@users.riftprep.app' on conflict do nothing;
