import fitz  # PyMuPDF
import cv2
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class ZoneType(Enum):
    TEXT = "text"
    FIGURE = "figure"
    TABLE = "table"


@dataclass
class Zone:
    zone_type: ZoneType
    bbox: tuple  # (x0, y0, x1, y1) en pixels
    page_num: int
    image: np.ndarray = field(repr=False)


class PageSegmenter:
    """
    Segmente une page scannée en zones de texte et zones de figures
    en utilisant uniquement OpenCV (traitement local, aucun appel API).
    """

    def __init__(self, min_area_ratio=0.005, text_density_range=(0.15, 0.85)):
        self.min_area_ratio = min_area_ratio
        self.text_density_range = text_density_range

    def page_to_image(self, pdf_path: str, page_num: int, dpi: int = 200) -> np.ndarray:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        doc.close()
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif pix.n == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        return img

    def segment_page(self, img: np.ndarray, page_num: int) -> list[Zone]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        page_area = gray.shape[0] * gray.shape[1]

        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, blockSize=15, C=10
        )

        # Un noyau plus petit pour ne pas fusionner les lignes de texte entre elles
        kernel_figure = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        dilated_figure = cv2.dilate(binary, kernel_figure, iterations=1)

        contours_figure, _ = cv2.findContours(
            dilated_figure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        zones = []
        figure_mask = np.zeros(gray.shape, dtype=np.uint8)

        for contour in contours_figure:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            area_ratio = area / page_area

            if area_ratio < self.min_area_ratio:
                continue

            roi = binary[y:y+h, x:x+w]
            density = np.count_nonzero(roi) / area

            zone_type = self._classify_zone(w, h, density, area_ratio)

            if zone_type in (ZoneType.FIGURE, ZoneType.TABLE):
                margin = 10
                x0 = max(0, x - margin)
                y0 = max(0, y - margin)
                x1 = min(img.shape[1], x + w + margin)
                y1 = min(img.shape[0], y + h + margin)

                zones.append(Zone(
                    zone_type=zone_type,
                    bbox=(x0, y0, x1, y1),
                    page_num=page_num,
                    image=img[y0:y1, x0:x1].copy()
                ))
                cv2.rectangle(figure_mask, (x0, y0), (x1, y1), 255, -1)

        text_binary = cv2.bitwise_and(binary, cv2.bitwise_not(figure_mask))

        kernel_text = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 8))
        dilated_text = cv2.dilate(text_binary, kernel_text, iterations=3)

        contours_text, _ = cv2.findContours(
            dilated_text, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours_text:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            # Pour les zones de texte, le ratio minimal doit être beaucoup plus bas
            # car une ligne de texte seule est très petite
            if area / page_area < 0.0005:
                continue
            
            # Additional check to ensure we don't grab tiny specks of noise
            if w < 20 or h < 10:
                continue

            margin = 5
            x0 = max(0, x - margin)
            y0 = max(0, y - margin)
            x1 = min(img.shape[1], x + w + margin)
            y1 = min(img.shape[0], y + h + margin)

            zones.append(Zone(
                zone_type=ZoneType.TEXT,
                bbox=(x0, y0, x1, y1),
                page_num=page_num,
                image=img[y0:y1, x0:x1].copy()
            ))

        zones.sort(key=lambda z: z.bbox[1])
        return zones

    def _classify_zone(
        self, w: int, h: int, density: float, area_ratio: float
    ) -> ZoneType:
        aspect_ratio = w / max(h, 1)

        # Les tableaux ont souvent beaucoup d'espace vide (densité faible)
        if 0.5 < aspect_ratio < 4.0 and density < 0.18 and area_ratio > 0.02:
            return ZoneType.TABLE

        # Les figures (images, schémas denses) ont des densités anormales
        if density < self.text_density_range[0] or density > self.text_density_range[1]:
            if area_ratio > 0.02:
                return ZoneType.FIGURE

        return ZoneType.TEXT


def process_pdf_segmentation(pdf_path: str, output_dir: str, start_page: int = 0, end_page: int = None, dpi: int = 200):
    segmenter = PageSegmenter()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "figures").mkdir(exist_ok=True)
    (output_path / "text_zones").mkdir(exist_ok=True)

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()

    if end_page is None:
        end_page = total_pages - 1

    all_zones = {}

    for page_num in range(start_page, end_page + 1):
        print(f"Segmentation page {page_num}/{total_pages}...")
        img = segmenter.page_to_image(pdf_path, page_num, dpi=dpi)
        zones = segmenter.segment_page(img, page_num)

        all_zones[page_num] = zones

        for i, zone in enumerate(zones):
            if zone.zone_type in (ZoneType.FIGURE, ZoneType.TABLE):
                filename = f"page{page_num:04d}_fig{i:02d}_{zone.zone_type.value}.png"
                cv2.imwrite(
                    str(output_path / "figures" / filename),
                    zone.image
                )
            else:
                filename = f"page{page_num:04d}_text{i:02d}.png"
                cv2.imwrite(
                    str(output_path / "text_zones" / filename),
                    zone.image
                )

        print(f"  → {len([z for z in zones if z.zone_type == ZoneType.TEXT])} zones texte, "
              f"{len([z for z in zones if z.zone_type != ZoneType.TEXT])} figures/tableaux")

    return all_zones
