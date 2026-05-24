import { aiApi } from './client';

export async function uploadDiagram(file) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await aiApi.post('/upload-diagram', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function generateManifest(payload) {
  const { data } = await aiApi.post('/generate-manifest', payload);
  return data;
}

export async function validateManifest(payload) {
  const { data } = await aiApi.post('/validate-manifest', payload);
  return data;
}

export async function downloadManifest(manifestId) {
  const response = await aiApi.get('/download-manifest', {
    params: { manifest_id: manifestId },
    responseType: 'blob',
  });
  return response;
}

export async function checkAgentHealth() {
  const { data } = await aiApi.get('/health');
  return data;
}
