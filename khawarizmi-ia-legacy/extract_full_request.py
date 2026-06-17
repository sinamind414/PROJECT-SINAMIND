import os
import json
import sys

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

log_dir = r"C:\Users\zakaria\.gemini\antigravity-ide\brain\6c3b64a5-56a5-4e61-9a44-97049fe3a2b2\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript.jsonl")

if os.path.exists(transcript_path):
    print("Reading transcript.jsonl...")
    found_full = None
    with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "nirenberg" in line.lower() and "4 expériences classiques" in line.lower():
                try:
                    obj = json.loads(line)
                    content = obj.get("content", "")
                    # We want the content which does not contain the word "<truncated"
                    if content and "<truncated" not in content:
                        print(f"Found untruncated match! Length: {len(content)}")
                        found_full = content
                except Exception as e:
                    pass
    if found_full:
        out_path = r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\extracted_untruncated_request.txt"
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(found_full)
        print(f"Successfully wrote untruncated content to {out_path}")
    else:
        print("No untruncated match found.")
else:
    print("Transcript not found.")
