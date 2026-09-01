import React, { useMemo } from 'react';
import type { Camera, GPSLocation } from '../types';
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MapPin, Video } from 'lucide-react';

interface TacticalMapProps {
  cameras: Camera[];
  onSelectCamera: (camera: Camera) => void;
  bopLocation: GPSLocation | null;
}

export const TacticalMap: React.FC<TacticalMapProps> = ({ cameras, onSelectCamera, bopLocation }) => {
  // Default to a central coordinate if bopLocation is null
  const defaultLocation = { lat: 28.6139, lng: 77.2090 };
  const center = bopLocation || defaultLocation;

  const activeCameras = useMemo(() => {
    return cameras.filter(c => c.latitude !== undefined && c.longitude !== undefined);
  }, [cameras]);

  return (
    <div className="tactical-map-container" style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Map
        initialViewState={{
          longitude: center.lng,
          latitude: center.lat,
          zoom: 14
        }}
        mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        mapLib={maplibregl}
        style={{ width: '100%', height: '100%' }}
      >
        <NavigationControl position="top-right" />

        {/* Command Post Marker */}
        {bopLocation && (
          <Marker longitude={bopLocation.lng} latitude={bopLocation.lat} anchor="bottom">
            <div className="bop-marker" style={{ color: 'var(--status-critical)', display: 'flex', flexDirection: 'column', alignItems: 'center', filter: 'drop-shadow(0 0 4px rgba(239,68,68,0.8))' }}>
              <MapPin size={32} fill="currentColor" />
              <span style={{ fontSize: '12px', fontWeight: 'bold', background: 'rgba(0,0,0,0.7)', padding: '2px 4px', borderRadius: '4px', marginTop: '2px' }}>COMMAND POST</span>
            </div>
          </Marker>
        )}

        {/* Camera Markers */}
        {activeCameras.map(camera => (
          <Marker 
            key={camera.id} 
            longitude={camera.longitude!} 
            latitude={camera.latitude!} 
            anchor="bottom"
            onClick={(e: any) => {
              e.originalEvent.stopPropagation();
              onSelectCamera(camera);
            }}
          >
            <div className="camera-marker" style={{ cursor: 'pointer', color: camera.status === 'ONLINE' ? 'var(--status-operational)' : 'var(--status-warning)', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Video size={24} fill="currentColor" />
              <span style={{ fontSize: '10px', background: 'rgba(0,0,0,0.7)', padding: '1px 3px', borderRadius: '2px', marginTop: '2px' }}>{camera.id}</span>
            </div>
          </Marker>
        ))}
      </Map>
    </div>
  );
};
