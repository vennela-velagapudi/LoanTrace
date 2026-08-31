import re

file_path = 'frontend/src/app/reviewer/ai-tools/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div className="p-4 sm:p-8 max-w-5xl mx-auto text-white">',
    '<div className="p-4 sm:p-8 max-w-5xl mx-auto text-slate-900">'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
