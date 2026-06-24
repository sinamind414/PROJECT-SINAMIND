#!/usr/bin/env python3
"""
Pipeline OCR robuste — arabe (principal) + français.
Supporte : PDF scannés, images (PNG, JPG, TIFF, BMP, WEBP).

Corrections vs version précédente :
  - ara+fra au lieu de ara+eng
  - 300 DPI par défaut
  - Pré-traitement image (deskew, binarisation, débruitage)
  - Vrai mode reprise (append + pages déjà traitées ignorées)
  - Erreurs OCR marquées dans l'output
  - Parallélisation (ProcessPoolExecutor)
  - Vérification des prérequis au démarrage
  - Context manager pour fitz
  - Support images directes (PNG, JPG, TIFF, BMP, WEBP)
  - OEM explicite
  - Compatible Python 3.8+

Usage PDF :
  python ocr_pipeline.py input/doc.pdf --dpi 300 --workers 4

Usage image unique :
  python ocr_pipeline.py input/scan.jpg

Usage dossier d'images :
  python ocr_pipeline.py input/scans/ --workers 4

Reprise (pages déjà faites ignorées) :
  python ocr_pipeline.py input/doc.pdf --resume
"""

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Vérification des prérequis (une seule fois au démarrage)
# ---------------------------------------------------------------------------
def check_requirements() -> None:
    """Vérifie que tesseract est accessible et que les langues ara/fra sont installées."""
    tesseract_cmd = shutil.which("tesseract") or os.path.join(
        os.environ.get("TESSERACT_PATH", "C:\\Program Files\\Tesseract-OCR"), "tesseract.exe"
    )
    if not shutil.which("tesseract") and not os.path.exists(tesseract_cmd):
        log.error("Tesseract introuvable dans le PATH. Installez-le : choco install tesseract")
        sys.exit(1)

    result = subprocess.run([tesseract_cmd, "--list-langs"], capture_output=True, text=True)
    installed = result.stdout + result.stderr
    missing = [lang for lang in ("ara", "fra") if lang not in installed]
    if missing:
        log.error(
            "Langues Tesseract manquantes : %s\n  Telechargez : https://github.com/tesseract-ocr/tessdata/raw/main/%s",
            missing,
            ".traineddata / ".join(f"{l}.traineddata" for l in missing),
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pré-traitement image
# ---------------------------------------------------------------------------
def _deskew(image: np.ndarray) -> np.ndarray:
    """Corrige l'inclinaison du scan via la transformée de Hough."""
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


def preprocess_image(img_array: np.ndarray) -> np.ndarray:
    """
    Pipeline de pré-traitement pour OCR arabe/français sur scans.
    Ordre : deskew → niveaux de gris → débruitage → binarisation adaptative.
    """
    img = _deskew(img_array)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img

    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=10,
    )

    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.erode(binary, kernel, iterations=1)

    return processed


# ---------------------------------------------------------------------------
# OCR d'une page (worker)
# ---------------------------------------------------------------------------
def _ocr_single(args: tuple) -> tuple[int, str, str | None]:
    page_no, img_array, psm, oem, timeout = args
    error = None
    text = ""
    tmp_path = None

    try:
        processed = preprocess_image(img_array)

        fd, tmp_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        cv2.imwrite(tmp_path, processed)

        tesseract_cmd = shutil.which("tesseract") or os.path.join(
            os.environ.get("TESSERACT_PATH", "C:\\Program Files\\Tesseract-OCR"), "tesseract.exe"
        )

        result = subprocess.run(
            [
                tesseract_cmd,
                tmp_path,
                "-",
                "-l",
                "ara+fra",
                "--psm",
                str(psm),
                "--oem",
                str(oem),
                "-c",
                "preserve_interword_spaces=1",
                "-c",
                "textord_arabic_right_to_left=1",
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        text = result.stdout.strip()
        if result.returncode != 0:
            error = result.stderr.strip()[:400]
            text = f"[TESSERACT ERROR page {page_no}: {error}]"

    except subprocess.TimeoutExpired:
        error = f"Timeout ({timeout}s) dépassé"
        text = f"[TIMEOUT ERROR page {page_no}]"
    except Exception as e:
        error = str(e)
        text = f"[OCR ERROR page {page_no}: {e}]"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return page_no, text, error


# ---------------------------------------------------------------------------
# Extraction des numéros de pages déjà traitées (mode reprise)
# ---------------------------------------------------------------------------
def _already_done_pages(out_path: Path) -> set:
    if not out_path.exists():
        return set()
    pattern = re.compile(r"^={10,}\nPAGE (\d+)\n={10,}", re.MULTILINE)
    content = out_path.read_text(encoding="utf-8", errors="ignore")
    return {int(m.group(1)) for m in pattern.finditer(content)}


# ---------------------------------------------------------------------------
# Conversion source → liste de (page_no, np.ndarray)
# ---------------------------------------------------------------------------
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}


def _load_pages(source: Path, dpi: int, start: int, end: int | None) -> list[tuple[int, np.ndarray]]:
    pages = []

    if source.is_dir():
        files = sorted(f for f in source.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS)
        for idx, f in enumerate(files, start=1):
            img = cv2.imread(str(f))
            if img is not None:
                pages.append((idx, img))
            else:
                log.warning("Image illisible ignorée : %s", f.name)

    elif source.suffix.lower() in IMAGE_EXTENSIONS:
        img = cv2.imread(str(source))
        if img is None:
            log.error("Impossible de lire l'image : %s", source)
            sys.exit(1)
        pages.append((1, img))

    else:
        import fitz  # PyMuPDF

        with fitz.open(str(source)) as doc:
            total = doc.page_count
            end_ = min(end, total) if end else total
            start_ = max(1, start)

            mat = fitz.Matrix(dpi / 72, dpi / 72)
            for page_no in range(start_, end_ + 1):
                page = doc[page_no - 1]
                pix = page.get_pixmap(matrix=mat, alpha=False)
                img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                if pix.n == 4:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
                elif pix.n == 1:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
                else:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                pages.append((page_no, img_array))

    return pages


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def ocr_pipeline(
    source: str,
    dpi: int = 300,
    start: int = 1,
    end: int | None = None,
    timeout: int = 120,
    psm: int = 3,
    oem: int = 1,
    workers: int = 2,
    resume: bool = False,
    out_dir: str | None = None,
    suffix: str = ".ocr.txt",
) -> str:
    src = Path(source)
    if not src.exists():
        log.error("Source introuvable : %s", src)
        sys.exit(1)

    if out_dir:
        out_path = Path(out_dir) / (src.stem + suffix)
        Path(out_dir).mkdir(parents=True, exist_ok=True)
    elif src.is_dir():
        out_path = src.parent / (src.name + suffix)
    else:
        out_path = src.with_suffix(suffix)

    done_pages = _already_done_pages(out_path) if resume else set()
    if done_pages:
        log.info("Mode reprise — %d pages déjà traitées", len(done_pages))

    log.info("Chargement des pages depuis : %s", src)
    all_pages = _load_pages(src, dpi, start, end)

    pages_to_do = [(pno, img) for pno, img in all_pages if pno not in done_pages]
    if not pages_to_do:
        log.info("Toutes les pages sont déjà traitées. Rien à faire.")
        return str(out_path)

    log.info("%d pages à traiter (workers=%d, DPI=%d, OEM=%d, PSM=%d)", len(pages_to_do), workers, dpi, oem, psm)

    worker_args = [(pno, img, psm, oem, timeout) for pno, img in pages_to_do]

    results: dict = {}
    errors_summary: list[tuple[int, str]] = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_ocr_single, arg): arg[0] for arg in worker_args}
        for future in as_completed(futures):
            page_no, text, error = future.result()
            results[page_no] = text
            if error:
                errors_summary.append((page_no, error))
            total_pages = len(pages_to_do)
            done_count = len(results)
            log.info(
                "Page %d traitée [%d/%d] — %d chars%s",
                page_no,
                done_count,
                total_pages,
                len(text),
                " ⚠️ ERREUR" if error else "",
            )

    sep = "=" * 70
    new_blocks = []
    for pno in sorted(results.keys()):
        new_blocks.append(f"\n{sep}\nPAGE {pno}\n{sep}\n{results[pno]}")

    if resume and out_path.exists():
        with out_path.open("a", encoding="utf-8") as f:
            f.write("\n".join(new_blocks))
    else:
        all_blocks = []
        page_map = {pno: results[pno] for pno in results}
        for pno, _ in all_pages:
            if pno in page_map:
                all_blocks.append(f"\n{sep}\nPAGE {pno}\n{sep}\n{page_map[pno]}")
        out_path.write_text("\n".join(all_blocks), encoding="utf-8")

    total_chars = sum(len(t) for t in results.values())
    log.info("OCR terminé → %s (%d chars)", out_path, total_chars)

    if errors_summary:
        log.warning("%d page(s) avec erreurs :", len(errors_summary))
        for pno, err in errors_summary[:10]:
            log.warning("  Page %d : %s", pno, err)

    return str(out_path)


# ---------------------------------------------------------------------------
# Entrée CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="OCR arabe+français — PDF, images, dossiers")
    ap.add_argument("source", help="PDF, image (PNG/JPG/TIFF/BMP/WEBP) ou dossier d'images")
    ap.add_argument("--dpi", type=int, default=300, help="Résolution de rendu PDF (défaut: 300)")
    ap.add_argument("--start", type=int, default=1, help="Première page PDF (défaut: 1)")
    ap.add_argument("--end", type=int, default=None, help="Dernière page PDF (défaut: fin du document)")
    ap.add_argument("--timeout", type=int, default=120, help="Timeout Tesseract par page en secondes (défaut: 120)")
    ap.add_argument("--psm", type=int, default=3, help="Page Segmentation Mode Tesseract (défaut: 3)")
    ap.add_argument("--oem", type=int, default=1, help="OCR Engine Mode (défaut: 1=LSTM)")
    ap.add_argument("--workers", type=int, default=2, help="Nombre de workers parallèles (défaut: 2)")
    ap.add_argument("--resume", action="store_true", help="Reprendre : ignorer les pages déjà traitées")
    ap.add_argument("--out-dir", default=None, help="Dossier de sortie (défaut: même dossier que la source)")
    ap.add_argument("--suffix", default=".ocr.txt", help="Extension du fichier de sortie (défaut: .ocr.txt)")
    args = ap.parse_args()

    check_requirements()
    ocr_pipeline(
        source=args.source,
        dpi=args.dpi,
        start=args.start,
        end=args.end,
        timeout=args.timeout,
        psm=args.psm,
        oem=args.oem,
        workers=args.workers,
        resume=args.resume,
        out_dir=args.out_dir,
        suffix=args.suffix,
    )
