import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirm) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const data = await registerUser({
        email: form.email,
        username: form.username,
        password: form.password,
      });
      login(data);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="mx-auto max-w-md">
        <div className="card">
          <h1 className="mb-2 text-2xl font-bold text-brand-yellow">Create Account</h1>
          <p className="mb-6 text-sm text-gray-400">Start generating Kubernetes manifests from diagrams</p>

          {error && (
            <div className="mb-4 rounded-md border border-red-800 bg-red-950/50 px-3 py-2 text-sm text-red-300">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1 block text-sm text-gray-400">Email</label>
              <input name="email" type="email" className="input-field" value={form.email} onChange={handleChange} required />
            </div>
            <div>
              <label className="mb-1 block text-sm text-gray-400">Username</label>
              <input name="username" type="text" className="input-field" value={form.username} onChange={handleChange} required minLength={3} />
            </div>
            <div>
              <label className="mb-1 block text-sm text-gray-400">Password</label>
              <input name="password" type="password" className="input-field" value={form.password} onChange={handleChange} required minLength={8} />
            </div>
            <div>
              <label className="mb-1 block text-sm text-gray-400">Confirm Password</label>
              <input name="confirm" type="password" className="input-field" value={form.confirm} onChange={handleChange} required />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Creating account...' : 'Register'}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-brand-yellow hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </Layout>
  );
}
