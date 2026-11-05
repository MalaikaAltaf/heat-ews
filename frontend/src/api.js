const API_BASE = "/api";

let authToken = localStorage.getItem("heat_ews_token") || null;

export function setAuthToken(token) {
  authToken = token;
  if (token) {
    localStorage.setItem("heat_ews_token", token);
  } else {
    localStorage.removeItem("heat_ews_token");
  }
}

export function getAuthToken() {
  return authToken;
}

async function request(endpoint, options = {}) {
  const headers = {
    ...options.headers,
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// Authentication
export async function loginUser(username, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setAuthToken(data.access_token);
  return data;
}

export async function registerUser(userData) {
  const data = await request("/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });
  setAuthToken(data.access_token);
  return data;
}

export function logoutUser() {
  setAuthToken(null);
}

export async function fetchDemoAccounts() {
  return await request("/auth/demo-accounts");
}

export async function fetchCurrentUser() {
  if (!authToken) return null;
  return await request("/auth/me");
}

// Sites
export async function fetchSites() {
  return await request("/sites");
}

export async function fetchSiteDetail(siteId) {
  return await request(`/sites/${siteId}`);
}

// Environment
export async function fetchSiteEnvironment(siteId) {
  return await request(`/environment/${siteId}/current`);
}

export async function fetchSiteForecast(siteId, hours = 72) {
  return await request(`/environment/${siteId}/forecast?hours=${hours}`);
}

export async function syncSiteEnvironment(siteId) {
  return await request(`/environment/${siteId}/sync`, { method: "POST" });
}

// Alerts & Playbooks
export async function fetchAlerts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await request(`/alerts${query ? `?${query}` : ""}`);
}

export async function fetchAlertDetail(alertId) {
  return await request(`/alerts/${alertId}`);
}

export async function acknowledgeAlert(alertId) {
  return await request(`/alerts/${alertId}/acknowledge`, { method: "POST" });
}

export async function logAlertAction(alertId, actionCode, feedback = "") {
  return await request(`/alerts/${alertId}/action`, {
    method: "POST",
    body: JSON.stringify({ action_code: actionCode, feedback }),
  });
}

// Workplace Shifts
export async function fetchWorkplaceHistory(siteId, days = 30) {
  return await request(`/workplace/${siteId}/history?days=${days}`);
}

export async function fetchWorkplaceAnalytics(siteId, days = 14) {
  return await request(`/workplace/${siteId}/analytics?days=${days}`);
}

export async function uploadWorkplaceCsv(file) {
  const formData = new FormData();
  formData.append("file", file);
  return await request("/workplace/upload", {
    method: "POST",
    body: formData,
  });
}

// Validation Lab
export async function fetchValidationScenarios() {
  return await request("/validation/scenarios");
}

export async function fetchValidationMetrics() {
  return await request("/validation/metrics");
}

export async function retrainML() {
  return await request("/validation/train-ml", { method: "POST" });
}

