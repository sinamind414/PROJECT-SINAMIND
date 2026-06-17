import httpx, json

r = httpx.get("http://localhost:8000/api/cours/Rappel%20des%20acquis", timeout=15)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    json.dump(d, open("test_rappel.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"chunks: {d['total_chunks']}")
else:
    print(r.text[:300])
