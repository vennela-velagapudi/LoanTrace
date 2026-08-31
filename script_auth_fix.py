import re

file_path = 'frontend/src/lib/auth.ts'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = """
const DEMO_KEY = "LT_SECURE_DEMO_KEY";

function xorEncode(text: string): string {
  let result = "";
  for (let i = 0; i < text.length; i++) {
    result += String.fromCharCode(text.charCodeAt(i) ^ DEMO_KEY.charCodeAt(i % DEMO_KEY.length));
  }
  return btoa(result);
}

function xorDecode(encoded: string): string {
  try {
    let text = atob(encoded);
    let result = "";
    for (let i = 0; i < text.length; i++) {
      result += String.fromCharCode(text.charCodeAt(i) ^ DEMO_KEY.charCodeAt(i % DEMO_KEY.length));
    }
    return result;
  } catch (e) {
    return "";
  }
}

function getStoredCredentials(): Record<string, string> {
  if (typeof window !== "undefined") {
    try {
      const str = localStorage.getItem("demo_creds");
      if (str) return JSON.parse(str);
    } catch (e) {}
  }
  return {};
}

export function getDemoPassword(username: string): string {
  const creds = getStoredCredentials();
  if (creds[username]) {
    return xorDecode(creds[username]);
  }
  return "demo123";
}

export function updateDemoPassword(username: string, newPassword: string) {
  if (typeof window !== "undefined") {
    const creds = getStoredCredentials();
    creds[username] = xorEncode(newPassword);
    localStorage.setItem("demo_creds", JSON.stringify(creds));
  }
}
"""

content = re.sub(r'const demoPasswords[\s\S]*?demoPasswords\[username\] = newPassword;\n\}', new_logic, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
