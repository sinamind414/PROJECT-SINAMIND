import os

app_data_dir = r"C:\Users\zakaria\.gemini\antigravity-ide"
search_term = "audit"

found_files = []
for root, dirs, files in os.walk(app_data_dir):
    for f in files:
        if search_term in f.lower():
            filepath = os.path.join(root, f)
            found_files.append(filepath)

print(f"Found {len(found_files)} files with '{search_term}':")
for p in found_files:
    print(p)
