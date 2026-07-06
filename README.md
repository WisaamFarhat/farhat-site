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

## Adding a new IFIC
1. Run your parser to produce/append the IFIC's entry in `ific_data.json`.
2. Add its publication date to `PUB_DATES` in `generate.py`.
3. `python3 generate.py` — regenerates all pages + sitemap.
4. Review locally (`python3 -m http.server`), then commit & push.

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
