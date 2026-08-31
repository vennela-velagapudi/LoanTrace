import re

file_path = 'frontend/src/app/login/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'import { setToken, parseJwt, getDemoPassword } from "@/lib/auth";',
    'import { setToken, parseJwt } from "@/lib/auth";'
)

# Add a state for the info message
content = content.replace(
    '  const [error, setError] = useState("");',
    '  const [error, setError] = useState("");\n  const [infoMessage, setInfoMessage] = useState("");'
)

# Clear infoMessage on submit
content = content.replace(
    '    e.preventDefault();\n    setError("");\n    setIsLoading(true);',
    '    e.preventDefault();\n    setError("");\n    setInfoMessage("");\n    setIsLoading(true);'
)

# Render infoMessage above error
info_render = """            {infoMessage && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded text-blue-700 text-sm text-center">
                {infoMessage}
              </div>
            )}"""

content = content.replace(
    '            {error && (',
    f'{info_render}\n            {{error && ('
)

# Replace autofill logic
new_autofill = """  const autofill = (u: string) => {
    setUsername(u);
    setPassword("");
    setError("");
    setInfoMessage("Your password may have been changed. Please enter your updated password.");
  };"""

content = re.sub(r'  const autofill = \(u: string\) => \{[\s\S]*?\};\n', new_autofill + "\n", content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
