import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import FIRAnalyzer from './pages/FIRAnalyzer';
import CaseIntelligence from './pages/CaseIntelligence';
import LegalAssistant from './pages/LegalAssistant';
import MOPatterns from './pages/MOPatterns';
import Translation from './pages/Translation';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/fir-analyzer" element={<FIRAnalyzer />} />
          <Route path="/case-intelligence" element={<CaseIntelligence />} />
          <Route path="/legal-assistant" element={<LegalAssistant />} />
          <Route path="/mo-patterns" element={<MOPatterns />} />
          <Route path="/translation" element={<Translation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
