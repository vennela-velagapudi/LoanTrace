import re
file_path = 'frontend/src/app/login/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r',\s*getDemoPassword\s*', '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
