#!/usr/bin/env python3
"""
Pipeline OCR orienté production — arabe (principal) + français.

Traite :
- PDF (extraction native + OCR)
- Image unique (PNG, JPG, JPEG, TIFF, TIF, BMP, WEBP)
- Dossier d'images

Fonctionnalités :
- Reprise robuste par page via état JSON + artefacts intermédiaires
- PDF ouvert une seule fois par worker (cache par processus)
- Parallélisation par page sans sérialiser les images entre processus
- Extraction native du texte PDF avant OCR si demandé
- Détection de pages vides et de doublons perceptuels (images; PDF sans dédup rendu par défaut)
- Métriques d'exécution par page et globales (confidence, qualité)
- Sortie texte finale réassemblée dans l'ordre
- CSV et JSON de reporting
- PDF searchable optionnel
- Journal d'exécution sur disque
- Limitation mémoire configurable

Version nettoyée/corrigée depuis le script fourni dans le chat : suppression des
artefacts Markdown, correction des imports, écriture effective des métadonnées
par page, compatibilité avec l'environnement Agent Mode.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
PDF_EXTENSIONS: Set[str] = {".pdf"}
SEPARATOR: str = "=" * 70
STATE_VERSION: int = 3
MAX_SOURCE_MB: int = 2000
CONFIDENCE_THRESHOLD: float = 45.0
EMPTY_PAGE_THRESHOLD: float = 0.98
DEDUP_HASH_SIZE: Tuple[int, int] = (16, 16)

LOG = logging.getLogger("ocr_pipeline_production")

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PageRef:
    page_no: int
    kind: str  # 'pdf' | 'image'
    source_path: str
    pdf_index: Optional[int] = None
    perceptual_hash: Optional[str] = None


@dataclass(frozen=True)
class AttemptSpec:
    variant: str
    psm: int


# ---------------------------------------------------------------------------
# Worker-level PDF cache (un cache par processus worker)
# ---------------------------------------------------------------------------

_worker_pdf_cache: Dict[str, Any] = {}


def _get_cached_pdf_doc(pdf_path: str) -> Any:
    """Retourne un document PyMuPDF ouvert, avec cache par processus worker."""
    if pdf_path not in _worker_pdf_cache:
        import fitz
        _worker_pdf_cache[pdf_path] = fitz.open(pdf_path)
    return _worker_pdf_cache[pdf_path]


def _close_worker_pdf_cache() -> None:
    """Ferme tous les documents PDF ouverts dans le worker courant."""
    for doc in _worker_pdf_cache.values():
        try:
            doc.close()
        except Exception:
            pass
    _worker_pdf_cache.clear()


# ---------------------------------------------------------------------------
# Logging / utilitaires de base
# ---------------------------------------------------------------------------


def configure_logging(log_file: Optional[Path] = None, verbose: bool = False) -> None:
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers.clear()
    LOG.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(formatter)
    LOG.addHandler(console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        LOG.addHandler(file_handler)


def die(message: str, code: int = 1) -> None:
    LOG.error(message)
    raise SystemExit(code)


def utc_now_iso() -> str:
    """Retourne l'heure UTC courante en ISO 8601."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def natural_key(value: str) -> List[Any]:
    """Tri naturel pour les noms de fichiers (page_2 avant page_10)."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), encoding=encoding) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def _json_sanitize(obj: Any) -> Any:
    """Convertit les scalaires NumPy et objets Path en types JSON natifs."""
    if isinstance(obj, dict):
        return {str(k): _json_sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_sanitize(v) for v in obj]
    if isinstance(obj, tuple):
        return [_json_sanitize(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def atomic_write_json(path: Path, data: Dict) -> None:
    atomic_write_text(path, json.dumps(_json_sanitize(data), ensure_ascii=False, indent=2) + "\n")


def atomic_write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(path.parent)) as tmp:
        tmp.write(payload)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text or ""))


def safe_error_text(text: str, limit: int = 500) -> str:
    return (text or "").strip().replace("\n", " ")[:limit] or "Erreur sans détail"


# ---------------------------------------------------------------------------
# Chemins d'artefacts
# ---------------------------------------------------------------------------


def compute_paths(source: Path, out_dir: Optional[str], suffix: str) -> Dict[str, Path]:
    if out_dir:
        out_root = Path(out_dir)
        out_root.mkdir(parents=True, exist_ok=True)
        txt_out = out_root / f"{source.stem}{suffix}"
        searchable_pdf = out_root / f"{source.stem}.searchable.pdf"
    elif source.is_dir():
        txt_out = source.parent / f"{source.name}{suffix}"
        searchable_pdf = source.parent / f"{source.name}.searchable.pdf"
    else:
        txt_out = source.with_suffix(suffix)
        searchable_pdf = txt_out.parent / f"{source.stem}.searchable.pdf"

    bundle = txt_out.with_name(txt_out.name + ".bundle")
    return {
        "txt_out": txt_out,
        "searchable_pdf": searchable_pdf,
        "bundle": bundle,
        "pages_txt": bundle / "pages_txt",
        "pages_meta": bundle / "pages_meta",
        "pages_pdf": bundle / "pages_pdf",
        "state": bundle / "run.state.json",
        "summary": bundle / "summary.json",
        "pages_csv": bundle / "pages.csv",
        "run_log": bundle / "run.log",
    }


def page_text_path(paths: Dict[str, Path], page_no: int) -> Path:
    return paths["pages_txt"] / f"page_{page_no:06d}.txt"


def page_meta_path(paths: Dict[str, Path], page_no: int) -> Path:
    return paths["pages_meta"] / f"page_{page_no:06d}.json"


def page_pdf_path(paths: Dict[str, Path], page_no: int) -> Path:
    return paths["pages_pdf"] / f"page_{page_no:06d}.pdf"


def reset_outputs(paths: Dict[str, Path], resume: bool) -> None:
    if resume:
        for key in ("bundle", "pages_txt", "pages_meta", "pages_pdf"):
            paths[key].mkdir(parents=True, exist_ok=True)
        return

    if paths["bundle"].exists():
        shutil.rmtree(paths["bundle"])
    if paths["txt_out"].exists():
        paths["txt_out"].unlink()
    if paths["searchable_pdf"].exists():
        paths["searchable_pdf"].unlink()

    for key in ("bundle", "pages_txt", "pages_meta", "pages_pdf"):
        paths[key].mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Validation / prérequis
# ---------------------------------------------------------------------------


def parse_langs(lang_spec: str) -> List[str]:
    langs = [chunk.strip() for chunk in lang_spec.split("+") if chunk.strip()]
    if not langs:
        raise ValueError("Aucune langue Tesseract valide dans --lang")
    return langs


def check_tesseract_languages(lang_spec: str) -> None:
    if not shutil.which("tesseract"):
        die("Tesseract introuvable dans le PATH.")

    result = subprocess.run(
        ["tesseract", "--list-langs"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        die(f"Échec de tesseract --list-langs : {safe_error_text(result.stderr)}")

    installed: Set[str] = set()
    for line in (result.stdout + "\n" + result.stderr).splitlines():
        line = line.strip()
        if not line:
            continue
        if "language" in line.lower() and "list" in line.lower():
            continue
        parts = re.split(r"[\s,\n]+", line)
        for part in parts:
            part = part.strip()
            if part and re.match(r"^[a-z]{2,4}(_[A-Z]{2,4})?$", part):
                installed.add(part)

    missing = [lang for lang in parse_langs(lang_spec) if lang not in installed]
    if missing:
        die(
            "Langues Tesseract manquantes : "
            f"{', '.join(missing)}\n"
            f"Ubuntu/Debian : apt install {' '.join(f'tesseract-ocr-{x}' for x in missing)}"
        )


def check_pdf_support_if_needed(source: Path) -> None:
    need_pdf = source.is_file() and source.suffix.lower() in PDF_EXTENSIONS
    if not need_pdf:
        return
    try:
        import fitz  # noqa: F401
    except Exception as exc:
        die(f"Support PDF indisponible. Installez PyMuPDF (pymupdf). Détail : {exc}")


def check_source_file(source: Path, max_source_mb: int) -> None:
    """Validation approfondie du fichier source."""
    if not source.exists():
        die(f"Source introuvable : {source}")

    if not os.access(source, os.R_OK):
        die(f"Source non lisible (permissions) : {source}")

    if source.is_file():
        size_mb = source.stat().st_size / (1024 * 1024)
        if size_mb > max_source_mb:
            die(
                f"Source trop volumineuse : {size_mb:.1f} Mo "
                f"(limite : {max_source_mb} Mo). Ajustez avec --max-source-mb."
            )

    if source.is_file() and source.suffix.lower() in PDF_EXTENSIONS:
        try:
            import fitz
            with fitz.open(str(source)) as doc:
                if doc.page_count == 0:
                    die(f"Le PDF ne contient aucune page : {source}")
        except Exception as exc:
            die(f"Le PDF semble corrompu ou invalide : {source} — {exc}")


def validate_args(args: argparse.Namespace) -> None:
    source = Path(args.source)

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
    if args.min_chars < 0:
        die("--min-chars doit être >= 0")
    if args.retries < 0:
        die("--retries doit être >= 0")
    if args.max_source_mb <= 0:
        die("--max-source-mb doit être > 0")

    if source.is_file() and source.suffix.lower() not in (IMAGE_EXTENSIONS | PDF_EXTENSIONS):
        die(f"Extension non supportée : {source.suffix}")

    if source.is_dir():
        files = [p for p in source.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        if not files:
            die(f"Aucune image supportée trouvée dans : {source}")

    check_source_file(source, args.max_source_mb)
    check_tesseract_languages(args.lang)
    check_pdf_support_if_needed(source)


# ---------------------------------------------------------------------------
# État de reprise
# ---------------------------------------------------------------------------


def runtime_params() -> Set[str]:
    """Paramètres qui n'affectent PAS la compatibilité de l'état."""
    return {"workers", "timeout", "verbose", "resume", "out_dir", "suffix", "max_source_mb", "dedup"}


def resume_identity(args: argparse.Namespace) -> Dict[str, object]:
    return {
        "source": str(Path(args.source).resolve()),
        "dpi": args.dpi,
        "lang": args.lang,
        "psm": args.psm,
        "oem": args.oem,
        "pdf_mode": args.pdf_mode,
        "text_threshold": args.text_threshold,
        "no_preprocess": args.no_preprocess,
        "min_chars": args.min_chars,
        "retries": args.retries,
        "tsv_metrics": not args.no_tsv_metrics,
        "searchable_pdf": args.searchable_pdf,
        "start": args.start,
        "end": args.end,
    }


def load_state(path: Path) -> Dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        LOG.warning("Fichier d'état corrompu, reprise ignorée : %s", exc)
        return {}
    except Exception as exc:
        die(f"Fichier d'état illisible : {path} ({exc})")


def save_state(path: Path, state: Dict) -> None:
    state["updated_at"] = utc_now_iso()
    atomic_write_json(path, state)


def ensure_state_compatible(state: Dict, args: argparse.Namespace, paths: Dict[str, Path]) -> None:
    if not state:
        return
    if state.get("version") != STATE_VERSION:
        die(
            f"Version d'état incompatible (attendu v{STATE_VERSION}, obtenu v{state.get('version')}). "
            "Relancez sans --resume ou supprimez le bundle."
        )
    current_identity = resume_identity(args)
    saved_identity = state.get("identity", {})
    functional_keys = set(current_identity.keys()) - runtime_params()

    for key in functional_keys:
        if current_identity.get(key) != saved_identity.get(key):
            die(
                f"Le bundle existant ne correspond pas à la même configuration fonctionnelle. "
                f"Différence sur : {key} (bundle={saved_identity.get(key)!r}, "
                f"actuel={current_identity.get(key)!r}). Relancez sans --resume."
            )

    if state.get("output_txt") != str(paths["txt_out"].resolve()):
        die("Le bundle existant ne correspond pas à cette destination texte.")


def init_state(args: argparse.Namespace, paths: Dict[str, Path], pages: Sequence[PageRef]) -> Dict:
    return {
        "version": STATE_VERSION,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "identity": resume_identity(args),
        "output_txt": str(paths["txt_out"].resolve()),
        "output_searchable_pdf": str(paths["searchable_pdf"].resolve()) if args.searchable_pdf else None,
        "page_count": len(pages),
        "pages": {},
        "run_config": {
            "workers": args.workers,
            "timeout": args.timeout,
            "verbose": args.verbose,
        },
    }


def completed_pages_from_state(state: Dict, paths: Dict[str, Path], valid_page_nos: Set[int]) -> Set[int]:
    done: Set[int] = set()
    for key, meta in state.get("pages", {}).items():
        try:
            pno = int(key)
        except (ValueError, TypeError):
            continue
        if pno not in valid_page_nos:
            continue
        try:
            if (
                meta.get("status") == "done"
                and page_text_path(paths, pno).exists()
                and page_meta_path(paths, pno).exists()
            ):
                done.add(pno)
        except Exception:
            continue
    return done


# ---------------------------------------------------------------------------
# Pages source
# ---------------------------------------------------------------------------


def to_gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image.copy()
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def compute_perceptual_hash(image: np.ndarray) -> str:
    """Hash perceptuel simple (dHash) pour la dé-duplication."""
    resized = cv2.resize(image, (DEDUP_HASH_SIZE[0] + 1, DEDUP_HASH_SIZE[1]), interpolation=cv2.INTER_AREA)
    gray = to_gray(resized)
    diff = gray[:, 1:] > gray[:, :-1]
    return "".join("1" if val else "0" for row in diff for val in row)


def list_pages(source: Path, start: int, end: Optional[int], dedup: bool = False) -> List[PageRef]:
    if source.is_dir():
        files = sorted(
            [p for p in source.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS],
            key=lambda p: natural_key(p.name),
        )
        first = max(1, start)
        last = len(files) if end is None else min(len(files), end)
        if first > last:
            die(f"Intervalle vide : start={first}, end={last}, total={len(files)}")
        selected_files = files[first - 1:last]
        pages: List[PageRef] = []
        seen_hashes: Set[str] = set()
        for i, path in enumerate(selected_files, start=first):
            phash = None
            if dedup:
                img = read_image(str(path))
                phash = compute_perceptual_hash(img)
                if phash in seen_hashes:
                    LOG.debug("Page doublon détectée (hash=%s), ignorée : %s", phash[:16], path.name)
                    continue
                seen_hashes.add(phash)
            pages.append(PageRef(page_no=i, kind="image", source_path=str(path.resolve()), perceptual_hash=phash))
        return pages

    if source.suffix.lower() in IMAGE_EXTENSIONS:
        phash = None
        if dedup:
            img = read_image(str(source))
            phash = compute_perceptual_hash(img)
        return [PageRef(page_no=1, kind="image", source_path=str(source.resolve()), perceptual_hash=phash)]

    if source.suffix.lower() in PDF_EXTENSIONS:
        import fitz
        with fitz.open(str(source)) as doc:
            total = doc.page_count

        first = max(1, start)
        last = total if end is None else min(total, end)
        if first > last:
            die(f"Intervalle vide : start={first}, end={last}, total={total}")

        pages = []
        for pno in range(first, last + 1):
            pages.append(
                PageRef(
                    page_no=pno,
                    kind="pdf",
                    source_path=str(source.resolve()),
                    pdf_index=pno - 1,
                    perceptual_hash=None,
                )
            )
        return pages

    die(f"Type de source non supporté : {source}")
    return []


# ---------------------------------------------------------------------------
# Lecture / rendu source
# ---------------------------------------------------------------------------


def read_image(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Impossible de lire l'image : {path}")
    return img


def render_pdf_page(pdf_path: str, pdf_index: int, dpi: int) -> np.ndarray:
    """Rend une page PDF en image, en utilisant le cache worker."""
    import fitz
    doc = _get_cached_pdf_doc(pdf_path)
    page = doc[pdf_index]
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=matrix, alpha=False)

    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n).copy()
    if pix.n == 1:
        return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    if pix.n == 4:
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def extract_pdf_native_text(pdf_path: str, pdf_index: int) -> str:
    """Extrait le texte natif d'une page PDF, en utilisant le cache worker."""
    doc = _get_cached_pdf_doc(pdf_path)
    return doc[pdf_index].get_text("text").strip()


def is_empty_page(image: np.ndarray, threshold: float = EMPTY_PAGE_THRESHOLD) -> bool:
    """Détecte si une page est essentiellement vide (blanc/noir uniforme)."""
    gray = to_gray(image)
    unique, counts = np.unique(gray, return_counts=True)
    max_count = counts.max()
    total_pixels = gray.size
    return (max_count / total_pixels) > threshold


def meaningful_text(text: str, threshold: int) -> bool:
    return compact_len(text) >= threshold


# ---------------------------------------------------------------------------
# Prétraitement image
# ---------------------------------------------------------------------------


def estimate_skew_angle(gray: np.ndarray) -> float:
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _ret, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))
    if coords.shape[0] < 200:
        return 0.0

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    angle = float(angle)
    if abs(angle) < 0.2 or abs(angle) > 15:
        return 0.0
    return angle


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
    border_value = 255 if image.ndim == 2 else (255, 255, 255)
    return cv2.warpAffine(
        image,
        matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=border_value,
    )


def normalize_gray(gray: np.ndarray) -> np.ndarray:
    angle = estimate_skew_angle(gray)
    if angle:
        gray = rotate_image(gray, angle)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    normalized = clahe.apply(gray)
    denoised = cv2.fastNlMeansDenoising(normalized, h=7, templateWindowSize=7, searchWindowSize=21)
    return denoised


def preprocess_variant(image: np.ndarray, variant: str) -> np.ndarray:
    gray = to_gray(image)

    if variant == "raw-gray":
        return gray

    normalized = normalize_gray(gray)

    if variant == "gray":
        return normalized

    if variant == "adaptive":
        return cv2.adaptiveThreshold(
            normalized,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )

    if variant == "otsu":
        _ret, binary = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    raise ValueError(f"Variant de prétraitement inconnue : {variant}")


def build_attempt_plan(base_psm: int, no_preprocess: bool, retries: int) -> List[AttemptSpec]:
    candidates: List[AttemptSpec] = []

    if no_preprocess:
        raw = [AttemptSpec("raw-gray", base_psm)]
        if base_psm != 6:
            raw.append(AttemptSpec("raw-gray", 6))
        if base_psm != 11:
            raw.append(AttemptSpec("raw-gray", 11))
        candidates.extend(raw)
    else:
        candidates.extend([
            AttemptSpec("adaptive", base_psm),
            AttemptSpec("gray", base_psm),
            AttemptSpec("otsu", base_psm),
        ])
        if base_psm != 6:
            candidates.append(AttemptSpec("adaptive", 6))
        if base_psm != 11:
            candidates.append(AttemptSpec("gray", 11))

    deduped: List[AttemptSpec] = []
    seen = set()
    for item in candidates:
        key = (item.variant, item.psm)
        if key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped[: max(1, 1 + retries)]


# ---------------------------------------------------------------------------
# Tesseract
# ---------------------------------------------------------------------------


def tesseract_base_command(img_path: str, output_base: str, lang: str, psm: int, oem: int) -> List[str]:
    # NB: certains builds Tesseract ignorent tessedit-threads; pour compatibilité
    # maximale on limite plutôt via variables d'environnement dans run_command.
    return [
        "tesseract",
        img_path,
        output_base,
        "-l",
        lang,
        "--psm",
        str(psm),
        "--oem",
        str(oem),
        "-c",
        "preserve_interword_spaces=1",
    ]


def run_command(command: List[str], timeout: int) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.setdefault("OMP_THREAD_LIMIT", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        env=env,
    )


def run_tesseract_text(image: np.ndarray, lang: str, psm: int, oem: int, timeout: int) -> Tuple[str, Optional[str]]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        img_path = str(Path(tmp_dir) / "page.png")
        if not cv2.imwrite(img_path, image):
            raise RuntimeError("Échec d'écriture de l'image temporaire")

        try:
            result = run_command(tesseract_base_command(img_path, "stdout", lang, psm, oem), timeout)
        except subprocess.TimeoutExpired:
            return "[TIMEOUT ERROR]", f"Timeout Tesseract dépassé ({timeout}s)"

        if result.returncode != 0:
            err = safe_error_text(result.stderr)
            return f"[TESSERACT ERROR: {err}]", err

        return result.stdout.strip(), None


def parse_tsv_metrics(tsv_text: str) -> Tuple[Optional[float], int]:
    lines = [line for line in tsv_text.splitlines() if line.strip()]
    if len(lines) <= 1:
        return None, 0

    scores: List[float] = []
    word_count = 0
    reader = csv.DictReader(lines, delimiter="\t")
    for row in reader:
        text = (row.get("text") or "").strip()
        conf_raw = (row.get("conf") or "").strip()
        if text:
            word_count += 1
        if conf_raw and conf_raw not in {"-1", "nan"}:
            try:
                scores.append(float(conf_raw))
            except ValueError:
                pass

    if not scores:
        return None, word_count
    return round(sum(scores) / len(scores), 2), word_count


def collect_tsv_metrics(image: np.ndarray, lang: str, psm: int, oem: int, timeout: int) -> Tuple[Optional[float], int, Optional[str]]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        img_path = str(Path(tmp_dir) / "page.png")
        if not cv2.imwrite(img_path, image):
            return None, 0, "Échec d'écriture de l'image temporaire pour TSV"

        command = tesseract_base_command(img_path, "stdout", lang, psm, oem) + ["tsv"]
        try:
            result = run_command(command, timeout)
        except subprocess.TimeoutExpired:
            return None, 0, f"Timeout TSV dépassé ({timeout}s)"

        if result.returncode != 0:
            return None, 0, safe_error_text(result.stderr)

        mean_conf, words = parse_tsv_metrics(result.stdout)
        return mean_conf, words, None


def generate_searchable_page_pdf(image: np.ndarray, lang: str, psm: int, oem: int, timeout: int, dest_path: Path) -> Optional[str]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        img_path = str(Path(tmp_dir) / "page.png")
        out_base = str(Path(tmp_dir) / "page_ocr")

        if not cv2.imwrite(img_path, image):
            return "Échec d'écriture de l'image temporaire pour PDF"

        command = tesseract_base_command(img_path, out_base, lang, psm, oem) + ["pdf"]
        try:
            result = run_command(command, timeout)
        except subprocess.TimeoutExpired:
            return f"Timeout PDF Tesseract dépassé ({timeout}s)"

        if result.returncode != 0:
            return safe_error_text(result.stderr)

        produced = Path(out_base + ".pdf")
        if not produced.exists():
            return "Tesseract n'a pas produit le PDF attendu"

        atomic_write_bytes(dest_path, produced.read_bytes())
        return None


# ---------------------------------------------------------------------------
# Worker par page
# ---------------------------------------------------------------------------


def _build_meta(
    page: PageRef,
    method: str,
    text: str,
    error: Optional[str],
    confidence_mean: Optional[float],
    confidence_words: int,
    pdf_error: Optional[str],
    pdf_path: Optional[Path],
    attempts_meta: List[Dict[str, object]],
    selected_attempt: Optional[AttemptSpec],
    is_empty: bool,
    duration_ms: float,
) -> Dict[str, object]:
    return {
        "page_no": page.page_no,
        "status": "done",
        "source_kind": page.kind,
        "source_path": page.source_path,
        "pdf_index": page.pdf_index,
        "method": method,
        "chars": len(text),
        "non_ws_chars": compact_len(text),
        "attempt_count": len(attempts_meta),
        "attempts": attempts_meta,
        "selected_attempt": None if selected_attempt is None else {"variant": selected_attempt.variant, "psm": selected_attempt.psm},
        "confidence_mean": confidence_mean,
        "confidence_words": confidence_words,
        "error": error,
        "pdf_page_error": pdf_error,
        "searchable_pdf_page": str(pdf_path.resolve()) if pdf_path else None,
        "duration_ms": duration_ms,
        "is_empty_page": is_empty,
        "processed_at": utc_now_iso(),
    }


def process_page(task: Dict[str, object]) -> Dict[str, object]:
    """Traite une seule page. Appelé dans un worker ProcessPoolExecutor."""
    cv2.setNumThreads(1)

    page = PageRef(**task["page"])
    page_no = page.page_no
    started = time.perf_counter()

    lang = str(task["lang"])
    psm = int(task["psm"])
    oem = int(task["oem"])
    dpi = int(task["dpi"])
    timeout = int(task["timeout"])
    pdf_mode = str(task["pdf_mode"])
    no_preprocess = bool(task["no_preprocess"])
    text_threshold = int(task["text_threshold"])
    min_chars = int(task["min_chars"])
    retries = int(task["retries"])
    collect_conf = bool(task["collect_conf"])
    searchable_pdf = bool(task["searchable_pdf"])
    paths = {k: Path(v) for k, v in task["paths"].items()}

    text_path = page_text_path(paths, page_no)
    meta_path = page_meta_path(paths, page_no)
    pdf_path = page_pdf_path(paths, page_no)

    attempts_meta: List[Dict[str, object]] = []
    selected_attempt: Optional[AttemptSpec] = None
    selected_image: Optional[np.ndarray] = None
    selected_text = ""
    selected_error: Optional[str] = None
    method = "failed"
    confidence_mean: Optional[float] = None
    confidence_words = 0
    pdf_error: Optional[str] = None
    is_empty = False

    def finish(meta: Dict[str, object]) -> Dict[str, object]:
        atomic_write_json(meta_path, meta)
        return meta

    try:
        # === Étape 1 : Extraction texte natif PDF ===
        if page.kind == "pdf" and pdf_mode in {"auto", "text"}:
            try:
                native_text = extract_pdf_native_text(page.source_path, int(page.pdf_index))
            except Exception as exc:
                native_text = ""
                LOG.warning("Échec extraction texte natif page %d : %s", page_no, exc)

            if meaningful_text(native_text, text_threshold):
                method = "native-text"
                selected_text = native_text
                atomic_write_text(text_path, selected_text + "\n")
                duration_ms = round((time.perf_counter() - started) * 1000, 2)
                return finish(_build_meta(page, method, selected_text, None, None, 0, None, None,
                                          [], None, False, duration_ms))

            if pdf_mode == "text":
                selected_error = f"Aucun texte natif exploitable sur la page {page_no}"
                selected_text = f"[NO NATIVE TEXT page {page_no}]"
                method = "native-text"
                atomic_write_text(text_path, selected_text + "\n")
                duration_ms = round((time.perf_counter() - started) * 1000, 2)
                return finish(_build_meta(page, method, selected_text, selected_error, None, 0, None, None,
                                          [], None, False, duration_ms))

        # === Étape 2 : Rendu de l'image source ===
        if page.kind == "image":
            source_image = read_image(page.source_path)
        elif page.kind == "pdf":
            source_image = render_pdf_page(page.source_path, int(page.pdf_index), dpi)
        else:
            raise RuntimeError(f"Type de page inconnu : {page.kind}")

        # === Étape 3 : Détection de page vide ===
        is_empty = is_empty_page(source_image)
        if is_empty:
            selected_text = "[EMPTY PAGE]"
            method = "empty"
            atomic_write_text(text_path, selected_text + "\n")
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            return finish(_build_meta(page, method, selected_text, None, None, 0, None, None,
                                      [], None, True, duration_ms))

        # === Étape 4 : Tentatives OCR ===
        best_score = -1.0
        plan = build_attempt_plan(psm, no_preprocess, retries)

        for attempt in plan:
            try:
                processed = preprocess_variant(source_image, attempt.variant)
                text, err = run_tesseract_text(processed, lang, attempt.psm, oem, timeout)
            except Exception as exc:
                text = f"[OCR ERROR page {page_no}: {exc}]"
                err = str(exc)
                processed = None

            score = compact_len(text)

            attempt_conf: Optional[float] = None
            attempt_words: int = 0
            if collect_conf and processed is not None and err is None:
                attempt_conf, attempt_words, _conf_err = collect_tsv_metrics(processed, lang, attempt.psm, oem, timeout)

            attempts_meta.append({
                "variant": attempt.variant,
                "psm": attempt.psm,
                "chars": len(text),
                "non_ws_chars": score,
                "error": err,
                "confidence_mean": attempt_conf,
                "confidence_words": attempt_words,
            })

            combined_score = float(score)
            if attempt_conf is not None and attempt_conf > CONFIDENCE_THRESHOLD:
                combined_score = score + (attempt_conf * 10)

            if combined_score > best_score:
                best_score = combined_score
                selected_attempt = attempt
                selected_image = processed
                selected_text = text
                selected_error = err
                method = "ocr"
                confidence_mean = attempt_conf
                confidence_words = attempt_words

            if err is None and score >= min_chars and (attempt_conf is None or attempt_conf >= CONFIDENCE_THRESHOLD):
                selected_attempt = attempt
                selected_image = processed
                selected_text = text
                selected_error = None
                method = "ocr"
                confidence_mean = attempt_conf
                confidence_words = attempt_words
                break

        if selected_attempt is None or selected_image is None:
            raise RuntimeError("Aucune tentative OCR exploitable")

        # === Étape 5 : PDF searchable ===
        if searchable_pdf and method == "ocr":
            pdf_error = generate_searchable_page_pdf(selected_image, lang, selected_attempt.psm, oem, timeout, pdf_path)

        # === Étape 6 : Écriture des résultats ===
        atomic_write_text(text_path, selected_text + "\n")
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        return finish(_build_meta(
            page=page,
            method=method,
            text=selected_text,
            error=selected_error,
            confidence_mean=confidence_mean,
            confidence_words=confidence_words,
            pdf_error=pdf_error,
            pdf_path=pdf_path if pdf_path.exists() else None,
            attempts_meta=attempts_meta,
            selected_attempt=selected_attempt,
            is_empty=is_empty,
            duration_ms=duration_ms,
        ))

    except Exception as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        error = str(exc)
        tb = traceback.format_exc()
        fallback_text = f"[OCR ERROR page {page_no}: {error}]\n\n{tb}"
        atomic_write_text(text_path, fallback_text + "\n")
        meta = {
            "page_no": page_no,
            "status": "error",
            "source_kind": page.kind,
            "source_path": page.source_path,
            "pdf_index": page.pdf_index,
            "method": "failed",
            "chars": len(fallback_text),
            "non_ws_chars": compact_len(fallback_text),
            "attempt_count": len(attempts_meta),
            "attempts": attempts_meta,
            "selected_attempt": None,
            "confidence_mean": None,
            "confidence_words": 0,
            "error": error,
            "traceback": tb,
            "pdf_page_error": None,
            "searchable_pdf_page": None,
            "duration_ms": duration_ms,
            "is_empty_page": False,
            "processed_at": utc_now_iso(),
        }
        atomic_write_json(meta_path, meta)
        return meta


# ---------------------------------------------------------------------------
# Assemblage texte / PDF / rapports
# ---------------------------------------------------------------------------


def assemble_text_output(paths: Dict[str, Path], pages: Sequence[PageRef]) -> None:
    blocks: List[str] = []
    for page in pages:
        part = page_text_path(paths, page.page_no)
        if part.exists():
            text = part.read_text(encoding="utf-8", errors="replace").rstrip()
        else:
            text = f"[MISSING PAGE {page.page_no}]"
        blocks.append(f"{SEPARATOR}\nPAGE {page.page_no}\n{SEPARATOR}\n{text}")
    atomic_write_text(paths["txt_out"], "\n\n".join(blocks) + "\n")


def append_image_as_pdf_page(doc, image_path: str) -> None:
    import fitz
    rect = fitz.Rect(0, 0, 595, 842)
    try:
        pix = fitz.Pixmap(image_path)
        rect = fitz.Rect(0, 0, pix.width, pix.height)
    except Exception:
        pass

    page = doc.new_page(width=rect.width, height=rect.height)
    page.insert_image(rect, filename=image_path)


def assemble_searchable_pdf(paths: Dict[str, Path], pages: Sequence[PageRef]) -> None:
    import fitz
    out_doc = fitz.open()
    source_pdf_doc = None

    try:
        if pages and pages[0].kind == "pdf":
            source_pdf_doc = fitz.open(pages[0].source_path)

        for page in pages:
            meta_file = page_meta_path(paths, page.page_no)
            meta = {}
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                except Exception:
                    meta = {}

            method = meta.get("method")
            page_pdf = page_pdf_path(paths, page.page_no)

            if method == "native-text" and source_pdf_doc is not None and page.pdf_index is not None:
                out_doc.insert_pdf(source_pdf_doc, from_page=page.pdf_index, to_page=page.pdf_index)
                continue

            if page_pdf.exists():
                try:
                    with fitz.open(str(page_pdf)) as tmp_doc:
                        out_doc.insert_pdf(tmp_doc)
                except Exception:
                    append_image_as_pdf_page(out_doc, str(page_pdf))
                continue

            if page.kind == "pdf" and source_pdf_doc is not None and page.pdf_index is not None:
                out_doc.insert_pdf(source_pdf_doc, from_page=page.pdf_index, to_page=page.pdf_index)
            elif page.kind == "image":
                append_image_as_pdf_page(out_doc, page.source_path)

        out_doc.save(str(paths["searchable_pdf"]), garbage=3, deflate=True)
    finally:
        if source_pdf_doc is not None:
            source_pdf_doc.close()
        out_doc.close()


def generate_reports(paths: Dict[str, Path], pages: Sequence[PageRef], state: Dict, args: argparse.Namespace) -> None:
    rows: List[Dict[str, object]] = []
    method_counts: Dict[str, int] = {}
    total_chars = 0
    error_count = 0
    total_duration_ms = 0.0
    confidence_values: List[float] = []

    for page in pages:
        meta_file = page_meta_path(paths, page.page_no)
        if not meta_file.exists():
            rows.append({
                "page_no": page.page_no,
                "status": "missing",
                "method": None,
                "chars": 0,
                "non_ws_chars": 0,
                "duration_ms": 0,
                "confidence_mean": None,
                "confidence_words": 0,
                "attempt_count": 0,
                "error": "missing meta",
                "searchable_pdf_page": None,
                "source_kind": page.kind,
                "source_path": page.source_path,
                "pdf_index": page.pdf_index,
                "is_empty_page": False,
            })
            error_count += 1
            continue

        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            rows.append({
                "page_no": page.page_no,
                "status": "missing",
                "method": None,
                "chars": 0,
                "non_ws_chars": 0,
                "duration_ms": 0,
                "confidence_mean": None,
                "confidence_words": 0,
                "attempt_count": 0,
                "error": "corrupted meta",
                "searchable_pdf_page": None,
                "source_kind": page.kind,
                "source_path": page.source_path,
                "pdf_index": page.pdf_index,
                "is_empty_page": False,
            })
            error_count += 1
            continue

        rows.append({
            "page_no": meta.get("page_no"),
            "status": meta.get("status"),
            "method": meta.get("method"),
            "chars": meta.get("chars"),
            "non_ws_chars": meta.get("non_ws_chars"),
            "duration_ms": meta.get("duration_ms"),
            "confidence_mean": meta.get("confidence_mean"),
            "confidence_words": meta.get("confidence_words"),
            "attempt_count": meta.get("attempt_count"),
            "error": meta.get("error"),
            "searchable_pdf_page": meta.get("searchable_pdf_page"),
            "source_kind": meta.get("source_kind"),
            "source_path": meta.get("source_path"),
            "pdf_index": meta.get("pdf_index"),
            "is_empty_page": meta.get("is_empty_page", False),
        })

        method = str(meta.get("method"))
        method_counts[method] = method_counts.get(method, 0) + 1
        total_chars += int(meta.get("chars") or 0)
        total_duration_ms += float(meta.get("duration_ms") or 0.0)
        if meta.get("error"):
            error_count += 1
        if meta.get("confidence_mean") is not None:
            try:
                confidence_values.append(float(meta["confidence_mean"]))
            except Exception:
                pass

    fieldnames = [
        "page_no", "status", "method", "chars", "non_ws_chars", "duration_ms",
        "confidence_mean", "confidence_words", "attempt_count", "error",
        "searchable_pdf_page", "source_kind", "source_path", "pdf_index", "is_empty_page",
    ]
    paths["pages_csv"].parent.mkdir(parents=True, exist_ok=True)
    with paths["pages_csv"].open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    avg_confidence = None
    if confidence_values:
        avg_confidence = round(sum(confidence_values) / len(confidence_values), 2)

    quality_warning = None
    low_conf_pages = sum(1 for v in confidence_values if v < CONFIDENCE_THRESHOLD)
    if confidence_values and low_conf_pages / len(confidence_values) > 0.3:
        quality_warning = (
            f"ATTENTION: {low_conf_pages}/{len(confidence_values)} pages "
            f"ont une confiance moyenne < {CONFIDENCE_THRESHOLD}"
        )

    summary = {
        "generated_at": utc_now_iso(),
        "source": str(Path(args.source).resolve()),
        "text_output": str(paths["txt_out"].resolve()),
        "searchable_pdf_output": str(paths["searchable_pdf"].resolve()) if args.searchable_pdf else None,
        "page_count": len(pages),
        "method_counts": method_counts,
        "error_pages": error_count,
        "total_chars": total_chars,
        "avg_confidence_mean": avg_confidence,
        "total_duration_ms": round(total_duration_ms, 2),
        "quality_warning": quality_warning,
        "bundle": str(paths["bundle"].resolve()),
        "csv_report": str(paths["pages_csv"].resolve()),
        "state_file": str(paths["state"].resolve()),
        "config": {
            "dpi": args.dpi,
            "lang": args.lang,
            "psm": args.psm,
            "oem": args.oem,
            "workers": args.workers,
            "timeout": args.timeout,
            "pdf_mode": args.pdf_mode,
            "text_threshold": args.text_threshold,
            "no_preprocess": args.no_preprocess,
            "min_chars": args.min_chars,
            "retries": args.retries,
            "searchable_pdf": args.searchable_pdf,
            "tsv_metrics": not args.no_tsv_metrics,
            "max_source_mb": args.max_source_mb,
            "dedup": args.dedup,
        },
        "state_snapshot": state,
    }
    atomic_write_json(paths["summary"], summary)


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------


def ocr_pipeline(args: argparse.Namespace, paths: Dict[str, Path]) -> str:
    source = Path(args.source)
    pages = list_pages(source, args.start, args.end, dedup=args.dedup)
    valid_page_nos = {p.page_no for p in pages}

    state = load_state(paths["state"]) if args.resume else {}
    if state:
        ensure_state_compatible(state, args, paths)
    else:
        state = init_state(args, paths, pages)
        save_state(paths["state"], state)

    done_pages = completed_pages_from_state(state, paths, valid_page_nos)
    pages_to_do = [p for p in pages if p.page_no not in done_pages]

    if done_pages:
        LOG.info("Mode reprise — %d page(s) déjà finalisées", len(done_pages))

    if not pages_to_do:
        LOG.info("Toutes les pages demandées sont déjà traitées.")
        assemble_text_output(paths, pages)
        if args.searchable_pdf:
            assemble_searchable_pdf(paths, pages)
        generate_reports(paths, pages, state, args)
        return str(paths["txt_out"])

    worker_count = min(args.workers, len(pages_to_do))
    LOG.info(
        "%d page(s) à traiter (workers=%d, dpi=%d, psm=%d, oem=%d, pdf_mode=%s, "
        "preprocess=%s, retries=%d, dedup=%s)",
        len(pages_to_do), worker_count, args.dpi, args.psm, args.oem, args.pdf_mode,
        not args.no_preprocess, args.retries, args.dedup,
    )

    base_task = {
        "lang": args.lang,
        "psm": args.psm,
        "oem": args.oem,
        "dpi": args.dpi,
        "timeout": args.timeout,
        "pdf_mode": args.pdf_mode,
        "no_preprocess": args.no_preprocess,
        "text_threshold": args.text_threshold,
        "min_chars": args.min_chars,
        "retries": args.retries,
        "collect_conf": not args.no_tsv_metrics,
        "searchable_pdf": args.searchable_pdf,
        "paths": {k: str(v) for k, v in paths.items()},
    }

    tasks: List[Dict[str, object]] = []
    for page in pages_to_do:
        task = dict(base_task)
        task["page"] = {
            "page_no": page.page_no,
            "kind": page.kind,
            "source_path": page.source_path,
            "pdf_index": page.pdf_index,
        }
        tasks.append(task)

    total = len(tasks)
    completed = 0

    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        future_map = {executor.submit(process_page, task): task["page"]["page_no"] for task in tasks}

        for future in as_completed(future_map):
            page_no = future_map[future]
            try:
                meta = future.result()
            except Exception as exc:
                error = f"Crash worker: {exc}"
                tb = traceback.format_exc()
                fallback_text = f"[OCR ERROR page {page_no}: {error}]\n\n{tb}"
                atomic_write_text(page_text_path(paths, page_no), fallback_text + "\n")
                meta = {
                    "page_no": page_no,
                    "status": "error",
                    "source_kind": None,
                    "source_path": None,
                    "pdf_index": None,
                    "method": "failed",
                    "chars": len(fallback_text),
                    "non_ws_chars": compact_len(fallback_text),
                    "attempt_count": 0,
                    "attempts": [],
                    "selected_attempt": None,
                    "confidence_mean": None,
                    "confidence_words": 0,
                    "error": error,
                    "traceback": tb,
                    "pdf_page_error": None,
                    "searchable_pdf_page": None,
                    "duration_ms": 0.0,
                    "is_empty_page": False,
                    "processed_at": utc_now_iso(),
                }
                atomic_write_json(page_meta_path(paths, page_no), meta)

            state["pages"][str(page_no)] = {
                "status": meta.get("status"),
                "method": meta.get("method"),
                "chars": meta.get("chars"),
                "error": meta.get("error"),
                "duration_ms": meta.get("duration_ms"),
                "processed_at": meta.get("processed_at"),
            }
            save_state(paths["state"], state)

            completed += 1
            error_mark = " ⚠️ ERREUR" if meta.get("error") or meta.get("pdf_page_error") else ""
            LOG.info(
                "Page %d traitée [%d/%d] — %s — %d chars%s",
                page_no, completed, total, meta.get("method"), int(meta.get("chars") or 0), error_mark,
            )

    assemble_text_output(paths, pages)
    if args.searchable_pdf:
        LOG.info("Assemblage du PDF searchable…")
        assemble_searchable_pdf(paths, pages)

    state["assembled_at"] = utc_now_iso()
    save_state(paths["state"], state)
    generate_reports(paths, pages, state, args)

    total_chars = sum(
        len(page_text_path(paths, p.page_no).read_text(encoding="utf-8", errors="replace"))
        for p in pages
        if page_text_path(paths, p.page_no).exists()
    )
    LOG.info("OCR terminé → %s (%d chars)", paths["txt_out"], total_chars)
    if args.searchable_pdf:
        LOG.info("PDF searchable → %s", paths["searchable_pdf"])
    LOG.info("Bundle de run → %s", paths["bundle"])

    return str(paths["txt_out"])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="OCR orienté production — PDF, images, dossiers")
    ap.add_argument("source", help="PDF, image ou dossier d'images")
    ap.add_argument("--dpi", type=int, default=300, help="Résolution de rendu PDF (défaut: 300)")
    ap.add_argument("--start", type=int, default=1, help="Première page PDF (défaut: 1)")
    ap.add_argument("--end", type=int, default=None, help="Dernière page PDF (défaut: fin document)")
    ap.add_argument("--timeout", type=int, default=120, help="Timeout Tesseract par page (s)")
    ap.add_argument("--psm", type=int, default=3, help="Page Segmentation Mode Tesseract")
    ap.add_argument("--oem", type=int, default=1, help="OCR Engine Mode Tesseract")
    ap.add_argument(
        "--workers",
        type=int,
        default=max(1, (os.cpu_count() or 2) // 2),
        help="Nombre de workers parallèles",
    )
    ap.add_argument("--resume", action="store_true", help="Reprendre une run interrompue")
    ap.add_argument("--out-dir", default=None, help="Dossier de sortie")
    ap.add_argument("--suffix", default=".ocr.txt", help="Suffixe de la sortie texte")
    ap.add_argument("--lang", default="ara+fra", help="Langues Tesseract (défaut: ara+fra)")
    ap.add_argument(
        "--pdf-mode",
        choices=["auto", "ocr", "text"],
        default="auto",
        help="PDF: auto=texte natif si exploitable sinon OCR ; ocr=OCR forcé ; text=texte natif seul",
    )
    ap.add_argument(
        "--text-threshold",
        type=int,
        default=25,
        help="Seuil minimal de caractères non blancs pour accepter le texte natif PDF",
    )
    ap.add_argument("--no-preprocess", action="store_true", help="Désactive le prétraitement image")
    ap.add_argument(
        "--min-chars",
        type=int,
        default=10,
        help="Seuil minimal de caractères non blancs pour accepter une tentative OCR",
    )
    ap.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Nombre de tentatives supplémentaires avec variantes de prétraitement / PSM",
    )
    ap.add_argument(
        "--no-tsv-metrics",
        action="store_true",
        help="Désactive la collecte de métriques TSV (confiance moyenne, nombre de mots)",
    )
    ap.add_argument(
        "--searchable-pdf",
        action="store_true",
        help="Produit un PDF searchable final quand possible",
    )
    ap.add_argument(
        "--max-source-mb",
        type=int,
        default=MAX_SOURCE_MB,
        help=f"Taille max du fichier source en Mo (défaut: {MAX_SOURCE_MB})",
    )
    ap.add_argument("--dedup", action="store_true", help="Active la dé-duplication des pages images")
    ap.add_argument("--verbose", action="store_true", help="Logs verbeux")
    return ap


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    configure_logging(None, verbose=args.verbose)
    validate_args(args)
    paths = compute_paths(Path(args.source), args.out_dir, args.suffix)
    reset_outputs(paths, args.resume)
    configure_logging(paths["run_log"], verbose=args.verbose)

    # Déjà vérifié dans validate_args; on re-vérifie après installation des handlers fichier.
    check_tesseract_languages(args.lang)
    check_pdf_support_if_needed(Path(args.source))

    try:
        ocr_pipeline(args, paths)
    except KeyboardInterrupt:
        die("Interruption utilisateur.", code=130)
    finally:
        _close_worker_pdf_cache()


if __name__ == "__main__":
    main()
