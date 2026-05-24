import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navClass = ({ isActive }) =>
  `px-3 py-2 rounded-md text-sm font-medium transition ${
    isActive ? 'bg-brand-yellow text-brand-black' : 'text-gray-300 hover:text-brand-yellow'
  }`;

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="border-b border-gray-800 bg-brand-dark">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-brand-yellow">K8sGen</span>
          <span className="hidden text-xs text-gray-500 sm:inline">Manifest Generator</span>
        </Link>

        {isAuthenticated && (
          <nav className="flex flex-wrap items-center gap-1">
            <NavLink to="/dashboard" className={navClass}>
              Dashboard
            </NavLink>
            <NavLink to="/upload" className={navClass}>
              Upload
            </NavLink>
            <NavLink to="/manifest" className={navClass}>
              Manifests
            </NavLink>
            <NavLink to="/validation" className={navClass}>
              Validation
            </NavLink>
          </nav>
        )}

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="hidden text-sm text-gray-400 sm:inline">{user?.username}</span>
              <button type="button" onClick={handleLogout} className="btn-secondary text-sm py-1.5">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-gray-300 hover:text-brand-yellow">
                Login
              </Link>
              <Link to="/register" className="btn-primary text-sm py-1.5">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
