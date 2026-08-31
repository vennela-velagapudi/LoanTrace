file_path = 'frontend/src/app/operator/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("      </div>\n\n  );\n}", "      </div>\n    </div>\n  );\n}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
