# Farhat Regulatory — public site

Static site for GitHub Pages: the IFIC Digest archive (SEO engine), homepage, and
newsletter subscribe. No server required.

## Structure
- `index.html` — homepage
- `ific/` — digest archive index + one folder per IFIC (`ific/3067/`, etc.)
- `assets/` — shared CSS + the orbital-arc / animation JS
- `sitemap.xml`, `robots.txt` — SEO infrastructure
- `CNAME` — custom domain for GitHub Pages
- `generate.py` — regenerates all HTML from `ific_data.json` (kept private/local)

## Deploy (GitHub Pages)
1. Create a repo (e.g. `farhat-site`) and push these files to the `main` branch.
2. Repo Settings → Pages → Source: `main` branch, root folder.
3. Add your custom domain `farhatregulatory.com` (the `CNAME` file is already set).
4. Point your domain's DNS at GitHub Pages:
   - Apex `@`: A records to 185.199.108–111.153, plus AAAA for IPv6.
   - `www`: CNAME to `<username>.github.io`.
5. Enable "Enforce HTTPS" once the cert provisions.

## Subscribe form
The subscribe form posts to Buttondown. Set your username in `generate.py`
(`BUTTONDOWN_USER`) and regenerate, or edit the form action in the HTML.
Create a free account at buttondown.email, then paste each biweekly digest as an issue.

## Fetching IFICs straight from the ITU (your machine)
`_generator/fetch_ifics.py` downloads official IFIC zips from itu.int and feeds the
pipeline. Requires Python 3 plus one way to read Access databases:
  * Linux/Mac: mdb-tools (`apt install mdbtools` / `brew install mdbtools`)
  * Windows: `pip install pyodbc` plus the Microsoft Access Database Engine
    redistributable matching your Python bitness (64 bit for 64 bit Python):
    https://www.microsoft.com/en-us/download/details.aspx?id=54920
    (or simply run the script inside WSL with mdbtools)
Examples:

    python3 fetch_ifics.py --year-to-date     # every 2026 issue published so far
    python3 fetch_ifics.py 3075               # one issue
    python3 fetch_ifics.py --inspect 3068     # check the database schema only

Comments format databases are extracted automatically into ific_data.json; if the
official zip carries a different schema, the script prints the table list so the
extractor can be adapted once. Then run generate.py as usual.

## Publishing a new IFIC (minimal touch)
The site is designed so a new circular changes as little as possible. Every page that
mentions "the latest issue" (homepage latest section, hero button, the subscribe
preview card, footer link, schedule statuses, prev/next links, live deadline chips)
is a stable shell filled in the browser from `data/site.json`.

1. Run `extract.py` on the new comments mdb so `ific_data.json` gains the issue.
2. `python3 generate.py` (2026 dates are already built in; nothing to edit).
3. Exactly these paths change, and they are all you need to upload:
   - `ific/<number>/index.html` (the new digest page)
   - `og/og-<number>.png` (its share card)
   - `data/site.json` (carries "latest" to every page)
   - `sitemap.xml` (one added URL)
   - `ific/index.html` (one added archive row)
   The homepage, services, schedule, and all earlier IFIC pages stay byte identical.
4. Review locally (`python3 -m http.server`), commit, push.

## Paid consultation calls (Calendly + Stripe)

The /services/ page offers a paid consultation call. Booking and payment are handled
entirely by Calendly with its native Stripe integration, so the static site needs no server.

Setup (about 15 minutes):
1. Create a Calendly account and an event type, e.g. "Spectrum consultation, 60 minutes".
   Collecting payments requires a paid Calendly plan (Standard or above).
2. In the event type, open "Payments" (or "Collect payments"), choose Stripe, and connect
   your Stripe account. Set the price there, matching CONSULT_PRICE in the generator.
3. Copy the event link (like https://calendly.com/yourname/consultation) into
   CALENDLY_URL in _generator/generate.py, adjust CONSULT_PRICE and CONSULT_LENGTH,
   then run generate.py and push.
4. The "Book and pay online" button opens the Calendly popup on the page. Stripe charges
   the client at the moment they confirm the slot; payouts land in your Stripe account.

Also set the proposal email: the "Request a proposal" button uses
consult@farhatregulatory.com; change the mailto in the generator if you prefer another address.

## Adding a section to the IFIC digest pages

The digest page is composed from a list of section functions in _generator/generate.py.
Each section is a small function (num, d, ctx) that returns an HTML string, or an empty
string to skip itself. `d` is the IFIC's data from ific_data.json (filings, fleets,
top_adms, provmix, and per filing: bands, freq_span, fmin_mhz, fmax_mhz, reach).
`ctx` carries pub, pubfmt, dlfmt, days, and the composed summary.

To add a section: write a function like sec_spectrum, then insert it at the position
you want in the IFIC_SECTIONS list. Run generate.py and every IFIC page gets it.
Current order: summary, stats, service CTA, spectrum, filings table, fleets,
administrations, subscribe, prev/next.
