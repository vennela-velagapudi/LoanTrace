import re

file_path = 'frontend/src/lib/auth.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
export function markPasswordChanged(username: string) {
  if (typeof window !== "undefined") {
    try {
      const flags = JSON.parse(localStorage.getItem("pwd_changed_flags") || "{}");
      flags[username.toLowerCase()] = true;
      localStorage.setItem("pwd_changed_flags", JSON.stringify(flags));
    } catch (e) {}
  }
}

export function hasPasswordChanged(username: string): boolean {
  if (typeof window !== "undefined") {
    try {
      const flags = JSON.parse(localStorage.getItem("pwd_changed_flags") || "{}");
      return !!flags[username.toLowerCase()];
    } catch (e) {}
  }
  return false;
}
"""

if "markPasswordChanged" not in content:
    content += new_logic

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
