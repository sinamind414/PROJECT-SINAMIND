import os
import json
import sys

if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

log_dir = r"C:\Users\zakaria\.gemini\antigravity-ide\brain\6c3b64a5-56a5-4e61-9a44-97049fe3a2b2\.system_generated\logs"
transcript_path = os.path.join(log_dir, "transcript.jsonl")

if os.path.exists(transcript_path):
    print("Transcript found! Reading last step...")
    steps = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    steps.append(json.loads(line))
                except Exception as e:
                    pass
    
    # We want to find the latest USER_INPUT step or planner response
    # Let's search from the end
    user_inputs = [s for s in steps if s.get("type") == "USER_INPUT"]
    if user_inputs:
        latest_input = user_inputs[-1]
        content = latest_input.get("content", "")
        print(f"Found user input from transcript! Length: {len(content)}")
        
        # Write to local file
        out_path = r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\latest_user_request.txt"
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(content)
        print(f"Written to {out_path}")
    else:
        print("No USER_INPUT found in transcript.")
else:
    print(f"Transcript path {transcript_path} not found.")
