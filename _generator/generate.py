import json, os, html, re
from datetime import datetime
from dateutil.relativedelta import relativedelta

DATA = json.load(open(os.path.join(os.path.dirname(__file__),'ific_data.json')))
DOMAIN = "https://farhatregulatory.com"
BUTTONDOWN_USER = "farhatregulatory"   # <-- change to your Buttondown username
CALENDLY_URL   = "https://calendly.com/farhatregulatory/consultation"  # <-- your Calendly event link
CONSULT_PRICE  = "USD 300"    # shown on the consultation card; set the same price in Calendly/Stripe
CONSULT_LENGTH = "60 minutes"

# Publication dates (biweekly cadence). Anchor 3067 = 31 Mar 2026; step back 14 days.
# Official ITU BR IFIC (space) publication schedule, per
# https://www.itu.int/en/ITU-R/space/Pages/brificSchedule.aspx
# Note: no late December circular; 3087 publishes 05.01.2027.
PUB_DATES = {
    "3062":"06.01.2026","3063":"20.01.2026","3064":"03.02.2026","3065":"17.02.2026",
    "3066":"03.03.2026","3067":"17.03.2026","3068":"31.03.2026","3069":"14.04.2026",
    "3070":"28.04.2026","3071":"12.05.2026","3072":"26.05.2026","3073":"09.06.2026",
    "3074":"23.06.2026","3075":"07.07.2026","3076":"21.07.2026","3077":"04.08.2026",
    "3078":"18.08.2026","3079":"01.09.2026","3080":"15.09.2026","3081":"29.09.2026",
    "3082":"13.10.2026","3083":"27.10.2026","3084":"10.11.2026","3085":"24.11.2026",
    "3086":"08.12.2026","3087":"05.01.2027",
}
def fmt_date(dstr):
    d=datetime.strptime(dstr,"%d.%m.%Y"); return d.strftime("%-d %B %Y")
def deadline_of(dstr):
    d=datetime.strptime(dstr,"%d.%m.%Y")+relativedelta(months=4); return d
def esc(s): return html.escape(str(s))

NAV = '''<nav class="nav"><div class="wrap">
  <a href="/" class="brand"><span class="l1" style="display:block;line-height:.96">Farhat</span><span class="l2" style="display:block;line-height:.96;color:var(--sand)">Regulatory</span></a>
  <div class="nav-links">
    <a href="/ific/">IFIC Digest</a>
    <a href="/ific/quarterly/">Quarterly</a>
    <a href="/guides/">Guides</a>
    <a href="/services/">Services</a>
    <a href="#subscribe" class="nav-cta">Subscribe</a>
  </div>
</div></nav>'''

def FOOTER():
    return f'''<footer><div class="wrap">
  <div><div class="brand"><span class="l1" style="display:block;line-height:.96">Farhat</span><span class="l2" style="display:block;line-height:.96;color:var(--sand)">Regulatory</span></div>
    <p style="max-width:34ch;font-size:.9rem">Independent ITU satellite-spectrum intelligence. We decode every BR IFIC and prepare the comment filings that keep your networks protected.</p></div>
  <div><h4>The Digest</h4>
    <a href="/ific/">All issues</a><a href="/ific/quarterly/">Quarterly reviews</a><a href="/ific/schedule/">2026 schedule</a><a href="/ific/" data-l-foot>Latest issue</a></div>
  <div><h4>Reference</h4>
    <a href="/guides/">Guides</a><a href="/services/">Coordination service</a><a href="#subscribe">Newsletter</a></div>
  <div class="colophon"><span>© {datetime.now().year} Farhat Regulatory</span><span>Data extracted from ITU BR IFIC publications</span></div>
</div></footer>\n<script defer src="/assets/latest.js?v=1"></script>'''

def subscribe_block(idp="subscribe"):
    # Stable shell: latest-brief details are filled client side from /data/site.json,
    # so this block never changes when a new IFIC publishes. Fallback copy stands alone.
    return f'''<div class="subscribe reveal" id="{idp}">
  <div style="display:flex;gap:44px;align-items:flex-start;flex-wrap:wrap">
    <div style="flex:1;min-width:280px">
      <h2>The brief we build from every IFIC. Get the next one.</h2>
      <p class="sub-p">Each BR IFIC, read the day it publishes and condensed to the filings, positions, and deadlines that matter.</p>
      <form class="sub-form" action="https://buttondown.email/api/emails/embed-subscribe/{BUTTONDOWN_USER}" method="post" target="_blank">
        <input type="email" name="email" placeholder="you@company.com" required>
        <button type="submit">Subscribe</button>
      </form>
      <div class="sub-note">Sent within a day of each BR IFIC publication.</div>
    </div>
    <div style="flex:1;min-width:280px;background:#1C1810;border:1px solid #3A3226;border-radius:3px;padding:22px 24px">
      <div style="display:flex;justify-content:space-between;gap:10px;font-family:var(--mono);font-size:.66rem;letter-spacing:.2em;text-transform:uppercase;color:var(--sand);margin-bottom:14px"><span>From the latest brief</span><span style="color:#8A7A60" data-l-pv-issue>LATEST</span></div>
      <div class="pv-lines" style="font-family:var(--mono);font-size:.8rem;line-height:2.05;color:#D8CDBB">
        <div data-l-pv-stats>Every circular condensed to one page</div>
        <div data-l-pv-lead>The filings with the broadest reach, named and placed</div>
        <div data-l-pv-fleet>Fleets and clusters flagged</div>
        <div data-l-pv-deadline>The RR No. 9.52C comment deadline tracked</div>
      </div>
      <a href="/ific/" data-l-pv-link style="display:inline-block;margin-top:14px;font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;color:var(--sand)">READ THE FULL BRIEF \u2192</a>
    </div>
  </div>
</div>'''

def head(title, desc, path, og_extra="", og_image="/og/og-default.png"):
    url = DOMAIN+path
    img = DOMAIN+og_image
    return f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta property="og:site_name" content="Farhat Regulatory">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img}">
<meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="alternate icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&family=Space+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=11">{og_extra}
</head><body>{NAV}'''

# ---------------- IFIC detail page: modular sections ----------------
# Each section is a function (num, d, ctx) -> HTML string (or "" to skip).
# To add a new section: write a function below and add it to IFIC_SECTIONS.

BAND_ORDER = ["HF","VHF","UHF","L","S","C","X","Ku","K","Ka","V","W","mm"]

def _fmt_mhz(v):
    if v is None: return ""
    if v < 1000: return ("%.4g" % v) + " MHz"
    return ("%.4g" % (v/1000.0)) + " GHz"

def sec_summary(num, d, ctx):
    return f'''
  <div class="section" style="padding-bottom:24px">
    <p class="summary reveal">{ctx["summary"]}</p>
  </div>'''

def sec_stats(num, d, ctx):
    return f'''
  <div class="stat-band reveal">
    <div class="s"><b>{d['total_filings']}</b><span>Filings</span></div>
    <div class="s"><b>{d['gso']}</b><span>GSO</span></div>
    <div class="s"><b>{d['ngso']}</b><span>NGSO</span></div>
    <div class="s"><b>{sum(d['provmix'].values())}</b><span>Coordination pairings</span></div>
  </div>
  <div style="font-family:var(--mono);font-size:.7rem;color:var(--muted);margin-top:-28px;margin-bottom:32px">One pairing is one existing network flagged as potentially affected by one new filing in this circular.</div>'''

def sec_service_cta(num, d, ctx):
    return '''
  <div class="svc-cta reveal">
    <div class="txt"><h3>Affected by one of these filings?</h3>
      <p>We match every CR/C against your networks, draft the coordination letters, and prepare the comments file ready for the BR. You forward it to your administration.</p></div>
    <a href="/services/" class="btn btn-sand">See the service &#8594;</a>
  </div>'''

def sec_spectrum(num, d, ctx):
    """Frequency picture of the round: band occupancy bars + overall span."""
    counts = {b:0 for b in BAND_ORDER}
    lo = hi = None
    for f in d["filings"]:
        for b in f.get("bands", []):
            counts[b] = counts.get(b, 0) + 1
        if f.get("fmin_mhz") is not None:
            lo = f["fmin_mhz"] if lo is None else min(lo, f["fmin_mhz"])
            hi = f["fmax_mhz"] if hi is None else max(hi, f["fmax_mhz"])
    touched = [(b, counts[b]) for b in BAND_ORDER if counts.get(b)]
    if not touched:
        return ""
    mx = max(n for _, n in touched)
    rows = ""
    for b, n in touched:
        w = int(260 * n / mx)
        rows += (f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:9px">'
                 f'<span class="mono" style="width:38px;font-size:.78rem;color:var(--ink)">{b}</span>'
                 f'<span style="display:inline-block;height:10px;flex:0 1 {w}px;min-width:3px;background:var(--sand);border-radius:2px"></span>'
                 f'<span class="mono" style="font-size:.76rem;color:var(--muted);flex:none;white-space:nowrap">{n} filing{"s" if n!=1 else ""}</span></div>')
    span_line = ""
    if lo is not None:
        span_line = (f'<p class="sub reveal" style="margin-top:18px;font-size:.92rem">Assignments this round span '
                     f'<b>{_fmt_mhz(lo)}</b> to <b>{_fmt_mhz(hi)}</b>.</p>')
    return f'''
  <div class="section" style="padding-top:20px;padding-bottom:26px">
    <div class="section-label reveal">Spectrum this round</div>
    <h2 style="font-size:1.6rem" class="reveal">Bands under coordination</h2>
    <div class="reveal" style="margin-top:22px">{rows}</div>
    {span_line}
  </div>'''

def sec_filings_table(num, d, ctx):
    has_areas = any(f.get("areas") for f in d["filings"])
    rows=""
    for f in d["filings"]:
        pos=f["position"] or ('<span style="color:var(--muted)">NGSO</span>' if f['type']=='NGSO' else 'n/a')
        bands=" ".join(f'<span class="tag" style="background:rgba(196,168,130,.16);color:#8A6F45">{b}</span>' for b in f.get("bands",[])) or '<span class="mono" style="color:var(--muted)">n/a</span>'
        span=esc(f.get("freq_span","")) or "n/a"
        area_cell=""
        if has_areas:
            atxt=", ".join(f.get("areas",[])[:4])+("\u2026" if len(f.get("areas",[]))>4 else "")
            area_cell='<td data-label="Service area" style="font-size:.82rem">'+ (esc(atxt) if atxt else '<span style="color:var(--muted)">n/a</span>') +"</td>"
        rows+=f'''<tr>
          <td class="crc" data-label="CR/C">CR/C/{esc(f['crc'])}</td>
          <td class="sat" data-label="Satellite">{esc(f['satellite'])}</td>
          <td data-label="Administration">{esc(f['adm'])}</td>
          <td data-label="Type"><span class="tag {f['type'].lower()}">{f['type']}</span></td>
          <td class="mono" data-label="Position">{pos}</td>
          <td data-label="Bands">{bands}</td>
          <td class="mono" data-label="Frequencies" style="font-size:.82rem;white-space:nowrap">{span}</td>{area_cell}
        </tr>'''
    return f'''
  <div class="section" style="padding-top:20px">
    <div class="section-label">Every filing this round</div>
    <h2 style="font-size:1.6rem">The {d['total_filings']} coordination requests</h2>
    <div style="overflow-x:auto">
    <table class="ftable stackable">
      <thead><tr><th>CR/C</th><th>Satellite</th><th>Adm.</th><th>Type</th><th>Position</th><th>Bands</th><th>Frequencies</th>{'<th>Service area</th>' if has_areas else ""}</tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
  </div>'''

def sec_fleets(num, d, ctx):
    if not d["fleets"]:
        return ""
    items=""
    for fl in d["fleets"]:
        sats=", ".join(fl["sats"][:8])+("\u2026" if len(fl["sats"])>8 else "")
        items+=f'<div class="fleet reveal"><b>{esc(fl["adm"])}</b> filed a cluster of <b>{fl["count"]}</b> networks in the {esc(fl["family"])} family<div class="sats">{esc(sats)}</div></div>'
    return f'<div class="section" style="padding-top:0"><div class="section-label">Fleets &amp; clusters</div>{items}</div>'

def sec_administrations(num, d, ctx):
    adms = d.get("top_adms", [])
    if not adms:
        return ""
    chips = " ".join(
        f'<span style="display:inline-block;background:var(--paper-2);border:1px solid var(--line);border-radius:14px;padding:4px 14px;font-size:.85rem;margin:0 6px 8px 0">{esc(adm_name(a))} <b class="mono" style="font-size:.78rem">{n}</b></span>'
        for a, n in adms)
    return f'''
  <div class="section" style="padding-top:0;padding-bottom:26px">
    <div class="section-label reveal">Who filed</div>
    <div class="reveal">{chips}</div>
  </div>'''

def sec_subscribe(num, d, ctx):
    return subscribe_block("subscribe")

def sec_prev_next(num, d, ctx):
    # Neighbour links resolve client side from site.json, so an already published
    # page never needs regenerating when the next circular arrives.
    return (f'<div data-this-ific="{num}" style="display:flex;justify-content:space-between;margin-top:40px;font-family:var(--mono);font-size:.85rem">'
            '<a data-nav-prev hidden style="color:var(--sand)"></a>'
            '<a data-nav-next hidden style="color:var(--sand)"></a></div>')

IFIC_SECTIONS = [
    sec_summary,
    sec_stats,
    sec_service_cta,
    sec_spectrum,
    sec_filings_table,
    sec_fleets,
    sec_administrations,
    sec_subscribe,
    sec_prev_next,
]

def ific_page(num):
    d = DATA[num]; pub = PUB_DATES.get(num)
    pubfmt = fmt_date(pub) if pub else ""
    dl = deadline_of(pub) if pub else None
    dlfmt = dl.strftime("%-d %B %Y") if dl else "(see IFIC)"
    days = (dl - datetime.now()).days if dl else None

    top = d["filings"][:3]
    names = "; ".join(f"{esc(f['satellite'])} ({esc(f['adm'])}, {f['type']}{', '+f['position'] if f['position'] else ''})" for f in top)
    fleet_txt = ""
    if d["fleets"]:
        fl=d["fleets"][0]; fleet_txt=f" Notably, {esc(fl['adm'])} filed a cluster of {fl['count']} networks in the {esc(fl['family'])} family."
    provmix = ", ".join(f"{k} ({v})" for k,v in sorted(d["provmix"].items()))
    summary = (f"BR IFIC {num}, published {pubfmt}, carries {d['total_filings']} coordination "
               f"requests, of which {d['gso']} are GSO and {d['ngso']} NGSO. The filings with the broadest reach include "
               f"{names}.{fleet_txt} Coordination is invoked under {provmix or 'multiple provisions'}. "
               f"The comment window under RR No. 9.52C, which runs for four months, closes {dlfmt}.")
    title = f"BR IFIC {num}: {d['total_filings']} Filings, Deadline {dl.strftime('%-d %b %Y') if dl else 'TBC'} | Farhat Regulatory"
    desc = (f"IFIC {num} ({pubfmt}): {d['total_filings']} coordination requests including "
            f"{esc(top[0]['satellite']) if top else 'multiple networks'}. Comment deadline {dlfmt}. Every filing decoded.")
    orbit=[]
    for f in d["filings"]:
        deg=None
        m=re.match(r"([\d.]+)\u00b0([EW])",f["position"] or "")
        if m:
            deg=float(m.group(1)); deg=deg if m.group(2)=="E" else -deg
        orbit.append({"name":f["satellite"],"type":f["type"],"deg":deg})
    ld = {"@context":"https://schema.org","@type":"Article",
          "headline":f"BR IFIC {num}: {d['total_filings']} coordination filings",
          "datePublished":datetime.strptime(pub,"%d.%m.%Y").strftime("%Y-%m-%d") if pub else "",
          "author":{"@type":"Organization","name":"Farhat Regulatory"},
          "publisher":{"@type":"Organization","name":"Farhat Regulatory"},
          "description":desc}
    og = f'\n<script type="application/ld+json">{json.dumps(ld)}</script>'

    dl_iso = dl.strftime("%Y-%m-%d") if dl else ""
    dchip=(f'<div class="deadline-chip" data-chip data-deadline="{dl_iso}" style="flex-wrap:wrap;row-gap:2px">'
           f'<span style="opacity:.65;letter-spacing:.12em;font-size:.72rem;margin-right:14px">COMMENT DEADLINE</span>'
           f'<span style="margin-right:14px">{dlfmt}</span>'
           f'<span data-chip-status></span></div>')

    ctx = {"pub":pub, "pubfmt":pubfmt, "dlfmt":dlfmt, "days":days, "summary":summary}
    sections = "".join(s(num, d, ctx) for s in IFIC_SECTIONS)

    body=f'''
<header class="doc-hero">
  <canvas id="orbit-canvas"></canvas>
  <div class="wrap">
    <div class="kicker"><span>BR IFIC</span>&nbsp;&nbsp;&nbsp;<span>{pubfmt}</span></div>
    <h1>IFIC {num}</h1>
    {dchip}
  </div>
</header>
<div class="wrap">{sections}
</div>
{FOOTER()}
<script>window.ORBIT_FILINGS={json.dumps(orbit)};</script>
<script src="/assets/orbit.js?v=3"></script>
</body></html>'''
    return head(title,desc,f"/ific/{num}/",og,og_image=f"/og/og-{num}.png")+body

# ---------------- quarterly summaries ----------------
# Aggregated from ific_data.json so figures stay consistent with the digest pages.
# To add a quarter: add an entry to QUARTERS with its IFIC numbers. Pages regenerate
# automatically. A circular belongs to the quarter of its publication (WIC) date, so
# IFIC 3062 (6 Jan 2026) opens Q1 and IFIC 3075 (7 Jul 2026) opens Q3.
QUARTERS = {
    "2026-q1": {"label":"First Quarter 2026", "short":"Q1 2026", "year":2026, "q":1,
                "ifics":["3062","3063","3064","3065","3066","3067","3068"]},
    "2026-q2": {"label":"Second Quarter 2026", "short":"Q2 2026", "year":2026, "q":2,
                "ifics":["3069","3070","3071","3072","3073","3074"]},
}

# Clean table-form administration names (adm_name carries articled prose forms).
ADM_TABLE = {
 "G":"United Kingdom","F":"France","D":"Germany","I":"Italy","E":"Spain","S":"Sweden",
 "USA":"United States","CHN":"China","RUS":"Russia","J":"Japan","KOR":"Rep. of Korea",
 "IND":"India","LUX":"Luxembourg","NOR":"Norway","QAT":"Qatar","UAE":"United Arab Emirates",
 "SAU":"Saudi Arabia","ARS":"Saudi Arabia","CAN":"Canada","AUS":"Australia","HOL":"Netherlands",
 "SUI":"Switzerland","CYP":"Cyprus","AZE":"Azerbaijan","OMA":"Oman","EGY":"Egypt","POR":"Portugal",
}
def adm_table_name(code): return ADM_TABLE.get(code, adm_name(code))

import statistics as _stats

def quarter_data(key):
    """Aggregate a quarter from the per-IFIC DATA, keeping figures site-consistent."""
    cfg = QUARTERS[key]
    ifics = [n for n in cfg["ifics"] if n in DATA]
    tot = gso = ngso = pairings = 0
    adm_counts = {}
    fleets = []
    reaches = []
    lead_filings = []
    per_ific = []
    prov_all = {}
    for n in ifics:
        d = DATA[n]
        tot += d["total_filings"]; gso += d["gso"]; ngso += d["ngso"]
        pairings += sum(d["provmix"].values())
        for k,v in d["provmix"].items(): prov_all[k] = prov_all.get(k,0)+v
        for a,c in d.get("top_adms", []): adm_counts[a] = adm_counts.get(a,0)+c
        for fl in d.get("fleets", []):
            fleets.append({**fl, "ific":n})
        for f in d["filings"]:
            if f.get("reach"): reaches.append(f["reach"])
            lead_filings.append({**f, "ific":n})
        pub = PUB_DATES.get(n)
        per_ific.append({"n":n, "pub":pub, "pubfmt":fmt_date(pub) if pub else "",
                         "filings":d["total_filings"], "gso":d["gso"], "ngso":d["ngso"]})
    top_adms = sorted(adm_counts.items(), key=lambda kv:(-kv[1], kv[0]))
    fleets.sort(key=lambda fl:-fl["count"])
    lead_filings.sort(key=lambda f:-(f.get("reach") or 0))
    med = int(_stats.median(reaches)) if reaches else 0
    pubs = [datetime.strptime(p["pub"],"%d.%m.%Y") for p in per_ific if p["pub"]]
    start = min(pubs) if pubs else None
    end = max(pubs) if pubs else None
    return {"cfg":cfg, "ifics":ifics, "tot":tot, "gso":gso, "ngso":ngso,
            "pairings":pairings, "top_adms":top_adms, "fleets":fleets,
            "lead_filings":lead_filings, "median_reach":med, "per_ific":per_ific,
            "prov_all":prov_all, "start":start, "end":end,
            "n_adms":len(adm_counts), "reach_filings":len(reaches)}

def _quarter_prov_line(q):
    top = sorted(q["prov_all"].items(), key=lambda kv:-kv[1])[:4]
    return ", ".join(f"{k} ({v:,})" for k,v in top)

def quarter_page(key):
    q = quarter_data(key); cfg = q["cfg"]
    lead = q["top_adms"][0] if q["top_adms"] else ("",0)
    span = ""
    if q["start"] and q["end"]:
        span = f'{q["start"].strftime("%-d %B")} to {q["end"].strftime("%-d %B %Y")}'
    ifrange = f'IFIC {q["ifics"][0]} to {q["ifics"][-1]}'

    # per-circular table
    irows = ""
    for i, p in enumerate(q["per_ific"]):
        irows += f'''<tr>
          <td class="crc" style="font-weight:600;color:var(--ink)"><a href="/ific/{p['n']}/" style="color:var(--sand)">IFIC {p['n']}</a></td>
          <td class="mono">{p['pubfmt']}</td>
          <td class="mono">{p['gso']} / {p['ngso']}</td>
          <td class="mono" style="text-align:right">{p['filings']}</td>
        </tr>'''

    # administrations chips
    chips = " ".join(
        f'<span style="display:inline-block;background:var(--paper-2);border:1px solid var(--line);border-radius:14px;padding:4px 14px;font-size:.85rem;margin:0 6px 8px 0">{esc(adm_table_name(a))} <b class="mono" style="font-size:.78rem">{n}</b></span>'
        for a, n in q["top_adms"][:12])

    # highest-reach filings
    brows = ""
    for f in q["lead_filings"][:8]:
        pos = f["position"] or ('<span style="color:var(--muted)">NGSO</span>' if f["type"]=="NGSO" else "n/a")
        brows += f'''<tr>
          <td class="sat" data-label="Satellite">{esc(f['satellite'])}</td>
          <td data-label="Administration">{esc(adm_table_name(f['adm']))}</td>
          <td data-label="Type"><span class="tag {f['type'].lower()}">{f['type']}</span></td>
          <td class="mono" data-label="Position">{pos}</td>
          <td data-label="IFIC"><a href="/ific/{f['ific']}/" style="color:var(--sand)">{f['ific']}</a></td>
          <td class="mono" data-label="Networks reached" style="text-align:right">{(f.get('reach') or 0):,}</td>
        </tr>'''

    # fleets
    fleet_html = ""
    if q["fleets"]:
        items = ""
        for fl in q["fleets"][:6]:
            sats = ", ".join(fl["sats"][:8]) + ("\u2026" if len(fl["sats"])>8 else "")
            items += f'<div class="fleet reveal"><b>{esc(adm_table_name(fl["adm"]))}</b> filed a cluster of <b>{fl["count"]}</b> networks in the {esc(fl["family"])} family <span class="mono" style="color:var(--muted);font-size:.78rem">(IFIC {fl["ific"]})</span><div class="sats">{esc(sats)}</div></div>'
        fleet_html = f'<div class="section" style="padding-top:0"><div class="section-label">Fleets &amp; clusters this quarter</div>{items}</div>'

    prov_line = _quarter_prov_line(q)
    summary = (f"Across {cfg['short']}, the Bureau published {len(q['ifics'])} space services circulars "
               f"carrying {q['tot']} coordination requests, {q['gso']} GSO and {q['ngso']} NGSO. "
               f"{adm_table_name(lead[0])} was the single largest source with {lead[1]} filings. "
               f"Coordination was invoked most often under {prov_line or 'multiple provisions'}. "
               f"The {q['pairings']:,} coordination pairings are dominated by a handful of large NGSO "
               f"constellation filings, so the typical filing reached a median of {q['median_reach']:,} "
               f"existing networks.")

    title = f"BR IFIC {cfg['short']} Summary: {q['tot']} Coordination Filings | Farhat Regulatory"
    desc = (f"{cfg['short']} in review: {q['tot']} CR/C coordination requests across {len(q['ifics'])} "
            f"BR IFIC circulars ({q['gso']} GSO, {q['ngso']} NGSO). Led by {adm_table_name(lead[0])}. "
            f"Every filing decoded by Farhat Regulatory.")

    # neighbour links
    qkeys = list(QUARTERS.keys())
    idx = qkeys.index(key)
    prev_k = qkeys[idx-1] if idx>0 else None
    next_k = qkeys[idx+1] if idx < len(qkeys)-1 else None
    nav_prev = f'<a href="/ific/quarterly/{prev_k}/" style="color:var(--sand)">&#8592; {QUARTERS[prev_k]["short"]}</a>' if prev_k else '<span></span>'
    nav_next = f'<a href="/ific/quarterly/{next_k}/" style="color:var(--sand)">{QUARTERS[next_k]["short"]} &#8594;</a>' if next_k else '<span></span>'

    ld = {"@context":"https://schema.org","@type":"Article",
          "headline":f"BR IFIC {cfg['short']}: {q['tot']} coordination filings",
          "datePublished":q["end"].strftime("%Y-%m-%d") if q["end"] else "",
          "author":{"@type":"Organization","name":"Farhat Regulatory"},
          "publisher":{"@type":"Organization","name":"Farhat Regulatory"},
          "description":desc}
    og = f'\n<script type="application/ld+json">{json.dumps(ld)}</script>'

    body = f'''
<header class="doc-hero">
  <canvas id="orbit-canvas"></canvas>
  <div class="wrap">
    <div class="kicker"><span>Quarterly Review</span>&nbsp;&nbsp;&nbsp;<span>{ifrange}</span></div>
    <h1>{cfg['label']}</h1>
    <p style="color:#CBBFA6;max-width:54ch;font-size:1.06rem">{span}. The quarter's BR IFIC coordination activity, aggregated across every circular.</p>
  </div>
</header>
<div class="wrap">
  <div class="section" style="padding-bottom:24px">
    <p class="summary reveal">{summary}</p>
  </div>
  <div class="stat-band reveal">
    <div class="s"><b>{q['tot']}</b><span>Filings</span></div>
    <div class="s"><b>{q['gso']}</b><span>GSO</span></div>
    <div class="s"><b>{q['ngso']}</b><span>NGSO</span></div>
    <div class="s"><b>{len(q['ifics'])}</b><span>Circulars</span></div>
  </div>
  <div style="font-family:var(--mono);font-size:.7rem;color:var(--muted);margin-top:-28px;margin-bottom:32px">Figures aggregate every space services circular published in the quarter, keyed to each circular's publication date.</div>

  <div class="section" style="padding-top:8px">
    <div class="section-label">Filing volume by circular</div>
    <h2 style="font-size:1.6rem">The {len(q['ifics'])} circulars</h2>
    <div style="overflow-x:auto">
    <table class="ftable">
      <thead><tr><th>Circular</th><th>Published</th><th>GSO / NGSO</th><th style="text-align:right">Filings</th></tr></thead>
      <tbody>{irows}</tbody>
    </table></div>
  </div>

  <div class="section" style="padding-top:0;padding-bottom:26px">
    <div class="section-label reveal">Who filed</div>
    <h2 style="font-size:1.6rem" class="reveal">Leading administrations</h2>
    <div class="reveal" style="margin-top:18px">{chips}</div>
  </div>

  <div class="section" style="padding-top:0">
    <div class="section-label">Coordination pressure</div>
    <h2 style="font-size:1.6rem">Highest-reach filings</h2>
    <p class="sub reveal" style="margin-top:10px;font-size:.94rem">Ranked by the number of existing networks each filing flags as potentially affected. Reach is concentrated: the median filing reached {q['median_reach']:,} networks, while the largest reached into the hundreds of thousands.</p>
    <div style="overflow-x:auto;margin-top:18px">
    <table class="ftable stackable">
      <thead><tr><th>Satellite</th><th>Adm.</th><th>Type</th><th>Position</th><th>IFIC</th><th style="text-align:right">Networks reached</th></tr></thead>
      <tbody>{brows}</tbody>
    </table></div>
  </div>

  {fleet_html}

  <div style="display:flex;justify-content:space-between;margin-top:40px;font-family:var(--mono);font-size:.85rem">
    {nav_prev}{nav_next}
  </div>

  {subscribe_block("subscribe")}
</div>
{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script>
</body></html>'''
    return head(title, desc, f"/ific/quarterly/{key}/", og) + body

def quarterly_index():
    title = "BR IFIC Quarterly Reviews | ITU Coordination Activity by Quarter | Farhat Regulatory"
    desc = "Quarterly reviews of BR IFIC satellite coordination activity: filing volumes, leading administrations, and the highest-reach networks, aggregated from every circular."
    cards = ""
    for key in QUARTERS:
        q = quarter_data(key); cfg = q["cfg"]
        lead = q["top_adms"][0] if q["top_adms"] else ("",0)
        span = ""
        if q["start"] and q["end"]:
            span = f'{q["start"].strftime("%-d %b")} to {q["end"].strftime("%-d %b %Y")}'
        cards += f'''<a href="/ific/quarterly/{key}/" class="issue reveal">
          <div class="num">{cfg['short'].split()[0]}<small>{cfg['year']}</small></div>
          <div class="meta"><h3>{q['tot']} coordination filings&nbsp;&nbsp;&nbsp;<span style="color:var(--muted);font-weight:400">led by {esc(adm_table_name(lead[0]))}</span></h3>
            <p>{span}<span style="display:inline-block;width:1px;height:.75em;background:var(--line);margin:0 12px;vertical-align:middle"></span>{q['gso']} GSO / {q['ngso']} NGSO<span style="display:inline-block;width:1px;height:.75em;background:var(--line);margin:0 12px;vertical-align:middle"></span>{len(q['ifics'])} circulars</p></div>
          <div class="stat"><b>{q['pairings']:,}</b>coordination<br>pairings</div>
        </a>'''
    body = f'''
<header class="doc-hero"><canvas id="orbit-canvas"></canvas><div class="wrap">
  <div class="kicker">Quarterly Review</div>
  <h1>IFIC by the quarter</h1>
  <p style="color:#CBBFA6;max-width:52ch;font-size:1.1rem">Every BR IFIC circular, aggregated into a quarterly picture: how much was filed, by whom, and which networks carried the broadest coordination reach.</p>
  <p style="margin-top:14px"><a href="/ific/" class="mono" style="font-size:.78rem;letter-spacing:.1em;color:var(--sand)">BROWSE INDIVIDUAL ISSUES &#8594;</a></p>
</div></header>
<div class="wrap"><div class="section">
  <div class="issue-list">{cards}</div>
</div>
{subscribe_block("subscribe")}
</div>{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script></body></html>'''
    return head(title, desc, "/ific/quarterly/") + body


# ---------------- archive index ----------------
def archive_index():
    nums=sorted(DATA.keys(),reverse=True)
    items=""
    for num in nums:
        d=DATA[num]; pub=PUB_DATES.get(num); pubfmt=fmt_date(pub) if pub else ""
        top=d["filings"][0]["satellite"] if d["filings"] else ""
        items+=f'''<a href="/ific/{num}/" class="issue reveal">
          <div class="num">{num}<small>BR IFIC</small></div>
          <div class="meta"><h3>{d['total_filings']} coordination filings&nbsp;&nbsp;&nbsp;<span style="color:var(--muted);font-weight:400">{esc(top)}{' +'+str(d['total_filings']-1) if d['total_filings']>1 else ''}</span></h3>
            <p>{pubfmt}<span style="display:inline-block;width:1px;height:.75em;background:var(--line);margin:0 12px;vertical-align:middle"></span>{d['gso']} GSO / {d['ngso']} NGSO<span style="display:inline-block;width:1px;height:.75em;background:var(--line);margin:0 12px;vertical-align:middle"></span>{len(d['fleets'])} fleet{'s' if len(d['fleets'])!=1 else ''} detected</p></div>
          <div class="stat" title="Each pairing is one existing network flagged against one new filing"><b>{sum(d['provmix'].values())}</b>coordination<br>pairings</div>
        </a>'''
    title="BR IFIC Digest Archive | Every ITU Coordination Circular Decoded | Farhat Regulatory"
    desc="Browse every BR IFIC: coordination filings, satellites, orbital positions, and comment deadlines, decoded issue by issue by Farhat Regulatory."
    body=f'''
<header class="doc-hero"><canvas id="orbit-canvas"></canvas><div class="wrap">
  <div class="kicker">The Archive</div>
  <h1>The IFIC Digest</h1>
  <p style="color:#CBBFA6;max-width:52ch;font-size:1.1rem">Every ITU BR International Frequency Information Circular, parsed and decoded: the filings, the players, the deadlines.</p>
  <p style="margin-top:14px"><a href="/ific/schedule/" class="mono" style="font-size:.78rem;letter-spacing:.1em;color:var(--sand)">FULL 2026 SCHEDULE &#8594;</a></p>
</div></header>
<div class="wrap"><div class="section">
  <div class="issue-list">{items}</div>
</div>
{subscribe_block("subscribe")}
</div>{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script></body></html>'''
    return head(title,desc,"/ific/")+body

# ---------------- friendly prose for the latest issue ----------------
ADM_NAMES = {"G":"the United Kingdom","OMA":"Oman","UAE":"the UAE","LUX":"Luxembourg",
 "EGY":"Egypt","CHN":"China","IND":"India","USA":"the United States","POR":"Portugal",
 "I":"Italy","D":"Germany","F":"France","RUS":"Russia","J":"Japan","KOR":"Korea",
 "CAN":"Canada","AUS":"Australia","ESP":"Spain","HOL":"the Netherlands","NOR":"Norway"}
_NUMS=["zero","one","two","three","four","five","six","seven","eight","nine","ten",
 "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty"]
def numword(n, cap=False):
    w=_NUMS[n] if 0<=n<len(_NUMS) else str(n)
    return w.capitalize() if cap else w
def adm_name(code):
    return ADM_NAMES.get(code, code)

def friendly_latest(d, pub):
    """Two or three natural sentences about the latest IFIC, composed from the data."""
    bits=[]
    lead = d["filings"][0] if d["filings"] else None
    fleets = d.get("fleets", [])
    if fleets:
        fl=fleets[0]
        an=adm_name(fl['adm'])
        s=f"{an[0].upper()+an[1:]} filed {numword(fl['count'])} {fl['family'].title()} networks in a single sweep this round"
        if len(fleets)>1:
            f2=fleets[1]
            s+=f", while {adm_name(f2['adm'])} staked {numword(f2['count'])} {f2['family'].title()} slots"
        bits.append(s+".")
    if lead:
        pos=f" at {lead['position']}" if lead["position"] else ""
        reach=f", and it alone touches {lead['reach']} existing networks" if lead.get("reach") else ""
        bits.append(f"The single biggest filing is {lead['satellite']} from {adm_name(lead['adm'])}{pos}{reach}.")
    bits.append(f"{numword(d['total_filings'],cap=True)} coordination requests in all, {numword(d['gso'])} geostationary and {numword(d['ngso'])} NGSO.")
    if pub:
        dld=deadline_of(pub)
        dl=dld.strftime("%-d %B %Y")
        if (dld - datetime.now()).days < 0:
            bits.append(f"The comment window closed {dl}.")
        else:
            bits.append(f"Comments close {dl}.")
    return " ".join(bits)


# ---------------- homepage ----------------
def homepage():
    # Latest issue details are injected client side from /data/site.json.
    title="Farhat Regulatory | ITU BR IFIC Intelligence &amp; Satellite Coordination"
    desc="Independent ITU satellite-spectrum intelligence. We decode every BR IFIC, covering filings, orbital slots and deadlines, and prepare the comment filings that protect your networks."
    body=f'''
<header class="hero">
  <canvas id="orbit-canvas"></canvas>
  <div class="wrap">
    <div class="eyebrow reveal" style="display:flex;align-items:center;gap:16px"><span style="display:inline-block;width:42px;height:1px;background:var(--sand)"></span>ITU BR IFIC Intelligence</div>
    <h1 class="reveal">We parse every IFIC and pinpoint what matters to your constellation.</h1>
    <p class="lede reveal"><span class="lede-full">The BR publishes a new International Frequency Information Circular every two weeks. Each one holds hundreds of coordination requests in a raw database almost no one reads. We turn every circular into intelligence, and prepare the comment filings <span style="color:var(--sand-lt);font-weight:600">that keep your priority intact</span>.</span><span class="lede-short">Hundreds of coordination requests land every two weeks. We decode them and prepare the comments <span style="color:var(--sand-lt);font-weight:600">that keep your priority intact</span>.</span></p>
    <div class="cta-row reveal">
      <a href="/ific/" class="btn btn-sand" data-l-cta>Read the latest circular →</a>
      <a href="#subscribe" class="btn btn-ghost">Get the free digest</a>
    </div>
  </div>
</header>
<div class="wrap">
  <div class="section">
    <div class="section-label reveal">What we do</div>
    <h2 class="reveal">Between raw ITU data and expensive consulting.</h2>
    <p class="sub reveal">The Bureau gives you a database. The specialist tools are closed and costly. We sit in between, with clear intelligence on every IFIC and a service that prepares and files the comments for you.</p>
    <div class="grid-3">
      <div class="cell reveal"><div class="n">01</div><h3>Decode</h3><p>Every IFIC parsed the day it publishes: satellites, administrations, orbital slots, provisions, and the deadline, in plain language.</p></div>
      <div class="cell reveal"><div class="n">02</div><h3>Monitor</h3><p>We watch each circular for the filings that affect your networks, so a coordination window never closes without you knowing.</p></div>
      <div class="cell reveal"><div class="n">03</div><h3>File</h3><p>We draft the coordination letters and prepare the comments file ready for the BR. You review it and forward to your administration.</p></div>
    </div>
  </div>

  <div class="section" style="padding-top:0">
    <div class="section-label reveal">Latest issue</div>
    <h2 class="reveal" data-l-heading>The newest circular, decoded</h2>
    <p class="sub reveal" data-l-summary>Every two weeks we parse the newest BR IFIC into a plain language brief: who filed, which satellites and orbital slots, the fleets moving together, and the comment deadline it opens.</p>
    <a href="/ific/" class="btn btn-sand reveal" style="margin-top:24px" data-l-open>Open the latest issue →</a>
  </div>

  {subscribe_block("subscribe")}
</div>
{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script></body></html>'''
    return head(title,desc,"/")+body

# ---------------- services page ----------------
def services_page():
    title="Services | IFIC Comment Filing and Spectrum Consultation | Farhat Regulatory"
    desc="Two ways to work with Farhat Regulatory: a done for you IFIC comment filing service, and paid one on one spectrum consultation calls booked online."
    calendly_head=(f'\n<link href="https://assets.calendly.com/assets/external/widget.css" rel="stylesheet">'
                   f'\n<script src="https://assets.calendly.com/assets/external/widget.js" async></script>')
    body=f'''
<header class="doc-hero"><canvas id="orbit-canvas"></canvas><div class="wrap">
  <div class="kicker">Services</div>
  <h1>Work with us</h1>
  <p style="color:#CBBFA6;max-width:54ch;font-size:1.1rem">Intelligence is free. When you need the work done, or an expert across the table, these are the two ways in.</p>
</div></header>
<div class="wrap">

  <div class="section" style="padding-bottom:30px">
    <div class="grid-2">

      <div class="cell reveal" style="padding:40px 38px">
        <div class="n">01</div>
        <h3 style="font-size:1.6rem">IFIC comment filing</h3>
        <p style="margin-top:10px">We monitor every BR IFIC for filings that affect your networks, prepare the coordination letters, and build the comments file ready for the BR. You review and forward to your administration before the deadline.</p>
        <ul style="margin:18px 0 0 18px;color:var(--muted);font-size:.93rem;line-height:1.9">
          <li>Every IFIC checked against your filings, within a day of publication</li>
          <li>Coordination letters drafted per filing administration</li>
          <li>Comments file prepared in the format the BR accepts</li>
          <li>Deadline tracking under RR No. 9.52C</li>
        </ul>
        <p style="margin-top:20px;font-size:.9rem;color:var(--muted)">Scoped per operator and portfolio size.</p>
        <a href="mailto:consult@farhatregulatory.com?subject=IFIC%20comment%20filing" class="btn btn-sand" style="margin-top:18px">Request a proposal</a>
      </div>

      <div class="cell reveal" style="padding:40px 38px;background:var(--ink);color:var(--white)">
        <div class="n" style="color:var(--sand)">02</div>
        <h3 style="font-size:1.6rem;color:var(--white)">Spectrum consultation call</h3>
        <p style="margin-top:10px;color:#CBBFA6">One on one with a satellite spectrum regulatory specialist. Bring a coordination problem, a filing question, or a market entry plan and leave with a clear position.</p>
        <ul style="margin:18px 0 0 18px;color:#B5A98F;font-size:.93rem;line-height:1.9">
          <li>ITU coordination strategy, Articles 9 and 11</li>
          <li>CR/C responses and comment tactics</li>
          <li>NGSO and GSO licensing across markets</li>
          <li>Written summary of the discussion afterwards</li>
        </ul>
        <div style="margin-top:22px;font-family:var(--mono);font-size:.9rem;color:var(--sand-lt)">{CONSULT_LENGTH}<span style="display:inline-block;width:1px;height:.75em;background:#3A3226;margin:0 14px;vertical-align:middle"></span>{CONSULT_PRICE}</div>
        <a href="" onclick="Calendly.initPopupWidget({{url:'{CALENDLY_URL}'}});return false;" class="btn btn-sand" style="margin-top:16px">Book and pay online</a>
        <div style="font-family:var(--mono);font-size:.68rem;letter-spacing:.1em;color:#8A7A60;margin-top:12px;text-transform:uppercase">Scheduling by Calendly, payment by Stripe at booking</div>
      </div>

    </div>
  </div>

  <div class="section" style="padding-top:10px">
    <div class="section-label reveal">How the paid call works</div>
    <div class="grid-3">
      <div class="cell reveal"><div class="n">1</div><h3>Pick a slot</h3><p>The booking window opens right here. Choose a time that works across your time zone.</p></div>
      <div class="cell reveal"><div class="n">2</div><h3>Pay at booking</h3><p>Stripe collects payment when you confirm the slot. No invoicing back and forth, no holds.</p></div>
      <div class="cell reveal"><div class="n">3</div><h3>Meet and decide</h3><p>We take the call, work the problem, and you receive a written summary of positions and next steps.</p></div>
    </div>
  </div>

  {subscribe_block("subscribe")}
</div>
{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script></body></html>'''
    return head(title,desc,"/services/",calendly_head)+body


# ---------------- 2026 schedule page ----------------
def schedule_page():
    title="BR IFIC Schedule 2026: Publication Dates and Comment Deadlines | Farhat Regulatory"
    desc="Every 2026 BR IFIC (space services): official publication dates, the four month RR No. 9.52C comment deadline for each, and links to decoded issues."
    now=datetime.now()
    rows=""
    nums=[n for n in sorted(PUB_DATES.keys()) if PUB_DATES[n].endswith("2026")]
    for n in nums:
        pub=PUB_DATES[n]
        pd=datetime.strptime(pub,"%d.%m.%Y")
        dl=deadline_of(pub)
        # Baseline status uses dates only, so this page's bytes never depend on which
        # digests exist; latest.js links decoded issues and recomputes with the
        # viewer's date, keeping statuses live without any regeneration.
        if pd <= now:
            status='<span style="color:var(--muted)">Published</span>'
        else:
            status='<span class="mono" style="font-size:.78rem;letter-spacing:.08em;color:var(--muted)">UPCOMING</span>'
        rows+=f'''<tr data-ific="{n}" data-pub="{pd.strftime("%Y-%m-%d")}">
          <td class="crc" style="font-weight:600;color:var(--ink)">IFIC {n}</td>
          <td class="mono">{pd.strftime("%-d %b %Y")}</td>
          <td class="mono">{dl.strftime("%-d %b %Y")}</td>
          <td data-status>{status}</td>
        </tr>'''
    body=f'''
<header class="doc-hero"><canvas id="orbit-canvas"></canvas><div class="wrap">
  <div class="kicker">2026 calendar</div>
  <h1>BR IFIC schedule</h1>
  <p style="color:#CBBFA6;max-width:56ch;font-size:1.08rem">Every space services circular the Bureau publishes in 2026, with the four month comment deadline each one opens under RR No. 9.52C. Dates follow the official ITU publication schedule.</p>
</div></header>
<div class="wrap">
  <div class="section">
    <div style="overflow-x:auto">
    <table class="ftable">
      <thead><tr><th>Circular</th><th>Published</th><th>Comment deadline</th><th>Status</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p class="sub reveal" style="margin-top:18px;font-size:.9rem">The Bureau publishes no circular in late December; IFIC 3087 follows on 5 January 2027.</p>
  </div>
  {subscribe_block("subscribe")}
</div>
{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script></body></html>'''
    return head(title,desc,"/ific/schedule/")+body


# ---------------- social share images (WhatsApp/OG previews) ----------------
def make_og_images():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("!! Pillow not installed; skipping OG images (pip install pillow)")
        return
    import os
    os.makedirs("og", exist_ok=True)
    FD="/usr/share/fonts/truetype/dejavu/"
    serif_xl = ImageFont.truetype(FD+"DejaVuSerif-Bold.ttf", 118)
    serif_lg = ImageFont.truetype(FD+"DejaVuSerif-Bold.ttf", 76)
    serif_md = ImageFont.truetype(FD+"DejaVuSerif-Bold.ttf", 44)
    mono_md  = ImageFont.truetype(FD+"DejaVuSansMono.ttf", 30)
    mono_sm  = ImageFont.truetype(FD+"DejaVuSansMono.ttf", 24)
    INK=(18,16,11); SAND=(196,168,130); SANDLT=(232,220,196); MUT=(156,142,118)

    def base():
        im=Image.new("RGB",(1200,630),INK)
        dr=ImageDraw.Draw(im)
        # gso arc across lower half + dots
        dr.arc([600-1150,1480-1150,600+1150,1480+1150],start=195,end=345,fill=SAND,width=4)
        dr.arc([600-1050,1480-1050,600+1050,1480+1050],start=200,end=340,fill=(90,81,66),width=2)
        for dx,dy,r,col in [(300,382,10,SANDLT),(760,352,7,SAND),(1020,392,6,SAND)]:
            dr.ellipse([dx-r,dy-r,dx+r,dy+r],fill=col)
        # stacked logo
        dr.text((70,54),"Farhat",font=serif_md,fill=(253,251,246))
        dr.text((70,104),"Regulatory",font=serif_md,fill=SAND)
        dr.text((70,556),"farhatregulatory.com",font=mono_sm,fill=MUT)
        return im,dr

    # default card
    im,dr=base()
    dr.text((70,240),"Every BR IFIC,",font=serif_lg,fill=(253,251,246))
    dr.text((70,330),"decoded.",font=serif_lg,fill=SANDLT)
    dr.text((70,440),"ITU BR IFIC INTELLIGENCE",font=mono_md,fill=SAND)
    im.save("og/og-default.png")

    # per-IFIC cards
    for num,d in DATA.items():
        im,dr=base()
        dr.text((70,200),f"BR IFIC {num}",font=serif_xl,fill=(253,251,246))
        pub=PUB_DATES.get(num)
        dl=deadline_of(pub).strftime("%-d %b %Y") if pub else ""
        line1=f"{d['total_filings']} filings   {d['gso']} GSO / {d['ngso']} NGSO"
        dr.text((74,352),line1,font=mono_md,fill=SANDLT)
        if dl:
            dr.text((74,404),f"comment deadline {dl}",font=mono_md,fill=SAND)
        im.save(f"og/og-{num}.png")
    print("OG images:", ", ".join(sorted(os.listdir("og"))))


# ---------------- write files ----------------
os.makedirs("ific",exist_ok=True)
os.makedirs("ific/schedule",exist_ok=True)
os.makedirs("services",exist_ok=True)
os.makedirs("data",exist_ok=True)
make_og_images()

# site.json: the single file that carries "latest" to every stable page
def _issue_entry(n):
    d=DATA[n]; pub=PUB_DATES.get(n)
    pd=datetime.strptime(pub,"%d.%m.%Y") if pub else None
    dl=deadline_of(pub) if pub else None
    lead=d["filings"][0] if d["filings"] else None
    lead_line=""
    if lead:
        pos=(" at "+lead["position"]) if lead["position"] else ""
        lead_line="%s (%s, %s%s), reaching %d networks"%(lead["satellite"],lead["adm"],lead["type"],pos,lead["reach"])
    fleet_line=""
    if d["fleets"]:
        fl=d["fleets"][0]
        fleet_line="%s cluster flagged: %d %s networks filed together"%(fl["adm"],fl["count"],fl["family"])
    orbit=[]
    for f in d["filings"]:
        m=re.match(r"([\d.]+)\u00b0([EW])",f["position"] or "")
        deg=(float(m.group(1)) if m.group(2)=="E" else -float(m.group(1))) if m else None
        orbit.append({"name":f["satellite"],"type":f["type"],"deg":deg})
    return {"no":n,
            "pub":pd.strftime("%Y-%m-%d") if pd else "","pub_h":fmt_date(pub) if pub else "",
            "deadline":dl.strftime("%Y-%m-%d") if dl else "","deadline_h":dl.strftime("%-d %B %Y") if dl else "",
            "filings":d["total_filings"],"gso":d["gso"],"ngso":d["ngso"],
            "pairings":sum(d["provmix"].values()),
            "lead":lead["satellite"] if lead else "","lead_line":lead_line,"fleet_line":fleet_line,
            "summary":friendly_latest(d,pub),"orbit":orbit}
site={"issues":[_issue_entry(n) for n in sorted(DATA.keys(),reverse=True)]}
open("data/site.json","w").write(json.dumps(site))
print("data/site.json written with", len(site["issues"]), "issues")
open("ific/schedule/index.html","w").write(schedule_page())
os.makedirs("ific/quarterly",exist_ok=True)
open("ific/quarterly/index.html","w").write(quarterly_index())
for _qkey in QUARTERS:
    os.makedirs(f"ific/quarterly/{_qkey}",exist_ok=True)
    open(f"ific/quarterly/{_qkey}/index.html","w").write(quarter_page(_qkey))
print("quarterly pages written:", ", ".join(QUARTERS.keys()))
open("index.html","w").write(homepage())
open("services/index.html","w").write(services_page())
open("ific/index.html","w").write(archive_index())
for num in DATA:
    os.makedirs(f"ific/{num}",exist_ok=True)
    open(f"ific/{num}/index.html","w").write(ific_page(num))

# sitemap + robots + CNAME
urls=[("/",1.0),("/ific/",0.9),("/services/",0.9),("/ific/schedule/",0.85),("/ific/quarterly/",0.85)]+[(f"/ific/quarterly/{q}/",0.8) for q in QUARTERS]+[(f"/ific/{n}/",0.8) for n in sorted(DATA,reverse=True)]
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u,p in urls:
    sm+=f'  <url><loc>{DOMAIN}{u}</loc><changefreq>weekly</changefreq><priority>{p}</priority></url>\n'
sm+='</urlset>\n'
open("sitemap.xml","w").write(sm)
open("robots.txt","w").write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
open("CNAME","w").write("farhatregulatory.com\n")

print("Generated:")
for root,_,files in os.walk("."):
    if ".git" in root: continue
    for f in files:
        if f.endswith((".html",".xml",".txt",".css",".js")) and "site_data" not in root:
            print("  ",os.path.join(root,f))
