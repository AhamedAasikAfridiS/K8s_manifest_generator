import { Navigate, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import ManifestViewer from './pages/ManifestViewer';
import Register from './pages/Register';
import Upload from './pages/Upload';
import ValidationResults from './pages/ValidationResults';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/upload"
        element={
          <ProtectedRoute>
            <Upload />
          </ProtectedRoute>
        }
      />
      <Route
        path="/manifest"
        element={
          <ProtectedRoute>
            <ManifestViewer />
          </ProtectedRoute>
        }
      />
      <Route
        path="/validation"
        element={
          <ProtectedRoute>
            <ValidationResults />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
