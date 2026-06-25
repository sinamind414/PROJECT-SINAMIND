#!/usr/bin/env python3
"""
Pipeline KHELIFA 1 & 2 complet — OCR Tesseract + extraction de questions.
Étape 1 : OCR via ocr_pipeline_production.py (Tesseract, parallélisé)
Étape 2 : Extraction des questions SVT depuis le texte OCR
Étape 3 : Consolidation et rapports

Usage :
  python scripts/run_khelifa_complete.py
  python scripts/run_khelifa_complete.py --resume
  python scripts/run_khelifa_complete.py --serie 1 --start-volume 6
  python scripts/run_khelifa_complete.py --no-ocr (ré-extraction des questions seulement)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("khelifa_complete")

BASE_DIR = Path(__file__).resolve().parent.parent
PROD_SCRIPT = BASE_DIR / "scripts" / "ocr_pipeline_production.py"
OCR_OUT_DIR = BASE_DIR / "data" / "ocr_production"
QUESTIONS_OUT_DIR = BASE_DIR / "data" / "ocr_output"
KHELIFA_BASE = BASE_DIR / "data" / "ANNALES_SVT_BAC_ALGERIE"

VOLUMES_CONFIG = {
    1: {
        "dir": KHELIFA_BASE / "KHELIFA_1" / "VOLUMES_KHELIFA1",
        "pdf_pattern": "KHELIFA1_VOLUME_{:02d}.pdf",
        "stem_pattern": "khelifa1_volume{:02d}",
    },
    2: {
        "dir": KHELIFA_BASE / "KHELIFA_2" / "VOLUMES_KHELIFA2",
        "pdf_pattern": "KHELIFA2_VOLUME_{:02d}.pdf",
        "stem_pattern": "khelifa2_volume{:02d}",
    },
}

# ---------------------------------------------------------------------------
# Expressions régulières et dictionnaire de concepts
# ---------------------------------------------------------------------------

Q_PATTERN = re.compile(
    r"(التمرين|السؤال|سؤال|تمرين|question|exercice|exo?\s*\d+|"
    r"أذكر|بين|حدد|صف|فسر|استخرج|قارن|استنتج|وضح|علل|ارسم|"
    r"بماذا|كيف|لماذا|ما هو|ما هي|ماذا|انطلاقا|الجزء|الوثيقة|التعليمة)",
    re.IGNORECASE,
)

MC_MAP: dict[str, str] = {
    "استنساخ": "mc_prot_01", "نسخ": "mc_prot_01", "transcription": "mc_prot_01",
    "ADN": "mc_prot_01", "ARNm": "mc_prot_04", "الرنا الرسول": "mc_prot_04",
    "ترجمة": "mc_prot_02", "traduction": "mc_prot_02",
    "ARNt": "mc_prot_05", "الرنا الناقل": "mc_prot_05", "anticodon": "mc_prot_05",
    "ريبوزوم": "mc_prot_06", "ribosome": "mc_prot_06",
    "كودون": "mc_prot_03", "رامزة": "mc_prot_03", "شفرة": "mc_prot_03",
    "بدء": "mc_prot_07", "initiation": "mc_prot_07",
    "استطالة": "mc_prot_08", "إطالة": "mc_prot_08", "إنهاء": "mc_prot_08",
    "بنية أولية": "mc_struc_01", "بنية اولية": "mc_struc_01",
    "بنية ثانوية": "mc_struc_02", "بنية ثالثية": "mc_struc_03",
    "بنية رباعية": "mc_struc_04", "بنية فراغية": "mc_struc_05",
    "إنزيم": "mc_enz_01", "enzyme": "mc_enz_01", "موقع فعال": "mc_enz_01",
    "نوعية إنزيمية": "mc_enz_02", "تثبيط": "mc_enz_05", "inhibition": "mc_enz_05",
    "لمفاويات B": "mc_imm_01", "LB": "mc_imm_01",
    "لمفاويات T": "mc_imm_02", "LT4": "mc_imm_02", "LT8": "mc_imm_02",
    "مستضد": "mc_imm_03", "antigene": "mc_imm_03",
    "جسم مضاد": "mc_imm_03", "anticorps": "mc_imm_03",
    "مناعة خلطية": "mc_imm_04", "humorale": "mc_imm_04",
    "مناعة خلوية": "mc_imm_05", "cellulaire": "mc_imm_05", "CTL": "mc_imm_05",
    "ذاكرة مناعية": "mc_imm_06", "memoire": "mc_imm_06", "vaccin": "mc_imm_06",
    "كلوروبلاست": "mc_photo_01", "chloroplaste": "mc_photo_01",
    "طور ضوئي": "mc_photo_02", "دورة كالفن": "mc_photo_03",
    "ميتوكندري": "mc_resp_01", "mitochondrie": "mc_resp_01",
    "تحلل سكري": "mc_resp_02", "glycolyse": "mc_resp_02",
    "كريس": "mc_resp_03", "Krebs": "mc_resp_03",
    "سلسلة تنفسية": "mc_resp_04", "تخمر": "mc_resp_05", "fermentation": "mc_resp_05",
    "بنية الأرض": "mc_tec_01", "sismique": "mc_tec_01",
    "صفائح": "mc_tec_02", "plaques": "mc_tec_02",
    "تباعد": "mc_tec_03", "تقارب": "mc_tec_03",
    "غوص": "mc_tec_04", "subduction": "mc_tec_04",
    "زلزال": "mc_tec_05", "بركان": "mc_tec_05", "volcan": "mc_tec_05",
}
# ---------------------------------------------------------------------------
# Utilitaires texte
# ---------------------------------------------------------------------------


def clean_arabic(text: str) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    t = re.sub(r"[|¦•●]", "", t)
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    t = t.replace("ة", "ه").replace("ى", "ا")
    t = t.replace("٠", "0").replace("١", "1").replace("٢", "2")
    t = t.replace("٣", "3").replace("٤", "4").replace("٥", "5")
    t = t.replace("٦", "6").replace("٧", "7").replace("٨", "8").replace("٩", "9")
    return t


def tag_concept(text: str):
    tl = text.lower()
    found = set()
    for kw, cid in MC_MAP.items():
        if kw.lower() in tl:
            found.add(cid)
    if not found:
        return "mc_xxx_xx", [], True
    spec = {
        "mc_prot_07": 3, "mc_prot_08": 3, "mc_prot_05": 3, "mc_prot_06": 3,
        "mc_enz_01": 3, "mc_enz_02": 3, "mc_imm_04": 3, "mc_imm_05": 3, "mc_imm_06": 3,
        "mc_struc_01": 2, "mc_struc_02": 2, "mc_struc_03": 2, "mc_struc_04": 2,
        "mc_prot_01": 2, "mc_prot_02": 2, "mc_prot_03": 2, "mc_prot_04": 2,
        "mc_imm_01": 2, "mc_imm_02": 2, "mc_imm_03": 2,
    }
    sf = sorted(found, key=lambda x: spec.get(x, 0), reverse=True)
    return sf[0], sf[1:3], False


# ---------------------------------------------------------------------------
# Extraction des questions depuis un fichier .ocr.txt
# ---------------------------------------------------------------------------

def extract_questions_from_ocr_text(text: str, source_label: str, serie: int, vol_num: int, page_no: int) -> list[dict]:
    questions = []
    lines = text.split("\n")
    current_q: list[str] = []
    in_question = False

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            if in_question and current_q:
                raw = " ".join(current_q)
                cleaned = clean_arabic(raw)
                if len(cleaned) > 10:
                    main, sec, av = tag_concept(cleaned)
                    qid = f"q_khelifa{serie}_v{vol_num:02d}_p{page_no:02d}_{len(questions) + 1:02d}"
                    questions.append({
                        "id": qid,
                        "texte_brut": raw[:500],
                        "texte_corrige": cleaned[:500],
                        "micro_concept_id": main,
                        "secondary_concepts": sec,
                        "a_verifier": av,
                        "confidence": 0.5,
                        "source": source_label,
                        "type": "question",
                        "difficulte": "moyenne",
                        "bac_frequent": not av,
                        "notes": "OCR Tesseract + extraction regex",
                        "source_page": page_no,
                    })
                current_q = []
                in_question = False
            continue

        if Q_PATTERN.search(line_stripped):
            if in_question and current_q:
                raw = " ".join(current_q)
                cleaned = clean_arabic(raw)
                if len(cleaned) > 10:
                    main, sec, av = tag_concept(cleaned)
                    qid = f"q_khelifa{serie}_v{vol_num:02d}_p{page_no:02d}_{len(questions) + 1:02d}"
                    questions.append({
                        "id": qid,
                        "texte_brut": raw[:500],
                        "texte_corrige": cleaned[:500],
                        "micro_concept_id": main,
                        "secondary_concepts": sec,
                        "a_verifier": av,
                        "confidence": 0.5,
                        "source": source_label,
                        "type": "question",
                        "difficulte": "moyenne",
                        "bac_frequent": not av,
                        "notes": "OCR Tesseract + extraction regex",
                        "source_page": page_no,
                    })
            current_q = [line_stripped]
            in_question = True
        elif in_question and len(current_q) < 15:
            current_q.append(line_stripped)

    if in_question and current_q:
        raw = " ".join(current_q)
        cleaned = clean_arabic(raw)
        if len(cleaned) > 10:
            main, sec, av = tag_concept(cleaned)
            qid = f"q_khelifa{serie}_v{vol_num:02d}_p{page_no:02d}_{len(questions) + 1:02d}"
            questions.append({
                "id": qid,
                "texte_brut": raw[:500],
                "texte_corrige": cleaned[:500],
                "micro_concept_id": main,
                "secondary_concepts": sec,
                "a_verifier": av,
                "confidence": 0.5,
                "source": source_label,
                "type": "question",
                "difficulte": "moyenne",
                "bac_frequent": not av,
                "notes": "OCR Tesseract + extraction regex",
                "source_page": page_no,
            })

    return questions


def parse_ocr_pages(ocr_text: str) -> dict[int, str]:
    """Extrait le texte par page depuis le format assemble de ocr_pipeline_production."""
    pages: dict[int, str] = {}
    current_page = None
    current_lines: list[str] = []

    page_header = re.compile(r"^={70,}\nPAGE (\d+)\n={70,}", re.MULTILINE)

    # Split by page headers
    parts = re.split(r"={70,}\n(PAGE \d+)\n={70,}", ocr_text)
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        if part.startswith("PAGE ") and i + 1 < len(parts):
            page_no = int(part.split()[1])
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            pages[page_no] = content
            i += 2
        else:
            if part:
                pages[len(pages) + 1] = part
            i += 1

    return pages


def process_ocr_file(ocr_path: Path, serie: int, vol_num: int) -> tuple[list[dict], dict]:
    """Convertit un fichier .ocr.txt en questions structurées."""
    text = ocr_path.read_text(encoding="utf-8", errors="replace")
    pages = parse_ocr_pages(text)

    all_questions: list[dict] = []
    volume_pages: list[dict] = []

    for page_no in sorted(pages.keys()):
        page_text = pages[page_no]
        source_label = f"KHELIFA {serie} - Volume {vol_num} - Page {page_no}"
        qs = extract_questions_from_ocr_text(page_text, source_label, serie, vol_num, page_no)
        all_questions.extend(qs)
        volume_pages.append({
            "page": page_no,
            "chars": len(page_text),
            "questions": len(qs),
        })

    vol_data = {
        "source": f"KHELIFA {serie} - Volume {vol_num}",
        "fichier": ocr_path.name,
        "total_pages": len(pages),
        "processed_pages": len(pages),
        "pages": volume_pages,
    }

    return all_questions, vol_data
# ---------------------------------------------------------------------------
# Étape 1 : OCR (appelle ocr_pipeline_production.py)
# ---------------------------------------------------------------------------


def ocr_stem(pdf_path: Path) -> str:
    """Nom du fichier de sortie produit par ocr_pipeline_production (basé sur le nom du PDF)."""
    return pdf_path.stem


def run_ocr_volume(pdf_path: Path, out_dir: Path, workers: int, dpi: int, pdf_mode: str) -> bool:
    cmd = [
        sys.executable, str(PROD_SCRIPT),
        str(pdf_path),
        "--workers", str(workers),
        "--dpi", str(dpi),
        "--out-dir", str(out_dir),
        "--lang", "ara+fra",
        "--pdf-mode", pdf_mode,
        "--suffix", ".ocr.txt",
        "--timeout", "120",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stem = ocr_stem(pdf_path)
    if result.returncode != 0:
        log.error("ÉCHEC OCR %s : %s", stem, result.stderr[-500:])
        return False
    return True


def is_ocr_done(out_dir: Path, pdf_path: Path) -> bool:
    stem = ocr_stem(pdf_path)
    txt_file = out_dir / f"{stem}.ocr.txt"
    state_file = out_dir / f"{stem}.ocr.txt.bundle" / "run.state.json"
    return txt_file.exists() and state_file.exists()


# ---------------------------------------------------------------------------
# Étape 2 : Extraction des questions
# ---------------------------------------------------------------------------

def extract_volume_questions(serie: int, vol: int, pdf_path: Path, ocr_dir: Path, q_dir: Path) -> bool:
    stem_ocr = ocr_stem(pdf_path)
    stem_out = VOLUMES_CONFIG[serie]["stem_pattern"].format(vol)
    ocr_path = ocr_dir / f"{stem_ocr}.ocr.txt"

    if not ocr_path.exists():
        log.warning("Fichier OCR introuvable : %s", ocr_path)
        return False

    log.info("Extraction questions : %s", stem_out)
    questions, vol_data = process_ocr_file(ocr_path, serie, vol)

    q_dir.mkdir(parents=True, exist_ok=True)
    vol_path = q_dir / f"{stem_out}.json"
    q_path = q_dir / f"{stem_out}_questions.json"
    vol_path.write_text(json.dumps(vol_data, ensure_ascii=False, indent=2), encoding="utf-8")
    q_path.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")

    log.info("  -> %d questions extraites vers %s", len(questions), q_path.name)
    return True


# ---------------------------------------------------------------------------
# Étape 3 : Consolidation
# ---------------------------------------------------------------------------

def consolidate_questions(q_dir: Path) -> None:
    log.info("Consolidation des questions…")
    all_q: list[dict] = []
    for qfile in sorted(q_dir.glob("*_questions.json")):
        try:
            all_q.extend(json.loads(qfile.read_text(encoding="utf-8")))
        except Exception as exc:
            log.warning("Erreur lecture %s : %s", qfile.name, exc)

    consolidated_path = q_dir / "khelifa_all_questions.json"
    consolidated_path.write_text(
        json.dumps(all_q, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    log.info("Total questions : %d", len(all_q))
    mc_counts = Counter(q.get("micro_concept_id", "N/A") for q in all_q)
    log.info("Distribution des micro-concepts :")
    for mc, count in mc_counts.most_common():
        log.info("  %s: %d", mc, count)
# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------


def run_pipeline(args: argparse.Namespace) -> None:
    OCR_OUT_DIR.mkdir(parents=True, exist_ok=True)
    QUESTIONS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    series_to_run = [args.serie] if args.serie else [1, 2]

    # --- Étape 1 : OCR ---
    if not args.no_ocr:
        for serie in series_to_run:
            cfg = VOLUMES_CONFIG[serie]
            pdf_dir = cfg["dir"]
            if not pdf_dir.exists():
                log.warning("Dossier introuvable : %s", pdf_dir)
                continue

            pdfs = sorted(pdf_dir.glob("*.pdf"))
            log.info("Série KHELIFA %d — %d PDFs dans %s", serie, len(pdfs), pdf_dir)

            for pdf_path in pdfs:
                m = re.search(r"VOLUME[_\s]?(\d+)", pdf_path.stem, re.IGNORECASE)
                vol = int(m.group(1)) if m else None
                if vol is None:
                    log.warning("Volume non détecté : %s", pdf_path.name)
                    continue
                if args.start_volume and vol < args.start_volume:
                    continue
                if args.end_volume and vol > args.end_volume:
                    continue

                stem_ocr = ocr_stem(pdf_path)
                if args.resume and is_ocr_done(OCR_OUT_DIR, pdf_path):
                    log.info("OCR déjà fait (skip) : %s", stem_ocr)
                    continue

                log.info("=" * 60)
                log.info("OCR : KHELIFA %d Volume %d (%s)", serie, vol, pdf_path.name)
                log.info("=" * 60)

                success = run_ocr_volume(
                    pdf_path, OCR_OUT_DIR,
                    workers=args.workers,
                    dpi=args.dpi,
                    pdf_mode=args.pdf_mode,
                )
                if success:
                    log.info("OCR terminé : %s", stem_ocr)
                else:
                    log.error("OCR échoué : %s", stem_ocr)

    # --- Étape 2 : Extraction des questions ---
    if not args.no_extract:
        for serie in series_to_run:
            cfg = VOLUMES_CONFIG[serie]
            pdf_dir = cfg["dir"]
            for pdf_path in sorted(pdf_dir.glob("*.pdf")):
                m = re.search(r"VOLUME[_\s]?(\d+)", pdf_path.stem, re.IGNORECASE)
                vol = int(m.group(1)) if m else None
                if vol is None:
                    continue
                if args.start_volume and vol < args.start_volume:
                    continue
                if args.end_volume and vol > args.end_volume:
                    continue
                extract_volume_questions(serie, vol, pdf_path, OCR_OUT_DIR, QUESTIONS_OUT_DIR)

    # --- Étape 3 : Consolidation ---
    if not args.no_extract:
        consolidate_questions(QUESTIONS_OUT_DIR)

    log.info("=== PIPELINE TERMINÉ ===")
    log.info("OCR output : %s", OCR_OUT_DIR)
    log.info("Questions  : %s", QUESTIONS_OUT_DIR)
    for f in sorted(QUESTIONS_OUT_DIR.glob("*")):
        size = f.stat().st_size / 1e6
        log.info("  %s (%.1f MB)", f.name, size)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Pipeline KHELIFA 1 & 2 complet")
    ap.add_argument("--serie", type=int, choices=[1, 2], default=None)
    ap.add_argument("--start-volume", type=int, default=None)
    ap.add_argument("--end-volume", type=int, default=None)
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--pdf-mode", choices=["auto", "ocr", "text"], default="ocr")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--no-ocr", action="store_true", help="Skiper l'OCR (ré-extraction des questions)")
    ap.add_argument("--no-extract", action="store_true", help="Skiper l'extraction des questions")
    return ap


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        run_pipeline(args)
    except KeyboardInterrupt:
        log.warning("Interruption utilisateur.")
        sys.exit(130)


if __name__ == "__main__":
    main()
