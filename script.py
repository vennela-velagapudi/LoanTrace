import re

file_path = 'frontend/src/components/ClientNav.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add a dropdown state
content = content.replace(
    "const [username, setUsername] = useState<string | null>(null);",
    "const [username, setUsername] = useState<string | null>(null);\n  const [dropdownOpen, setDropdownOpen] = useState(false);"
)

# Add close dropdown handler on route change
content = content.replace(
    "setUsername(getUsername());\n  }, [pathname]); // Re-check on route change",
    "setUsername(getUsername());\n    setDropdownOpen(false);\n  }, [pathname]); // Re-check on route change"
)

# replace the logout logic
old_logout_div = """          <div className="flex items-center gap-4 ml-4 border-l border-slate-300 pl-4">
            <span className="text-slate-600 text-xs">Logged in as <span className="font-bold text-slate-900">{username}</span></span>
            <button onClick={handleLogout} className="px-4 py-2 rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-300 transition-colors cursor-pointer text-sm font-medium">Logout</button>
          </div>"""

new_logout_div = """          <div className="relative ml-4 border-l border-slate-300 pl-4">
            <button 
              onClick={() => setDropdownOpen(!dropdownOpen)} 
              className="flex items-center gap-2 text-slate-700 font-semibold hover:text-slate-900 transition-colors cursor-pointer"
            >
              {username} ?
            </button>
            
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-md shadow-lg py-1 z-50 overflow-hidden">
                <Link 
                  href="/settings/security" 
                  className="block px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
                  onClick={() => setDropdownOpen(false)}
                >
                  Security Settings
                </Link>
                <div className="border-t border-slate-100 my-1"></div>
                <button 
                  onClick={() => { setDropdownOpen(false); handleLogout(); }} 
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
                >
                  Logout
                </button>
              </div>
            )}
          </div>"""

content = content.replace(old_logout_div, new_logout_div)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
