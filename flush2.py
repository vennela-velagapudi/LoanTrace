import re
with open("backend/app/services/validation.py", "r") as f:
    content = f.read()

content = re.sub(r'print\((f"\[Timer\].*?")\)', r'print(\1, flush=True)', content)

with open("backend/app/services/validation.py", "w") as f:
    f.write(content)
