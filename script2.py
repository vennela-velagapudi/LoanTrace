import re

file_path = 'frontend/src/app/operator/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will find "      </div>\n\n          <div>\n            <label className=\"block text-sm font-medium mb-1\">New Password</label>"
# and replace it with just "      </div>\n    </div>\n  );\n}\n"

start_idx = content.find('          <div>\n            <label className="block text-sm font-medium mb-1">New Password</label>')
if start_idx != -1:
    content = content[:start_idx] + "  );\n}\n"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
