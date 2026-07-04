"""Parse 25 SVT course HTML files into structured JSON."""
import json, re, os, sys
from pathlib import Path
from bs4 import BeautifulSoup, Tag

SRC = Path(__file__).resolve().parent.parent / "svt_course"
OUT = Path(__file__).resolve().parent / "experimental_lessons.json"

# Files to skip (duplicate)
SKIP = {"phase3_chapitres_5_6 (1).html"}

def extract_title(soup: BeautifulSoup) -> str:
    t = soup.select_one("title")
    return t.get_text(strip=True) if t else ""

def extract_breadcrumb(soup: BeautifulSoup) -> str:
    el = soup.select_one(".lesson-breadcrumb")
    return el.get_text(" ", strip=True) if el else ""

def extract_objectives(soup: BeautifulSoup) -> list:
    els = soup.select(".lesson-objectives > div")
    return [e.get_text(" ", strip=True) for e in els]

def extract_phases(soup: BeautifulSoup) -> list:
    phases = []
    cards = soup.select("section.card")
    for i, card in enumerate(cards):
        step_el = card.select_one(".step-num")
        step_num = step_el.get_text(strip=True) if step_el else str(i + 1)

        blocks = []

        # --- problem-box (step 1) ---
        pb = card.select_one(".problem-box")
        if pb:
            title_el = pb.select_one(".problem-title")
            p_title = title_el.get_text(" ", strip=True) if title_el else ""
            p_paras = [p.get_text(" ", strip=True) for p in pb.find_all("p", recursive=False)]
            blocks.append({"type": "problem", "title": p_title, "texts": p_paras})
            # also grab any trailing <p> after problem-box
            for sib in pb.find_next_siblings("p"):
                blocks.append({"type": "text", "texts": [sib.get_text(" ", strip=True)]})

        # --- tab-content documents ---
        for tab in card.select(".tab-content"):
            is_active = "active" in tab.get("class", [])
            doc_viewer = tab.select_one(".doc-viewer")
            if doc_viewer:
                analysis = doc_viewer.select_one(".doc-analysis")
                items = []
                if analysis:
                    for li in analysis.select("li"):
                        items.append(li.get_text(" ", strip=True))
                blocks.append({
                    "type": "document",
                    "active": is_active,
                    "texts": items or [analysis.get_text(" ", strip=True)] if analysis else []
                })

        # --- sim-box (simulation) ---
        sim = card.select_one(".sim-box")
        if sim:
            sim_texts = [p.get_text(" ", strip=True) for p in sim.find_all(["p", "div"]) if not p.select_one("button")]
            sim_buttons = [b.get_text(" ", strip=True) for b in sim.find_all("button")]
            blocks.append({"type": "simulation", "texts": sim_texts, "buttons": sim_buttons})

        # --- scientific text ---
        st = card.select_one(".scientific-text")
        if st:
            parts = st.select(".text-part")
            texts = [p.get_text(" ", strip=True) for part in parts for p in part.find_all("p")]
            blocks.append({"type": "scientific_text", "texts": texts})

        # --- bac-tip ---
        bac = card.select_one(".bac-tip")
        if bac:
            header = bac.select_one(".bac-tip-header")
            items = [li.get_text(" ", strip=True) for li in bac.select("li")]
            blocks.append({
                "type": "bac_tip",
                "title": header.get_text(" ", strip=True) if header else "",
                "texts": items
            })

        # --- quiz / question-item ---
        for qi in card.select(".question-item"):
            q_text = qi.find("h4")
            opts = qi.find_all("button", class_="option-btn")
            options = []
            correct_idx = -1
            for idx, opt in enumerate(opts):
                onclick = opt.get("onclick", "")
                options.append(opt.get_text(" ", strip=True))
                if "true" in onclick:
                    correct_idx = idx
            blocks.append({
                "type": "quiz",
                "question": q_text.get_text(" ", strip=True) if q_text else "",
                "options": options,
                "correct": correct_idx
            })

        # --- standalone <p> tags not already captured ---
        for p in card.find_all("p", recursive=True):
            if not p.find_parent(class_=["problem-box", "doc-analysis", "sim-box", "scientific-text", "bac-tip", "question-item", "tab-content"]):
                txt = p.get_text(" ", strip=True)
                if txt and len(txt) > 20:
                    blocks.append({"type": "text", "texts": [txt]})

        if blocks:
            phases.append({"step": step_num, "blocks": blocks})

    return phases

def extract_title_from_header(soup: BeautifulSoup) -> str:
    h1 = soup.select_one(".lesson-header h1")
    return h1.get_text(" ", strip=True) if h1 else ""

def parse_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "lxml")
    slug = path.stem if path.stem != "lecon_transcription" else "lecon_transcription"
    # also handle the (1) duplicate
    if slug.endswith(" (1)"):
        slug = slug.replace(" (1)", "")
    return {
        "slug": slug,
        "title": extract_title_from_header(soup) or extract_title(soup),
        "breadcrumb": extract_breadcrumb(soup),
        "objectives": extract_objectives(soup),
        "phases": extract_phases(soup),
        "source": path.name
    }

def main():
    files = sorted(SRC.glob("*.html"))
    lessons = []
    for f in files:
        if f.name in SKIP:
            continue
        try:
            lesson = parse_file(f)
            lessons.append(lesson)
        except Exception as e:
            print(f"ERROR parsing {f.name}: {e}", file=sys.stderr)

    OUT.write_text(json.dumps(lessons, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(lessons)} lessons -> {OUT}")

if __name__ == "__main__":
    main()
