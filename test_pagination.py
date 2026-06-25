# -*- coding: utf-8 -*-
"""
Verify: pagination is fast AND stable under concurrent writes.
"""
import json, os, time, urllib.request, urllib.parse
from dotenv import load_dotenv
load_dotenv()

API = "http://127.0.0.1:8000"
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_KEY"]

def api_get(path, params=None):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k:v for k,v in params.items() if v is not None})
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())

def sb_post(data):
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/products",
        data=json.dumps(data).encode(),
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json","Prefer":"return=representation"},
        method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def sb_delete(pid):
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/products?id=eq.{pid}",
        headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"},
        method="DELETE")
    urllib.request.urlopen(req)

print("")
print("=" * 60)
print("TEST 1: PAGINATION SPEED")
print("=" * 60)

cursor_ca, cursor_id = None, None
page = 0
checkpoints = {1,5,10,50,100,200,500}
times = []

while page < 500:
    page += 1
    p = {"limit": 20}
    if cursor_ca: p["cursor_created_at"] = cursor_ca; p["cursor_id"] = cursor_id
    t0 = time.perf_counter()
    d = api_get("/api/products", p)
    ms = (time.perf_counter()-t0)*1000
    if page in checkpoints:
        print(f"  Page {page:>5}: {ms:>7.1f} ms  ({len(d['data'])} items)")
        times.append(ms)
    if not d["has_next"]: break
    cursor_ca = d["next_cursor"]["created_at"]
    cursor_id = d["next_cursor"]["id"]

avg = sum(times)/len(times)
mx = max(times)
print(f"\n  Avg: {avg:.1f}ms | Max: {mx:.1f}ms")
if mx < 500:
    print("  [PASS] All checkpoint pages under 500ms")
else:
    print("  [WARN] Some pages exceeded 500ms")

print("")
print("=" * 60)
print("TEST 2: STABILITY UNDER CONCURRENT WRITES")
print("=" * 60)
print("  Simulating: browse 3 pages, insert 50 new products, continue browsing")

# Step 1: Browse pages 1-3
cursor_ca, cursor_id = None, None
seen = []
for pg in range(1,4):
    p = {"limit": 20}
    if cursor_ca: p["cursor_created_at"] = cursor_ca; p["cursor_id"] = cursor_id
    d = api_get("/api/products", p)
    ids = [x["id"] for x in d["data"]]
    seen.extend(ids)
    if d["has_next"]:
        cursor_ca = d["next_cursor"]["created_at"]
        cursor_id = d["next_cursor"]["id"]
    print(f"  Page {pg}: {len(ids)} products")

print(f"  Cursor saved at: created_at={cursor_ca}")

# Step 2: Insert 50 new products (created_at = now, so they are the NEWEST)
print("\n  Inserting 50 new products with created_at = NOW ...")
new = [{"name":f"STABILITY_TEST_{i}","category":"Electronics","price":1.00} for i in range(50)]
inserted = sb_post(new)
inserted_ids = {x["id"] for x in inserted}
print(f"  Inserted {len(inserted)} products")

# Step 3: Continue from saved cursor (pages 4-6)
print("\n  Continuing from saved cursor...")
continued = []
for pg in range(4,7):
    p = {"limit": 20}
    if cursor_ca: p["cursor_created_at"] = cursor_ca; p["cursor_id"] = cursor_id
    d = api_get("/api/products", p)
    ids = [x["id"] for x in d["data"]]
    continued.extend(ids)
    if d["has_next"]:
        cursor_ca = d["next_cursor"]["created_at"]
        cursor_id = d["next_cursor"]["id"]
    print(f"  Page {pg}: {len(ids)} products")

# Step 4: Verify
all_ids = seen + continued
unique = set(all_ids)
dups = len(all_ids) - len(unique)
leaked = inserted_ids & unique

print(f"\n  --- RESULTS ---")
print(f"  Total products seen (6 pages): {len(all_ids)}")
print(f"  Unique products:               {len(unique)}")
print(f"  Duplicates:                     {dups}")
print(f"  New inserts leaked in:          {len(leaked)}")

if dups == 0 and len(leaked) == 0:
    print("\n  [PASS] Zero duplicates. Zero leakage. Cursor pagination is stable!")
else:
    if dups > 0: print(f"\n  [FAIL] {dups} duplicate(s) found!")
    if leaked:   print(f"\n  [FAIL] {len(leaked)} new insert(s) leaked into old pages!")

# Cleanup
print("\n  Cleaning up test data...")
for pid in inserted_ids:
    sb_delete(pid)
print(f"  Deleted {len(inserted_ids)} test products.")
print("\nAll tests complete.")
