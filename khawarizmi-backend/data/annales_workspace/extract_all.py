#!/usr/bin/env python3
"""Extract all images and page JPGs from SVT PDFs."""
import fitz, json, sys, time
from pathlib import Path

BASE = Path("/home/user/ANNALES_SVT")
OUT = Path("/home/user/EXTRACTION")
OUT.mkdir(exist_ok=True)

log = OUT / "log.txt"
summary = {}

pdfs = sorted(BASE.rglob("*.pdf"))
total = len(pdfs)
t0 = time.time()

for idx, pdf in enumerate(pdfs):
    col = pdf.parent.name
    vol = pdf.stem
    label = f"{col}/{pdf.name}"
    
    out_img = OUT / col / vol / "images"
    out_pg = OUT / col / vol / "pages_jpg"
    out_img.mkdir(parents=True, exist_ok=True)
    out_pg.mkdir(parents=True, exist_ok=True)
    
    doc = fitz.open(str(pdf))
    nb = doc.page_count
    imgs = 0
    for pn in range(nb):
        page = doc[pn]
        for ii, img in enumerate(page.get_images(full=True)):
            base = doc.extract_image(img[0])
            (out_img / f"p{pn+1:03d}_i{ii:02d}.{base['ext']}").write_bytes(base["image"])
            imgs += 1
        pix = page.get_pixmap(dpi=120)
        pix.save(str(out_pg / f"page_{pn+1:03d}.jpg"))
    doc.close()
    
    summary[vol] = {"collection": col, "pages": nb, "images": imgs}
    msg = f"[{idx+1}/{total}] {label}  → {nb}p, {imgs} img  ({time.time()-t0:.0f}s)"
    print(msg)
    log.write_text(msg + "\n", encoding="utf-8")

# Résumé
summary_file = OUT / "resume.json"
summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

total_pages = sum(v["pages"] for v in summary.values())
total_images = sum(v["images"] for v in summary.values())
final = f"\n✅ Terminé ! {total} PDF, {total_pages} pages, {total_images} images en {time.time()-t0:.0f}s"
print(final)
log.write_text(log.read_text() + final + "\n", encoding="utf-8")
