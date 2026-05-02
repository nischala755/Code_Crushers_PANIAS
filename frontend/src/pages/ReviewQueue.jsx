import { useState, useEffect } from 'react';
import API from '../api/client';

export default function ReviewQueue() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [deciding, setDeciding] = useState(false);
  const [learningResult, setLearningResult] = useState(null);

  const fetchQueue = () => {
    setLoading(true);
    API.get('/review/queue').then(r => { setQueue(r.data); setLoading(false); }).catch(() => setLoading(false));
  };

  useEffect(() => { fetchQueue(); }, []);

  const openDetail = (evidenceId) => {
    setSelectedId(evidenceId);
    setLearningResult(null);
    API.get(`/review/${evidenceId}`).then(r => setDetail(r.data));
  };

  const submitDecision = (decision) => {
    setDeciding(true);
    API.post(`/review/${selectedId}/decide`, { decision, reason: `Reviewer ${decision.toLowerCase()} the match`, reviewer: 'REVIEWER' })
      .then(r => {
        setLearningResult(r.data);
        setDeciding(false);
        fetchQueue();
      })
      .catch(() => setDeciding(false));
  };

  const signals = [
    { key: 'pan_score', label: 'PAN Match' },
    { key: 'gstin_score', label: 'GSTIN Match' },
    { key: 'name_score', label: 'Name Similarity' },
    { key: 'address_score', label: 'Address Similarity' },
    { key: 'phone_score', label: 'Phone Match' },
  ];

  return (
    <div>
      <h2 className="page-title">Review Queue</h2>

      <div className="card">
        <div className="card-header">Pending Review Pairs ({queue.length})</div>
        <div className="card-body" style={{ padding: 0 }}>
          <table className="data-table">
            <thead><tr><th>#</th><th>Record 1</th><th>Record 2</th><th>Business 1</th><th>Business 2</th><th>Score</th><th>Action</th></tr></thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="text-center text-muted" style={{ padding: 24 }}>Loading...</td></tr>
              ) : queue.length === 0 ? (
                <tr><td colSpan={7} className="text-center text-muted" style={{ padding: 24 }}>No pending reviews</td></tr>
              ) : queue.map((item, i) => (
                <tr key={item.evidence_id}>
                  <td>{i + 1}</td>
                  <td className="mono text-xs">{item.record_id_1}</td>
                  <td className="mono text-xs">{item.record_id_2}</td>
                  <td>{item.name_1}</td>
                  <td>{item.name_2}</td>
                  <td><span className="badge badge-review">{(item.weighted_score * 100).toFixed(0)}%</span></td>
                  <td><button className="btn btn-sm btn-primary" onClick={() => openDetail(item.evidence_id)}>Review</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {detail && (
        <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) { setSelectedId(null); setDetail(null); setLearningResult(null); } }}>
          <div className="modal-content">
            <div className="modal-header">
              <h3>Review: {detail.record_1.business_name} vs {detail.record_2.business_name}</h3>
              <button className="modal-close" onClick={() => { setSelectedId(null); setDetail(null); setLearningResult(null); }}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="compare-grid">
                {[detail.record_1, detail.record_2].map((rec, idx) => (
                  <div className="card" key={idx}>
                    <div className="card-header">Record {idx + 1}: {rec.department_display || rec.department}</div>
                    <div className="card-body">
                      {[['Record ID', rec.record_id], ['Business Name', rec.business_name],
                        ['PAN', rec.pan], ['GSTIN', rec.gstin], ['Phone', rec.phone],
                        ['Address', rec.address], ['License', rec.license_number]].map(([l, v]) => (
                        <div className="detail-row" key={l}>
                          <span className="detail-label">{l}</span>
                          <span className="detail-value">{v || '-'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="card mt-3">
                <div className="card-header">Signal Breakdown</div>
                <div className="card-body">
                  {signals.map(s => {
                    const val = detail.evidence[s.key] || 0;
                    const cls = val >= 0.8 ? 'high' : val >= 0.5 ? 'medium' : 'low';
                    return (
                      <div className="signal-bar-container" key={s.key}>
                        <span className="signal-label">{s.label}</span>
                        <div className="signal-bar-track"><div className={`signal-bar-fill ${cls}`} style={{ width: `${val * 100}%` }} /></div>
                        <span className="signal-value">{(val * 100).toFixed(0)}%</span>
                      </div>
                    );
                  })}
                  <div className="mt-2" style={{ borderTop: '1px solid var(--color-border-light)', paddingTop: 8 }}>
                    <div className="signal-bar-container">
                      <span className="signal-label" style={{ fontWeight: 700 }}>TOTAL</span>
                      <div className="signal-bar-track" style={{ height: 18 }}><div className="signal-bar-fill" style={{ width: `${(detail.evidence.weighted_score || 0) * 100}%`, background: 'var(--color-primary)' }} /></div>
                      <span className="signal-value" style={{ fontWeight: 700 }}>{((detail.evidence.weighted_score || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {learningResult && learningResult.success && (
                <div className="learning-banner mt-3">
                  <div className="learning-title">System Learning: Confidence improved for similar cases</div>
                  <div className="learning-detail">
                    The system has adjusted matching weights based on your decision. Future similar pairs will benefit from this feedback.
                  </div>
                  <div className="confidence-change">
                    <span className="text-xs font-bold">Confidence:</span>
                    <span className="before">{((learningResult.confidence_before || 0) * 100).toFixed(1)}%</span>
                    <span className="arrow">&rarr;</span>
                    <span className="after">{((learningResult.confidence_after || 0) * 100).toFixed(1)}%</span>
                  </div>
                  {learningResult.weight_changes && (
                    <div className="mt-2 text-xs text-muted">
                      Weight adjustments: {Object.entries(learningResult.weight_changes.after || {}).map(([k, v]) => `${k}: ${(v * 100).toFixed(1)}%`).join(' | ')}
                    </div>
                  )}
                </div>
              )}
            </div>
            {!learningResult && (
              <div className="modal-footer">
                <button className="btn btn-success" disabled={deciding} onClick={() => submitDecision('CONFIRMED')}>
                  {deciding ? 'Processing...' : 'Confirm Merge'}
                </button>
                <button className="btn btn-danger" disabled={deciding} onClick={() => submitDecision('REJECTED')}>Reject</button>
                <button className="btn" disabled={deciding} onClick={() => submitDecision('DEFERRED')}>Defer</button>
              </div>
            )}
            {learningResult && (
              <div className="modal-footer">
                <button className="btn btn-primary" onClick={() => { setSelectedId(null); setDetail(null); setLearningResult(null); }}>Close</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
