/**
 * Centralized API client for communicating with Flask backend.
 * Uses native Fetch API with proper headers and error handling.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export class ApiError extends Error {
  constructor(message, status = 500, code = 'UNKNOWN_ERROR', data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  // Add anonymous session ID header
  const sessionId = localStorage.getItem('eit_session_id');
  if (sessionId) {
    headers['X-Session-ID'] = sessionId;
  }

  // Add auth token if logged in
  const token = localStorage.getItem('eit_auth_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { ...options, headers });
    let body = null;
    try {
      body = await res.json();
    } catch {
      // Non-JSON response
    }

    if (!res.ok) {
      const errorMsg = body?.error?.message || `Request failed with status ${res.status}`;
      const errorCode = body?.error?.code || 'HTTP_ERROR';
      throw new ApiError(errorMsg, res.status, errorCode, body);
    }

    return body;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      err.message || 'Unable to connect to the backend server.',
      0,
      'NETWORK_ERROR'
    );
  }
}

export const api = {
  // Health
  health: () => request('/health'),

  // Topics & Lessons
  getTopics: (page = 1, perPage = 20) => request(`/topics?page=${page}&per_page=${perPage}`),
  getLessons: (topicId = null, page = 1, perPage = 50) => {
    const q = topicId ? `?topic_id=${topicId}&page=${page}&per_page=${perPage}` : `?page=${page}&per_page=${perPage}`;
    return request(`/lessons${q}`);
  },
  getLesson: (id) => request(`/lessons/${id}`),

  // Learning Sessions
  createSession: (data) => request('/sessions', { method: 'POST', body: JSON.stringify(data) }),
  getSession: (id) => request(`/sessions/${id}`),
  updateSession: (id, data) => request(`/sessions/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  endSession: (id) => request(`/sessions/${id}/end`, { method: 'POST' }),

  // Progress
  getProgress: () => request('/progress'),
  updateProgress: (data) => request('/progress', { method: 'POST', body: JSON.stringify(data) }),

  // AI Tutor
  tutorChat: (data) => request('/tutor/chat', { method: 'POST', body: JSON.stringify(data) }),
  tutorExplain: (data) => request('/tutor/explain', { method: 'POST', body: JSON.stringify(data) }),
  tutorQuiz: (data) => request('/tutor/quiz', { method: 'POST', body: JSON.stringify(data) }),
  tutorFeedback: (data) => request('/tutor/feedback', { method: 'POST', body: JSON.stringify(data) }),

  // Computer Vision (Consent-gated)
  analyzeExpression: (data) => request('/expression/analyze', { method: 'POST', body: JSON.stringify(data) }),
  saveExpressionSummary: (data) => request('/expression/session', { method: 'POST', body: JSON.stringify(data) }),

  // Auth
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  getMe: () => request('/auth/me'),
};
