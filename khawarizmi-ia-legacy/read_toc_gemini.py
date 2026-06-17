# -*- coding: utf-8 -*-
import os
import google.generativeai as genai
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('khawarizmi-backend/.env')
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

PROMPT = """
Voici les images des dernières pages d'un livre scolaire de SVT algérien de 3ème année secondaire.
Trouve la page qui correspond au "Findex" / "Table de matières" (الفهرس).
Une fois trouvée, extrais les numéros de page de début et de fin pour chacun des 3 domaines suivants :
1. المجال التعلمي الأول: التخصص الوظيفي للبروتينات
2. المجال التعلمي الثاني: تحويل الطاقة على مستوى ما فوق البنية الخلوية
3. المجال التعلمي الثالث: التكتونية العامة

Affiche clairement la page contenant le sommaire, et les plages de pages pour chaque domaine.
"""

temp_toc_dir = Path("temp_toc")
images = []
for p in sorted(temp_toc_dir.glob("page_*.jpg")):
    print(f"Loading {p.name}...")
    images.append(Image.open(p))

try:
    response = model.generate_content([PROMPT] + images)
    with open("toc_result.txt", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("SUCCESS: Result written to toc_result.txt")
except Exception as e:
    print("Error:", e)
