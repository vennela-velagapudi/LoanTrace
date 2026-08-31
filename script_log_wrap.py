import re

file_path = 'frontend/src/app/login/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('max-w-md p-8', 'max-w-md p-6 sm:p-8')
content = content.replace('className="flex justify-center gap-2 text-xs"', 'className="flex flex-wrap justify-center gap-2 text-xs"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
