import re

file_path = 'frontend/src/components/ClientNav.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'Logged in as <span className="font-bold text-slate-900 ml-1 capitalize">{username}</span>',
    '<span className="hidden sm:inline">Logged in as</span> <span className="font-bold text-slate-900 sm:ml-1 capitalize">{username}</span>'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
