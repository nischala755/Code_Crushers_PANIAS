import { useState, useEffect } from 'react';
import API from '../api/client';

export default function AuditLog() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    const params = { page, page_size: 50 };
    if (category) params.category = category;
    API.get('/audit/', { params }).then(r => { setEntries(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, [page, category]);

  return (
    <div>
      <div className="flex-between mb-3">
        <h2 className="page-title" style={{marginBottom:0}}>Audit Log</h2>
        <select className="form-select" value={category} onChange={e => { setCategory(e.target.value); setPage(1); }}>
          <option value="">All Categories</option>
          <option value="SYSTEM">System</option>
          <option value="REVIEW">Review</option>
          <option value="MERGE">Merge</option>
          <option value="QUERY">Query</option>
        </select>
      </div>

      <div className="card">
        <div className="card-body" style={{padding:0}}>
          <table className="data-table">
            <thead><tr><th>Timestamp</th><th>Action</th><th>Actor</th><th>UBID</th><th>Records</th><th>Details</th><th>Category</th></tr></thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center text-muted" style={{padding:24}}>Loading...</td></tr>
              ) : entries.length === 0 ? (
                <tr><td colSpan={7} className="text-center text-muted" style={{padding:24}}>No audit entries</td></tr>
              ) : entries.map(e => (
                <tr key={e.id}>
                  <td className="mono text-xs" style={{whiteSpace:'nowrap'}}>{e.timestamp ? new Date(e.timestamp).toLocaleString('en-IN') : '-'}</td>
                  <td className="text-xs">{e.action}</td>
                  <td className="text-xs">{e.actor}</td>
                  <td className="mono text-xs" style={{color:'var(--color-primary)'}}>{e.ubid_code || '-'}</td>
                  <td className="mono text-xs">{e.record_ids || '-'}</td>
                  <td className="text-xs" style={{maxWidth:300, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap'}}>{e.details}</td>
                  <td><span className="tag">{e.category}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="pagination">
        <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Prev</button>
        <span className="text-sm text-muted">Page {page}</span>
        <button onClick={() => setPage(p => p + 1)} disabled={entries.length < 50}>Next</button>
      </div>
    </div>
  );
}
