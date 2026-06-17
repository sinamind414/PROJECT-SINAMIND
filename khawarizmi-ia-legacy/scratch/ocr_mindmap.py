import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('khawarizmi-backend/.env')
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

image_path = 'DOCUMENTATION TECHNIQUES IMPORTANTES/MIND MANTAL -CHAPITRE 1 programme national .png'
if not os.path.exists(image_path):
    print(f"Error: {image_path} does not exist!")
    exit(1)

print("Reading image and calling Gemini...")
model = genai.GenerativeModel('gemini-2.5-flash')

# Load the image using PIL
from PIL import Image
img = Image.open(image_path)

prompt = """
Analyse cette image qui contient la carte mentale (mind map) du Chapitre 1 du programme national de Sciences de la Nature et de la Vie (SVT) pour le Baccalauréat Algérien.
Extrait textuellement et de façon structurée l'ensemble des informations présentes sur cette carte mentale :
- Les thèmes principaux,
- Les unités d'apprentissage,
- Les concepts clés,
- Les définitions,
- Les flèches ou liens logiques décrits.
Donne le résultat structuré en Markdown propre et lisible (en arabe et/ou français selon ce qui est écrit sur l'image).
"""

response = model.generate_content([prompt, img])
output_path = 'scratch/extracted_mindmap.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(response.text)
print(f"Extracted content saved to {output_path} successfully!")
