import httpx, json, asyncio

async def test():
    chapters = [
        "Siege+de+la+synthese+des+proteines",
        "Transcription+de+l+information+genetique+au+niveau+de+l+ADN",
        "La+traduction",
        "Les+etapes+de+la+traduction",
        "Le+potentiel+d+action",
        "Le+soi+et+le+non-soi",
        "Rappel+des+acquis",
        "Notion+d+enzyme+et+son+importance",
    ]
    results = {}
    async with httpx.AsyncClient() as client:
        for ch in chapters:
            try:
                r = await client.get(f"http://localhost:8000/api/cours/{ch}", timeout=30)
                data = r.json()
                content_len = len(data["contenu"])
                chapitre = data["chapitre_rag"]
                results[ch] = {
                    "status": r.status_code,
                    "chapitre_rag": chapitre,
                    "content_len": content_len,
                    "total_chunks": data["total_chunks"],
                    "content_preview": data["contenu"][:300],
                }
            except Exception as e:
                results[ch] = {"status": "error", "error": str(e)}

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Results written to test_results.json")
    for ch, info in results.items():
        status = info["status"]
        if status == 200:
            print(f"  OK {ch:55s} -> {info['content_len']:5d}c")
        else:
            print(f"  ER {ch:55s} -> {status}")

asyncio.run(test())
