import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export default client;
