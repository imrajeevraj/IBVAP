import React, { useState } from 'react';
import type { SystemStats } from '../types';
import { ChevronUp, UploadCloud } from 'lucide-react';
import { AuditUploadModal } from './AuditUploadModal';

interface OperationalStripProps {
  stats: SystemStats;
  dataOrigin: 'LIVE' | 'DEMO' | 'IMPORTED';
  onToggleDataOrigin: () => void;
  onRunDemo: (scenario: 'seed-intrusion' | 'seed-watchlist') => void;
}

export const OperationalStrip: React.FC<OperationalStripProps> = ({
  stats,
  dataOrigin,
  onToggleDataOrigin,
  onRunDemo,
}) => {
  const [showSimControls, setShowSimControls] = useState(false);
  const [showAuditModal, setShowAuditModal] = useState(false);
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  return (
    <>
    <footer className="operational-strip" role="contentinfo">
      <div className="strip-metrics">
        <div className="strip-metric">
          <span className="strip-metric-label">Cameras</span>
          <span className={`strip-metric-value ${stats.cameras_online === stats.total_cameras ? 'healthy' : 'warning'}`}>
            {stats.cameras_online}/{stats.total_cameras}
          </span>
        </div>

        <span className="strip-separator" />

        <div className="strip-metric">
          <span className="strip-metric-label">Persons</span>
          <span className="strip-metric-value">{String(stats.person_detections).padStart(2, '0')}</span>
        </div>

        <div className="strip-metric">
          <span className="strip-metric-label">Vehicles</span>
          <span className="strip-metric-value">{String(stats.vehicle_detections).padStart(2, '0')}</span>
        </div>

        <span className="strip-separator" />

        <div className="strip-metric">
          <span className="strip-metric-label">Active Alerts</span>
          <span className={`strip-metric-value ${stats.active_alerts > 0 ? 'warning' : ''}`}>
            {stats.active_alerts}
          </span>
        </div>

        <div className="strip-metric">
          <span className="strip-metric-label">Critical</span>
          <span className={`strip-metric-value ${stats.critical_alerts > 0 ? 'critical' : ''}`}>
            {stats.critical_alerts}
          </span>
        </div>

        <span className="strip-separator" />

        <div className="strip-metric">
          <span className="strip-metric-label">AI Engine</span>
          <span className="strip-metric-value" style={{ color: 'var(--accent)' }}>RF-DETR</span>
        </div>
      </div>

      <div className="strip-right">
        <div className="strip-metric">
          <span className="strip-metric-label">Data</span>
          <span className={`strip-metric-value ${dataOrigin === 'DEMO' ? 'warning' : 'healthy'}`}>
            {dataOrigin}
          </span>
        </div>

        <div className="demo-controls flex items-center gap-2">
          <button 
            className="btn btn-sm flex items-center gap-2"
            onClick={() => setShowAuditModal(true)}
            title="Upload Offline Video"
          >
            <UploadCloud size={14} />
            Offline Audit
          </button>
        </div>

        {/* Simulation Controls */}
        <div className="sim-controls">
          <button
            className="btn btn-sm"
            onClick={() => setShowSimControls(prev => !prev)}
            title="Simulation controls"
          >
            <ChevronUp size={11} style={{ transform: showSimControls ? 'rotate(180deg)' : undefined, transition: 'transform 0.2s' }} />
            Sim
          </button>
          {showSimControls && (
            <div className="sim-dropdown">
              <button className="btn btn-sm" onClick={() => { onRunDemo('seed-intrusion'); setShowSimControls(false); }}>
                Demo Intrusion
              </button>
              <button className="btn btn-sm" onClick={() => { onRunDemo('seed-watchlist'); setShowSimControls(false); }}>
                Demo ANPR
              </button>
              <button className="btn btn-sm" onClick={() => { onToggleDataOrigin(); setShowSimControls(false); }}>
                Cycle Data Source (Currently {dataOrigin})
              </button>
            </div>
          )}
        </div>
      </div>
    </footer>
    {showAuditModal && (
      <AuditUploadModal 
        onClose={() => setShowAuditModal(false)}
        apiBase={apiBase}
      />
    )}
    </>
  );
};
