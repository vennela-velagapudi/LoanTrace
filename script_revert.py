import re

file_path = 'frontend/src/lib/auth.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace everything from `const DEMO_KEY` onwards
new_logic = """
// Explicit demo-account configuration used only for the hackathon demo.
// These reflect the initial seeded state of the database.
const DEMO_CREDENTIALS: Record<string, string> = {
  operator: "demo123",
  reviewer: "demo123",
  consumer: "demo123"
};

export function getDemoPassword(username: string): string {
  return DEMO_CREDENTIALS[username] || "demo123";
}
"""

content = re.sub(r'const DEMO_KEY[\s\S]*', new_logic, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
