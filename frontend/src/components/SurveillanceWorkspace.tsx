import React from 'react';
import type { Camera, GPSLocation } from '../types';
import { Maximize2, LayoutGrid, Map as MapIcon } from 'lucide-react';
import { VideoViewport } from './VideoViewport';
import { CameraGrid } from './CameraGrid';
import { TacticalMap } from './TacticalMap';

interface SurveillanceWorkspaceProps {
  viewMode: 'focus' | 'grid2x2' | 'map';
  setViewMode: (mode: 'focus' | 'grid2x2' | 'map') => void;
  selectedCamera: Camera | null;
  cameras: Camera[];
  onSelectCamera: (camera: Camera) => void;
  bopLocation: GPSLocation | null;
}

export const SurveillanceWorkspace: React.FC<SurveillanceWorkspaceProps> = ({
  viewMode,
  setViewMode,
  selectedCamera,
  cameras,
  onSelectCamera,
  bopLocation,
}) => {
  return (
    <main className="surveillance-workspace" aria-label="Surveillance workspace">
      {/* Toolbar */}
      <div className="workspace-toolbar">
        <div className="toolbar-left">
          {viewMode === 'focus' && selectedCamera && (
            <>
              <span className={`cam-status-dot ${selectedCamera.status.toLowerCase()}`} />
              <span className="toolbar-cam-label">{selectedCamera.id}</span>
              <span>{selectedCamera.name}</span>
            </>
          )}
          {viewMode === 'grid2x2' && <span>Multi-Camera Grid (2×2)</span>}
          {viewMode === 'map' && <span>Geospatial View</span>}
        </div>

        <div className="view-switcher" role="radiogroup" aria-label="View mode">
          <button
            className={`view-btn ${viewMode === 'focus' ? 'active' : ''}`}
            onClick={() => setViewMode('focus')}
            role="radio"
            aria-checked={viewMode === 'focus'}
            title="Single camera focus"
          >
            <Maximize2 size={12} /> Focus
          </button>
          <button
            className={`view-btn ${viewMode === 'grid2x2' ? 'active' : ''}`}
            onClick={() => setViewMode('grid2x2')}
            role="radio"
            aria-checked={viewMode === 'grid2x2'}
            title="2×2 camera grid"
          >
            <LayoutGrid size={12} /> Grid
          </button>
          <button
            className={`view-btn ${viewMode === 'map' ? 'active' : ''}`}
            onClick={() => setViewMode('map')}
            role="radio"
            aria-checked={viewMode === 'map'}
            title="Geospatial map"
          >
            <MapIcon size={12} /> Map
          </button>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'focus' ? (
        <VideoViewport camera={selectedCamera} />
      ) : viewMode === 'grid2x2' ? (
        <CameraGrid
          cameras={cameras}
          selectedCamera={selectedCamera}
          onSelectCamera={onSelectCamera}
          onFocusCamera={(cam) => {
            onSelectCamera(cam);
            setViewMode('focus');
          }}
        />
      ) : (
        <TacticalMap
          cameras={cameras}
          bopLocation={bopLocation}
          onSelectCamera={(cam) => {
            onSelectCamera(cam);
            setViewMode('focus');
          }}
        />
      )}
    </main>
  );
};
