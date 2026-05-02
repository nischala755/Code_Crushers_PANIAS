import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API from '../api/client';

function SignalBreakdown({ evidence }) {
  if (!evidence || evidence.length === 0) return null;
  const signals = [
    { key: 'pan_score', label: 'PAN' },
    { key: 'gstin_score', label: 'GSTIN' },
    { key: 'name_score', label: 'Name' },
    { key: 'address_score', label: 'Address' },
    { key: 'phone_score', label: 'Phone' },
  ];
  return (
    <div>
      {evidence.map((ev, idx) => (
        <div key={idx} style={{ marginBottom: 12 }}>
          <div className="text-xs text-muted mb-2">
            {ev.record_id_1} &harr; {ev.record_id_2}
            <span className={`badge badge-${ev.decision === 'AUTO_LINKED' ? 'auto' : 'review'}`} style={{ marginLeft: 8 }}>
              {ev.decision} ({(ev.weighted_score * 100).toFixed(0)}%)
            </span>
          </div>
          {signals.map(s => {
            const val = ev[s.key] || 0;
            const cls = val >= 0.8 ? 'high' : val >= 0.5 ? 'medium' : 'low';
            return (
              <div className="signal-bar-container" key={s.key}>
                <span className="signal-label">{s.label}</span>
                <div className="signal-bar-track"><div className={`signal-bar-fill ${cls}`} style={{ width: `${val * 100}%` }} /></div>
                <span className="signal-value">{(val * 100).toFixed(0)}%</span>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

export default function EntityDetail() {
  const { ubidCode } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    API.get(`/registry/${ubidCode}`).then(r => { setData(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, [ubidCode]);

  if (loading) return <div className="loading-spinner">Loading entity...</div>;
  if (!data) return <div className="empty-state">Entity not found</div>;

  const activity = data.activity || {};
  let signalsPresent = [], signalsMissing = [];
  try { signalsPresent = JSON.parse(activity.signals_present || '[]'); } catch {}
  try { signalsMissing = JSON.parse(activity.signals_missing || '[]'); } catch {}

  return (
    <div>
      <button className="btn btn-sm mb-3" onClick={() => navigate('/registry')}>&larr; Back to Registry</button>

      <div className="flex-between mb-3">
        <div>
          <h2 className="page-title" style={{ marginBottom: 2 }}>{data.primary_name}</h2>
          <span className="mono text-sm" style={{ color: 'var(--color-primary)' }}>{data.ubid_code}</span>
        </div>
        <div className="flex gap-2">
          <span className={`badge badge-${(data.activity_status || 'closed').toLowerCase()}`}>{data.activity_status}</span>
          <span className={`badge badge-risk-${(data.risk_level || 'low').toLowerCase()}`}>{data.risk_level}</span>
          <span className="badge badge-auto">{(data.confidence_score * 100).toFixed(0)}% confidence</span>
        </div>
      </div>

      <div className="detail-grid">
        <div className="card">
          <div className="card-header">Business Information</div>
          <div className="card-body">
            {[['Owner', data.primary_owner], ['PAN', data.primary_pan], ['GSTIN', data.primary_gstin],
              ['Phone', data.primary_phone], ['City', data.primary_city], ['Pincode', data.primary_pincode],
              ['Departments', data.department_count], ['Linked Records', data.record_count]].map(([l, v]) => (
              <div className="detail-row" key={l}>
                <span className="detail-label">{l}</span>
                <span className="detail-value">{v || '-'}</span>
              </div>
            ))}
            <div className="detail-row">
              <span className="detail-label">Address</span>
              <span className="detail-value">{data.primary_address || '-'}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">Activity Classification</div>
          <div className="card-body">
            <div className="detail-row">
              <span className="detail-label">Status</span>
              <span className={`badge badge-${(data.activity_status || 'closed').toLowerCase()}`}>{data.activity_status}</span>
            </div>
            {activity.last_activity_date && (
              <div className="detail-row">
                <span className="detail-label">Last Activity</span>
                <span className="detail-value">{activity.last_activity_date}</span>
              </div>
            )}
            {activity.days_since_activity > 0 && (
              <div className="detail-row">
                <span className="detail-label">Days Since</span>
                <span className="detail-value">{activity.days_since_activity} days</span>
              </div>
            )}
            <div className="mt-3 text-sm" style={{ color: 'var(--color-text-secondary)', lineHeight: 1.6 }}>
              {activity.reasoning}
            </div>
            <div className="mt-3">
              <div className="text-xs font-bold mb-2" style={{color:'var(--color-active)'}}>Signals Present</div>
              {signalsPresent.map(s => <span className="tag" key={s} style={{background:'#e6f5f0',color:'var(--color-active)',borderColor:'#a7d8c8'}}>{s}</span>)}
              {signalsPresent.length === 0 && <span className="text-xs text-muted">None</span>}
            </div>
            <div className="mt-2">
              <div className="text-xs font-bold mb-2" style={{color:'var(--color-risk-high)'}}>Signals Missing</div>
              {signalsMissing.map(s => <span className="tag" key={s} style={{background:'#fde8e8',color:'var(--color-risk-high)',borderColor:'#fca5a5'}}>{s}</span>)}
              {signalsMissing.length === 0 && <span className="text-xs text-muted">None</span>}
            </div>
          </div>
        </div>
      </div>

      <div className="detail-grid mt-4">
        <div className="card">
          <div className="card-header">Risk Intelligence</div>
          <div className="card-body">
            <div className="detail-row">
              <span className="detail-label">Risk Level</span>
              <span className={`badge badge-risk-${(data.risk_level || 'low').toLowerCase()}`}>{data.risk_level}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Risk Score</span>
              <span className="detail-value font-bold">{data.risk_score}/100</span>
            </div>
            {data.risk && data.risk.reasons && data.risk.reasons.map((r, i) => (
              <div key={i} className="text-sm mt-2" style={{color:'var(--color-text-secondary)'}}>- {r}</div>
            ))}
            {data.risk && data.risk.recommendation && (
              <div className="mt-3" style={{padding:'8px 12px', background:'#f8f9fa', border:'1px solid var(--color-border-light)'}}>
                <span className="text-xs font-bold" style={{color:'var(--color-primary)'}}>RECOMMENDATION: </span>
                <span className="text-sm">{data.risk.recommendation}</span>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">Match Evidence (Signal Breakdown)</div>
          <div className="card-body">
            {data.match_evidence && data.match_evidence.length > 0 ? (
              <SignalBreakdown evidence={data.match_evidence} />
            ) : (
              <div className="text-sm text-muted">Single-record UBID — no match evidence</div>
            )}
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">Linked Department Records</div>
        <div className="card-body" style={{padding:0}}>
          <table className="data-table">
            <thead>
              <tr><th>Record ID</th><th>Department</th><th>Business Name</th><th>PAN</th><th>GSTIN</th><th>Phone</th><th>License No.</th><th>Status</th></tr>
            </thead>
            <tbody>
              {(data.linked_records || []).map(r => (
                <tr key={r.record_id}>
                  <td className="mono">{r.record_id}</td>
                  <td className="text-xs">{r.department_display || r.department}</td>
                  <td>{r.business_name}</td>
                  <td className="mono">{r.pan || '-'}</td>
                  <td className="mono text-xs">{r.gstin || '-'}</td>
                  <td className="mono">{r.phone || '-'}</td>
                  <td className="mono text-xs">{r.license_number || '-'}</td>
                  <td><span className="badge badge-active">{r.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header">Activity Timeline</div>
        <div className="card-body" style={{padding:0, maxHeight:300, overflowY:'auto'}}>
          <table className="data-table">
            <thead><tr><th>Date</th><th>Event</th><th>Description</th><th>Dept</th></tr></thead>
            <tbody>
              {(data.events || []).map((e, i) => (
                <tr key={i}>
                  <td className="mono">{e.event_date}</td>
                  <td className="text-xs">{e.event_type}</td>
                  <td>{e.description}</td>
                  <td className="text-xs">{e.department}</td>
                </tr>
              ))}
              {(!data.events || data.events.length === 0) && (
                <tr><td colSpan={4} className="text-center text-muted">No events recorded</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
