import { authApi } from './client';

export async function registerUser({ email, username, password }) {
  const { data } = await authApi.post('/register', { email, username, password });
  return data;
}

export async function loginUser({ email, password }) {
  const { data } = await authApi.post('/login', { email, password });
  return data;
}

export async function checkAuthHealth() {
  const { data } = await authApi.get('/health');
  return data;
}
