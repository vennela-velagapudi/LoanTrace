import re

file_path = 'frontend/src/app/consumer/[id]/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    '<div className="flex justify-between items-start mb-8">',
    '<div className="flex flex-col sm:flex-row justify-between items-start gap-4 sm:gap-0 mb-8">'
)

content = content.replace(
    '<div className="bg-white border border-slate-200 px-4 py-2 rounded flex flex-col items-end">',
    '<div className="bg-white border border-slate-200 px-4 py-2 rounded flex flex-col items-start sm:items-end w-full sm:w-auto overflow-hidden break-all">'
)

content = content.replace(
    '<div className="p-4 grid grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-4">',
    '<div className="p-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-4">'
)

content = content.replace('+?', '?')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
