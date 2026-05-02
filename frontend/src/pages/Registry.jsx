import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/client';

export default function Registry() {
  const [ubids, setUbids] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ activity_status: '', risk_level: '', search: '', department: '' });
  const navigate = useNavigate();
  const pageSize = 30;

  const fetchData = () => {
    setLoading(true);
    const params = { page, page_size: pageSize };
    if (filters.activity_status) params.activity_status = filters.activity_status;
    if (filters.risk_level) params.risk_level = filters.risk_level;
    if (filters.search) params.search = filters.search;
    if (filters.department) params.department = filters.department;

    Promise.all([
      API.get('/registry/', { params }),
      API.get('/registry/count', { params }),
    ]).then(([r1, r2]) => {
      setUbids(r1.data);
      setTotal(r2.data.count);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [page, filters]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      <div className="flex-between mb-3">
        <h2 className="page-title" style={{marginBottom:0}}>UBID Registry (State Identity Layer)</h2>
        <span className="text-muted text-sm">{total} records</span>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Search</label>
          <input className="form-input" placeholder="UBID, name, PAN..." value={filters.search}
            onChange={e => { setFilters({...filters, search: e.target.value}); setPage(1); }}
            style={{width:200}} />
        </div>
        <div className="form-group">
          <label>Status</label>
          <select className="form-select" value={filters.activity_status}
            onChange={e => { setFilters({...filters, activity_status: e.target.value}); setPage(1); }}>
            <option value="">All</option>
            <option value="ACTIVE">Active</option>
            <option value="DORMANT">Dormant</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
        <div className="form-group">
          <label>Risk</label>
          <select className="form-select" value={filters.risk_level}
            onChange={e => { setFilters({...filters, risk_level: e.target.value}); setPage(1); }}>
            <option value="">All</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>
        </div>
        <div className="form-group">
          <label>Department</label>
          <select className="form-select" value={filters.department}
            onChange={e => { setFilters({...filters, department: e.target.value}); setPage(1); }}>
            <option value="">All</option>
            <option value="SHOPS_ESTABLISHMENT">Shops & Establishment</option>
            <option value="FACTORIES">Factories</option>
            <option value="LABOUR">Labour</option>
            <option value="POLLUTION_BOARD">Pollution Board</option>
          </select>
        </div>
      </div>

      <div className="card">
        <table className="data-table">
          <thead>
            <tr>
              <th>UBID</th>
              <th>Business Name</th>
              <th>City</th>
              <th>Depts</th>
              <th>Records</th>
              <th>Confidence</th>
              <th>Activity</th>
              <th>Risk</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center text-muted" style={{padding:24}}>Loading...</td></tr>
            ) : ubids.length === 0 ? (
              <tr><td colSpan={8} className="text-center text-muted" style={{padding:24}}>No results found</td></tr>
            ) : ubids.map(u => (
              <tr key={u.ubid_code} className="clickable" onClick={() => navigate(`/registry/${u.ubid_code}`)}>
                <td className="mono" style={{fontWeight:600, color:'var(--color-primary)'}}>{u.ubid_code}</td>
                <td>{u.primary_name}</td>
                <td>{u.primary_city}</td>
                <td style={{textAlign:'center'}}>{u.department_count}</td>
                <td style={{textAlign:'center'}}>{u.record_count}</td>
                <td><span className={`badge ${u.confidence_score >= 0.85 ? 'badge-active' : u.confidence_score >= 0.6 ? 'badge-dormant' : 'badge-closed'}`}>
                  {(u.confidence_score * 100).toFixed(0)}%</span></td>
                <td><span className={`badge badge-${(u.activity_status || 'closed').toLowerCase()}`}>{u.activity_status}</span></td>
                <td><span className={`badge badge-risk-${(u.risk_level || 'low').toLowerCase()}`}>{u.risk_level}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Prev</button>
          <span className="text-sm text-muted">Page {page} of {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
        </div>
      )}
    </div>
  );
}
