import { useState, useEffect } from 'react';
import type { Camera, Alert, SystemStats, GPSLocation } from './types';
import { MissionHeader } from './components/MissionHeader';
import { CameraDirectory } from './components/CameraDirectory';
import { SurveillanceWorkspace } from './components/SurveillanceWorkspace';
import { IntelligencePanel, DEFAULT_FILTERS } from './components/IntelligencePanel';
import type { EventFilters } from './components/IntelligencePanel';
import { OperationalStrip } from './components/OperationalStrip';

function App() {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // ── Auth State ──────────────────────────────────────────
  const [authenticated, setAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  // ── Data State ──────────────────────────────────────────
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<SystemStats>({
    cameras_online: 0, total_cameras: 0,
    person_detections: 0, vehicle_detections: 0,
    active_alerts: 0, critical_alerts: 0,
  });
  const [filters, setFilters] = useState<EventFilters>(DEFAULT_FILTERS);
  const [dataOrigin, setDataOrigin] = useState<'LIVE' | 'DEMO' | 'IMPORTED'>('LIVE');
  const [bopLocation, setBopLocation] = useState<GPSLocation | null>(null);

  // ── UI State ────────────────────────────────────────────
  const [viewMode, setViewMode] = useState<'focus' | 'grid2x2' | 'map'>('focus');
  const [time, setTime] = useState('');

  // ── Derived State ───────────────────────────────────────
  const systemStatus: 'operational' | 'degraded' | 'critical' = 
    stats.critical_alerts > 0 ? 'critical' :
    stats.cameras_online < stats.total_cameras ? 'degraded' : 'operational';

  // ── Clock ───────────────────────────────────────────────
  useEffect(() => {
    const tick = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) +
        ' · ' +
        now.toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })
      );
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  // ── Sync alert counts ──────────────────────────────────
  useEffect(() => {
    const active = alerts.filter(a => a.status === 'NEW').length;
    const critical = alerts.filter(a => a.status === 'NEW' && a.severity === 'CRITICAL').length;
    setStats(prev => ({ ...prev, active_alerts: active, critical_alerts: critical }));
  }, [alerts]);

  // ── Auth Check ──────────────────────────────────────────
  useEffect(() => {
    fetch(`${apiBase}/api/auth/me`, { credentials: 'include' })
      .then(async res => {
        setAuthenticated(res.ok);
        if (res.ok) { const me = await res.json(); setUsername(me.username); setRole(me.role); }
      })
      .catch(() => setAuthenticated(false))
      .finally(() => setAuthChecked(true));
  }, [apiBase]);

  // ── Data Fetching ───────────────────────────────────────
  useEffect(() => {
    if (!authenticated) return;
    fetchCameras();
    fetchEvents();

    const wsUrl = apiBase.replace('http', 'ws') + '/ws/events';
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'NEW_ALERT' || msg.type === 'ALERT_UPDATED') fetchEvents();
        if (msg.event_type === 'gps_update' && msg.data?.bop_location) {
          setBopLocation(msg.data.bop_location);
        }
      } catch (e) { console.error("WS error", e); }
    };

    const interval = setInterval(fetchCameras, 2000);
    return () => { clearInterval(interval); ws.close(); };
  }, [authenticated, selectedCamera?.id, filters, dataOrigin]);

  const fetchCameras = async () => {
    try {
      const response = await fetch(`${apiBase}/api/cameras`, { credentials: 'include' });
      if (response.status === 401) { setAuthenticated(false); return; }
      if (!response.ok) return;
      const data: Camera[] = await response.json();
      setCameras(data);

      if (selectedCamera) {
        const updated = data.find(c => c.id === selectedCamera.id);
        if (updated) setSelectedCamera(updated);
      } else if (data.length > 0) {
        setSelectedCamera(data[0]);
      }

      const onlineCount = data.filter(c => c.status === 'ONLINE').length;
      let persons = 0, vehicles = 0;
      data.forEach(c => {
        if (c.detections) {
          persons += new Set(c.detections.filter(d => d.class === 'person' && d.track_id).map(d => d.track_id)).size;
          vehicles += new Set(c.detections.filter(d => d.class !== 'person' && d.track_id).map(d => d.track_id)).size;
        }
      });
      setStats(prev => ({ ...prev, cameras_online: onlineCount, total_cameras: data.length, person_detections: persons, vehicle_detections: vehicles }));
    } catch (error) { console.error('Failed to fetch cameras:', error); }
  };

  const fetchEvents = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.cameraId !== 'ALL') params.append('camera_id', filters.cameraId);
      if (filters.severity !== 'ALL') params.append('severity', filters.severity);
      if (filters.eventType !== 'ALL') params.append('event_type', filters.eventType);
      if (filters.status !== 'ALL') params.append('status', filters.status);
      params.append('data_origin', dataOrigin);
      if (filters.timeRange !== 'all') {
        const now = new Date();
        const mins = filters.timeRange === '1h' ? 60 : filters.timeRange === '24h' ? 1440 : 15;
        params.append('start_time', new Date(now.getTime() - mins * 60000).toISOString());
      }
      const qs = params.toString();
      const response = await fetch(`${apiBase}/api/events/recent${qs ? `?${qs}` : ''}`, { credentials: 'include' });
      if (response.status === 401) { setAuthenticated(false); return; }
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.filter((evt: Alert) => evt.status !== 'DISMISSED'));
      }
    } catch (error) { console.error('Failed to fetch events:', error); }
  };

  // ── Alert Actions ───────────────────────────────────────
  const updateAlertDisposition = async (alertId: string, status: 'ACKNOWLEDGED' | 'DISMISSED' | 'ESCALATED') => {
    const response = await fetch(`${apiBase}/api/events/${alertId.replace('evt-', '')}/disposition`, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' },
      credentials: 'include', body: JSON.stringify({ status }),
    });
    if (response.ok) setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status } : a));
  };

  // ── Auth Actions ────────────────────────────────────────
  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoginError('');
    try {
      const response = await fetch(`${apiBase}/api/auth/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        credentials: 'include', body: new URLSearchParams({ username, password }),
      });
      if (!response.ok) { setLoginError('Invalid credentials'); return; }
      const data = await response.json();
      setAuthenticated(true); setUsername(data.username || username); setRole(data.role || ''); setPassword('');
    } catch { setLoginError('Backend unavailable'); }
  };

  const handleLogout = async () => {
    try { await fetch(`${apiBase}/api/auth/logout`, { method: 'POST', credentials: 'include' }); } catch {}
    setAuthenticated(false); setCameras([]); setSelectedCamera(null); setAlerts([]); setUsername(''); setRole('');
  };

  const runDemoScenario = async (scenario: 'seed-intrusion' | 'seed-watchlist') => {
    const response = await fetch(`${apiBase}/api/demo/${scenario}`, { method: 'POST', credentials: 'include' });
    if (response.ok) { setDataOrigin('DEMO'); return; }
    const data = await response.json().catch(() => ({}));
    setLoginError(data.detail || 'Demo camera is not ready yet');
  };

  // ── Pre-render Guards ───────────────────────────────────
  if (!authChecked) return null;

  // ── Login Screen ────────────────────────────────────────
  if (!authenticated) {
    return (
      <main className="login-screen">
        <div className="login-modal">
          <div className="login-header">
            <div className="login-brand">IBVAP <span>Command Center</span></div>
            <p className="login-subtitle">Intelligent Border Visual Analytics Platform</p>
          </div>
          <form className="login-form" onSubmit={handleLogin}>
            <div className="form-group">
              <label className="form-label" htmlFor="login-username">Operator Username</label>
              <input
                className="form-input" id="login-username" type="text"
                value={username} onChange={e => setUsername(e.target.value)}
                placeholder="e.g. ibvap-admin" required autoFocus
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="login-password">Password</label>
              <input
                className="form-input" id="login-password" type="password"
                value={password} onChange={e => setPassword(e.target.value)}
                placeholder="Enter password" required
              />
            </div>
            {loginError && <p className="login-error" role="alert">{loginError}</p>}
            <button className="btn btn-primary login-submit" type="submit">Sign In to Console</button>
          </form>
          <div className="login-footer">
            <span>Restricted Access · Authorized Defense & Surveillance Personnel Only</span>
          </div>
        </div>
      </main>
    );
  }

  // ── Main Application Shell ──────────────────────────────
  return (
    <div className="app-shell">
      <MissionHeader
        time={time}
        username={username}
        role={role}
        stats={stats}
        dataOrigin={dataOrigin}
        systemStatus={systemStatus}
        onLogout={handleLogout}
      />

      <div className="workspace">
        <CameraDirectory
          cameras={cameras}
          selectedCamera={selectedCamera}
          onSelectCamera={setSelectedCamera}
        />

        <SurveillanceWorkspace
          viewMode={viewMode}
          setViewMode={setViewMode}
          selectedCamera={selectedCamera}
          cameras={cameras}
          onSelectCamera={setSelectedCamera}
          bopLocation={bopLocation}
        />

        <IntelligencePanel
          alerts={alerts}
          cameras={cameras}
          selectedCamera={selectedCamera}
          apiBase={apiBase}
          dataOrigin={dataOrigin}
          filters={filters}
          setFilters={setFilters}
          onAcknowledge={(id) => void updateAlertDisposition(id, 'ACKNOWLEDGED')}
          onDismiss={(id) => void updateAlertDisposition(id, 'DISMISSED')}
          onEscalate={(id) => void updateAlertDisposition(id, 'ESCALATED')}
        />
      </div>

      <OperationalStrip
        stats={stats}
        dataOrigin={dataOrigin}
        onToggleDataOrigin={() => {
          setDataOrigin(d => d === 'LIVE' ? 'DEMO' : d === 'DEMO' ? 'IMPORTED' : 'LIVE');
        }}
        onRunDemo={runDemoScenario}
      />
    </div>
  );
}

export default App;
