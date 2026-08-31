import re

file_path = 'frontend/src/app/login/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'import { setToken, parseJwt } from "@/lib/auth";',
    'import { setToken, parseJwt, hasPasswordChanged } from "@/lib/auth";'
)

autofill_old = """  const autofill = (u: string) => {
    setUsername(u);
    setPassword("");
    setError("");
    setInfoMessage("Your password may have been changed. Please enter your updated password.");
  };"""

autofill_new = """  const autofill = (u: string) => {
    setUsername(u);
    setPassword("");
    setError("");
    if (hasPasswordChanged(u)) {
      setInfoMessage("Your password was changed. Please enter your updated password.");
    } else {
      setInfoMessage("");
    }
  };"""

content = content.replace(autofill_old, autofill_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
