#!/usr/bin/env python3
"""
Pipeline OCR local pour KHELIFA 1 & 2 (30 volumes).
Extraction des questions SVT des annales du Bac Algérien.

Lit les PDFs depuis :
  data/ANNALES_SVT_BAC_ALGERIE/KHELIFA_1/VOLUMES_KHELIFA1/
  data/ANNALES_SVT_BAC_ALGERIE/KHELIFA_2/VOLUMES_KHELIFA2/

Sortie :
  data/ocr_output/khelifa{1,2}_volume{XX}.json           (métadonnées par page)
  data/ocr_output/khelifa{1,2}_volume{XX}_questions.json  (questions extraites)
  data/ocr_output/khelifa_all_questions.json               (consolidé)

Usage :
  python scripts/run_khelifa_pipeline_local.py
  python scripts/run_khelifa_pipeline_local.py --resume
  python scripts/run_khelifa_pipeline_local.py --serie 1
  python scripts/run_khelifa_pipeline_local.py --serie 2 --no-preprocess
  python scripts/run_khelifa_pipeline_local.py --serie 1 --start-volume 6
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("khelifa_local")
# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
ANNALES_DIR = BASE_DIR / "data" / "ANNALES_SVT_BAC_ALGERIE"
OCR_OUTPUT_DIR = BASE_DIR / "data" / "ocr_output"

KHELIFA1_DIR = ANNALES_DIR / "KHELIFA_1" / "VOLUMES_KHELIFA1"
KHELIFA2_DIR = ANNALES_DIR / "KHELIFA_2" / "VOLUMES_KHELIFA2"


# ---------------------------------------------------------------------------
# EasyOCR (initialisation paresseuse)
# ---------------------------------------------------------------------------

_reader = None


def get_reader(gpu: bool = True) -> "easyocr.Reader":
    global _reader
    if _reader is None:
        import easyocr
        log.info("Initialisation EasyOCR (gpu=%s)...", gpu)
        _reader = easyocr.Reader(["ar", "en"], gpu=gpu)
    return _reader


# ---------------------------------------------------------------------------
# Prétraitement image OpenCV
# ---------------------------------------------------------------------------

def _deskew(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    if lines is None:
        return image
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angles.append(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
    if not angles:
        return image
    median_angle = np.median(angles)
    if abs(median_angle) < 0.5:
        return image
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), median_angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def preprocess_for_ocr(img_array: np.ndarray) -> np.ndarray:
    img = _deskew(img_array)
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
    binary = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=31, C=10)
    return binary


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
# Fonctions OCR et extraction
# ---------------------------------------------------------------------------

def ocr_page(pix, reader, use_preprocess: bool = True) -> list[dict]:
    tmp = f"/tmp/ocr_{os.urandom(4).hex()}.png"
    if use_preprocess:
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif pix.n == 1:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif pix.n == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        processed = preprocess_for_ocr(img_array)
        cv2.imwrite(tmp, processed)
    else:
        pix.save(tmp)
    try:
        results = reader.readtext(tmp, paragraph=False, detail=1)
        blocks = []
        for r in results:
            if len(r) == 3:
                bbox, text, conf = r
            elif len(r) == 2:
                bbox, text = r
                conf = 0.5
            else:
                continue
            if conf > 0.3 and text.strip():
                blocks.append({
                    "text": text.strip(),
                    "confidence": round(float(conf), 2),
                    "bbox": [round(float(x), 1) for pt in bbox for x in pt],
                })
        return blocks
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def extract_questions(blocks: list[dict]) -> list[dict]:
    questions = []
    cur = None
    for b in blocks:
        if Q_PATTERN.search(b["text"]):
            if cur:
                questions.append(cur)
            cur = {"texte_brut": b["text"], "confidence": b["confidence"], "blocks": [b]}
        elif cur and len(cur["blocks"]) < 10:
            cur["blocks"].append(b)
            cur["texte_brut"] += " " + b["text"]
    if cur:
        questions.append(cur)
    return questions


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


def clean_arabic(text: str) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    t = re.sub(r"[|¦•●]", "", t)
    t = t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    t = t.replace("ة", "ه").replace("ى", "ا")
    t = t.replace("٠", "0").replace("١", "1").replace("٢", "2")
    t = t.replace("٣", "3").replace("٤", "4").replace("٥", "5")
    t = t.replace("٦", "6").replace("٧", "7").replace("٨", "8").replace("٩", "9")
    return t
# ---------------------------------------------------------------------------
# Traitement d'un volume
# ---------------------------------------------------------------------------

def process_volume(
    pdf_path: Path,
    serie: int,
    vol_num: int,
    reader,
    dpi: int = 150,
    use_preprocess: bool = True,
    resume: bool = False,
) -> tuple[dict, list[dict]]:
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    total = len(doc)

    vol_data = {
        "source": f"KHELIFA {serie} - Volume {vol_num}",
        "fichier": pdf_path.name,
        "total_pages": total,
        "processed_pages": 0,
        "pages": [],
    }
    all_q: list[dict] = []
    t_start = time.time()

    for pn in range(total):
        page_no = pn + 1
        pix = doc[pn].get_pixmap(dpi=dpi)
        blocks = ocr_page(pix, reader, use_preprocess=use_preprocess)
        qs = extract_questions(blocks)

        pd = {"page": page_no, "blocks": len(blocks), "questions": []}
        for qi, q in enumerate(qs):
            cleaned = clean_arabic(q["texte_brut"])
            main, sec, av = tag_concept(cleaned)
            avg_conf = round(sum(b["confidence"] for b in q["blocks"]) / len(q["blocks"]), 2)
            qd = {
                "id": f"q_khelifa{serie}_v{vol_num:02d}_p{page_no:02d}_{qi+1:02d}",
                "texte_brut": q["texte_brut"][:500],
                "texte_corrige": cleaned[:500],
                "micro_concept_id": main,
                "secondary_concepts": sec,
                "a_verifier": av,
                "confidence": avg_conf,
                "source": f"KHELIFA {serie} - Volume {vol_num} - Page {page_no}",
                "type": "question",
                "difficulte": "moyenne",
                "bac_frequent": not av,
                "notes": "OCR auto + preprocessing",
                "source_page": page_no,
            }
            pd["questions"].append(qd)
            all_q.append(qd)

        vol_data["pages"].append(pd)

        elapsed = time.time() - t_start
        eta = (elapsed / (pn + 1)) * (total - pn - 1) / 60
        log.info("  Page %d/%d — %d blocs, %d q | %ds ecoulees, ETA ~%dmin", page_no, total, len(blocks), len(qs), int(elapsed), int(eta))

    doc.close()
    vol_data["processed_pages"] = total
    return vol_data, all_q
# ---------------------------------------------------------------------------
# Volumes déjà traités (détection automatique)
# ---------------------------------------------------------------------------

def already_processed(set_ids: set[str]) -> set[str]:
    """Retourne les IDs de volumes déjà présents dans ocr_output."""
    done: set[str] = set()
    for f in OCR_OUTPUT_DIR.glob("khelifa*_volume*_questions.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            for q in data:
                sid = q.get("id", "")
                parts = sid.split("_")
                if len(parts) >= 3:
                    vol_id = f"{parts[0]}_{parts[1]}"  # khelifa1_volume01
                    done.add(vol_id)
        except Exception:
            pass
    return done


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run_pipeline(args: argparse.Namespace) -> None:
    OCR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.serie in (1, None):
        series: list[tuple[int, Path]] = [(1, KHELIFA1_DIR)]
    else:
        series = [(2, KHELIFA2_DIR)]

    reader = get_reader(gpu=not args.no_gpu)
    total_questions = 0

    if args.resume:
        already_ids = already_processed(set())
        log.info("Volumes déjà traités détectés : %d", len(already_ids))
    else:
        already_ids = set()

    for serie, pdf_dir in series:
        if not pdf_dir.exists():
            log.warning("Dossier introuvable : %s", pdf_dir)
            continue

        pdfs = sorted(pdf_dir.glob("*.pdf"))
        log.info("Série KHELIFA %d — %d PDFs trouvés dans %s", serie, len(pdfs), pdf_dir)

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

            vol_id = f"khelifa{serie}_volume{vol:02d}"
            if args.resume and vol_id in already_ids:
                log.info("Volume déjà traité (skip) : %s", vol_id)
                continue

            log.info("=" * 60)
            log.info("Traitement : KHELIFA %d Volume %d (%s)", serie, vol, pdf_path.name)
            log.info("=" * 60)

            try:
                vol_data, questions = process_volume(
                    pdf_path, serie, vol, reader,
                    dpi=args.dpi,
                    use_preprocess=not args.no_preprocess,
                    resume=args.resume,
                )
            except Exception as exc:
                log.error("ÉCHEC KHELIFA %d Volume %d : %s", serie, vol, exc)
                continue

            out_vol = OCR_OUTPUT_DIR / f"{vol_id}.json"
            out_q = OCR_OUTPUT_DIR / f"{vol_id}_questions.json"
            with out_vol.open("w", encoding="utf-8") as f:
                json.dump(vol_data, f, ensure_ascii=False, indent=2)
            with out_q.open("w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)

            total_questions += len(questions)
            log.info("  -> %d questions extraites → %s", len(questions), out_q.name)

    # Consolidation
    log.info("=" * 60)
    log.info("Consolidation de toutes les questions…")
    all_consolidated: list[dict] = []
    for qfile in sorted(OCR_OUTPUT_DIR.glob("*_questions.json")):
        try:
            all_consolidated.extend(json.loads(qfile.read_text(encoding="utf-8")))
        except Exception as exc:
            log.warning("Erreur lecture %s : %s", qfile.name, exc)

    consolidated_path = OCR_OUTPUT_DIR / "khelifa_all_questions.json"
    with consolidated_path.open("w", encoding="utf-8") as f:
        json.dump(all_consolidated, f, ensure_ascii=False, indent=2)

    log.info("Total questions extraites : %d", len(all_consolidated))
    log.info("Fichier consolidé : %s", consolidated_path)

    mc_counts = Counter(q.get("micro_concept_id", "N/A") for q in all_consolidated)
    log.info("Distribution des micro-concepts :")
    for mc, count in mc_counts.most_common():
        log.info("  %s: %d", mc, count)

    log.info("=== TERMINÉ ===")
    for f in sorted(OCR_OUTPUT_DIR.iterdir()):
        size = f.stat().st_size / 1e6
        log.info("  %s (%.1f MB)", f.name, size)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Pipeline OCR local KHELIFA 1 & 2")
    ap.add_argument("--serie", type=int, choices=[1, 2], default=None, help="Série à traiter (1 ou 2, défaut: les deux)")
    ap.add_argument("--start-volume", type=int, default=None, help="Premier volume (défaut: 1)")
    ap.add_argument("--end-volume", type=int, default=None, help="Dernier volume (défaut: 15)")
    ap.add_argument("--dpi", type=int, default=150, help="DPI de rendu PDF (défaut: 150)")
    ap.add_argument("--resume", action="store_true", help="Ignorer les volumes déjà traités")
    ap.add_argument("--no-preprocess", action="store_true", help="Désactive le prétraitement OpenCV")
    ap.add_argument("--no-gpu", action="store_true", help="Force CPU pour EasyOCR")
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