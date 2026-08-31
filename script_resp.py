import os
import re

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Update main container paddings (p-8 -> p-4 sm:p-8)
    # Be careful not to replace p-8 inside buttons or specific small elements unless it's a structural container
    content = re.sub(r'<div className="p-8([^"]*)">', r'<div className="p-4 sm:p-8\1">', content)
    content = re.sub(r'<div className="p-8">', r'<div className="p-4 sm:p-8">', content)
    content = re.sub(r'<div className="p-6">', r'<div className="p-4 sm:p-6">', content)
    
    # 2. Update flex layouts for headers that might overlap (flex justify-between items-center mb-8)
    content = re.sub(r'className="flex justify-between items-center mb-8"', r'className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 sm:gap-0 mb-6 sm:mb-8"', content)
    content = re.sub(r'className="flex justify-between items-center mb-6"', r'className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 sm:gap-0 mb-4 sm:mb-6"', content)

    # 3. Update tables to have wrapper for overflow
    # Let's find <table and ensure it's wrapped in a div with overflow-x-auto
    # We can do this carefully where table is directly inside a glass-panel or similar
    # Actually, the user says "Instead, contain table overflow properly: overflow-x-auto inside the table's own container"
    # We will search for <table and see if we need to wrap it.

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.tsx'):
            process_file(os.path.join(root, file))
