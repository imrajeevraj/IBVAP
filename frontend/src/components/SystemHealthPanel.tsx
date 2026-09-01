import { useEffect, useState } from 'react';

interface Health {
  status: string;
  cpu: { percent: number };
  memory: { percent: number; used_mb: number; total_mb: number };
  gpu?: { percent: number; vram_used_mb: number; vram_total_mb: number; name: string };
  database_status: string;
  cameras: { online: number; total: number; inference_fps: number; stale: string[] };
  anpr: { queue_depth: number };
}

function barClass(value: number): string {
  if (value >= 90) return 'critical';
  if (value >= 70) return 'warning';
  return 'ok';
}

export function SystemHealthPanel({ apiBase }: { apiBase: string }) {
  const [health, setHealth] = useState<Health | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await fetch(`${apiBase}/api/system/health/detailed`, { credentials: 'include' });
        if (response.ok) setHealth(await response.json());
      } catch { /* silent */ }
    };
    void load();
    const timer = window.setInterval(() => void load(), 5000);
    return () => window.clearInterval(timer);
  }, [apiBase]);

  if (!health) {
    return (
      <div className="health-section">
        <div className="empty-state">
          <span className="empty-state-sub">Loading system health…</span>
        </div>
      </div>
    );
  }

  const statusClass = health.status === 'HEALTHY' ? 'ok' : health.status === 'DEGRADED' ? 'warning' : 'error';
  const ramPercent = health.memory.percent;
  const cpuPercent = health.cpu.percent;
  const gpuPercent = health.gpu?.percent ?? 0;
  const vramPercent = health.gpu ? Math.round((health.gpu.vram_used_mb / health.gpu.vram_total_mb) * 100) : 0;

  const staleText = health.cameras.stale.length
    ? `AI results stale: ${health.cameras.stale.join(', ')}`
    : 'All AI results current';

  // Determine degradation reason
  let degradeReason = '';
  if (health.status !== 'HEALTHY') {
    if (ramPercent >= 90) degradeReason = `RAM usage elevated at ${ramPercent}%`;
    else if (cpuPercent >= 90) degradeReason = `CPU usage elevated at ${cpuPercent}%`;
    else if (health.cameras.stale.length > 0) degradeReason = `Stale AI results on ${health.cameras.stale.length} camera(s)`;
    else degradeReason = 'Performance below optimal thresholds';
  }

  return (
    <div className="health-section">
      {/* Overall Status */}
      <div className="health-status-bar">
        <span className="health-status-label">System Status</span>
        <span className={`health-status-value ${statusClass}`}>{health.status}</span>
      </div>

      {degradeReason && (
        <div className={`health-stale-warn warning`}>
          {degradeReason}
        </div>
      )}

      {/* Progress Bar Metrics */}
      <div className="health-metrics">
        <div className="health-metric">
          <span className="health-metric-label">CPU</span>
          <div className="health-bar-track">
            <div className={`health-bar-fill ${barClass(cpuPercent)}`} style={{ width: `${cpuPercent}%` }} />
          </div>
          <span className="health-metric-value">{cpuPercent}%</span>
        </div>

        <div className="health-metric">
          <span className="health-metric-label">RAM</span>
          <div className="health-bar-track">
            <div className={`health-bar-fill ${barClass(ramPercent)}`} style={{ width: `${ramPercent}%` }} />
          </div>
          <span className="health-metric-value">{ramPercent}%</span>
        </div>

        {health.gpu && (
          <>
            <div className="health-metric">
              <span className="health-metric-label">GPU</span>
              <div className="health-bar-track">
                <div className={`health-bar-fill ${barClass(gpuPercent)}`} style={{ width: `${gpuPercent}%` }} />
              </div>
              <span className="health-metric-value">{gpuPercent}%</span>
            </div>

            <div className="health-metric">
              <span className="health-metric-label">VRAM</span>
              <div className="health-bar-track">
                <div className={`health-bar-fill ${barClass(vramPercent)}`} style={{ width: `${vramPercent}%` }} />
              </div>
              <span className="health-metric-value">{vramPercent}%</span>
            </div>
          </>
        )}
      </div>

      {/* Detail Grid */}
      <div className="health-detail-grid">
        <div className="health-detail">
          <span className="health-detail-label">Cameras</span>
          <span className="health-detail-value">{health.cameras.online}/{health.cameras.total}</span>
        </div>
        <div className="health-detail">
          <span className="health-detail-label">AI FPS</span>
          <span className="health-detail-value">{health.cameras.inference_fps}</span>
        </div>
        <div className="health-detail">
          <span className="health-detail-label">ANPR Queue</span>
          <span className="health-detail-value">{health.anpr.queue_depth}</span>
        </div>
        <div className="health-detail">
          <span className="health-detail-label">Database</span>
          <span className="health-detail-value">{health.database_status}</span>
        </div>
        {health.gpu && (
          <div className="health-detail" style={{ gridColumn: '1 / -1' }}>
            <span className="health-detail-label">GPU</span>
            <span className="health-detail-value" style={{ fontSize: 'var(--text-xs)' }}>{health.gpu.name}</span>
          </div>
        )}
      </div>

      {/* Stale Warning */}
      <div className={`health-stale-warn ${health.cameras.stale.length ? 'warning' : 'ok'}`}>
        {staleText}
      </div>
    </div>
  );
}
