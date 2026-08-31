import re

file_path = 'frontend/src/app/reviewer/ai-tools/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the Rule Name text
content = content.replace('className="font-mono text-white bg-slate-50 px-3 py-2 rounded"', 'className="font-mono text-slate-800 bg-slate-50 px-3 py-2 rounded border border-slate-200"')

# Fix the Target Field and Suggested Severity text colors
content = content.replace('text-blue-400 bg-slate-50', 'text-blue-700 bg-slate-50 border border-slate-200')
content = content.replace('text-red-400 bg-slate-50', 'text-red-700 bg-slate-50 border border-slate-200')

# Fix severity labels in the exception list
content = content.replace('className="text-red-400"', 'className="text-red-600 font-bold"')
content = content.replace('className="text-orange-400"', 'className="text-orange-600 font-bold"')
content = content.replace('className="text-yellow-400"', 'className="text-yellow-600 font-bold"')

# Fix Logic Pattern colors
content = content.replace('span className="text-purple-400"', 'span className="text-purple-700"')
content = content.replace('span className="text-green-400"', 'span className="text-green-700"')
content = content.replace('span className="text-yellow-400"', 'span className="text-yellow-700"')

# Fix Most Common Rule output
content = content.replace('className="font-mono text-purple-400"', 'className="font-mono text-purple-700"')

# Fix tab active text color
content = content.replace("text-purple-400 border-b-2 border-purple-400", "text-purple-700 border-b-2 border-purple-700")
content = content.replace('text-purple-400 w-8 h-8', 'text-purple-700 w-8 h-8')
content = content.replace('text-purple-400 text-center', 'text-purple-700 text-center')

# Add border to text area
content = content.replace('border border-slate-300 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 rounded', 'bg-white border border-slate-300 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 rounded')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
