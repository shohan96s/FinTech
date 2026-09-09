from collections import defaultdict
from ledger import TX, DECLARED, CANON

MONTHS = ["Jun", "Jul", "Aug"]
CARDS = ["Aurora", "Meridian", "Summit"]
INTEREST_DESC = "INTEREST CHARGE"

def rows():
    for card, month, date, desc, cat, amt in TX:
        yield dict(card=card, month=month, date=date, desc=desc,
                   cat=CANON[cat], amt=round(amt, 2))

def reconcile():
    print("="*74)
    print("RECONCILIATION  (computed transactions  vs  statement-declared totals)")
    print("="*74)
    ok = True
    for card in CARDS:
        for m in MONTHS:
            pays = round(sum(r["amt"] for r in rows() if r["card"]==card and r["month"]==m and r["cat"]=="Payment"),2)
            interest_line = round(sum(r["amt"] for r in rows() if r["card"]==card and r["month"]==m and r["desc"]==INTEREST_DESC),2)
            purch = round(sum(r["amt"] for r in rows() if r["card"]==card and r["month"]==m and r["cat"]!="Payment" and r["desc"]!=INTEREST_DESC),2)
            d = DECLARED[(card,m)]
            p_ok = abs(pays - d["payments"]) < 0.005
            # declared purchases excludes the interest line (interest broken out separately)
            pu_ok = abs(purch - d["purchases"]) < 0.005
            # interest: Summit lists it as a txn line; Aurora shows it only in summary (no line)
            i_ok = abs(interest_line - d["interest"]) < 0.005 or interest_line == 0.0
            line_ok = p_ok and pu_ok and i_ok
            ok = ok and line_ok
            flag = "PASS" if line_ok else "**FAIL**"
            print(f"{card:9} {m}: pay {pays:>9.2f}/{d['payments']:>9.2f}  "
                  f"purch {purch:>8.2f}/{d['purchases']:>8.2f}  {flag}")
    print(f"\nOverall reconciliation: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return ok

def spend_rows():
    return [r for r in rows() if r["cat"] not in ("Payment",)]

def by_month():
    out = {m: 0.0 for m in MONTHS}
    for r in spend_rows():
        out[r["month"]] += r["amt"]
    return {m: round(v,2) for m,v in out.items()}

def by_category(month=None):
    out = defaultdict(float)
    for r in spend_rows():
        if month and r["month"]!=month: continue
        out[r["cat"]] += r["amt"]
    return {k: round(v,2) for k,v in sorted(out.items(), key=lambda x:-x[1])}

def by_category_month():
    out = {}
    for cat in set(r["cat"] for r in spend_rows()):
        out[cat] = {m: round(sum(r["amt"] for r in spend_rows() if r["cat"]==cat and r["month"]==m),2) for m in MONTHS}
    return out

def by_card():
    out = defaultdict(float)
    for r in spend_rows():
        out[r["card"]] += r["amt"]
    return {k: round(v,2) for k,v in sorted(out.items(), key=lambda x:-x[1])}

def fees():
    out = []
    for r in rows():
        if r["cat"]=="Fees":
            out.append(r)
    total = round(sum(r["amt"] for r in out),2)
    return out, total

def normalize_merchant(desc):
    d = desc.upper()
    # strip order/reference suffixes
    for token in ["*", "#"]:
        if token in d:
            d = d.split(token)[0]
    d = d.replace(".COM","").replace(" ORDER","").replace(" MEMBERSHIP","")
    d = d.replace(" FREE TRIAL","").replace(" MONTHLY","")
    return d.strip()

def subscriptions():
    seen = defaultdict(lambda: defaultdict(list))  # merchant -> month -> [amts]
    for r in spend_rows():
        if r["cat"] in ("Subscriptions","Utilities") or r["desc"].split()[0] in ("NETFLIX","SPOTIFY"):
            seen[normalize_merchant(r["desc"])][r["month"]].append(r["amt"])
    subs = {}
    for merch, mo in seen.items():
        if len(mo) >= 2:  # recurring
            latest = mo.get("Aug") or mo.get("Jul") or mo.get("Jun")
            subs[merch] = dict(months=sorted(mo.keys()),
                               monthly=round(latest[0],2),
                               all_amts={m: mo[m] for m in mo})
    return subs

def duplicates():
    hits = []
    from datetime import date
    def d2(mon, day): return date(2026, {"Jun":6,"Jul":7,"Aug":8}[mon], day)
    bykey = defaultdict(list)
    for r in spend_rows():
        day = int(r["date"].split()[1])
        bykey[(r["card"], normalize_merchant(r["desc"]), r["amt"])].append((r["month"], day, r["date"]))
    for (card, merch, amt), occ in bykey.items():
        occ.sort(key=lambda x: d2(x[0], x[1]))
        for i in range(len(occ)-1):
            gap = (d2(occ[i+1][0], occ[i+1][1]) - d2(occ[i][0], occ[i][1])).days
            if gap <= 4:
                hits.append(dict(card=card, merchant=merch, amount=amt,
                                 first=occ[i][2], second=occ[i+1][2], gap_days=gap))
    return hits

def trend(cat):
    m = {mo: round(sum(r["amt"] for r in spend_rows() if r["cat"]==cat and r["month"]==mo),2) for mo in MONTHS}
    return m

if __name__ == "__main__":
    ok = reconcile()
    print("\n" + "="*74); print("CONSOLIDATED SPEND BY MONTH (all 3 cards)"); print("="*74)
    print(by_month())
    print("\nBY CATEGORY (3-mo total):")
    for k,v in by_category().items(): print(f"  {k:14} {v:>9.2f}")
    print("\nBY CARD (3-mo total):")
    for k,v in by_card().items(): print(f"  {k:10} {v:>9.2f}")
    f, ftot = fees()
    print(f"\nFEES & INTEREST total: {ftot:.2f}")
    for r in f: print(f"  {r['card']:9} {r['date']} {r['desc']:20} {r['amt']:.2f}")
    print("\nRECURRING SUBSCRIPTIONS/UTILITIES:")
    subs = subscriptions()
    print(f"  count={len(subs)}  est monthly total={round(sum(s['monthly'] for s in subs.values()),2)}")
    for m,s in sorted(subs.items(), key=lambda x:-x[1]['monthly']):
        print(f"  {m:24} ${s['monthly']:>6.2f}/mo  months={s['months']}")
    print("\nDUPLICATE / DOUBLE-CHARGE FLAGS:")
    for h in duplicates(): print(f"  {h}")
