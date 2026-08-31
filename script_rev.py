import re

file_path = 'frontend/src/app/reviewer/[id]/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div className="grid grid-cols-2 gap-4">',
    '<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">'
)
content = content.replace(
    '<div className="grid grid-cols-2 gap-3 mt-3">',
    '<div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
