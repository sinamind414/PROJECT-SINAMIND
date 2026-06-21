# Generate gpu_batch_ocr.py
content = '''#!/usr/bin/env python3
"""GPU Batch OCR — EasyOCR + RTX 3060"""

from __future__ import annotations
import argparse, json, logging, os, re, sys, tempfile, time, traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Set, Tuple

import cv2
import numpy as np

PDF_DIR = Path(r"C:\\Users\\zakaria\\Documents\\projet khawarizmi A\\LIVRES SCOLAIRES\\ANALES SCIENCES\\LIVRES ANNALES SVT BAC\\DOSSIER ANNALES KHELIFA")
OUTPUT_BASE = Path(r"C:\\Users\\zakaria\\Documents\\PROJET KHAWARIZMI IA\\khawarizmi-backend\\data\\ocr_gpu_output")
MAX_DIM = 1600
SEP = "=" * 70

LOG = logging.getLogger("gpu_batch_ocr")


@dataclass
class VolInfo:
    name: str
    pdf_path: Path
    category: str
    size_mb: float = 0.0
    page_count: int = 0


@dataclass
class PageRes:
    page_no: int
    text: str
    char_count: int = 0
    confidence: float = 0.0
    word_count: int = 0
    duration_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class VolRes:
    volume: str
    total_pages: int = 0
    pages_done: int = 0
    errors: int = 0
    total_chars: int = 0
    avg_confidence: float = 0.0
    total_duration_s: float = 0.0
    output_txt: Optional[str] = None
    status: str = "pending"


def setup_logging(verbose: bool = False) -> None:
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers.clear()
    LOG.propagate = False
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.DEBUG if verbose else logging.INFO)
    h.setFormatter(fmt)
    LOG.addHandler(h)
    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(OUTPUT_BASE / "batch_run.log", encoding="utf-8", mode="a")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    LOG.addHandler(fh)


def discover(pdf_dir: Path) -> List[VolInfo]:
    vols = []
    for cat_dir in sorted(pdf_dir.iterdir()):
        if not cat_dir.is_dir():
            continue
        for sub in cat_dir.iterdir():
            if not sub.is_dir():
                continue
            for pdf in sorted(sub.glob("*.pdf")):
                cat = "FINALBAC" if "FINAL" in pdf.stem.upper() else "KHELIFA1"
                vols.append(VolInfo(name=pdf.stem, pdf_path=pdf, category=cat, size_mb=round(pdf.stat().st_size / 1e6, 1)))
    return vols


_reader = None


def get_reader():
    global _reader
    if _reader is None:
        import easyocr

        LOG.info("Initialisation EasyOCR GPU (ar+en)...")
        _reader = easyocr.Reader(["ar", "en"], gpu=True, verbose=False)
        LOG.info("EasyOCR GPU OK.")
    return _reader


def ocr_page(img: np.ndarray) -> Tuple[str, float, int]:
    h, w = img.shape[:2]
    if max(h, w) > MAX_DIM:
        s = MAX_DIM / max(h, w)
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    res = get_reader().readtext(img, paragraph=False, width_ths=0.7)
    parts = [t.strip() for _, t, c in res if t.strip()]
    confs = [float(c) for _, _, c in res]
    avg = round(sum(confs) / len(confs), 2) if confs else 0.0
    return "\\n".join(parts), avg, len(parts)


def proc_vol(vol: VolInfo, dpi: int, out_dir: Path, resume: bool) -> VolRes:
    import fitz

    res = VolRes(volume=vol.name)
    vd = out_dir / vol.name
    vd.mkdir(parents=True, exist_ok=True)
    txt_p = out_dir / f"{vol.name}.ocr.txt"
    st_p = vd / "state.json"
    done: Set[int] = set()
    if resume and st_p.exists():
        try:
            s = json.loads(st_p.read_text("utf-8"))
            done = set(s.get("done_pages", []))
            res.pages_done = len(done)
            res.total_chars = s.get("total_chars", 0)
        except Exception:
            done = set()

    doc = fitz.open(str(vol.pdf_path))
    page_count = doc.page_count
    doc.close()
    res.total_pages = page_count
    todo = [i for i in range(page_count) if i not in done]
    if not todo:
        res.status = "already_done"
        res.output_txt = str(txt_p)
        return res

    LOG.info("[START] %s - %d pages (%d reste)", vol.name, page_count, len(todo))
    pg_res: List[Tuple[int, PageRes]] = []
    tot_dur = 0.0
    confs = []

    for idx, pi in enumerate(todo):
        pn = pi + 1
        st = time.perf_counter()
        try:
            doc = fitz.open(str(vol.pdf_path))
            pg = doc[pi]
            z = dpi / 72.0
            pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
            doc.close()
            a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n).copy()
            if pix.n == 1:
                a = np.stack([a] * 3, axis=-1)
            elif pix.n == 4:
                a = cv2.cvtColor(a, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                a = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)

            gray = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
            uniq, cnt = np.unique(gray, return_counts=True)
            empty = (cnt.max() / gray.size) > 0.98

            if empty:
                pr = PageRes(pn, "[VIDE]", confidence=0.0)
                LOG.info("  P %d/%d - VIDE", pn, page_count)
            else:
                txt, cf, wc = ocr_page(a)
                dms = round((time.perf_counter() - st) * 1000, 1)
                pr = PageRes(pn, txt, confidence=cf, word_count=wc, duration_ms=dms)
                LOG.info("  P %d/%d - %d chars, conf=%.1f, %.1fs", pn, page_count, len(txt), cf, dms / 1000)
                confs.append(cf)

            pg_res.append((pi, pr))
            done.add(pi)
            res.pages_done += 1
            res.total_chars += pr.char_count
            tot_dur += pr.duration_ms / 1000
        except Exception as e:
            dms = round((time.perf_counter() - st) * 1000, 1)
            pg_res.append((pi, PageRes(pn, f"[ERR: {e}]", error=str(e), duration_ms=dms)))
            res.errors += 1
            LOG.error("  P %d/%d - ERR: %s", pn, page_count, e)

        if len(done) % 5 == 0:
            _save_state(st_p, done, res.total_chars)

    pg_res.sort(key=lambda x: x[0])
    blks = []
    for _, pr in pg_res:
        blks.append(f"{SEP}\\nPAGE {pr.page_no}\\n{SEP}\\n{pr.text}")

    def sk(b):
        m = re.search(r"PAGE (\\d+)", b)
        return int(m.group(1)) if m else 0

    blks.sort(key=sk)

    tmp = tempfile.NamedTemporaryFile("w", delete=False, dir=str(out_dir), encoding="utf-8")
    tmp.write("\\n\\n".join(blks) + "\\n")
    tmp.close()
    os.replace(tmp.name, txt_p)

    pd = vd / "pages"
    pd.mkdir(exist_ok=True)
    for _, pr in pg_res:
        (pd / f"page_{pr.page_no:06d}.txt").write_text(pr.text, encoding="utf-8")

    _save_state(st_p, done, res.total_chars)

    res.avg_confidence = round(sum(confs) / len(confs), 2) if confs else 0.0
    res.total_duration_s = round(tot_dur, 2)
    res.output_txt = str(txt_p)
    res.status = "done"
    LOG.info("[DONE] %s - %d chars, conf=%.1f, %.1fs", vol.name, res.total_chars, res.avg_confidence, res.total_duration_s)
    return res


def _save_state(path: Path, done: Set[int], total_chars: int) -> None:
    json.dump(
        {"done_pages": sorted(done), "total_chars": total_chars, "updated_at": datetime.now(timezone.utc).isoformat()},
        open(path, "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="GPU Batch OCR - RTX 3060")
    p.add_argument("--dpi", type=int, default=200)
    p.add_argument("--cat", default=None)
    p.add_argument("--vol", default=None)
    p.add_argument("--max", type=int, default=None)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    setup_logging(args.verbose)

    pdf_dir = PDF_DIR
    vols = discover(pdf_dir)
    LOG.info("Volumes: %d", len(vols))

    if args.cat:
        vols = [v for v in vols if v.category.lower() == args.cat.lower()]
    if args.vol:
        vols = [v for v in vols if args.vol.lower() in v.name.lower()]
    if args.max:
        vols = vols[: args.max]

    import fitz

    tot_pages = 0
    for v in vols:
        d = fitz.open(str(v.pdf_path))
        v.page_count = d.page_count
        d.close()
        tot_pages += v.page_count
        LOG.info("  %s - %d p, %.1f MB", v.name, v.page_count, v.size_mb)

    LOG.info("%s\\nBATCH GPU: %d vols, %d pages | DPI=%d\\n%s", SEP, len(vols), tot_pages, args.dpi, SEP)

    all_res: List[VolRes] = []
    bt = time.perf_counter()

    for i, v in enumerate(vols, 1):
        LOG.info("--- %d/%d: %s ---", i, len(vols), v.name)
        try:
            all_res.append(proc_vol(v, args.dpi, OUTPUT_BASE, args.resume))
        except Exception as e:
            LOG.error("FAIL %s: %s", v.name, e)
            all_res.append(VolRes(volume=v.name, status="failed", errors=1))

    bd = time.perf_counter() - bt

    LOG.info("%s\\nRESUME BATCH\\n%s", SEP, SEP)
    tc = te = td = 0
    for r in all_res:
        ic = "OK" if r.status == "done" else ("SKIP" if r.status == "already_done" else "FAIL")
        LOG.info("  [%s] %s - %d/%d p, %d chars, conf=%.1f", ic, r.volume, r.pages_done, r.total_pages, r.total_chars, r.avg_confidence)
        tc += r.total_chars
        te += r.errors
        td += r.pages_done

    LOG.info("Total: %d pages, %d chars, %d err | %.1fs (%.1f min) | %.1f p/min", td, tc, te, bd, bd / 60, td / (bd / 60) if bd > 0 else 0)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "volumes": len(all_res),
        "total_pages": tot_pages,
        "pages_done": td,
        "total_chars": tc,
        "total_errors": te,
        "batch_duration_s": round(bd, 2),
        "dpi": args.dpi,
        "results": [
            {
                "volume": r.volume,
                "status": r.status,
                "total_pages": r.total_pages,
                "pages_done": r.pages_done,
                "total_chars": r.total_chars,
                "avg_confidence": r.avg_confidence,
                "errors": r.errors,
                "duration_s": r.total_duration_s,
                "output_txt": r.output_txt,
            }
            for r in all_res
        ],
    }
    json.dump(summary, open(OUTPUT_BASE / "batch_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    LOG.info("Termine.")


if __name__ == "__main__":
    main()
'''

with open(r'C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-backend\scripts\gpu_batch_ocr.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Script created:', len(content), 'bytes')
