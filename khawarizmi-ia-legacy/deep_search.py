import os
import sys

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

search_dirs = [
    r"C:\Users\zakaria\.gemini\antigravity-ide\brain",
    r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA"
]

print("Starting deep search for Nirenberg...")
for s_dir in search_dirs:
    for root, dirs, files in os.walk(s_dir):
        for file in files:
            path = os.path.join(root, file)
            # Skip read_last_input.py or scan files to avoid circular matches
            if "read_transcript" in file or "scan" in file or "read_last" in file:
                continue
            try:
                # check size
                size = os.path.getsize(path)
                if size > 100:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if "nirenberg" in content.lower():
                            idx = content.lower().find("nirenberg")
                            snippet = content[max(0, idx-50):min(len(content), idx+150)].replace('\n', ' ')
                            print(f"MATCH: {path} (size: {size} bytes) - Snippet: ... {snippet} ...")
            except Exception as e:
                pass
print("Deep search finished.")
