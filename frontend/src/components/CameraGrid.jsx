import React from 'react';
import CameraCard from './CameraCard';

const CameraGrid = ({ cameras, camerasActive }) => {
    const getGridClass = (count) => {
        if (count <= 1) return 'grid-cols-1';
        if (count <= 2) return 'grid-cols-2';
        if (count <= 4) return 'grid-cols-2 grid-rows-2';
        if (count <= 6) return 'grid-cols-3 grid-rows-2';
        return 'grid-cols-3 grid-rows-3';
    };

    // Inline grid styles based on count
    const gridStyle = {
        display: 'grid',
        gap: '1rem',
        flex: 1,
        minHeight: 0,
        gridTemplateColumns: cameras.length <= 1 ? '1fr' :
            cameras.length <= 4 ? 'repeat(2, 1fr)' :
                'repeat(3, 1fr)',
        gridTemplateRows: cameras.length <= 2 ? '1fr' :
            cameras.length <= 6 ? 'repeat(2, 1fr)' :
                'repeat(3, 1fr)'
    };

    return (
        <div style={gridStyle}>
            {cameras.map(camera => (
                <CameraCard
                    key={camera.id}
                    camera={camera}
                    active={camerasActive}
                />
            ))}
            {cameras.length === 0 && (
                <div style={{
                    gridColumn: '1 / -1',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--text-muted)',
                    background: 'var(--bg-card)',
                    borderRadius: '0.75rem',
                    border: '1px dashed var(--border)'
                }}>
                    No cameras detected
                </div>
            )}
        </div>
    );
};

export default CameraGrid;
