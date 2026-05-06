import pandas as pd
import requests as r
from bs4 import BeautifulSoup as bs
from bs4 import XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
from urllib.parse import urlparse
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

ORIGINAL_PATH   = r"D:\codes\project\AI\improved version of phishguard\data\processed\final_data_frame.csv"
SAVED_ORIG_PATH = r"D:\codes\project\AI\improved version of phishguard\output\features\test\hyper_textual_features.csv"
SAVED_FIXED_PATH= r"D:\codes\project\AI\improved version of phishguard\output\features\test\hyper_textual_features1.csv"

SAMPLES_PER_CHUNK = 5   # how many URLs to live-fetch per chunk
TIMEOUT           = 5


def live_fetch(url):
    try:
        resp = r.get(url, timeout=TIMEOUT)
        soup = bs(resp.text, "html.parser")

        link  = soup.find_all("a")
        total = len(link)
        empty = sum(1 for i in link if not i.get("href") or i.get("href") in ["#", "", "javascript:void(0);"])
        ext   = sum(1 for i in link if i.get("href") and urlparse(i.get("href")).netloc and urlparse(i.get("href")).netloc != urlparse(url).netloc)
        intern= total - empty - ext
        ratio = ext / total if total > 0 else 0

        forms = soup.find_all("form")
        sf    = sum(1 for f in forms if f.get("action") and urlparse(f.get("action")).netloc and urlparse(f.get("action")).netloc != urlparse(url).netloc)

        title = soup.title.string.lower() if soup.title and soup.title.string else ""
        domain= urlparse(url).netloc
        text  = soup.get_text().lower()

        return {
            "total_links": total, "empty_links": empty, "external_links": ext,
            "internal_links": intern, "ratio_external_total": ratio,
            "total_forms": len(forms), "suspicious_forms": sf,
            "title_match": int(domain in title),
            "has_copyright": int("©" in text or "copyright" in text),
            "iframes": len(soup.find_all("iframe")),
            "password_fields": len(soup.find_all("input", {"type": "password"})),
            "has_favicon": int(bool(soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon"))),
            "has_meta": int(bool(soup.find("meta", {"name": "description"}))),
        }
    except:
        return None


def row_matches(live_data, saved_row):
    if live_data is None:
        return None  # site is down, can't judge
    saved = saved_row.to_dict()
    matches = {}
    for k, v in live_data.items():
        saved_val = saved.get(k)
        matches[k] = (round(float(v), 4) == round(float(saved_val), 4)) if saved_val is not None else False
    all_match = all(matches.values())
    return all_match, matches


print("Loading files...")
original     = pd.read_csv(ORIGINAL_PATH)
saved_orig   = pd.read_csv(SAVED_ORIG_PATH)
saved_fixed  = pd.read_csv(SAVED_FIXED_PATH)

n        = len(original)
n_chunks = 10
chunk_sz = n // n_chunks

print(f"\nOriginal rows  : {len(original)}")
print(f"Saved (orig)   : {len(saved_orig)}")
print(f"Saved (fixed)  : {len(saved_fixed)}")
print(f"Chunk size     : {chunk_sz}\n")
print("=" * 70)


for chunk_idx in range(n_chunks):
    start = chunk_idx * chunk_sz
    end   = start + chunk_sz if chunk_idx < n_chunks - 1 else n

    # pick evenly spaced sample indices within this chunk
    step    = max(1, (end - start) // SAMPLES_PER_CHUNK)
    indices = [start + i * step for i in range(SAMPLES_PER_CHUNK) if start + i * step < end]

    orig_ok  = 0
    fixed_ok = 0
    failed   = 0

    rows_detail = []

    for idx in indices:
        url = original["url"].iloc[idx]
        live = live_fetch(url)

        orig_row_exists  = idx < len(saved_orig)
        fixed_row_exists = idx < len(saved_fixed)

        orig_result  = row_matches(live, saved_orig.iloc[idx])  if orig_row_exists  else (False, {})
        fixed_result = row_matches(live, saved_fixed.iloc[idx]) if fixed_row_exists else (False, {})

        if live is None:
            failed += 1
            status = "DOWN"
        else:
            if orig_result  and orig_result[0]:  orig_ok  += 1
            if fixed_result and fixed_result[0]: fixed_ok += 1
            status = "OK"

        rows_detail.append((idx, url, status, orig_result, fixed_result))

    # chunk summary line
    orig_pct  = f"{orig_ok}/{len(indices) - failed}"
    fixed_pct = f"{fixed_ok}/{len(indices) - failed}"
    flag = "  ← MISMATCH STARTS HERE?" if (orig_ok < len(indices) - failed or fixed_ok < len(indices) - failed) else ""

    print(f"\nChunk {chunk_idx+1:>2}  rows {start:>7}–{end-1:<7}  |  orig matched: {orig_pct}  |  fixed matched: {fixed_pct}{flag}")
    print("-" * 70)

    for idx, url, status, orig_result, fixed_result in rows_detail:
        short_url = url[:55] + "..." if len(url) > 55 else url
        if status == "DOWN":
            print(f"  row {idx:>7}  {short_url}  → SITE DOWN (skipped)")
            continue

        orig_match  = orig_result[0]  if orig_result  else "N/A"
        fixed_match = fixed_result[0] if fixed_result else "N/A"

        print(f"  row {idx:>7}  {short_url}")
        print(f"           orig={orig_match}  fixed={fixed_match}")

        # if there is a mismatch, show which keys differ
        if orig_result and not orig_result[0]:
            bad_keys = [k for k, v in orig_result[1].items() if not v]
            print(f"           orig mismatch keys: {bad_keys}")
        if fixed_result and not fixed_result[0]:
            bad_keys = [k for k, v in fixed_result[1].items() if not v]
            print(f"           fixed mismatch keys: {bad_keys}")

print("\n" + "=" * 70)
print("Done. Look for the first chunk where 'orig matched' drops — that is")
print("the chunk containing the duplicate row offset.")