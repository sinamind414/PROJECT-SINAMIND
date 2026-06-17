import os
import json
import sys

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

log_dir = r"C:\Users\zakaria\.gemini\antigravity-ide\brain\6c3b64a5-56a5-4e61-9a44-97049fe3a2b2\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript.jsonl")

if os.path.exists(transcript_path):
    print("Reading user inputs from transcript...")
    with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if "nirenberg" in line.lower():
                try:
                    obj = json.loads(line)
                    if obj.get("source") == "USER_EXPLICIT":
                        content = obj.get("content", "")
                        print(f"Index {i}: Source={obj.get('source')}, Type={obj.get('type')}, Length={len(content)}")
                        if "<truncated" in content:
                            print("  (Contains truncation markers)")
                        else:
                            print("  (NO truncation markers!)")
                except Exception as e:
                    pass
else:
    print("Transcript not found.")
