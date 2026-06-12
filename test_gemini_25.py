import os
import io
import fitz
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('khawarizmi-backend/.env')
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

pdf_path = "LIVRES SCOLAIRES/ANALES SCIENCES/ANALES SCIENCE DEATILLE/Ahmed amin khelifa version 2 parte 1.pdf"
doc = fitz.open(pdf_path)
page = doc.load_page(15)
pix = page.get_pixmap(dpi=50) 
img_bytes = pix.tobytes("jpeg")
img = Image.open(io.BytesIO(img_bytes))

try:
    response = model.generate_content(["Test simple.", img])
    print("SUCCESS:", response.text)
except Exception as e:
    print("ERROR:", e)
