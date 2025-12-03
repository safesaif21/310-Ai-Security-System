import React from 'react';
import { Play, Square, Activity } from 'lucide-react';

const Controls = ({ camerasActive, setCamerasActive, detectionEnabled }) => {
    return (
        <div className="card" style={{ padding: '1.5rem' }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1rem'
            }}>
                <h2 style={{
                    fontSize: '1.1rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem'
                }}>
                    <Activity size={20} color="var(--primary)" />
                    Live Feed Controls
                </h2>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                    className={`btn ${camerasActive ? 'btn-danger' : 'btn-success'}`}
                    onClick={() => setCamerasActive(!camerasActive)}
                    style={{ padding: '0.75rem 1.5rem' }}
                >
                    {camerasActive ? (
                        <>
                            <Square size={18} fill="currentColor" />
                            Stop All Cameras
                        </>
                    ) : (
                        <>
                            <Play size={18} fill="currentColor" />
                            Start All Cameras
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default Controls;
