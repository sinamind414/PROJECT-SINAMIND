#!/usr/bin/env python3
"""
Pipeline OCR robuste — arabe (principal) + français.

Ce script traite :
- PDF
- image unique (PNG, JPG, JPEG, TIFF, TIF, BMP, WEBP)
- dossier d'images

Points clés :
- PDF : mode auto par défaut
  - si une page contient déjà du texte natif exploitable, on l'extrait
  - sinon on bascule en OCR
- Reprise réellement robuste via fichiers intermédiaires par page + état JSON
- Pas de chargement de toutes les pages en RAM
- Parallélisation par page sans sérialiser d'images numpy entre processus
- Prétraitement configurable pour scans difficiles
- Sortie finale toujours réassemblée dans l'ordre des pages
- Erreurs et timeouts marqués dans le texte final

Dépendances Python :
  pip install numpy opencv-python pymupdf

Dépendances système :
  tesseract-ocr + langues voulues (par défaut ara et fra)

Exemples :
  python ocr_pipeline_robuste.py input/doc.pdf --workers 4 --resume
  python ocr_pipeline_robuste.py input/scan.jpg
  python ocr_pipeline_robuste.py input/scans/ --workers 4
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import cv2
import numpy as np


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
PDF_EXTENSIONS = {".pdf"}
SEPARATOR = "=" * 70
STATE_VERSION = 1


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ocr_pipeline")


@dataclass(frozen=True)
class PageRef:
    page_no: int
    kind: str  # 'pdf' | 'image'
    source_path: str
    pdf_index: Optional[int] = None


def die(message: str, code: int = 1) -> None:
    log.error(message)
    raise SystemExit(code)


def natural_key(value: str):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding=encoding) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def page_part_path(parts_dir: Path, page_no: int) -> Path:
    return parts_dir / f"page_{page_no:06d}.txt"


def parse_langs(lang_spec: str) -> List[str]:
    langs = [chunk.strip() for chunk in lang_spec.split("+") if chunk.strip()]
    if not langs:
        raise ValueError("Aucune langue Tesseract valide dans --lang")
    return langs


def check_tesseract_languages(lang_spec: str) -> None:
    if not shutil.which("tesseract"):
        die("Tesseract introuvable dans le PATH. Installez-le d'abord.")

    result = subprocess.run(
        ["tesseract", "--list-langs"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        die(f"Impossible d'interroger Tesseract (--list-langs): {result.stderr.strip()}")

    installed = {
        line.strip()
        for line in (result.stdout + "\n" + result.stderr).splitlines()
        if line.strip() and not line.lower().startswith("list of available languages")
    }
    required = parse_langs(lang_spec)
    missing = [lang for lang in required if lang not in installed]
    if missing:
        packages = " ".join(f"tesseract-ocr-{lang}" for lang in missing)
        die(
            "Langues Tesseract manquantes : "
            f"{', '.join(missing)}\n"
            f"Ubuntu/Debian : apt install {packages}"
        )


def check_pdf_support_if_needed(source: Path) -> None:
    if source.is_file() and source.suffix.lower() in PDF_EXTENSIONS:
        try:
            import fitz  # noqa: F401
        except Exception as exc:
            die(f"Support PDF indisponible. Installez PyMuPDF (pymupdf). Détail: {exc}")


def validate_args(args: argparse.Namespace) -> None:
    src = Path(args.source)
    if not src.exists():
        die(f"Source introuvable : {src}")

    if args.dpi <= 0:
        die("--dpi doit être > 0")
    if args.workers <= 0:
        die("--workers doit être >= 1")
    if args.timeout <= 0:
        die("--timeout doit être > 0")
    if args.start <= 0:
        die("--start doit être >= 1")
    if args.end is not None and args.end < args.start:
        die("--end doit être >= --start")
    if args.psm < 0 or args.psm > 13:
        die("--psm doit être entre 0 et 13")
    if args.oem not in (0, 1, 2, 3):
        die("--oem doit être dans {0,1,2,3}")
    if args.pdf_mode not in {"auto", "ocr", "text"}:
        die("--pdf-mode doit être dans {auto, ocr, text}")
    if args.text_threshold < 0:
        die("--text-threshold doit être >= 0")

    if src.is_file() and src.suffix.lower() not in IMAGE_EXTENSIONS | PDF_EXTENSIONS:
        die(f"Extension non supportée : {src.suffix}")

    if src.is_dir():
        files = [p for p in src.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        if not files:
            die(f"Aucune image supportée trouvée dans le dossier : {src}")


def output_paths(source: Path, out_dir: Optional[str], suffix: str) -> Tuple[Path, Path, Path]:
    if out_dir:
        out_root = Path(out_dir)
        out_root.mkdir(parents=True, exist_ok=True)
        out_path = out_root / f"{source.stem}{suffix}"
    elif source.is_dir():
        out_path = source.parent / f"{source.name}{suffix}"
    else:
        out_path = source.with_suffix(suffix)

    parts_dir = out_path.with_name(out_path.name + ".parts")
    state_path = out_path.with_name(out_path.name + ".state.json")
    return out_path, parts_dir, state_path


def reset_run_artifacts(parts_dir: Path, state_path: Path) -> None:
    if parts_dir.exists():
        shutil.rmtree(parts_dir)
    if state_path.exists():
        state_path.unlink()


def load_state(state_path: Path) -> Dict:
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"État de reprise illisible : {state_path} ({exc})")


def save_state(state_path: Path, state: Dict) -> None:
    atomic_write_text(state_path, json.dumps(state, ensure_ascii=False, indent=2))


def init_state(source: Path, out_path: Path, pages: Sequence[PageRef], args: argparse.Namespace) -> Dict:
    return {
        "version": STATE_VERSION,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "source": str(source.resolve()),
        "output": str(out_path.resolve()),
        "config": {
            "dpi": args.dpi,
            "lang": args.lang,
            "psm": args.psm,
            "oem": args.oem,
            "timeout": args.timeout,
            "workers": args.workers,
            "pdf_mode": args.pdf_mode,
            "preprocess": not args.no_preprocess,
            "text_threshold": args.text_threshold,
        },
        "page_count": len(pages),
        "pages": {},
    }


def ensure_state_compatible(state: Dict, source: Path, out_path: Path) -> None:
    if not state:
        return
    if state.get("version") != STATE_VERSION:
        die("Version d'état de reprise incompatible. Relancez sans --resume ou supprimez l'état.")
    if state.get("source") != str(source.resolve()):
        die("Le fichier d'état ne correspond pas à cette source.")
    if state.get("output") != str(out_path.resolve()):
        die("Le fichier d'état ne correspond pas à cette destination.")


def list_pages(source: Path, start: int, end: Optional[int]) -> List[PageRef]:
    if source.is_dir():
        files = sorted(
            [p for p in source.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS],
            key=lambda p: natural_key(p.name),
        )
        return [PageRef(page_no=i, kind="image", source_path=str(path.resolve())) for i, path in enumerate(files, start=1)]

    if source.suffix.lower() in IMAGE_EXTENSIONS:
        return [PageRef(page_no=1, kind="image", source_path=str(source.resolve()))]

    if source.suffix.lower() in PDF_EXTENSIONS:
        import fitz

        with fitz.open(str(source)) as doc:
            total_pages = doc.page_count

        first = max(1, start)
        last = total_pages if end is None else min(total_pages, end)
        if first > last:
            die(f"Intervalle vide : start={first}, end={last}, total={total_pages}")

        return [
            PageRef(page_no=pno, kind="pdf", source_path=str(source.resolve()), pdf_index=pno - 1)
            for pno in range(first, last + 1)
        ]

    die(f"Type de source non supporté : {source}")
    return []


def meaningful_text(text: str, threshold: int) -> bool:
    compact = re.sub(r"\s+", "", text or "")
    return len(compact) >= threshold


def read_image(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Impossible de lire l'image : {path}")
    return img


def render_pdf_page(pdf_path: str, pdf_index: int, dpi: int) -> np.ndarray:
    import fitz

    with fitz.open(pdf_path) as doc:
        page = doc[pdf_index]
        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 1:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if pix.n == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


def extract_pdf_native_text(pdf_path: str, pdf_index: int) -> str:
    import fitz

    with fitz.open(pdf_path) as doc:
        text = doc[pdf_index].get_text("text")
    return text.strip()


def estimate_skew_angle(gray: np.ndarray) -> float:
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))

    if coords.shape[0] < 200:
        return 0.0

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    angle = float(angle)
    if abs(angle) > 15:
        return 0.0
    if abs(angle) < 0.2:
        return 0.0
    return angle


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    h, w = image.shape[:2]
    center = (w / 2.0, h / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    border_value = 255 if image.ndim == 2 else (255, 255, 255)
    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )


def preprocess_image(image: np.ndarray) -> np.ndarray:
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    angle = estimate_skew_angle(gray)
    if angle:
        gray = rotate_image(gray, angle)

    # Normalisation locale du contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    normalized = clahe.apply(gray)

    # Débruitage léger, pour éviter de casser les détails fins
    denoised = cv2.fastNlMeansDenoising(normalized, h=7, templateWindowSize=7, searchWindowSize=21)

    # Binarisation adaptative pour scans non uniformes
    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )

    return binary


def run_tesseract_on_image(image: np.ndarray, lang: str, psm: int, oem: int, timeout: int) -> Tuple[str, Optional[str]]:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp_path = tmp.name

        ok = cv2.imwrite(tmp_path, image)
        if not ok:
            raise RuntimeError("Échec d'écriture du fichier image temporaire")

        env = os.environ.copy()
        env.setdefault("OMP_THREAD_LIMIT", "1")

        result = subprocess.run(
            [
                "tesseract",
                tmp_path,
                "-",
                "-l",
                lang,
                "--psm",
                str(psm),
                "--oem",
                str(oem),
                "-c",
                "preserve_interword_spaces=1",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
            check=False,
        )

        if result.returncode != 0:
            err = (result.stderr or "Erreur Tesseract sans détail").strip()[:500]
            return f"[TESSERACT ERROR: {err}]", err

        return result.stdout.strip(), None

    except subprocess.TimeoutExpired:
        return "[TIMEOUT ERROR]", f"Timeout Tesseract dépassé ({timeout}s)"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def process_page(task: Tuple[PageRef, int, str, int, int, int, str, bool, int]) -> Dict[str, object]:
    page, dpi, lang, psm, oem, timeout, pdf_mode, do_preprocess, text_threshold = task
    page_no = page.page_no

    try:
        if page.kind == "pdf" and pdf_mode in {"auto", "text"}:
            native_text = extract_pdf_native_text(page.source_path, int(page.pdf_index))
            if meaningful_text(native_text, text_threshold):
                return {
                    "page_no": page_no,
                    "text": native_text,
                    "error": None,
                    "method": "native-text",
                }
            if pdf_mode == "text":
                err = f"Aucun texte natif exploitable détecté sur la page {page_no}"
                return {
                    "page_no": page_no,
                    "text": f"[NO NATIVE TEXT page {page_no}]",
                    "error": err,
                    "method": "native-text",
                }

        if page.kind == "image":
            img = read_image(page.source_path)
        elif page.kind == "pdf":
            img = render_pdf_page(page.source_path, int(page.pdf_index), dpi)
        else:
            raise RuntimeError(f"Type de page inconnu : {page.kind}")

        if do_preprocess:
            img = preprocess_image(img)
        else:
            if img.ndim == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        text, err = run_tesseract_on_image(img, lang, psm, oem, timeout)
        if err:
            text = f"[OCR ERROR page {page_no}: {err}]"
        return {
            "page_no": page_no,
            "text": text,
            "error": err,
            "method": "ocr",
        }

    except Exception as exc:
        err = str(exc)
        return {
            "page_no": page_no,
            "text": f"[OCR ERROR page {page_no}: {err}]",
            "error": err,
            "method": "failed",
        }


def assemble_output(out_path: Path, parts_dir: Path, pages: Sequence[PageRef]) -> None:
    blocks: List[str] = []
    for page in pages:
        part = page_part_path(parts_dir, page.page_no)
        if part.exists():
            text = part.read_text(encoding="utf-8", errors="replace").rstrip()
        else:
            text = f"[MISSING PAGE {page.page_no}]"
        blocks.append(f"{SEPARATOR}\nPAGE {page.page_no}\n{SEPARATOR}\n{text}")

    atomic_write_text(out_path, "\n\n".join(blocks) + "\n")


def completed_pages_from_state(state: Dict, parts_dir: Path) -> Set[int]:
    done: Set[int] = set()
    for key, meta in state.get("pages", {}).items():
        try:
            page_no = int(key)
        except Exception:
            continue
        if meta.get("status") == "done" and page_part_path(parts_dir, page_no).exists():
            done.add(page_no)
    return done


def ocr_pipeline(args: argparse.Namespace) -> str:
    source = Path(args.source)
    out_path, parts_dir, state_path = output_paths(source, args.out_dir, args.suffix)
    pages = list_pages(source, args.start, args.end)

    if not args.resume:
        reset_run_artifacts(parts_dir, state_path)

    parts_dir.mkdir(parents=True, exist_ok=True)

    state = load_state(state_path) if args.resume else {}
    if state:
        ensure_state_compatible(state, source, out_path)
    else:
        state = init_state(source, out_path, pages, args)
        save_state(state_path, state)

    done_pages = completed_pages_from_state(state, parts_dir)
    page_nos = {p.page_no for p in pages}
    done_pages = {p for p in done_pages if p in page_nos}

    pages_to_do = [p for p in pages if p.page_no not in done_pages]

    if done_pages:
        log.info("Mode reprise — %d page(s) déjà finalisées", len(done_pages))

    if not pages_to_do:
        log.info("Toutes les pages demandées sont déjà traitées.")
        assemble_output(out_path, parts_dir, pages)
        return str(out_path)

    worker_count = min(args.workers, len(pages_to_do))
    log.info(
        "%d page(s) à traiter (workers=%d, dpi=%d, psm=%d, oem=%d, pdf_mode=%s, preprocess=%s)",
        len(pages_to_do),
        worker_count,
        args.dpi,
        args.psm,
        args.oem,
        args.pdf_mode,
        not args.no_preprocess,
    )

    tasks = [
        (
            page,
            args.dpi,
            args.lang,
            args.psm,
            args.oem,
            args.timeout,
            args.pdf_mode,
            not args.no_preprocess,
            args.text_threshold,
        )
        for page in pages_to_do
    ]

    total = len(pages_to_do)
    done_count = 0
    errors_summary: List[Tuple[int, str]] = []

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        future_map = {executor.submit(process_page, task): task[0].page_no for task in tasks}

        for future in as_completed(future_map):
            page_no = future_map[future]
            try:
                result = future.result()
            except Exception as exc:
                err = f"Crash worker: {exc}"
                result = {
                    "page_no": page_no,
                    "text": f"[OCR ERROR page {page_no}: {err}]",
                    "error": err,
                    "method": "failed",
                }

            part_path = page_part_path(parts_dir, int(result["page_no"]))
            atomic_write_text(part_path, str(result["text"]))

            state["pages"][str(result["page_no"])] = {
                "status": "done",
                "updated_at": utc_now_iso(),
                "method": result.get("method"),
                "chars": len(str(result["text"])),
                "error": result.get("error"),
            }
            state["updated_at"] = utc_now_iso()
            save_state(state_path, state)

            done_count += 1
            err = result.get("error")
            if err:
                errors_summary.append((int(result["page_no"]), str(err)))

            log.info(
                "Page %d traitée [%d/%d] — %d chars — mode=%s%s",
                int(result["page_no"]),
                done_count,
                total,
                len(str(result["text"])),
                result.get("method"),
                " ⚠️ ERREUR" if err else "",
            )

    assemble_output(out_path, parts_dir, pages)
    state["updated_at"] = utc_now_iso()
    state["assembled_at"] = utc_now_iso()
    save_state(state_path, state)

    total_chars = 0
    for page in pages:
        part = page_part_path(parts_dir, page.page_no)
        if part.exists():
            total_chars += len(part.read_text(encoding="utf-8", errors="replace"))

    log.info("OCR terminé → %s (%d chars)", out_path, total_chars)

    if errors_summary:
        log.warning("%d page(s) avec erreurs :", len(errors_summary))
        for pno, err in errors_summary[:20]:
            log.warning("  Page %d : %s", pno, err)

    return str(out_path)


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="OCR arabe+français — PDF, images, dossiers")
    ap.add_argument("source", help="PDF, image (PNG/JPG/TIFF/BMP/WEBP) ou dossier d'images")
    ap.add_argument("--dpi", type=int, default=300, help="Résolution de rendu PDF (défaut: 300)")
    ap.add_argument("--start", type=int, default=1, help="Première page PDF (défaut: 1)")
    ap.add_argument("--end", type=int, default=None, help="Dernière page PDF (défaut: fin du document)")
    ap.add_argument("--timeout", type=int, default=120, help="Timeout Tesseract par page en secondes")
    ap.add_argument("--psm", type=int, default=3, help="Page Segmentation Mode Tesseract (défaut: 3)")
    ap.add_argument("--oem", type=int, default=1, help="OCR Engine Mode (défaut: 1 = LSTM)")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) // 2), help="Nombre de workers parallèles")
    ap.add_argument("--resume", action="store_true", help="Reprendre une exécution interrompue")
    ap.add_argument("--out-dir", default=None, help="Dossier de sortie")
    ap.add_argument("--suffix", default=".ocr.txt", help="Suffixe de sortie (défaut: .ocr.txt)")
    ap.add_argument("--lang", default="ara+fra", help="Langues Tesseract (défaut: ara+fra)")
    ap.add_argument(
        "--pdf-mode",
        choices=["auto", "ocr", "text"],
        default="auto",
        help="PDF: auto = texte natif si exploitable sinon OCR ; ocr = OCR forcé ; text = texte natif uniquement",
    )
    ap.add_argument(
        "--text-threshold",
        type=int,
        default=25,
        help="Nombre minimal de caractères non blancs pour considérer le texte natif PDF exploitable",
    )
    ap.add_argument("--no-preprocess", action="store_true", help="Désactive le prétraitement image")
    return ap


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    validate_args(args)
    check_tesseract_languages(args.lang)
    check_pdf_support_if_needed(Path(args.source))

    try:
        ocr_pipeline(args)
    except KeyboardInterrupt:
        die("Interruption utilisateur.", code=130)


if __name__ == "__main__":
    main()
