file_path = 'frontend/src/app/settings/security/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("+? Back to Dashboard", "? Back to Dashboard")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
