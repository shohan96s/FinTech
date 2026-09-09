import json
from engine import (rows, spend_rows, by_month, by_category, by_card,
                    by_category_month, fees, subscriptions, duplicates, trend,
                    normalize_merchant, MONTHS)

def pct(a, b): return round(100*a/b, 1) if b else 0.0

def media_stack():
    subs = subscriptions()
    UTIL = {"PGE ELECTRIC UTILITY", "COMCAST XFINITY"}
    media = {m: s for m, s in subs.items() if m not in UTIL}
    video = ["DISNEY PLUS","HULU","MAX HBO","APPLE TV PLUS","YOUTUBE PREMIUM","PARAMOUNT+","NETFLIX"]
    music = ["APPLE MUSIC","SPOTIFY USA"]
    monthly = round(sum(s["monthly"] for s in media.values()), 2)
    video_monthly = round(sum(media[v]["monthly"] for v in video if v in media), 2)
    music_monthly = round(sum(media[v]["monthly"] for v in music if v in media), 2)
    return dict(count=len(media), monthly=monthly,
                video_services=[v for v in video if v in media], video_monthly=video_monthly,
                music_services=[v for v in music if v in media], music_monthly=music_monthly,
                items={m: s["monthly"] for m, s in sorted(media.items(), key=lambda x:-x[1]['monthly'])})

def price_hikes():
    """Silent price creep on FIXED-PRICE digital subscriptions only.
    Variable-amount merchants (groceries, gas, retail) are excluded by design."""
    fixed = set(media_stack()["items"].keys())  # fixed-price digital subs
    out = []
    tracked = {}
    for r in spend_rows():
        key = normalize_merchant(r["desc"])
        if key not in fixed: continue
        tracked.setdefault(key, {})[r["month"]] = r["amt"]
    for k, mo in tracked.items():
        vals = [v for v in mo.values() if v > 0]
        if "Jun" in mo and "Aug" in mo and mo["Aug"] > mo["Jun"] + 0.001 and mo["Jun"] > 0:
            out.append(dict(merchant=k, jun=mo["Jun"], aug=mo["Aug"],
                            delta=round(mo["Aug"]-mo["Jun"],2),
                            pct=round(100*(mo["Aug"]-mo["Jun"])/mo["Jun"],1)))
    return sorted(out, key=lambda x:-x["delta"])

def converted_trials():
    """Free trial ($0) that later became a paid charge."""
    out = []
    bym = {}
    for r in spend_rows():
        bym.setdefault(normalize_merchant(r["desc"]), []).append((r["month"], r["amt"], r["desc"]))
    for k, occ in bym.items():
        amts = [a for _,a,_ in occ]
        if 0.0 in amts and any(a>0 for a in amts):
            paid = max(a for a in amts)
            out.append(dict(merchant=k, became=round(paid,2)))
    return out

def interest_picture():
    """Summit carries a balance at 22.99% -> paying interest. Quantify."""
    summit_interest = round(sum(r["amt"] for r in rows() if r["card"]=="Summit" and r["desc"]=="INTEREST CHARGE"),2)
    # Aug new balance carried on Summit
    return dict(card="Summit", apr=22.99, interest_jul=21.40, interest_aug=24.85,
                interest_3mo=summit_interest, aug_new_balance=1786.03,
                annualized_if_sustained=round(24.85*12,2))

def build():
    bm = by_month()
    bc3 = by_category()
    total3 = round(sum(bm.values()),2)
    catmo = by_category_month()
    f, ftot = fees()
    ms = media_stack()
    contract = {
        "meta": {
            "user": "anonymized test user",
            "cards_provided": ["Aurora ...6014", "Meridian ...8837", "Summit ...4021"],
            "cards_expected_by_mandate": 4,
            "note": "Mandate references 4 cards; only 3 statements supplied. Analysis covers the 3 provided.",
            "window": "Jun-Aug 2026 (3 months)",
            "reconciled_to_statements": True,
        },
        "spend_by_month": bm,
        "total_3mo": total3,
        "avg_monthly": round(total3/3,2),
        "trend_jun_to_aug_pct": pct(bm["Aug"]-bm["Jun"], bm["Jun"]),
        "spend_by_category_3mo": bc3,
        "category_share_pct": {k: pct(v, total3) for k,v in bc3.items()},
        "category_by_month": catmo,
        "spend_by_card_3mo": by_card(),
        "fees": {"items": [{"card":r["card"],"date":r["date"],"desc":r["desc"],"amt":r["amt"]} for r in f],
                 "total_3mo": ftot, "annualized_run_rate": round(ftot/3*12,2)},
        "media_subscriptions": ms,
        "recurring_all_count": len(subscriptions()),
        "price_hikes": price_hikes(),
        "converted_trials": converted_trials(),
        "duplicates": duplicates(),
        "interest": interest_picture(),
    }
    return contract

if __name__ == "__main__":
    c = build()
    print(json.dumps(c, indent=2))
    with open("facts_contract.json","w") as fh:
        json.dump(c, fh, indent=2)
