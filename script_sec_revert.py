import re

file_path = 'frontend/src/app/settings/security/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'import { apiFetch, getToken, getUserRole, getUsername, updateDemoPassword } from "@/lib/auth";',
    'import { apiFetch, getToken, getUserRole, getUsername } from "@/lib/auth";'
)

# Remove the block:
block_to_remove = """      const user = getUsername();
      if (user) {
        updateDemoPassword(user.toLowerCase(), newPassword);
      }
      """
content = content.replace(block_to_remove, "")
content = content.replace("+?", "?")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
