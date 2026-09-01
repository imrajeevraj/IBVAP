import React, { useState } from 'react';
import type { Camera } from '../types';
import { VideoOff } from 'lucide-react';

interface CameraGridProps {
  cameras: Camera[];
  selectedCamera: Camera | null;
  onSelectCamera: (camera: Camera) => void;
  onFocusCamera: (camera: Camera) => void;
}

export const CameraGrid: React.FC<CameraGridProps> = ({
  cameras,
  selectedCamera,
  onSelectCamera,
  onFocusCamera,
}) => {
  const [refreshKeys] = useState<Record<string, number>>({});
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  if (cameras.length === 0) {
    return (
      <div className="video-empty">
        <VideoOff size={36} style={{ opacity: 0.3 }} />
        <span className="empty-state-title">No Cameras Available</span>
        <span className="empty-state-sub">No active cameras in directory.</span>
      </div>
    );
  }

  return (
    <div className="camera-grid">
      {cameras.map(camera => {
        const isSelected = selectedCamera?.id === camera.id;
        const key = refreshKeys[camera.id] || 0;
        const streamUrl = `${apiBase}/api/cameras/${camera.id}/stream?k=${key}`;
        const personCount = new Set(camera.detections?.filter(d => d.class === 'person' && d.track_id).map(d => d.track_id)).size;
        const vehicleCount = new Set(camera.detections?.filter(d => d.class !== 'person' && d.track_id).map(d => d.track_id)).size;
        const statusClass = camera.status.toLowerCase();
        const aiStale = (camera.ai_result_age_seconds ?? 0) > 5;

        return (
          <div
            key={camera.id}
            className={`grid-tile ${isSelected ? 'selected' : ''}`}
            onClick={() => { onSelectCamera(camera); onFocusCamera(camera); }}
            role="button"
            tabIndex={0}
            aria-label={`${camera.name} - ${camera.status}`}
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { onSelectCamera(camera); onFocusCamera(camera); } }}
          >
            {/* Top bar overlay */}
            <div className="grid-tile-bar">
              <div className="tile-label">
                <span className={`cam-status-dot ${statusClass}`} />
                <span>{camera.id}</span>
              </div>
              <div className="tile-meta">
                <span>{camera.status === 'ONLINE' ? `${camera.fps} FPS` : camera.status}</span>
              </div>
            </div>

            {/* Video */}
            <div className="grid-tile-viewer">
              {camera.status === 'ONLINE' || camera.status === 'DEGRADED' ? (
                <img src={streamUrl} alt={camera.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
              ) : (
                <div className="grid-offline">
                  <VideoOff size={28} style={{ color: 'var(--status-offline)', opacity: 0.5 }} />
                  <span>{camera.status}</span>
                </div>
              )}
            </div>

            {/* HUD badges */}
            {(camera.status === 'ONLINE' || camera.status === 'DEGRADED') && (
              <div className="grid-tile-hud">
                <div className="hud-tag live"><span className="live-dot" />LIVE</div>
                {personCount > 0 && <div className="hud-tag" style={{ color: 'var(--status-info)' }}>P:{personCount}</div>}
                {vehicleCount > 0 && <div className="hud-tag" style={{ color: 'var(--status-info)' }}>V:{vehicleCount}</div>}
                {camera.inference_fps !== undefined && camera.inference_fps > 0 && (
                  <div className={`hud-tag ${aiStale ? 'stale' : 'ai-active'}`}>
                    {aiStale ? 'AI:STALE' : `AI:${camera.inference_fps}fps`}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
