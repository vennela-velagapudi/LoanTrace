export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("token");
  }
  return null;
}

export function setToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("token", token);
  }
}

export function removeToken() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
  }
}

export function parseJwt(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export function getUserRole(): string | null {
  const token = getToken();
  if (!token) return null;
  const decoded = parseJwt(token);
  return decoded?.role || null;
}

export function getUsername(): string | null {
  const token = getToken();
  if (!token) return null;
  const decoded = parseJwt(token);
  return decoded?.sub || null;
}

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = getToken();
  const headers = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };

  let API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  if (API_URL.includes("localhost:8000") || API_URL.includes(":8001") || API_URL.includes(":8002") || API_URL.includes(":8004")) {
    API_URL = "http://127.0.0.1:8000";
  }
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (res.status === 401 || res.status === 403) {
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    }
  }

  return res;
}




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
