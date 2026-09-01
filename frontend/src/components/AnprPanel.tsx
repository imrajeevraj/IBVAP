import React, { useState, useEffect } from 'react';
import type { PlateEvent } from '../types';
import { Car } from 'lucide-react';

interface Props {
  apiBase: string;
  dataOrigin: 'LIVE' | 'DEMO' | 'IMPORTED';
}

export const AnprPanel: React.FC<Props> = ({ apiBase, dataOrigin }) => {
  const [plates, setPlates] = useState<PlateEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPlates = async () => {
    try {
      const res = await fetch(`${apiBase}/api/anpr/plates?data_origin=${dataOrigin}`, {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setPlates(data);
      }
    } catch (e) {
      console.error("Failed to fetch plates", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlates();
    const interval = setInterval(fetchPlates, 5000);
    return () => clearInterval(interval);
  }, [apiBase, dataOrigin]);

  return (
    <div className="anpr-section">
      <div className="anpr-header">
        <h3>Vehicle Intelligence (ANPR) — {dataOrigin}</h3>
      </div>

      <div className="anpr-list">
        {loading && plates.length === 0 ? (
          <div className="empty-state">
            <Car size={20} className="empty-state-icon" />
            <span className="empty-state-sub">Scanning for plates...</span>
          </div>
        ) : plates.length === 0 ? (
          <div className="empty-state">
            <Car size={20} className="empty-state-icon" />
            <span className="empty-state-title">No Vehicles Detected</span>
            <span className="empty-state-sub">No license plates captured recently.</span>
          </div>
        ) : (
          plates.map(plate => (
            <div
              key={plate.id}
              className={`plate-card ${plate.watchlist_status === 'WATCHLIST MATCH' ? 'watchlist' : ''}`}
            >
              <div className="plate-header">
                <span className="plate-number">{plate.plate_number}</span>
                {plate.watchlist_status === 'WATCHLIST MATCH' && (
                  <span className="plate-match-badge">MATCH</span>
                )}
              </div>
              <div className="plate-meta">
                <span>{plate.camera_id} · {plate.track_id}</span>
                <span>Conf: {(plate.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="plate-time">
                {new Date(plate.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
