import re

file_path = 'frontend/src/lib/auth.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

addition = """
const demoPasswords: Record<string, string> = {
  operator: "demo123",
  reviewer: "demo123",
  consumer: "demo123"
};

export function getDemoPassword(username: string): string {
  return demoPasswords[username] || "demo123";
}

export function updateDemoPassword(username: string, newPassword: string) {
  demoPasswords[username] = newPassword;
}
"""

if "demoPasswords" not in content:
    content += addition

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
