#!/usr/bin/env python3
# Apply final_wikidata_edits.csv to Wikidata, one lexeme at a time.
#   python3 apply_edits.py            dry run: prints the planned edits, no login
#   python3 apply_edits.py --apply    logs in (WD_USER env, password prompted) and edits
# Idempotent: before editing, each lexeme is re-fetched and anything already present
# (a sense with the same English gloss, a claim with the same value) is skipped.
# Every change is re-fetched and checked afterwards, and logged to applied_changes.csv.
import argparse, csv, getpass, json, os, re, sys, time

API = "https://www.wikidata.org/w/api.php"
HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY = "Hindustani lexeme enrichment (EMLDS): sense, grammar and dictionary source"
UL, PLATTS = "Q18625803", "Q108916279"
HELD = set()  # (lexeme_id, property) pairs held back after source checks; see notes

def item(q): return {"entity-type": "item", "id": q}
def snak(p, dtype, value):
    if dtype == "item":   dv = {"type": "wikibase-entityid", "value": item(value)}
    elif dtype == "sense": dv = {"type": "wikibase-entityid", "value": {"entity-type": "sense", "id": value}}
    elif dtype == "mono": dv = {"type": "monolingualtext", "value": {"text": value, "language": "ur"}}
    else:                 dv = {"type": "string", "value": value}
    return {"snaktype": "value", "property": p, "datavalue": dv}
def claim(p, dtype, value, quals=None, refs=None):
    c = {"mainsnak": snak(p, dtype, value), "type": "statement", "rank": "normal"}
    if quals: c["qualifiers"] = _group(quals)
    if refs: c["references"] = [{"snaks": _group(refs)}]
    return c
def _group(snaks):
    out = {}
    for s in snaks: out.setdefault(s["property"], []).append(s)
    return out
def qid(v): return re.search(r"Q\d+", v).group(0)

def load_plan():
    plan = {}
    with open(os.path.join(HERE, "final_wikidata_edits.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if not r["source"].strip():
                print("SKIP (no source):", r["lexeme_id"], r["property"]); continue
            plan.setdefault(r["lexeme_id"], {"lemma": r["lemma"], "rows": []})["rows"].append(r)
    return plan

def lexeme_claims(rows):
    """Lexeme-level statements (property, dtype, value, qualifiers, references, csv row)."""
    out = []
    for r in rows:
        p, v = r["property"], r["value"]
        if p in ("P5185", "P9295"):
            out.append((p, "item", qid(v), None, None, r))
        elif p == "P1343":
            page = re.search(r"page (\d+)", v).group(1)
            out.append((p, "item", qid(v), [snak("P304", "string", page)], None, r))
        elif p == "P11350":
            out.append((p, "string", v.strip(), None, None, r))
    return out

def has_claim(ent, p, value):
    for c in ent.get("claims", {}).get(p, []):
        dv = c["mainsnak"].get("datavalue", {}).get("value")
        got = dv.get("id") if isinstance(dv, dict) and "id" in dv else (dv.get("text") if isinstance(dv, dict) else dv)
        if got == value: return True
    return False

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sleep", type=float, default=8.0); ap.add_argument("--only")
    a = ap.parse_args()
    import requests
    s = requests.Session(); s.headers["User-Agent"] = "emlds-hindustani-lexeme-enrichment/0.1 (User:Abxxra)"
    def get(params):
        for i in range(6):
            r = s.get(API, params=dict(params, format="json"), timeout=60)
            if r.status_code == 429: time.sleep(int(r.headers.get("Retry-After", 60)) + 10 * i); continue
            return r.json()
        sys.exit("rate limited too long")
    def fetch(lid): return get({"action": "wbgetentities", "ids": lid})["entities"][lid]

    plan = load_plan()
    if a.only: plan = {k: v for k, v in plan.items() if k in a.only.split(",")}
    token = None
    if a.apply:
        user = os.environ.get("WD_USER") or input("Wikidata bot user (User@BotName): ").strip()
        pw = getpass.getpass("Wikidata bot password: ")
        lt = get({"action": "query", "meta": "tokens", "type": "login"})["query"]["tokens"]["logintoken"]
        r = s.post(API, data={"action": "login", "lgname": user, "lgpassword": pw, "lgtoken": lt, "format": "json"}).json()
        if r.get("login", {}).get("result") != "Success": sys.exit(f"Login failed: {r.get('login', {}).get('reason', r)}")
        token = get({"action": "query", "meta": "tokens"})["query"]["tokens"]["csrftoken"]
        print("Logged in as", user, flush=True)

    def post(data):
        for i in range(6):
            r = s.post(API, data=dict(data, token=token, format="json", bot=1, summary=SUMMARY), timeout=60).json()
            code = r.get("error", {}).get("code")
            if code in ("ratelimited", "maxlag", "no-automatic-entity-id"):
                print("  rate limited, waiting", 90 * (i + 1), "s", flush=True); time.sleep(90 * (i + 1)); continue
            if "error" in r: raise RuntimeError(json.dumps(r["error"], ensure_ascii=False)[:500])
            time.sleep(a.sleep); return r
        raise RuntimeError("rate limited too long")

    log_path = os.path.join(HERE, "applied_changes.csv")
    new_log = not os.path.exists(log_path)
    log = open(log_path, "a", encoding="utf-8", newline="")
    w = csv.writer(log)
    if new_log: w.writerow(["lexeme_id", "lemma", "target", "change", "value", "source", "revision_id", "verified", "status"])

    for lid, p in plan.items():
        rows, lemma = p["rows"], p["lemma"]
        ent = fetch(lid)
        print(f"== {lid} {lemma}", flush=True)
        gloss_row = next((r for r in rows if r["property"] == "sense_gloss_en"), None)
        sense_id = None
        for sn in ent.get("senses", []):
            if gloss_row and sn.get("glosses", {}).get("en", {}).get("value") == gloss_row["value"]: sense_id = sn["id"]
        # 1. lexeme statements + new sense in one edit
        data, pending = {}, []
        claims = []
        for prop, dt, val, quals, refs, r in lexeme_claims(rows):
            if (lid, prop) in HELD:
                w.writerow([lid, lemma, lid, prop, val, r["source"], "", "", "held"]); continue
            if has_claim(ent, prop, val):
                w.writerow([lid, lemma, lid, prop, val, r["source"], "", "yes", "already_present"]); continue
            claims.append(claim(prop, dt, val, quals, refs)); pending.append((prop, val, r))
        if claims: data["claims"] = claims
        if gloss_row and not sense_id:
            data["senses"] = [{"add": "", "glosses": {"en": {"language": "en", "value": gloss_row["value"]}}}]
        if data:
            print("  edit lexeme:", json.dumps(data, ensure_ascii=False)[:600], flush=True)
            if a.apply:
                res = post({"action": "wbeditentity", "id": lid, "data": json.dumps(data, ensure_ascii=False)})
                rev = res["entity"]["lastrevid"]
                ent = fetch(lid)
                for prop, val, r in pending:
                    w.writerow([lid, lemma, lid, prop, val, r["source"], rev, "yes" if has_claim(ent, prop, val) else "NO", "applied"])
                if gloss_row and not sense_id:
                    sense_id = next((sn["id"] for sn in ent.get("senses", []) if sn.get("glosses", {}).get("en", {}).get("value") == gloss_row["value"]), None)
                    w.writerow([lid, lemma, sense_id, "sense + gloss (en)", gloss_row["value"], gloss_row["source"], rev, "yes" if sense_id else "NO", "applied"])
                log.flush()
        elif gloss_row:
            w.writerow([lid, lemma, sense_id, "sense + gloss (en)", gloss_row["value"], gloss_row["source"], "", "yes", "already_present"])
        # 2. item for this sense (P5137) on the sense
        for r in (r for r in rows if r["property"] == "P5137"):
            val = qid(r["value"])
            if not a.apply: print("  sense claim P5137", val, flush=True); continue
            sent = next(sn for sn in ent["senses"] if sn["id"] == sense_id)
            if has_claim(sent, "P5137", val):
                w.writerow([lid, lemma, sense_id, "P5137", val, r["source"], "", "yes", "already_present"]); continue
            res = post({"action": "wbcreateclaim", "entity": sense_id, "property": "P5137", "snaktype": "value",
                        "value": json.dumps(item(val))})
            rev = res["pageinfo"]["lastrevid"]; ent = fetch(lid)
            ok = has_claim(next(sn for sn in ent["senses"] if sn["id"] == sense_id), "P5137", val)
            w.writerow([lid, lemma, sense_id, "P5137", val, r["source"], rev, "yes" if ok else "NO", "applied"]); log.flush()
        # 3. usage example (P5831) on the lexeme, qualifier P6072 = the sense, referenced to Urdu Lughat
        for r in (r for r in rows if r["property"] == "P5831"):
            ul_id = next((x["value"] for x in rows if x["property"] == "P11350"), None)
            c = claim("P5831", "mono", r["value"], quals=[snak("P6072", "sense", sense_id or "L0-S0")],
                      refs=[snak("P248", "item", UL)] + ([snak("P11350", "string", ul_id)] if ul_id else []))
            if not a.apply: print("  usage example:", json.dumps(c, ensure_ascii=False)[:400], flush=True); continue
            if has_claim(ent, "P5831", r["value"]):
                w.writerow([lid, lemma, lid, "P5831", r["value"], r["source"], "", "yes", "already_present"]); continue
            res = post({"action": "wbeditentity", "id": lid, "data": json.dumps({"claims": [c]}, ensure_ascii=False)})
            rev = res["entity"]["lastrevid"]; ent = fetch(lid)
            w.writerow([lid, lemma, lid, "P5831 (qualifier P6072 " + str(sense_id) + ")", r["value"], r["source"], rev,
                        "yes" if has_claim(ent, "P5831", r["value"]) else "NO", "applied"]); log.flush()
    log.close()
    print("done", flush=True)

if __name__ == "__main__":
    main()
