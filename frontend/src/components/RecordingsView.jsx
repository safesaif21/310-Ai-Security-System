
import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const RecordingsView = ({
    cameras,
    selectedCamera,
    setSelectedCamera,
    selectedFile,
    setSelectedFile
}) => {
    // Local state only for data fetching
    const [recordingsMap, setRecordingsMap] = useState({});
    const [loading, setLoading] = useState(false);

    // Initial fetch of all recordings
    useEffect(() => {
        const fetchRecordings = async () => {
            setLoading(true);
            try {
                const data = await api.dvr.get('/recordings');
                setRecordingsMap(data.recordings || {});

                // Auto-select first camera if not selected
                if (Object.keys(data.recordings).length > 0 && !selectedCamera) {
                    setSelectedCamera(Object.keys(data.recordings)[0]);
                }
            } catch (err) {
                console.error("Error loading recordings:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchRecordings();
        // Removed setInterval to prevent scroll jumping
    }, []);

    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
    useEffect(() => {
        const handleResize = () => setIsMobile(window.innerWidth <= 768);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const files = selectedCamera ? (recordingsMap[selectedCamera] || []) : [];

    return (
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>

            {/* Camera Selection */}
            <div style={{
                display: 'flex',
                gap: '1rem',
                overflowX: 'auto',
                padding: '0.5rem',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '12px',
                scrollbarWidth: 'thin'
            }}>
                {Object.keys(recordingsMap).map(camId => (
                    <button
                        key={camId}
                        onClick={() => {
                            setSelectedCamera(camId);
                            setSelectedFile(null);
                        }}
                        style={{
                            padding: '1rem 2rem',
                            borderRadius: '8px',
                            border: selectedCamera === camId ? '2px solid var(--primary)' : '1px solid rgba(255,255,255,0.1)',
                            background: 'rgba(20, 21, 25, 0.8)',
                            color: 'white',
                            cursor: 'pointer',
                            minWidth: '150px'
                        }}
                    >
                        <span style={{ fontWeight: '600' }}>Camera {camId}</span>
                    </button>
                ))}
            </div>

            {/* Main Content Area */}
            <div className="recordings-content" style={{
                display: 'flex',
                flexDirection: isMobile ? 'column' : 'row',
                gap: '1rem',
                flex: 1,
                minHeight: 0,
                overflowY: isMobile ? 'auto' : 'hidden'
            }}>

                {/* Video Player */}
                <div style={{
                    flex: isMobile ? 'none' : 2,
                    height: isMobile ? '300px' : 'auto',
                    background: 'black',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    {selectedFile ? (
                        <video
                            key={selectedFile}
                            controls
                            autoPlay
                            muted
                            playsInline
                            style={{ width: '100%', height: '100%' }}
                            src={`${api.SERVICES.DVR}/stream/camera_${selectedCamera}/${selectedFile}`}
                        />
                    ) : (
                        <div style={{ color: 'rgba(255,255,255,0.5)' }}>Select a recording to play</div>
                    )}
                </div>

                {/* File List */}
                <div style={{
                    flex: isMobile ? 'none' : 1,
                    // Limit height on mobile so it doesn't push video off screen
                    maxHeight: isMobile ? '50vh' : 'auto',
                    minHeight: 0,
                    background: 'rgba(20, 21, 25, 0.6)',
                    borderRadius: '12px',
                    padding: '1rem',
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem'
                }}>
                    <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-secondary)' }}>Files</h3>
                    {loading ? (
                        <div>Loading...</div>
                    ) : files.length === 0 ? (
                        <div style={{ color: 'rgba(255,255,255,0.3)' }}>No recordings found</div>
                    ) : (
                        files.map(filename => (
                            <div
                                key={filename}
                                onClick={() => setSelectedFile(filename)}
                                style={{
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    background: selectedFile === filename ? 'rgba(0, 255, 128, 0.1)' : 'rgba(255,255,255,0.05)',
                                    border: selectedFile === filename ? '1px solid var(--primary)' : 'none',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    justifyContent: 'space-between'
                                }}
                            >
                                <span style={{ fontSize: '0.85rem' }}>{filename}</span>
                                <span style={{ opacity: 0.5 }}>▶</span>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default RecordingsView;
