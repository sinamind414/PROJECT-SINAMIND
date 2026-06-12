# -*- coding: utf-8 -*-
import fitz
from pathlib import Path

pdf_path = Path("LIVRES SCOLAIRES/LIVRE SCOLAIRE SCIENCE BAC/livre_scolaire_3as_sciences_se.pdf")
doc = fitz.open(pdf_path)

output_dir = Path("temp_intro")
output_dir.mkdir(exist_ok=True)

# Render first 10 pages
for i in range(10):
    page = doc.load_page(i)
    pix = page.get_pixmap(dpi=100)
    output_path = output_dir / f"page_{i+1}.jpg"
    pix.save(output_path)
    print(f"Saved {output_path}")
