import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Registry from './pages/Registry';
import EntityDetail from './pages/EntityDetail';
import ReviewQueue from './pages/ReviewQueue';
import QueryInterface from './pages/QueryInterface';
import GraphView from './pages/GraphView';
import AuditLog from './pages/AuditLog';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/registry" element={<Registry />} />
          <Route path="/registry/:ubidCode" element={<EntityDetail />} />
          <Route path="/review" element={<ReviewQueue />} />
          <Route path="/query" element={<QueryInterface />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="/audit" element={<AuditLog />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
