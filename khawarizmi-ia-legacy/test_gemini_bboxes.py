import os
import io
import json
import fitz
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('khawarizmi-backend/.env')
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

pdf_path = "LIVRES SCOLAIRES/ANALES SCIENCES/ANALES SCIENCE DEATILLE/Ahmed amin khelifa version 2 parte 1.pdf"
doc = fitz.open(pdf_path)
page_idx = 15 # Try page 16, usually has exercises
page = doc.load_page(page_idx)
pix = page.get_pixmap(dpi=150)
img_bytes = pix.tobytes("jpeg")
img = Image.open(io.BytesIO(img_bytes))

PROMPT = """
Analyse cette page d'un livre de sciences naturelles.
Extrais les exercices et leurs questions.
Si un exercice contient des dessins, graphes ou tableaux, indique leurs coordonnées sous forme de boîte englobante [ymin, xmin, ymax, xmax] où chaque valeur est un entier entre 0 et 1000 proportionnel à la taille de l'image (0 en haut à gauche, 1000 en bas à droite).

Structure JSON attendue :
[
  {
    "exercice_id": "khelifa_p16_ex1",
    "questions": [ ... ],
    "images_et_tableaux": [
      {
         "type": "tableau" ou "dessin",
         "description": "Brève description de l'image",
         "box_2d": [ymin, xmin, ymax, xmax]
      }
    ]
  }
]

Retourne uniquement le JSON, sans balises markdown.
"""

response = model.generate_content([PROMPT, img])
print(response.text)
