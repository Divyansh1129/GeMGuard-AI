// api.js
// ---------
// The real HTTP client — replaces the old stub that just faked delays and
// returned null. This one actually calls your GeM Rakshak FastAPI backend.
//
// VITE_API_URL comes from .env (see .env.example) — defaults to your local
// backend if not set, so it works out of the box during development.

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(method, endpoint, body, isFormData = false) {
  const options = { method, headers: {} };

  if (body && !isFormData) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  } else if (body && isFormData) {
    options.body = body; // FormData sets its own Content-Type with boundary
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, options);

  let data = null;
  try {
    data = await res.json();
  } catch {
    // some endpoints may return no body — fine
  }

  if (!res.ok) {
    const message = data?.detail || `Request failed (${res.status})`;
    throw new Error(message);
  }

  return { data, status: res.status };
}

export const api = {
  async get(endpoint) {
    return request("GET", endpoint);
  },
  async post(endpoint, bodyOrFormData, isFormData = false) {
    return request("POST", endpoint, bodyOrFormData, isFormData);
  },
  async put(endpoint, body) {
    return request("PUT", endpoint, body);
  },
  async patch(endpoint, body) {
    return request("PATCH", endpoint, body);
  },
};

export { API_BASE_URL };
export default api;
