import re

file_path = 'frontend/src/components/AIAssistantPanel.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div className="mt-6 border-t border-slate-200 pt-4 flex space-x-3">',
    '<div className="mt-6 border-t border-slate-200 pt-4 flex flex-col sm:flex-row gap-3">'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
