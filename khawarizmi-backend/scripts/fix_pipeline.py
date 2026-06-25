"""Fix Colab-specific imports in the merged pipeline."""
with open('scripts/ocr_khelifa_pipeline.py', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "from google.colab import drive, files",
    "# from google.colab import drive, files  (local mode)"
)
content = content.replace(
    "drive.mount('/content/drive')",
    "# drive.mount('/content/drive')  (local mode)"
)

# Remove pip install call
content = content.replace(
    "subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pymupdf', 'easyocr'], capture_output=True)",
    "# pip install already done"
)

with open('scripts/ocr_khelifa_pipeline.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed')
