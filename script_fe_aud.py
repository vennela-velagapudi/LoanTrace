import re

file_path = 'frontend/src/app/reviewer/[id]/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'const auditRes = await apiFetch(`/api/audit/${d.loan.loan_id}`);',
    'const auditRes = await apiFetch(`/api/audit/exception/${d.exception.id}`);'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
