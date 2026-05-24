import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { checkAgentHealth } from '../api/agent';
import { checkAuthHealth } from '../api/auth';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const [services, setServices] = useState({ auth: null, agent: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHealth() {
      try {
        const [auth, agent] = await Promise.allSettled([
          checkAuthHealth(),
          checkAgentHealth(),
        ]);
        setServices({
          auth: auth.status === 'fulfilled' ? auth.value : { status: 'error' },
          agent: agent.status === 'fulfilled' ? agent.value : { status: 'error' },
        });
      } finally {
        setLoading(false);
      }
    }
    loadHealth();
  }, []);

  const workflow = [
    { step: 1, title: 'Upload Diagram', desc: 'Upload your Kubernetes architecture diagram', link: '/upload' },
    { step: 2, title: 'Generate Manifests', desc: 'AI analyzes components and builds YAML', link: '/upload' },
    { step: 3, title: 'Validate & Download', desc: 'Run kube-score/linter and export YAML', link: '/validation' },
  ];

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-brand-yellow">DevOps Dashboard</h1>
        <p className="mt-1 text-gray-400">Welcome back, {user?.username}</p>
      </div>

      {loading ? (
        <LoadingSpinner label="Checking services..." />
      ) : (
        <div className="mb-8 grid gap-4 sm:grid-cols-2">
          <div className="card">
            <h3 className="font-semibold text-brand-yellow">Auth Service</h3>
            <p className="mt-2 text-sm text-gray-400">Status: {services.auth?.status || 'unknown'}</p>
            <p className="text-sm text-gray-500">DB: {services.auth?.database || 'n/a'}</p>
          </div>
          <div className="card">
            <h3 className="font-semibold text-brand-yellow">AI Agent Service</h3>
            <p className="mt-2 text-sm text-gray-400">Status: {services.agent?.status || 'unknown'}</p>
            <p className="text-sm text-gray-500">LLM: {services.agent?.llm_mode || 'n/a'}</p>
          </div>
        </div>
      )}

      <h2 className="mb-4 text-xl font-semibold">Workflow</h2>
      <div className="grid gap-4 md:grid-cols-3">
        {workflow.map((item) => (
          <Link key={item.step} to={item.link} className="card block transition hover:border-brand-yellow">
            <span className="text-xs font-bold text-brand-yellow">STEP {item.step}</span>
            <h3 className="mt-2 font-semibold">{item.title}</h3>
            <p className="mt-1 text-sm text-gray-400">{item.desc}</p>
          </Link>
        ))}
      </div>

      <div className="mt-8 card">
        <h3 className="font-semibold text-brand-yellow">Quick Actions</h3>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link to="/upload" className="btn-primary">
            Upload Diagram
          </Link>
          <Link to="/manifest" className="btn-secondary">
            View Manifests
          </Link>
          <Link to="/validation" className="btn-secondary">
            Validation Results
          </Link>
        </div>
      </div>
    </Layout>
  );
}
