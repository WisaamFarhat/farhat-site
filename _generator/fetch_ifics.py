#!/usr/bin/env python3
"""Fetch BR IFIC databases directly from the ITU and feed the digest pipeline.

Run on a machine with normal internet access (itu.int reachable):

    python3 fetch_ifics.py 3068 3069 3070          # specific issues
    python3 fetch_ifics.py --year-to-date          # every 2026 issue published so far
    python3 fetch_ifics.py --inspect 3068          # download + list tables only

For each issue it downloads the official zip, extracts the Access database, and:
  * if the database has the comments format tables (com_el, all_aff_ntw, grp,
    grp_aff_rec, pub_ssn) it runs the existing extractor and merges the issue
    into ific_data.json, ready for generate.py;
  * otherwise it prints the table list so the extractor can be adapted to the
    publication schema, without guessing.

Downloads are cached in ./_ific_cache so re-runs cost nothing.
"""
import argparse, io, json, os, shutil, subprocess, sys, tempfile, urllib.request, zipfile
from datetime import datetime

ZIP_BASE = os.environ.get("ITU_ZIP_BASE", "https://www.itu.int/sns/ific10/ific{}.zip")
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "_ific_cache")
print(f"Downloads cache: {CACHE}")
print(f"Data file:       {os.path.join(HERE, 'ific_data.json')}")
NEEDED = {"com_el", "all_aff_ntw", "grp", "grp_aff_rec", "pub_ssn"}

# 2026 schedule (official)
SCHEDULE_2026 = ["3062","3063","3064","3065","3066","3067","3068","3069","3070",
    "3071","3072","3073","3074","3075","3076","3077","3078","3079","3080","3081",
    "3082","3083","3084","3085","3086"]
PUB = {"3062":"2026-01-06","3063":"2026-01-20","3064":"2026-02-03","3065":"2026-02-17",
 "3066":"2026-03-03","3067":"2026-03-17","3068":"2026-03-31","3069":"2026-04-14",
 "3070":"2026-04-28","3071":"2026-05-12","3072":"2026-05-26","3073":"2026-06-09",
 "3074":"2026-06-23","3075":"2026-07-07","3076":"2026-07-21","3077":"2026-08-04",
 "3078":"2026-08-18","3079":"2026-09-01","3080":"2026-09-15","3081":"2026-09-29",
 "3082":"2026-10-13","3083":"2026-10-27","3084":"2026-11-10","3085":"2026-11-24",
 "3086":"2026-12-08"}

def mdb_tables(path):
    if shutil.which("mdb-tables"):
        r = subprocess.run(["mdb-tables","-1",path], capture_output=True, text=True)
        if r.returncode == 0:
            return {t for t in r.stdout.split("\n") if t}
    # Windows: use the Microsoft Access ODBC driver through pyodbc
    import extract as EX
    cn = EX._access_connect(path)
    cur = cn.cursor()
    tabs = {row.table_name for row in cur.tables(tableType="TABLE")}
    cur.close()
    return tabs

def download(num):
    os.makedirs(CACHE, exist_ok=True)
    dest = os.path.join(CACHE, f"ific{num}.zip")
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"  [{num}] cached ({os.path.getsize(dest)//1048576} MB)")
        return dest
    url = ZIP_BASE.format(num)
    print(f"  [{num}] downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent":"FarhatRegulatory-Digest/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest,"wb") as f:
        shutil.copyfileobj(r, f)
    print(f"  [{num}] saved {os.path.getsize(dest)//1048576} MB")
    return dest

def find_mdbs(zpath, workdir):
    out=[]
    with zipfile.ZipFile(zpath) as z:
        for name in z.namelist():
            if name.lower().endswith((".mdb",".accdb")):
                z.extract(name, workdir)
                out.append(os.path.join(workdir,name))
            elif name.lower().endswith(".zip"):  # nested zips occur in BR media
                inner = z.extract(name, workdir)
                try:
                    with zipfile.ZipFile(inner) as z2:
                        for n2 in z2.namelist():
                            if n2.lower().endswith((".mdb",".accdb")):
                                z2.extract(n2, workdir)
                                out.append(os.path.join(workdir,n2))
                except zipfile.BadZipFile:
                    pass
    return out

def process(num, inspect_only=False):
    zpath = download(num)
    with tempfile.TemporaryDirectory() as tmp:
        mdbs = find_mdbs(zpath, tmp)
        if not mdbs:
            print(f"  [{num}] no Access database found in the zip"); return False
        for m in mdbs:
            tabs = mdb_tables(m)
            label = os.path.basename(m)
            if NEEDED <= tabs:
                if inspect_only:
                    print(f"  [{num}] {label}: comments format, ready"); return True
                print(f"  [{num}] {label}: comments format, extracting")
                sys.path.insert(0, HERE)
                import extract as EX  # reuses the site extractor
                data_path = os.path.join(HERE,"ific_data.json")
                data = json.load(open(data_path)) if os.path.exists(data_path) else {}
                data[num] = EX.extract(m, num)
                json.dump(data, open(data_path,"w"), indent=2)
                print(f"  [{num}] merged into ific_data.json "
                      f"({data[num]['total_filings']} filings)")
                return True
            print(f"  [{num}] {label}: different schema, tables = {sorted(tabs)}")
        print(f"  [{num}] none matched the comments format; send the table lists "
              f"above to adapt the extractor.")
        return False

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("issues", nargs="*", help="IFIC numbers, e.g. 3068 3069")
    ap.add_argument("--year-to-date", action="store_true",
                    help="every 2026 issue published up to today")
    ap.add_argument("--inspect", action="store_true",
                    help="download and report schema only")
    args = ap.parse_args()
    issues = list(args.issues)
    if args.year_to_date:
        today = datetime.now().date().isoformat()
        issues += [n for n in SCHEDULE_2026 if PUB[n] <= today]
    issues = sorted(set(issues))
    if not issues:
        ap.error("give issue numbers or --year-to-date")
    ok = 0
    for n in issues:
        try:
            ok += bool(process(n, inspect_only=args.inspect))
        except Exception as e:
            print(f"  [{n}] failed: {e}")
    print(f"\n{ok}/{len(issues)} processed."
          + ("" if args.inspect else " Now run: python3 generate.py"))
