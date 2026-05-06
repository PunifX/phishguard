import pandas as pd
import dns.resolver
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

ORIGINAL_PATH = r"D:\codes\project\AI\improved version of phishguard\data\processed\final_data_frame.csv"
DNS_PATH      = r"D:\codes\project\AI\improved version of phishguard\output\features\dns_features1.csv"

SAMPLES_PER_CHUNK = 5
N_CHUNKS          = 10


def live_dns(url):
    try:
        domain = urlparse(url).netloc
        if not domain:
            return None

        try:
            a = dns.resolver.resolve(domain, "A")
            has_a, ttl = 1, int(a.rrset.ttl)
        except:
            has_a, ttl = 0, 0

        try:
            dns.resolver.resolve(domain, "MX")
            has_mx = 1
        except:
            has_mx = 0

        try:
            txt = dns.resolver.resolve(domain, "TXT")
            has_spf = 1 if any("spf" in str(r).lower() for r in txt) else 0
        except:
            has_spf = 0

        return {"has_a": has_a, "ttl": ttl, "has_mx": has_mx, "has_spf": has_spf}
    except:
        return None


print("Loading files...")
original = pd.read_csv(ORIGINAL_PATH)
dns_saved = pd.read_csv(DNS_PATH)

n = len(original)
chunk_sz = n // N_CHUNKS

print(f"Original rows : {len(original)}")
print(f"DNS saved rows: {len(dns_saved)}")

if len(original) != len(dns_saved):
    print(f"\n ROW COUNT MISMATCH — {len(original) - len(dns_saved):+d} rows — you need to re-run DNS extraction")
else:
    print("\n Row counts match")

print("=" * 65)

total_checked = 0
total_a_match = 0
total_mx_match = 0
total_spf_match = 0

for chunk_idx in range(N_CHUNKS):
    start = chunk_idx * chunk_sz
    end   = start + chunk_sz if chunk_idx < N_CHUNKS - 1 else n

    step    = max(1, (end - start) // SAMPLES_PER_CHUNK)
    indices = [start + i * step for i in range(SAMPLES_PER_CHUNK) if start + i * step < end]

    a_ok = mx_ok = spf_ok = checked = skipped = 0
    details = []

    for idx in indices:
        if idx >= len(dns_saved):
            details.append((idx, "OUT OF BOUNDS", None, None))
            skipped += 1
            continue

        url   = original["url"].iloc[idx]
        live  = live_dns(url)
        saved = dns_saved.iloc[idx].to_dict()

        if live is None:
            details.append((idx, url, "TIMEOUT", saved))
            skipped += 1
            continue

        checked += 1
        total_checked += 1

        a_m   = live["has_a"]   == int(saved["has_a"])
        mx_m  = live["has_mx"]  == int(saved["has_mx"])
        spf_m = live["has_spf"] == int(saved["has_spf"])

        if a_m:   a_ok   += 1; total_a_match   += 1
        if mx_m:  mx_ok  += 1; total_mx_match  += 1
        if spf_m: spf_ok += 1; total_spf_match += 1

        details.append((idx, url, live, saved))

    flag = ""
    if checked > 0:
        worst = min(a_ok, mx_ok, spf_ok)
        if worst < checked:
            flag = "  ← issues"

    print(f"\nChunk {chunk_idx+1:>2}  rows {start:>7}–{end-1:<7}  "
          f"has_a: {a_ok}/{checked}  has_mx: {mx_ok}/{checked}  has_spf: {spf_ok}/{checked}"
          f"  (skipped: {skipped}){flag}")
    print("-" * 65)

    for idx, url, live, saved in details:
        short = url[:52] + "..." if len(url) > 52 else url

        if live == "TIMEOUT":
            print(f"  row {idx:>7}  {short}  → TIMEOUT")
            continue
        if live == "OUT OF BOUNDS":
            print(f"  row {idx:>7}  OUT OF BOUNDS (saved file is shorter)")
            continue

        a_m   = live["has_a"]   == int(saved["has_a"])
        mx_m  = live["has_mx"]  == int(saved["has_mx"])
        spf_m = live["has_spf"] == int(saved["has_spf"])
        all_m = a_m and mx_m and spf_m

        status = "OK" if all_m else "DIFF"
        print(f"  row {idx:>7}  {short}  [{status}]")
        if not all_m:
            if not a_m:
                print(f"             has_a   live={live['has_a']}  saved={int(saved['has_a'])}")
            if not mx_m:
                print(f"             has_mx  live={live['has_mx']}  saved={int(saved['has_mx'])}")
            if not spf_m:
                print(f"             has_spf live={live['has_spf']}  saved={int(saved['has_spf'])}")

print("\n" + "=" * 65)
print("SUMMARY")
print(f"  Total live-checked : {total_checked}")
if total_checked > 0:
    print(f"  has_a  match rate  : {total_a_match}/{total_checked}  ({100*total_a_match/total_checked:.0f}%)")
    print(f"  has_mx match rate  : {total_mx_match}/{total_checked}  ({100*total_mx_match/total_checked:.0f}%)")
    print(f"  has_spf match rate : {total_spf_match}/{total_checked}  ({100*total_spf_match/total_checked:.0f}%)")
    avg = (total_a_match + total_mx_match + total_spf_match) / (3 * total_checked) * 100
    print(f"\n  Overall accuracy   : {avg:.0f}%")

    print()
    if len(original) != len(dns_saved):
        print("VERDICT: RE-RUN — row count mismatch")
    elif avg >= 85:
        print("VERDICT: DNS data looks good, no need to re-run")
    elif avg >= 70:
        print("VERDICT: Marginal — DNS records may have changed since extraction (normal)")
        print("         Only re-run if you need high confidence on DNS features")
    else:
        print("VERDICT: Many mismatches — consider re-running DNS extraction")