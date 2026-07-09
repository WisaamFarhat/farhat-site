import subprocess, csv, io, json, re
from collections import Counter, defaultdict, OrderedDict

import shutil as _shutil
HAVE_MDBTOOLS = _shutil.which("mdb-export") is not None
_PYODBC_HELP = (
    "No way to read Access databases found.\n"
    "  Windows: pip install pyodbc, and install the Microsoft Access Database Engine\n"
    "  redistributable matching your Python (64 bit for 64 bit Python):\n"
    "  https://www.microsoft.com/en-us/download/details.aspx?id=54920\n"
    "  Alternative: run under WSL with mdbtools (sudo apt install mdbtools).")
_conns = {}

def _access_connect(mdb):
    import pyodbc
    cn = _conns.get(mdb)
    if cn is not None:
        return cn
    drivers = [d for d in pyodbc.drivers() if "Microsoft Access Driver" in d]
    if not drivers:
        raise SystemExit(_PYODBC_HELP)
    last = None
    for drv in drivers:
        try:
            cn = pyodbc.connect(r"DRIVER={%s};DBQ=%s" % (drv, mdb), autocommit=True)
            _conns[mdb] = cn
            return cn
        except Exception as e:
            last = e
    raise SystemExit("Access ODBC driver present but connection failed "
                     "(usually a 32/64 bit mismatch between Python and the driver).\n"
                     + _PYODBC_HELP + "\nDriver error: %s" % last)

def rows(mdb, table):
    if HAVE_MDBTOOLS:
        r = subprocess.run(["mdb-export", mdb, table], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip(): return [], []
        rr = list(csv.reader(io.StringIO(r.stdout)))
        return rr[0], rr[1:]
    try:
        import pyodbc  # noqa: F401
    except ImportError:
        raise SystemExit(_PYODBC_HELP)
    cn = _access_connect(mdb)
    cur = cn.cursor()
    try:
        cur.execute("SELECT * FROM [%s]" % table)
    except Exception:
        return [], []
    hdr = [d[0] for d in cur.description]
    data = [["" if v is None else str(v) for v in row] for row in cur.fetchall()]
    cur.close()
    return hdr, data

def col(h, name): return h.index(name) if name in h else -1

# IEEE standard radar-frequency band designations (ranges in MHz)
BANDS = [("HF",3,30),("VHF",30,300),("UHF",300,1000),("L",1000,2000),
         ("S",2000,4000),("C",4000,8000),("X",8000,12000),("Ku",12000,18000),
         ("K",18000,27000),("Ka",27000,40000),("V",40000,75000),
         ("W",75000,110000),("mm",110000,300000)]
def band_letters(ranges):
    out=[]
    for name,lo,hi in BANDS:
        if any(fmax>lo and fmin<hi for fmin,fmax in ranges):
            out.append(name)
    return out
def fmt_freq(mhz):
    if mhz < 1000: return ("%.4g" % mhz) + " MHz"
    g = mhz/1000.0
    s = ("%.4g" % g)
    return s + " GHz"

def extract(mdb, ific_no):
    """Schema adaptive: reads either the official BR IFIC publication database
    (pub_ssn ssn_ref, notice, geo, non_geo) or a SpaceCom comments export (com_el)."""
    hp, pr = rows(mdb, "pub_ssn")
    hn_probe, rn_probe = rows(mdb, "notice")
    official = bool(rn_probe)

    # ---- source filings: [{ntc, crc, adm, org, sat, typ, long_nom, d_rcv}] ----
    src=[]
    if official:
        ip={k:col(hp,k) for k in ["ntc_id","ssn_no","ssn_rev"]}
        crc_ids={}
        for r in pr:
            if r[col(hp,"ssn_ref")]=="CR/C":
                crc_ids[r[ip["ntc_id"]]] = r[ip["ssn_no"]] + (r[ip["ssn_rev"]] or "")
        hn,rn = hn_probe, rn_probe
        iN={k:col(hn,k) for k in ["ntc_id","adm","ntwk_org","ntc_type","d_rcv"]}
        hg,rgeo = rows(mdb,"geo")
        geo={r[col(hg,"ntc_id")]:(r[col(hg,"sat_name")], r[col(hg,"long_nom")]) for r in rgeo}
        hng,rng = rows(mdb,"non_geo")
        ngeo={r[col(hng,"ntc_id")]:r[col(hng,"sat_name")] for r in rng}
        for r in rn:
            ntc=r[iN["ntc_id"]]
            if ntc not in crc_ids: continue
            sat, lon = geo.get(ntc, ("",""))
            if not sat: sat = ngeo.get(ntc,"")
            src.append({"ntc":ntc,"crc":crc_ids[ntc],
                        "adm":r[iN["adm"]],"org":r[iN["ntwk_org"]],
                        "sat":sat,"typ":r[iN["ntc_type"]],"long_nom":lon,
                        "d_rcv":(r[iN["d_rcv"]] or "").split(" ")[0]})
    else:
        h, cr = rows(mdb, "com_el")
        i={k:col(h,k) for k in ["ntc_id","ntc_type","adm","sat_name","long_nom","long_dec","d_rcv","ntwk_org"]}
        for r in cr:
            src.append({"ntc":r[i["ntc_id"]],"crc":r[i["ntc_id"]],
                        "adm":r[i["adm"]],"org":r[i["ntwk_org"]],
                        "sat":r[i["sat_name"]],"typ":r[i["ntc_type"]],
                        "long_nom":(r[i["long_dec"]] if i["long_dec"]>=0 and r[i["long_dec"]] else r[i["long_nom"]]),
                        "d_rcv":(r[i["d_rcv"]] or "").split(" ")[0]})

    keep={s["ntc"] for s in src}

    # ---- affected networks + provisions + freq via grp joins (filtered to CR/C) ----
    ha, ar = rows(mdb, "all_aff_ntw")
    ia={k:col(ha,k) for k in ["aff_rec_id","coord_prov","adm","sat_name"]}
    arid2info=defaultdict(list)
    for r in ar: arid2info[r[ia["aff_rec_id"]]].append(r)
    hg, gr = rows(mdb, "grp")
    ig={k:col(hg,k) for k in ["grp_id","ntc_id","freq_min","freq_max","area_name"]}
    gid2ntc={}
    ntc_freqs=defaultdict(set); ntc_areas=defaultdict(set)
    for r in gr:
        ntc=r[ig["ntc_id"]]
        if ntc not in keep: continue
        gid2ntc[r[ig["grp_id"]]]=ntc
        if r[ig["freq_min"]] and r[ig["freq_max"]]:
            try: ntc_freqs[ntc].add((float(r[ig["freq_min"]]),float(r[ig["freq_max"]])))
            except ValueError: pass
        if ig["area_name"]>=0 and len(r)>ig["area_name"] and r[ig["area_name"]].strip():
            ntc_areas[ntc].add(r[ig["area_name"]].strip())
    hr, rrs = rows(mdb, "grp_aff_rec")
    ir={k:col(hr,k) for k in ["grp_id","aff_rec_id"]}
    ntc_prov_nets=defaultdict(lambda: defaultdict(set))
    ntc_reach=defaultdict(set)
    for r in rrs:
        ntc=gid2ntc.get(r[ir["grp_id"]])
        if not ntc: continue
        for arow in arid2info.get(r[ir["aff_rec_id"]], []):
            pv=arow[ia["coord_prov"]]; nm=arow[ia["sat_name"]]
            if pv and nm: ntc_prov_nets[ntc][pv].add(nm)
            if nm: ntc_reach[ntc].add(nm)

    # ---- assemble ----
    # one CR/C special section = one digest row; merge notices that share a section
    by_crc=OrderedDict()
    for s in src:
        by_crc.setdefault(s["crc"], []).append(s)
    merged=[]
    for crc, group in by_crc.items():
        g0=dict(group[0])
        g0["ntcs"]=[g["ntc"] for g in group]
        merged.append(g0)

    filings=[]; provmix=Counter(); admc=Counter(); ngso=gso=0; fleets=defaultdict(list)
    for s in merged:
        is_gso = (s["typ"]=="G")
        if is_gso: gso+=1
        else: ngso+=1
        pos=""
        if is_gso and s["long_nom"] not in ("","N-GSO","NGSO"):
            try:
                v=float(s["long_nom"]); pos=("%.1f\u00b0E"%v) if v>=0 else ("%.1f\u00b0W"%abs(v))
            except ValueError: pos=s["long_nom"]
        _pn=defaultdict(set)
        for _n in s["ntcs"]:
            for pv,nets in ntc_prov_nets.get(_n,{}).items(): _pn[pv]|=nets
        provs={pv:len(nets) for pv,nets in _pn.items()}
        for p,ct in provs.items(): provmix[p]+=ct
        if s["adm"]: admc[s["adm"]]+=1
        sat=s["sat"] or ""
        if sat:
            fam=re.split(r"[-\d]",sat)[0] or sat
            fleets[(s["adm"],fam)].append(sat)
        _fr=set(); _rc=set(); _ar=set()
        for _n in s["ntcs"]:
            _fr|=ntc_freqs.get(_n,set()); _rc|=ntc_reach.get(_n,set()); _ar|=ntc_areas.get(_n,set())
        franges=sorted(_fr)
        lo=hi=None; fspan=""
        if franges:
            lo=min(f[0] for f in franges); hi=max(f[1] for f in franges)
            fspan=fmt_freq(lo)+" to "+fmt_freq(hi) if abs(hi-lo)>1e-9 else fmt_freq(lo)
        filings.append({"ntc":s["ntc"],"crc":s["crc"],"satellite":sat or "(unnamed)","adm":s["adm"],
                        "type":"GSO" if is_gso else "NGSO","position":pos,
                        "provisions":provs,"reach":len(_rc),
                        "bands":band_letters(franges),"freq_span":fspan,
                        "fmin_mhz":lo,"fmax_mhz":hi,
                        "areas":sorted(_ar),
                        "d_rcv":s["d_rcv"]})
    filings.sort(key=lambda x:-x["reach"])
    fleet_list=[{"adm":a,"family":f,"count":len(ss),"sats":sorted(set(ss))} for (a,f),ss in fleets.items() if len(ss)>=2]
    fleet_list.sort(key=lambda x:-x["count"])
    return {"ific_no":ific_no,"total_filings":len(merged),"gso":gso,"ngso":ngso,
            "provmix":dict(provmix),"top_adms":admc.most_common(8),
            "filings":filings,"fleets":fleet_list[:6]}

if __name__ == "__main__":
    data = {}
    for num,f in [("3065","IFIC3065_USA-532/IFIC3065_USA-532.mdb"),
                  ("3066","IFIC3066_USA-532/IFIC3066_USA-532.mdb"),
                  ("3067","IFIC3067_USA-532.mdb")]:
        data[num] = extract(f, num)
        d=data[num]
        print(f"IFIC {num}: {d['total_filings']} filings, {d['gso']} GSO/{d['ngso']} NGSO, {len(d['fleets'])} fleets")
        for x in d["filings"][:3]:
            print(f"   {x['satellite']:<20} {x['adm']:<5} {x['type']:<5} {x['position'] or '-':<9} reach={x['reach']} provs={list(x['provisions'].keys())}")
    json.dump(data, open("ific_data.json","w"), indent=2)
    print("\nsaved ific_data.json")
