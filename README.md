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
