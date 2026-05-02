import { NavLink, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: 'grid' },
  { path: '/registry', label: 'UBID Registry', icon: 'database' },
  { path: '/review', label: 'Review Queue', icon: 'check-square' },
  { path: '/query', label: 'Query Interface', icon: 'search' },
  { path: '/graph', label: 'Graph View', icon: 'share-2' },
  { path: '/audit', label: 'Audit Log', icon: 'file-text' },
];

const ICONS = {
  'grid': <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>,
  'database': <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>,
  'check-square': <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>,
  'search': <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>,
  'share-2': <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>,
  'file-text': <svg className="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>,
};

export default function Layout({ children }) {
  const location = useLocation();
  const current = NAV_ITEMS.find(n => n.path === location.pathname) || NAV_ITEMS[0];

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>UBID Mesh</h1>
          <div className="subtitle">Karnataka State Platform</div>
        </div>
        <nav className="sidebar-nav">
          <div className="sidebar-section">Navigation</div>
          {NAV_ITEMS.map(item => (
            <NavLink key={item.path} to={item.path} className={({ isActive }) => isActive ? 'active' : ''} end={item.path === '/'}>
              {ICONS[item.icon]}
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div style={{ padding: '12px 16px', borderTop: '1px solid rgba(255,255,255,0.08)', fontSize: '0.65rem', color: 'rgba(255,255,255,0.25)' }}>
          v1.0.0 | Govt. of Karnataka
        </div>
      </aside>
      <main className="main-content">
        <header className="top-header">
          <div className="breadcrumb">
            UBID Mesh / <strong> {current.label}</strong>
          </div>
          <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
            Unified Business Identity & Active Intelligence Platform
          </div>
        </header>
        <div className="page-content">
          {children}
        </div>
      </main>
    </div>
  );
}
