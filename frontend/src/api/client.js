import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ──────────────────────── JWT Token Interceptor ────────────────────────
// Automatically attach stored JWT token to all requests.

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('firai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ──────────────────────── Retry + Auth Interceptor ────────────────────────
// Auto-retry on network errors (ECONNREFUSED) — backend may still be
// warming up (seeding DB + loading ML model) when frontend first loads.
// Also handles 401 by clearing token and redirecting to login.

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 3000;

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;
    if (!config) return Promise.reject(error);

    // Handle 401 — redirect to login
    if (error.response?.status === 401 && !config._isRetryAuth) {
      localStorage.removeItem('firai_token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }

    // Only retry on network errors (no response received = backend not ready yet)
    const isNetworkError = !error.response && (
      error.code === 'ECONNREFUSED' ||
      error.code === 'ERR_NETWORK' ||
      error.message === 'Network Error'
    );

    config._retryCount = config._retryCount || 0;

    if (isNetworkError && config._retryCount < MAX_RETRIES) {
      config._retryCount += 1;
      console.warn(`[API] Backend not ready, retrying (${config._retryCount}/${MAX_RETRIES})...`);
      await new Promise((res) => setTimeout(res, RETRY_DELAY_MS));
      return client(config);
    }

    return Promise.reject(error);
  }
);

// ──────────────────────── FIR Endpoints ────────────────────────

export const firAPI = {
  list: (params = {}) => client.get('/firs', { params }),
  get: (id) => client.get(`/firs/${id}`),
  uploadPDF: (file) => {
    const form = new FormData();
    form.append('file', file);
    return client.post('/firs/upload-pdf', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
  },
  analyzeText: (narrative, top_k = 5) =>
    client.post('/firs/analyze-text', { narrative, top_k }),
  analyzeAndSave: (narrative) =>
    client.post('/firs/analyze-and-save', { narrative, top_k: 5 }),
  getSimilar: (id, top_k = 5) =>
    client.get(`/firs/${id}/similar`, { params: { top_k } }),
  downloadFIR: (id) => client.get(`/firs/${id}/download`, { responseType: 'blob' }),
  exportAll: () => client.get('/firs/export/all'),
  bulkUploadPDF: (files) => {
    const form = new FormData();
    files.forEach((f) => form.append('files', f));
    return client.post('/firs/bulk-upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
    });
  },
  bulkUploadJSON: (files) => {
    const form = new FormData();
    files.forEach((f) => form.append('files', f));
    return client.post('/firs/bulk-upload-json', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
    });
  },
};

// ──────────────────────── Dashboard ────────────────────────

export const dashboardAPI = {
  getStats: () => client.get('/dashboard/stats'),
};

// ──────────────────────── Legal ────────────────────────

export const legalAPI = {
  query: (question, fir_id = null) =>
    client.post('/legal/query', { question, fir_id }),
  getSections: (act = null) =>
    client.get('/legal/sections', { params: act ? { act } : {} }),
  lookupSection: (act, section) =>
    client.get(`/legal/sections/${act}/${section}`),
  getEquivalent: (act, section) =>
    client.get(`/legal/equivalent/${act}/${section}`),
  getBatchEquivalents: (sections) =>
    client.post('/legal/equivalent/batch', sections),
  calcPunishment: (sections) =>
    client.post('/legal/punishment-calc', { sections }),
};

// ──────────────────────── MO Patterns ────────────────────────

export const moAPI = {
  getPatterns: () => client.get('/mo/patterns'),
  detect: () => client.post('/mo/detect'),
};

// ──────────────────────── Translation ────────────────────────

export const translateAPI = {
  translate: (text, source_lang = 'ml', target_lang = 'en') =>
    client.post('/translate', { text, source_lang, target_lang }),
};

// ──────────────────────── Health ────────────────────────

export const healthAPI = {
  check: () => client.get('/health'),
};

// ──────────────────────── Auth ────────────────────────

export const authAPI = {
  login: (badge_number, password) => client.post('/auth/login', { badge_number, password }),
  getProfile: () => client.get('/auth/me'),
  registerRequest: (data) => client.post('/auth/register-request', data),
  listRegistrationRequests: (status) =>
    client.get('/auth/registration-requests', { params: status ? { status_filter: status } : {} }),
  approveRequest: (id) => client.post(`/auth/registration-requests/${id}/approve`),
  rejectRequest: (id, reason) => client.post(`/auth/registration-requests/${id}/reject`, null, { params: { reason } }),
};

export default client;
