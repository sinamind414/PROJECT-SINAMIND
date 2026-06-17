import os
import glob
import sys

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

brain_dir = r"C:\Users\zakaria\.gemini\antigravity-ide\brain"
print(f"Scanning {brain_dir} for 'Nirenberg'...")

found = []
for root, dirs, files in os.walk(brain_dir):
    for file in files:
        if file.endswith((".jsonl", ".txt", ".md", ".json")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "marshall nirenberg" in content.lower():
                        # Let's check if the file size is substantial (not truncated)
                        if len(content) > 5000 and "truncated" not in content.lower():
                            print(f"Found in {path} (length: {len(content)})")
                            found.append((path, len(content)))
            except Exception as e:
                pass

print(f"Scan complete. Found {len(found)} candidate files.")
