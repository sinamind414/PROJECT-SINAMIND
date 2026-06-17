import os
import json
import glob
import sys

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

brain_dir = r"C:\Users\zakaria\.gemini\antigravity-ide\brain"
print(f"Searching for '4 Expériences Classiques' in {brain_dir}...")

pattern = os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl")
for path in glob.glob(pattern):
    print(f"Checking {path}...")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "4 Expériences Classiques" in line:
                # Let's see if we can find an untruncated version of the user input
                try:
                    obj = json.loads(line)
                    if obj.get("type") == "USER_INPUT":
                        content = obj.get("content", "")
                        if "truncated" not in content or content.count("truncated") < 2:
                            print(f"FOUND matching USER_INPUT in {path}! Length: {len(content)}")
                            out_path = r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\found_full_request.txt"
                            with open(out_path, "w", encoding="utf-8") as out_f:
                                out_f.write(content)
                            print(f"Successfully saved to {out_path}")
                            break
                except Exception as e:
                    pass
