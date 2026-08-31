import re

file_path = 'frontend/src/app/login/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """          <div className="mt-8 pt-6 border-t border-[var(--border)] text-center">
            <p className="text-xs text-[var(--muted-foreground)] mb-2">Demo Credentials (click to autofill)</p>
            <div className="flex justify-center gap-2 text-xs">"""

new_block = """          <div className="mt-8 pt-6 border-t border-[var(--border)] text-center">
            <p className="text-xs text-[var(--muted-foreground)] mb-1 font-medium">Demo Credentials (click to autofill)</p>
            <p className="text-[11px] text-slate-400 mb-4">(Initial demo password: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-600 font-mono">demo123</code> &mdash; until you change it manually.)</p>
            <div className="flex justify-center gap-2 text-xs">"""

content = content.replace(old_block, new_block)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
