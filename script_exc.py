import re

file_path = 'backend/app/api/exceptions.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'return query.offset(skip).limit(limit).all()',
    'return query.order_by(ExceptionModel.id.asc()).offset(skip).limit(limit).all()'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
