import { useEffect, useState } from 'react';
import { validateManifest } from '../api/agent';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';

export default function ValidationResults() {
  const [manifest, setManifest] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const stored = sessionStorage.getItem('last_manifest');
    if (stored) {
      try {
        setManifest(JSON.parse(stored));
      } catch {
        setError('Invalid manifest session data');
      }
    }
  }, []);

  const runValidation = async () => {
    if (!manifest?.manifest_id && !manifest?.combined_yaml) {
      setError('No manifest available. Generate manifests first.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const data = await validateManifest({
        manifest_id: manifest.manifest_id,
        yaml_content: manifest.combined_yaml,
      });
      setResult(data);
      sessionStorage.setItem('last_validation', JSON.stringify(data));
    } catch (err) {
      setError(err.response?.data?.detail || 'Validation failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const storedValidation = sessionStorage.getItem('last_validation');
    if (storedValidation && !result) {
      try {
        setResult(JSON.parse(storedValidation));
      } catch {
        /* ignore */
      }
    }
  }, [result]);

  const severityColor = (severity) => {
    if (severity === 'error') return 'text-red-400 border-red-800';
    if (severity === 'warning') return 'text-yellow-400 border-yellow-800';
    return 'text-gray-400 border-gray-700';
  };

  return (
    <Layout>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-brand-yellow">Validation Results</h1>
          <p className="text-gray-400">YAML syntax, kube-score, and kube-linter checks</p>
        </div>
        <button type="button" onClick={runValidation} className="btn-primary" disabled={loading}>
          {loading ? 'Validating...' : 'Run Validation'}
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-800 bg-red-950/50 px-3 py-2 text-sm text-red-300">
          {error}
        </div>
      )}

      {loading && <LoadingSpinner label="Running validation tools..." />}

      {result && (
        <div className="space-y-4">
          <div className="card">
            <div className="flex flex-wrap items-center gap-4">
              <span
                className={`rounded-full px-4 py-1 text-sm font-bold ${
                  result.valid ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                }`}
              >
                {result.valid ? 'VALID' : 'ISSUES FOUND'}
              </span>
              <span className="text-sm text-gray-400">Syntax: {result.syntax_valid ? 'OK' : 'FAILED'}</span>
              <span className="text-sm text-gray-400">Tools: {result.tools_run?.join(', ')}</span>
            </div>
            <p className="mt-3 text-gray-300">{result.summary}</p>
          </div>

          <div className="card">
            <h3 className="mb-4 font-semibold text-brand-yellow">Issues ({result.issues?.length || 0})</h3>
            {result.issues?.length === 0 ? (
              <p className="text-gray-400">No issues reported.</p>
            ) : (
              <ul className="space-y-2">
                {result.issues.map((issue, idx) => (
                  <li
                    key={`${issue.tool}-${idx}`}
                    className={`rounded-md border px-3 py-2 text-sm ${severityColor(issue.severity)}`}
                  >
                    <span className="font-semibold uppercase">{issue.severity}</span>
                    <span className="mx-2 text-gray-600">|</span>
                    <span className="text-brand-yellow">{issue.tool}</span>
                    <p className="mt-1">{issue.message}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="card text-center text-gray-400">
          <p>Click &quot;Run Validation&quot; to validate your latest generated manifest.</p>
        </div>
      )}
    </Layout>
  );
}
