import re

file_path = 'frontend/src/app/reviewer/ai-tools/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div className="flex gap-2">',
    '<div className="flex flex-wrap gap-2">'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
