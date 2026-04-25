import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import FIRAnalyzer from './pages/FIRAnalyzer';
import CaseIntelligence from './pages/CaseIntelligence';
import LegalAssistant from './pages/LegalAssistant';
import MOPatterns from './pages/MOPatterns';
import Translation from './pages/Translation';
import Login from './pages/Login';
import Profile from './pages/Profile';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#0a0e1a',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }} />
          <div style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Verifying session...</div>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/fir-analyzer" element={<FIRAnalyzer />} />
        <Route path="/case-intelligence" element={<CaseIntelligence />} />
        <Route path="/legal-assistant" element={<LegalAssistant />} />
        <Route path="/mo-patterns" element={<MOPatterns />} />
        <Route path="/translation" element={<Translation />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
