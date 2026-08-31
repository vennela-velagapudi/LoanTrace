import re

file_path = 'frontend/src/app/settings/security/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('className="glass-panel p-8 rounded-xl', 'className="glass-panel p-6 sm:p-8 rounded-xl')
content = content.replace('+?', '?')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
