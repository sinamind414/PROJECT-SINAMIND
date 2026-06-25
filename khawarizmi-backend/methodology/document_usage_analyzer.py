import re


def analyze_document_usage(answer: str, documents: list[dict] | None = None) -> dict:
    if not documents:
        return {
            "documents_used": 0,
            "total_documents": 0,
            "usage_quality": "no_docs",
            "references": [],
        }

    references = []
    answer_lower = answer.lower()

    for doc in documents:
        doc_id = doc.get("id", "")
        key_element = doc.get("key_element", "")
        title = doc.get("title", "")

        if doc_id and doc_id in answer:
            references.append({"doc_id": doc_id, "type": "direct"})
        elif key_element and key_element.lower() in answer_lower:
            references.append({"doc_id": doc_id, "type": "element"})
        elif title:
            title_words = [w for w in title.split() if len(w) > 3]
            if any(w.lower() in answer_lower for w in title_words):
                references.append({"doc_id": doc_id, "type": "title_match"})

    refs_count = len(references)

    if refs_count >= 3:
        quality = "excellent"
    elif refs_count >= 2:
        quality = "good"
    elif refs_count >= 1:
        quality = "weak"
    else:
        quality = "none"

    return {
        "documents_used": refs_count,
        "total_documents": len(documents),
        "usage_quality": quality,
        "references": references,
    }


def detect_document_markers(answer: str) -> dict:
    patterns = {
        "الوثيقة": r"الوثيق[هة]|document",
        "الشكل": r"الشكل|figure|sch[ée]ma",
        "الجدول": r"الجدول|tableau|table",
        "المنحنى": r"المنحنى|courbe|graphique",
        "الرسوم": r"الرسوم|diagramme",
    }

    found = {}
    for marker, pattern in patterns.items():
        if re.search(pattern, answer, re.IGNORECASE):
            found[marker] = True

    return {
        "markers_found": list(found.keys()),
        "markers_count": len(found),
        "has_any": len(found) > 0,
    }
