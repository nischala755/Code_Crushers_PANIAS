import { useState, useEffect } from 'react';
import API from '../api/client';
import { useNavigate } from 'react-router-dom';

const DEPT_LABELS = {
  SHOPS_ESTABLISHMENT: 'Shops & Establishment',
  FACTORIES: 'Factories & Boilers',
  LABOUR: 'Labour',
  POLLUTION_BOARD: 'Pollution Board',
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    API.get('/registry/stats').then(r => { setStats(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-spinner">Loading dashboard...</div>;
  if (!stats) return <div className="empty-state">Failed to load statistics</div>;

  return (
    <div>
      <h2 className="page-title">System Overview</h2>
      <div className="stats-row">
        <div className="stat-card" onClick={() => navigate('/registry')} style={{cursor:'pointer'}}>
          <div className="stat-label">Total UBIDs</div>
          <div className="stat-value primary">{stats.total_ubids}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Records</div>
          <div className="stat-value">{stats.total_records}</div>
        </div>
        <div className="stat-card" onClick={() => navigate('/review')} style={{cursor:'pointer'}}>
          <div className="stat-label">Pending Reviews</div>
          <div className="stat-value" style={{color: stats.pending_reviews > 0 ? '#b45309' : '#0f7b5f'}}>{stats.pending_reviews}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Auto-Linked</div>
          <div className="stat-value primary">{stats.auto_linked}</div>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">Active</div>
          <div className="stat-value active">{stats.active_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Dormant</div>
          <div className="stat-value dormant">{stats.dormant_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Closed</div>
          <div className="stat-value closed">{stats.closed_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">High Risk</div>
          <div className="stat-value risk-high">{stats.high_risk_count}</div>
        </div>
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'16px'}}>
        <div className="card">
          <div className="card-header">Department-wise Records</div>
          <div className="card-body">
            <table className="data-table">
              <thead><tr><th>Department</th><th style={{textAlign:'right'}}>Records</th></tr></thead>
              <tbody>
                {Object.entries(stats.department_counts || {}).map(([dept, count]) => (
                  <tr key={dept}>
                    <td>{DEPT_LABELS[dept] || dept}</td>
                    <td style={{textAlign:'right', fontWeight:600}}>{count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div className="card">
          <div className="card-header">Risk Distribution</div>
          <div className="card-body">
            <table className="data-table">
              <thead><tr><th>Risk Level</th><th style={{textAlign:'right'}}>Count</th></tr></thead>
              <tbody>
                <tr><td><span className="badge badge-risk-low">LOW</span></td><td style={{textAlign:'right', fontWeight:600}}>{stats.low_risk_count}</td></tr>
                <tr><td><span className="badge badge-risk-medium">MEDIUM</span></td><td style={{textAlign:'right', fontWeight:600}}>{stats.medium_risk_count}</td></tr>
                <tr><td><span className="badge badge-risk-high">HIGH</span></td><td style={{textAlign:'right', fontWeight:600}}>{stats.high_risk_count}</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
