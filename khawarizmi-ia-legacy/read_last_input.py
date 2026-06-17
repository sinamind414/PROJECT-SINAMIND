import os
import sys

# Reconfigure stdout to use utf-8 so we don't get encoding issues in output log
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

path = r"C:\Users\zakaria\.gemini\antigravity-ide\brain\6c3b64a5-56a5-4e61-9a44-97049fe3a2b2\scratch\last_user_input_content.txt"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    out_path = r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\last_input_utf8.txt"
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(content)
    print(f"Content written to {out_path} (length: {len(content)})")
else:
    print(f"File {path} does not exist.")
