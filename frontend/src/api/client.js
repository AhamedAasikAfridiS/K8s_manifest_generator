import axios from 'axios';

export const authApi = axios.create({
  baseURL: import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001',
  headers: { 'Content-Type': 'application/json' },
});

export const aiApi = axios.create({
  baseURL: import.meta.env.VITE_AI_API_URL || 'http://localhost:8002',
});

export function setAuthToken(token) {
  if (token) {
    aiApi.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete aiApi.defaults.headers.common.Authorization;
  }
}
