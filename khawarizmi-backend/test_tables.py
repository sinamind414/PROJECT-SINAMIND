import re

# Use escape sequences for box drawing chars
line_txt = "\u2554" + "\u2550" * 6 + "\u2566" + "\u2550" * 6 + "\u2557"
print(f"line: {[hex(ord(c)) for c in line_txt]}")
pattern = "[" + "\u2550\u2551\u255e\u256a\u256c\u2554\u2557\u255a\u255d\u2560\u2563\u2566\u2569" + "]"
result = re.sub(pattern, " ", line_txt)
print(f"result: {[hex(ord(c)) for c in result]}")

line2 = "\u2551 Col1 \u2551 Col2 \u2551"
norm = line2.replace("\u2551", "|")
print(f"norm starts with |: {norm.startswith('|')}")
print(f"norm: {[hex(ord(c)) for c in norm]}")
