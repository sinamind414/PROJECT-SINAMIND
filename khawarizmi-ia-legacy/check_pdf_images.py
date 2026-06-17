import fitz
from pathlib import Path

pdf_path = Path("LIVRES SCOLAIRES/ANALES SCIENCES/ANALES SCIENCE DEATILLE/Ahmed amin khelifa version 2 parte 1.pdf")
doc = fitz.open(pdf_path)

print(f"Total pages: {len(doc)}")
for i in range(min(5, len(doc))):
    page = doc.load_page(i)
    images = page.get_images(full=True)
    print(f"Page {i+1}: {len(images)} images")
    if images:
        print(f"  Image info: {images[0]}")
