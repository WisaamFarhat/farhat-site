"""
Quarterly IFIC summaries for Farhat Regulatory.

Aggregates the canonical ific_data.json (the same source the digest pages use, so
the numbers reconcile exactly) into per-quarter summary pages under /ific/quarterly/.

Quarters are keyed by each circular's publication date (WIC date), the same
PUB_DATES anchor the rest of the site uses. IFIC 3062 (6 Jan 2026) opens Q1;
IFIC 3075 (7 Jul 2026) opens Q3 and is therefore not part of H1.
"""
import json, html, collections
from datetime import datetime

def esc(s): return html.escape(str(s))

# ITU administration symbols to readable names. Extends the site's ADM_NAMES with
# every symbol that appears in H1 2026 so quarter pages never show a bare code.
ADM_FULL = {
    "CHN":"China","G":"United Kingdom","F":"France","USA":"United States","I":"Italy",
    "D":"Germany","J":"Japan","KOR":"Rep. of Korea","IND":"India","LUX":"Luxembourg",
    "NOR":"Norway","QAT":"Qatar","UAE":"United Arab Emirates","RUS":"Russia","CAN":"Canada",
    "AUS":"Australia","E":"Spain","HOL":"Netherlands","CYP":"Cyprus","ISR":"Israel",
    "ARS":"Saudi Arabia","MLA":"Malaysia","SNG":"Singapore","VTN":"Vietnam","TUR":"Turkey",
    "PAK":"Pakistan","IRN":"Iran","KAZ":"Kazakhstan","POL":"Poland","GRC":"Greece",
    "ROU":"Romania","BUL":"Bulgaria","SUI":"Switzerland","AZE":"Azerbaijan","JOR":"Jordan",
    "MCO":"Monaco","MNG":"Mongolia","NIG":"Niger","ALG":"Algeria","B":"Brazil",
    "BOL":"Bolivia","CBG":"Cambodia","INS":"Indonesia","SLM":"Solomon Islands","INT":"Intelsat",
}
def adm_full(code): return ADM_FULL.get(code, code)

# Quarter definition: ordered list of IFIC numbers per quarter key.
QUARTERS = {
    "2026-q1": {
        "label": "First Quarter 2026", "short": "Q1 2026",
        "range_h": "6 January to 31 March 2026",
        "issues": ["3062","3063","3064","3065","3066","3067","3068"],
    },
    "2026-q2": {
        "label": "Second Quarter 2026", "short": "Q2 2026",
        "range_h": "14 April to 23 June 2026",
        "issues": ["3069","3070","3071","3072","3073","3074"],
    },
}
QUARTER_ORDER = ["2026-q2", "2026-q1"]  # newest first for indexes


def quarter_stats(DATA, PUB_DATES, fmt_date, qkey):
    """Aggregate one quarter from the canonical DATA dict."""
    q = QUARTERS[qkey]
    nums = [n for n in q["issues"] if n in DATA]
    filings_all = []
    gso = ngso = pairings = fleets_n = 0
    adm_c = collections.Counter()
    prov_c = collections.Counter()
    fleets = []
    per_issue = []
    for n in nums:
        d = DATA[n]
        gso += d["gso"]; ngso += d["ngso"]
        pairings += sum(d["provmix"].values())
        fleets_n += len(d["fleets"])
        for a, v in d["provmix"].items():
            prov_c[a] += v
        for f in d["filings"]:
            adm_c[f["adm"]] += 1
            filings_all.append(dict(f, ific=n))
        for fl in d["fleets"]:
            fleets.append(dict(fl, ific=n))
        pub = PUB_DATES.get(n)
        per_issue.append({
            "no": n,
            "pub_h": fmt_date(pub) if pub else "",
            "filings": d["total_filings"],
            "gso": d["gso"], "ngso": d["ngso"],
            "pairings": sum(d["provmix"].values()),
            "lead": d["filings"][0]["satellite"] if d["filings"] else "",
        })
    total = len(filings_all)
    busiest = sorted(filings_all, key=lambda f: f.get("reach", 0), reverse=True)[:8]
    fleets.sort(key=lambda fl: fl["count"], reverse=True)
    return {
        "qkey": qkey, "label": q["label"], "short": q["short"], "range_h": q["range_h"],
        "issue_nums": nums,
        "first": nums[0], "last": nums[-1],
        "total": total, "gso": gso, "ngso": ngso, "pairings": pairings,
        "n_issues": len(nums), "n_adms": len(adm_c), "fleets_n": fleets_n,
        "avg_per_issue": round(total / len(nums), 1) if nums else 0,
        "top_adms": adm_c.most_common(12),
        "top_provs": prov_c.most_common(6),
        "busiest": busiest,
        "top_fleets": fleets[:6],
        "per_issue": per_issue,
    }


def quarter_page(head, NAV, FOOTER, subscribe_block, DATA, PUB_DATES, fmt_date, qkey):
    s = quarter_stats(DATA, PUB_DATES, fmt_date, qkey)
    lead_adm, lead_n = s["top_adms"][0]
    lead_pct = round(lead_n / s["total"] * 100) if s["total"] else 0

    # narrative summary (no em/en dashes, per house style)
    prov_txt = ", ".join(f"{k} ({v})" for k, v in s["top_provs"])
    summary = (
        f"Across {s['n_issues']} biweekly circulars, IFIC {s['first']} through {s['last']}, "
        f"the Bureau published {s['total']} coordination requests this quarter, an average of "
        f"{s['avg_per_issue']} per issue. Of these, {s['gso']} are GSO and {s['ngso']} NGSO. "
        f"Filings came from {s['n_adms']} administrations, led by {adm_full(lead_adm)} with "
        f"{lead_n} requests, {lead_pct} percent of the quarter. Coordination this quarter is "
        f"invoked most often under {prov_txt or 'multiple provisions'}."
    )

    # stat band (matches sec_stats styling on the digest pages)
    stat_band = f'''
  <div class="stat-band reveal">
    <div class="s"><b>{s['total']}</b><span>Filings</span></div>
    <div class="s"><b>{s['gso']}</b><span>GSO</span></div>
    <div class="s"><b>{s['ngso']}</b><span>NGSO</span></div>
    <div class="s"><b>{s['n_adms']}</b><span>Administrations</span></div>
    <div class="s"><b>{s['pairings']:,}</b><span>Coordination pairings</span></div>
  </div>
  <div style="font-family:var(--mono);font-size:.7rem;color:var(--muted);margin-top:-28px;margin-bottom:32px">One pairing is one existing network flagged as potentially affected by one new filing.</div>'''

    # per-issue table
    issue_rows = ""
    for it in s["per_issue"]:
        issue_rows += f'''<tr>
          <td class="crc" data-label="IFIC"><a href="/ific/{it['no']}/" style="color:var(--sand)">IFIC {it['no']}</a></td>
          <td data-label="Published" class="mono" style="font-size:.82rem;white-space:nowrap">{esc(it['pub_h'])}</td>
          <td data-label="Filings"><b>{it['filings']}</b></td>
          <td class="mono" data-label="GSO / NGSO">{it['gso']} / {it['ngso']}</td>
          <td class="mono" data-label="Pairings">{it['pairings']:,}</td>
          <td class="sat" data-label="Lead network">{esc(it['lead'])}</td>
        </tr>'''
    issue_table = f'''
  <div class="section" style="padding-top:20px">
    <div class="section-label">Circular by circular</div>
    <h2 style="font-size:1.6rem">The {s['n_issues']} circulars in {s['short']}</h2>
    <div style="overflow-x:auto">
    <table class="ftable stackable">
      <thead><tr><th>IFIC</th><th>Published</th><th>Filings</th><th>GSO / NGSO</th><th>Pairings</th><th>Lead network</th></tr></thead>
      <tbody>{issue_rows}</tbody>
    </table></div>
  </div>'''

    # administration chips (matches sec_administrations)
    chips = " ".join(
        f'<span style="display:inline-block;background:var(--paper-2);border:1px solid var(--line);border-radius:14px;padding:4px 14px;font-size:.85rem;margin:0 6px 8px 0">{esc(adm_full(a))} <b class="mono" style="font-size:.78rem">{n}</b></span>'
        for a, n in s["top_adms"])
    adm_block = f'''
  <div class="section" style="padding-top:0;padding-bottom:26px">
    <div class="section-label reveal">Who filed</div>
    <div class="reveal">{chips}</div>
  </div>'''

    # busiest filings table
    busy_rows = ""
    for f in s["busiest"]:
        pos = f["position"] or ('<span style="color:var(--muted)">NGSO</span>' if f["type"] == "NGSO" else "n/a")
        busy_rows += f'''<tr>
          <td class="sat" data-label="Satellite">{esc(f['satellite'])}</td>
          <td data-label="Administration">{esc(adm_full(f['adm']))}</td>
          <td data-label="Type"><span class="tag {f['type'].lower()}">{f['type']}</span></td>
          <td class="mono" data-label="Position">{pos}</td>
          <td data-label="IFIC"><a href="/ific/{f['ific']}/" style="color:var(--sand)">{f['ific']}</a></td>
          <td class="mono" data-label="Reach" style="text-align:right"><b>{f.get('reach',0):,}</b></td>
        </tr>'''
    busy_table = f'''
  <div class="section" style="padding-top:20px">
    <div class="section-label">Broadest reach</div>
    <h2 style="font-size:1.6rem">Highest-coordination filings of the quarter</h2>
    <p class="sub reveal" style="font-size:.92rem;margin-bottom:18px">Ranked by the number of existing networks each new filing was flagged against.</p>
    <div style="overflow-x:auto">
    <table class="ftable stackable">
      <thead><tr><th>Satellite</th><th>Adm.</th><th>Type</th><th>Position</th><th>IFIC</th><th style="text-align:right">Reach</th></tr></thead>
      <tbody>{busy_rows}</tbody>
    </table></div>
  </div>'''

    # fleets block (reuse .fleet styling)
    fleet_block = ""
    if s["top_fleets"]:
        items = ""
        for fl in s["top_fleets"]:
            sats = ", ".join(fl["sats"][:8]) + ("\u2026" if len(fl["sats"]) > 8 else "")
            items += f'<div class="fleet reveal"><b>{esc(adm_full(fl["adm"]))}</b> filed a cluster of <b>{fl["count"]}</b> networks in the {esc(fl["family"])} family <span class="mono" style="color:var(--muted);font-size:.75rem">(IFIC {fl["ific"]})</span><div class="sats">{esc(sats)}</div></div>'
        fleet_block = f'<div class="section" style="padding-top:0"><div class="section-label">Largest fleets &amp; clusters</div>{items}</div>'

    # cross links to the other quarter
    others = "".join(
        f'<a href="/ific/quarterly/{k}/" class="mono" style="font-size:.8rem;letter-spacing:.06em;color:var(--sand);margin-right:22px">{QUARTERS[k]["short"]} SUMMARY &#8594;</a>'
        for k in QUARTER_ORDER if k != qkey)
    nav_links = f'''
  <div class="section" style="padding-top:8px;padding-bottom:8px">
    <a href="/ific/quarterly/" class="mono" style="font-size:.8rem;letter-spacing:.06em;color:var(--muted);margin-right:22px">&#8592; ALL QUARTERLY SUMMARIES</a>
    {others}
  </div>'''

    title = f"IFIC {s['short']} Summary: {s['total']} Coordination Filings | Farhat Regulatory"
    desc = (f"BR IFIC {s['short']} in review: {s['total']} coordination requests across {s['n_issues']} circulars "
            f"({s['first']} to {s['last']}), {s['gso']} GSO and {s['ngso']} NGSO, from {s['n_adms']} administrations. "
            f"Every circular decoded by Farhat Regulatory.")

    ld = {"@context": "https://schema.org", "@type": "Article",
          "headline": f"BR IFIC {s['short']}: {s['total']} coordination filings",
          "author": {"@type": "Organization", "name": "Farhat Regulatory"},
          "publisher": {"@type": "Organization", "name": "Farhat Regulatory"},
          "description": desc}
    og = f'\n<script type="application/ld+json">{json.dumps(ld)}</script>'

    body = f'''
<header class="doc-hero">
  <canvas id="orbit-canvas"></canvas>
  <div class="wrap">
    <div class="kicker"><span>QUARTERLY SUMMARY</span>&nbsp;&nbsp;&nbsp;<span>{esc(s['range_h'])}</span></div>
    <h1>{esc(s['label'])}</h1>
    <p style="color:#CBBFA6;max-width:54ch;font-size:1.05rem">Every BR IFIC of the quarter, aggregated: the filings, the administrations behind them, and the networks with the broadest coordination reach.</p>
  </div>
</header>
<div class="wrap">
  <div class="section" style="padding-bottom:24px">
    <p class="summary reveal">{summary}</p>
  </div>
  {stat_band}
  {issue_table}
  {adm_block}
  {busy_table}
  {fleet_block}
  {nav_links}
  {subscribe_block("subscribe")}
</div>
{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script>
</body></html>'''
    return head(title, desc, f"/ific/quarterly/{qkey}/", og) + body


def quarterly_index(head, NAV, FOOTER, subscribe_block, DATA, PUB_DATES, fmt_date):
    cards = ""
    for qkey in QUARTER_ORDER:
        s = quarter_stats(DATA, PUB_DATES, fmt_date, qkey)
        lead_adm, lead_n = s["top_adms"][0]
        cards += f'''<a href="/ific/quarterly/{qkey}/" class="issue reveal">
          <div class="num">{s['short'].split()[0]}<small>{s['short'].split()[1]}</small></div>
          <div class="meta"><h3>{s['total']} coordination filings&nbsp;&nbsp;&nbsp;<span style="color:var(--muted);font-weight:400">{esc(s['range_h'])}</span></h3>
            <p>IFIC {s['first']} to {s['last']}<span style="display:inline-block;width:1px;height:.75em;background:var(--line);margin:0 12px;vertical-align:middle"></span>{s['gso']} GSO / {s['ngso']} NGSO<span style="display:inline-block;width:1px;height:.75em;background:var(--line);margin:0 12px;vertical-align:middle"></span>{s['n_adms']} administrations, led by {esc(adm_full(lead_adm))}</p></div>
          <div class="stat" title="Coordination pairings across the quarter"><b>{s['pairings']:,}</b>coordination<br>pairings</div>
        </a>'''
    title = "BR IFIC Quarterly Summaries | ITU Coordination in Review | Farhat Regulatory"
    desc = ("Quarterly reviews of ITU BR IFIC coordination activity: filings, administrations, and the "
            "networks with the broadest reach, aggregated circular by circular by Farhat Regulatory.")
    body = f'''
<header class="doc-hero"><canvas id="orbit-canvas"></canvas><div class="wrap">
  <div class="kicker">In Review</div>
  <h1>Quarterly Summaries</h1>
  <p style="color:#CBBFA6;max-width:52ch;font-size:1.1rem">The BR IFIC digest, stepped back a level: each quarter of ITU coordination activity aggregated into one view.</p>
  <p style="margin-top:14px"><a href="/ific/" class="mono" style="font-size:.78rem;letter-spacing:.1em;color:var(--sand)">BROWSE INDIVIDUAL CIRCULARS &#8594;</a></p>
</div></header>
<div class="wrap"><div class="section">
  <div class="issue-list">{cards}</div>
</div>
{subscribe_block("subscribe")}
</div>{FOOTER()}
<script>window.ORBIT_FILINGS=[];</script>
<script src="/assets/orbit.js?v=3"></script></body></html>'''
    return head(title, desc, "/ific/quarterly/") + body
