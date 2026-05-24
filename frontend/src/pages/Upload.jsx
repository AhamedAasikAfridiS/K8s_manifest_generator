import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateManifest, uploadDiagram } from '../api/agent';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [namespace, setNamespace] = useState('production');
  const [appName, setAppName] = useState('web-app');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a diagram image');
      return;
    }

    setLoading(true);
    setError('');

    try {
      setStep('Uploading diagram...');
      const uploadResult = await uploadDiagram(file);

      setStep('Generating Kubernetes manifests...');
      const manifestResult = await generateManifest({
        file_id: uploadResult.file_id,
        namespace,
        app_name: appName,
        description: description || undefined,
      });

      sessionStorage.setItem('last_manifest', JSON.stringify(manifestResult));
      navigate('/manifest', { state: { manifest: manifestResult } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process diagram');
    } finally {
      setLoading(false);
      setStep('');
    }
  };

  return (
    <Layout>
      <h1 className="mb-2 text-3xl font-bold text-brand-yellow">Upload Architecture Diagram</h1>
      <p className="mb-6 text-gray-400">Upload a PNG, JPEG, WEBP, GIF, or PDF diagram to generate manifests</p>

      {error && (
        <div className="mb-4 rounded-md border border-red-800 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-2">
        <div className="card space-y-4">
          <div>
            <label className="mb-1 block text-sm text-gray-400">Diagram File</label>
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif,application/pdf"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-400 file:mr-4 file:rounded-md file:border-0 file:bg-brand-yellow file:px-4 file:py-2 file:font-semibold file:text-brand-black"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm text-gray-400">Namespace</label>
            <input className="input-field" value={namespace} onChange={(e) => setNamespace(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm text-gray-400">Application Name</label>
            <input className="input-field" value={appName} onChange={(e) => setAppName(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm text-gray-400">Architecture Description (optional)</label>
            <textarea
              className="input-field min-h-[100px]"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. 3-tier app with frontend, API, Redis cache, and ingress"
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Processing...' : 'Upload & Generate'}
          </button>
        </div>

        <div className="card">
          <h3 className="mb-3 font-semibold text-brand-yellow">Preview</h3>
          {preview ? (
            <img src={preview} alt="Diagram preview" className="max-h-80 w-full rounded-md border border-gray-800 object-contain" />
          ) : (
            <div className="flex h-64 items-center justify-center rounded-md border border-dashed border-gray-700 text-gray-500">
              No file selected
            </div>
          )}
        </div>
      </form>

      {loading && <LoadingSpinner label={step || 'Processing...'} />}
    </Layout>
  );
}
