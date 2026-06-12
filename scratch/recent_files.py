import os
import time

root_dir = r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA"
three_days_ago = time.time() - 3 * 24 * 3600

results = []
for root, dirs, files in os.walk(root_dir):
    if '.git' in root or '__pycache__' in root or 'node_modules' in root:
        continue
    for f in files:
        filepath = os.path.join(root, f)
        try:
            mtime = os.path.getmtime(filepath)
            if mtime > three_days_ago:
                results.append((filepath, mtime, os.path.getsize(filepath)))
        except:
            pass

results.sort(key=lambda x: x[1], reverse=True)
for path, mtime, size in results[:50]:
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))} | {size:8d} | {path}")
