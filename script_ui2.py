import re

file_path = 'frontend/src/app/login/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '&mdash; until you change it manually.)',
    '&mdash; until you change it manually from the dashboard.)'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
