import re

file_path = 'frontend/src/app/reviewer/ai-tools/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Root text color
content = content.replace('<div className="p-8 max-w-7xl mx-auto text-white">', '<div className="p-4 sm:p-8 max-w-7xl mx-auto text-slate-900">')
content = content.replace('text-slate-400 hover:text-white', 'text-slate-500 hover:text-slate-900')

# Headings
content = content.replace('text-slate-200', 'text-slate-900')

# Cards
content = content.replace('bg-slate-900 border border-slate-700', 'bg-white border border-slate-200 shadow-sm')
content = content.replace('bg-slate-800 border border-slate-700', 'bg-slate-50 border border-slate-200')
content = content.replace('bg-slate-800 border-slate-700', 'bg-slate-50 border-slate-200')
content = content.replace('bg-slate-800', 'bg-slate-50')
content = content.replace('border-slate-700', 'border-slate-200')
content = content.replace('text-slate-300', 'text-slate-700')
content = content.replace('text-slate-400', 'text-slate-500')
content = content.replace('bg-black/50', 'bg-slate-100')
content = content.replace('border-slate-800', 'border-slate-300')
content = content.replace('text-white flex-1', 'text-slate-900 flex-1')
content = content.replace('border border-slate-600', 'border border-slate-300 focus:border-purple-500 focus:ring-1 focus:ring-purple-500')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
