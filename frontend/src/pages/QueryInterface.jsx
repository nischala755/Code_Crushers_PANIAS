import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/client';

const EXAMPLES = [
  'Active factories in pincode 560058 with no inspection in 18 months',
  'Dormant businesses in Bengaluru',
  'High risk establishments in Mysuru',
  'Closed factories with pollution board records',
  'Active shops in pincode 570001',
];

export default function QueryInterface() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const runQuery = (q) => {
    const text = q || query;
    if (!text.trim()) return;
    setLoading(true);
    API.post('/query/', { query: text }).then(r => { setResult(r.data); setLoading(false); }).catch(() => setLoading(false));
  };

  return (
    <div>
      <h2 className="page-title">Query Interface</h2>

      <div className="query-box">
        <input className="form-input" placeholder="Enter natural language query..."
          value={query} onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && runQuery()} />
        <button className="btn btn-primary" onClick={() => runQuery()} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="mb-3">
        <div className="text-xs text-muted mb-2">Example queries:</div>
        <div className="query-examples">
          {EXAMPLES.map((ex, i) => (
            <span key={i} className="query-example" onClick={() => { setQuery(ex); runQuery(ex); }}>{ex}</span>
          ))}
        </div>
      </div>

      {result && (
        <>
          <div className="interpreted-as">
            <strong>Interpreted as:</strong> {result.interpreted_as}
          </div>

          <div className="card">
            <div className="card-header">Results ({result.result_count})</div>
            <div className="card-body" style={{ padding: 0 }}>
              <table className="data-table">
                <thead>
                  <tr><th>UBID</th><th>Business Name</th><th>City</th><th>Pincode</th><th>Depts</th><th>Activity</th><th>Risk</th><th>Confidence</th><th>Last Activity</th></tr>
                </thead>
                <tbody>
                  {result.results.length === 0 ? (
                    <tr><td colSpan={9} className="text-center text-muted" style={{ padding: 24 }}>No results found</td></tr>
                  ) : result.results.map(r => (
                    <tr key={r.ubid_code} className="clickable" onClick={() => navigate(`/registry/${r.ubid_code}`)}>
                      <td className="mono" style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{r.ubid_code}</td>
                      <td>{r.business_name}</td>
                      <td>{r.city}</td>
                      <td className="mono">{r.pincode}</td>
                      <td>{r.departments.map(d => <span className="tag" key={d}>{d.split('_')[0]}</span>)}</td>
                      <td><span className={`badge badge-${r.activity_status.toLowerCase()}`}>{r.activity_status}</span></td>
                      <td><span className={`badge badge-risk-${r.risk_level.toLowerCase()}`}>{r.risk_level}</span></td>
                      <td>{(r.confidence * 100).toFixed(0)}%</td>
                      <td className="mono text-xs">{r.last_activity || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {result.results.length > 0 && result.results[0].activity_reasoning && (
            <div className="card mt-4">
              <div className="card-header">Activity Reasoning (Top Result)</div>
              <div className="card-body text-sm" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
                {result.results[0].activity_reasoning}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
