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

  const res = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers,
  });

  if (res.status === 401 || res.status === 403) {
    // Optionally trigger a logout or redirect event here, but we will handle it in the UI layers
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      // In a real app, you might want to redirect. But we will let components handle 401s for smoother UX
      // window.location.href = "/login";
    }
  }

  return res;
}
