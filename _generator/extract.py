import subprocess, csv, io, json, re
from collections import Counter, defaultdict

def rows(mdb, table):
    r = subprocess.run(["mdb-export", mdb, table], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip(): return [], []
    rr = list(csv.reader(io.StringIO(r.stdout)))
    return rr[0], rr[1:]

def col(h, name): return h.index(name) if name in h else -1

BANDS = [("VHF",30,300),("UHF",300,1000),("L",1000,2000),("S",2000,4000),
         ("C",4000,8000),("X",8000,12000),("Ku",12000,17300),("Ka",17300,31000),
         ("Q/V",33000,76000)]
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
    # com_el = the filings (satellite, adm, type, position)
    h, cr = rows(mdb, "com_el")
    i = {c: col(h, c) for c in ["ntc_id","ntc_type","adm","sat_name","long_nom","long_dec","d_rcv","ntwk_org"]}
    # all_aff_ntw = affected networks (for reach + provisions)
    ha, ar = rows(mdb, "all_aff_ntw")
    ia = {c: col(ha, c) for c in ["aff_ntc_id","coord_prov","adm","sat_name","confirmed"]}
    # map ntc_id -> provisions/reach via grp/grp_aff_rec/all_aff_ntw
    hg, gr = rows(mdb, "grp"); ig_gid=col(hg,"grp_id"); ig_ntc=col(hg,"ntc_id"); ig_prov=col(hg,"prov")
    ig_fmin=col(hg,"freq_min"); ig_fmax=col(hg,"freq_max")
    gid2ntc = {r[ig_gid]: r[ig_ntc] for r in gr}
    ntc_freqs = defaultdict(set)
    ig_area=col(hg,"area_name")
    ntc_areas = defaultdict(set)
    for r in gr:
        if ig_fmin>=0 and ig_fmax>=0 and r[ig_fmin] and r[ig_fmax]:
            try: ntc_freqs[r[ig_ntc]].add((float(r[ig_fmin]), float(r[ig_fmax])))
            except ValueError: pass
        if ig_area>=0 and len(r)>ig_area and r[ig_area].strip():
            ntc_areas[r[ig_ntc]].add(r[ig_area].strip())
    hgar, gar = rows(mdb, "grp_aff_rec"); ir_gid=col(hgar,"grp_id"); ir_arid=col(hgar,"aff_rec_id")
    # affected records per ntc
    arid2info = {}
    for r in ar:
        arid2info.setdefault(r[col(ha,"aff_rec_id")] if col(ha,"aff_rec_id")>=0 else "", []).append(r)
    # provisions & reach per filing ntc — dedupe by (ntc, network-name, provision)
    # so counts reflect distinct affected networks, not fanned-out join rows.
    ntc_prov_nets = defaultdict(lambda: defaultdict(set))  # ntc -> prov -> set(network)
    ntc_reach = defaultdict(set)
    for r in gar:
        ntc = gid2ntc.get(r[ir_gid])
        if not ntc: continue
        for arow in arid2info.get(r[ir_arid], []):
            pv = arow[ia["coord_prov"]] if ia["coord_prov"]>=0 else ""
            nm = arow[ia["sat_name"]] if ia["sat_name"]>=0 else ""
            key = nm or arow[ia["aff_ntc_id"]] if ia["aff_ntc_id"]>=0 else nm
            if pv and key: ntc_prov_nets[ntc][pv].add(key)
            if nm: ntc_reach[ntc].add(nm)
    ntc_provs = {ntc:{pv:len(nets) for pv,nets in pm.items()} for ntc,pm in ntc_prov_nets.items()}

    filings = []
    provmix = Counter(); admc=Counter(); ngso=gso=0; fleets=defaultdict(list)
    for r in cr:
        ntc = r[i["ntc_id"]]
        sat = r[i["sat_name"]] or ""
        adm = r[i["adm"]] or ""
        typ = r[i["ntc_type"]] or ""
        pos_dec = (r[i["long_dec"]] if i["long_dec"]>=0 and r[i["long_dec"]] else (r[i["long_nom"]] if i["long_nom"]>=0 else ""))
        pos = ""
        if pos_dec:
            try:
                v=float(pos_dec); pos = ("%.1f°E"%v) if v>=0 else ("%.1f°W"%abs(v))
            except: pos=pos_dec
        is_gso = (typ=="G")
        if is_gso: gso+=1
        else: ngso+=1
        provs = dict(ntc_provs.get(ntc, {}))
        reach = len(ntc_reach.get(ntc, set()))
        for p,ct in provs.items(): provmix[p]+=ct
        if adm: admc[adm]+=1
        if sat:
            fam = re.split(r"[-\d]", sat)[0] or sat
            fleets[(adm,fam)].append(sat)
        franges = sorted(ntc_freqs.get(ntc, set()))
        fspan = ""; lo=hi=None
        if franges:
            lo = min(f[0] for f in franges); hi = max(f[1] for f in franges)
            fspan = fmt_freq(lo) + " to " + fmt_freq(hi) if abs(hi-lo)>1e-9 else fmt_freq(lo)
        filings.append({"ntc":ntc,"crc":ntc,"satellite":sat,"adm":adm,
                        "type":"GSO" if is_gso else "NGSO","position":pos,
                        "provisions":provs,"reach":reach,
                        "bands":band_letters(franges),"freq_span":fspan,
                        "fmin_mhz":lo,"fmax_mhz":hi,
                        "areas":sorted(ntc_areas.get(ntc,set())),
                        "d_rcv":(r[i["d_rcv"]] or "").split(" ")[0]})
    filings.sort(key=lambda x:-x["reach"])
    fleet_list=[{"adm":a,"family":f,"count":len(s),"sats":sorted(set(s))} for (a,f),s in fleets.items() if len(s)>=2]
    fleet_list.sort(key=lambda x:-x["count"])
    return {"ific_no":ific_no,"total_filings":len(cr),"gso":gso,"ngso":ngso,
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
