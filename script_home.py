import re

file_path = 'frontend/src/app/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'text-5xl font-bold',
    'text-4xl md:text-5xl font-bold'
)
content = content.replace(
    'p-8 text-center',
    'p-4 sm:p-8 text-center'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
