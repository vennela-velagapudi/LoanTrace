import re

file_path = 'frontend/src/app/reviewer/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'const excRes = await apiFetch("/api/exceptions");',
    'const excRes = await apiFetch("/api/exceptions?limit=10000");'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
