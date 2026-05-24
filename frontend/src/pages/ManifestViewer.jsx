import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { downloadManifest } from '../api/agent';
import Layout from '../components/Layout';

export default function ManifestViewer() {
  const location = useLocation();
  const [manifest, setManifest] = useState(location.state?.manifest || null);
  const [activeFile, setActiveFile] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (!manifest) {
      const stored = sessionStorage.getItem('last_manifest');
      if (stored) {
        try {
          setManifest(JSON.parse(stored));
        } catch {
          setError('Could not load manifest data');
        }
      }
    }
  }, [manifest]);

  useEffect(() => {
    if (manifest?.manifests) {
      const files = Object.keys(manifest.manifests);
      if (files.length && !activeFile) {
        setActiveFile(files[0]);
      }
    }
  }, [manifest, activeFile]);

  const handleDownload = async () => {
    if (!manifest?.manifest_id) return;
    try {
      const response = await downloadManifest(manifest.manifest_id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `k8s-manifests-${manifest.manifest_id.slice(0, 8)}.yaml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Download failed');
    }
  };

  if (!manifest) {
    return (
      <Layout>
        <div className="card text-center">
          <p className="text-gray-400">No manifest generated yet.</p>
          <a href="/upload" className="btn-primary mt-4 inline-block">
            Upload Diagram
          </a>
        </div>
      </Layout>
    );
  }

  const files = Object.keys(manifest.manifests || {});

  return (
    <Layout>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-brand-yellow">Generated Manifests</h1>
          <p className="text-sm text-gray-400">
            ID: {manifest.manifest_id} | Namespace: {manifest.namespace} | Mode: {manifest.llm_mode}
          </p>
        </div>
        <button type="button" onClick={handleDownload} className="btn-primary">
          Download YAML
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-800 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="mb-4 flex flex-wrap gap-2">
        {manifest.components_detected?.map((c) => (
          <span key={c} className="rounded-full border border-brand-yellow/40 bg-brand-dark px-3 py-1 text-xs text-brand-yellow">
            {c}
          </span>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <div className="card lg:col-span-1">
          <h3 className="mb-3 font-semibold">Files</h3>
          <ul className="space-y-1">
            {files.map((f) => (
              <li key={f}>
                <button
                  type="button"
                  onClick={() => setActiveFile(f)}
                  className={`w-full rounded px-2 py-1 text-left text-sm ${
                    activeFile === f ? 'bg-brand-yellow text-brand-black' : 'text-gray-400 hover:text-brand-yellow'
                  }`}
                >
                  {f}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="card lg:col-span-3">
          <h3 className="mb-3 font-semibold text-brand-yellow">{activeFile || 'combined.yaml'}</h3>
          <pre className="max-h-[600px] overflow-auto rounded-md bg-black p-4 font-mono text-xs text-green-400">
            {activeFile ? manifest.manifests[activeFile] : manifest.combined_yaml}
          </pre>
        </div>
      </div>

      <div className="mt-4 card">
        <h3 className="mb-2 font-semibold">Combined YAML</h3>
        <pre className="max-h-96 overflow-auto rounded-md bg-black p-4 font-mono text-xs text-gray-300">
          {manifest.combined_yaml}
        </pre>
      </div>
    </Layout>
  );
}
