
import React, { useState, useEffect } from 'react';

const RecordingsView = ({ cameras, backendUrl }) => {
    const [selectedCamera, setSelectedCamera] = useState(null);
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [loading, setLoading] = useState(false);

    // Auto-select first camera if available
    useEffect(() => {
        if (cameras.length > 0 && !selectedCamera) {
            setSelectedCamera(cameras[0].id);
        }
    }, [cameras]);

    // Fetch files when camera changes
    useEffect(() => {
        if (selectedCamera !== null) {
            setLoading(true);
            fetch(`${backendUrl}/recordings/${selectedCamera}/files`)
                .then(res => res.json())
                .then(data => {
                    setFiles(data.files);
                    setLoading(false);
                    // Auto-select newest file if not currently playing something valid for this cam
                    if (data.files.length > 0) {
                        setSelectedFile(data.files[0]);
                    } else {
                        setSelectedFile(null);
                    }
                })
                .catch(err => {
                    console.error("Error loading recordings:", err);
                    setLoading(false);
                });
        }
    }, [selectedCamera, backendUrl]);

    return (
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>

            {/* Camera Selection - Horizontal Scroll */}
            <div style={{
                display: 'flex',
                gap: '1rem',
                overflowX: 'auto',
                padding: '0.5rem',
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '12px',
                scrollbarWidth: 'thin'
            }}>
                {cameras.map(cam => (
                    <button
                        key={cam.id}
                        onClick={() => setSelectedCamera(cam.id)}
                        style={{
                            padding: '1rem 2rem',
                            borderRadius: '8px',
                            border: selectedCamera === cam.id ? '2px solid var(--primary)' : '1px solid rgba(255,255,255,0.1)',
                            background: 'rgba(20, 21, 25, 0.8)',
                            color: 'white',
                            cursor: 'pointer',
                            minWidth: '150px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}
                    >
                        <span style={{ fontSize: '1.2rem' }}>📷</span>
                        <span style={{ fontWeight: '600' }}>{cam.name}</span>
                    </button>
                ))}
                {/* Master Recording Option */}
                <button
                    onClick={() => setSelectedCamera('master')}
                    style={{
                        padding: '1rem 2rem',
                        borderRadius: '8px',
                        border: selectedCamera === 'master' ? '2px solid #ff4444' : '1px solid rgba(255,255,255,0.1)',
                        background: 'rgba(20, 21, 25, 0.8)',
                        color: 'white',
                        cursor: 'pointer',
                        minWidth: '150px'
                    }}
                >
                    <span style={{ fontSize: '1.2rem', display: 'block' }}>🎬</span>
                    <span style={{ fontWeight: '600' }}>Master</span>
                </button>
            </div>

            {/* Main Content Area */}
            <div className="recordings-content" style={{
                display: 'flex',
                gap: '1rem',
                flex: 1,
                minHeight: 0,
                flexDirection: window.innerWidth <= 768 ? 'column' : 'row'
            }}>

                {/* Video Player */}
                <div style={{ flex: 2, background: 'black', borderRadius: '12px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {selectedFile ? (
                        <video
                            key={selectedFile.name} // Force reload on change
                            controls
                            autoPlay
                            muted
                            playsInline
                            style={{ width: '100%', height: '100%', maxHeight: '600px' }}
                            src={`${backendUrl}/recordings/serve/${selectedCamera === 'master' ? 'master' : selectedCamera}/${selectedFile.name}`}
                            onLoadStart={() => console.log("Video requesting:", `${backendUrl}/recordings/serve/${selectedCamera === 'master' ? 'master' : selectedCamera}/${selectedFile.name}`)}
                            onError={(e) => {
                                console.error("Video error:", e);
                                if (e.target.error) {
                                    console.error("MediaError code:", e.target.error.code, "message:", e.target.error.message);
                                }
                            }}
                        />
                    ) : (
                        <div style={{ color: 'rgba(255,255,255,0.5)' }}>Select a recording to play</div>
                    )}
                </div>

                {/* File List */}
                <div style={{
                    flex: 1,
                    background: 'rgba(20, 21, 25, 0.6)',
                    borderRadius: '12px',
                    padding: '1rem',
                    overflowY: 'auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem'
                }}>
                    <h3 style={{ margin: '0 0 1rem 0', color: 'var(--text-secondary)' }}>
                        {selectedCamera === 'master' ? 'Master Recordings' : 'Camera Recordings'}
                    </h3>
                    {loading ? (
                        <div>Loading...</div>
                    ) : files.length === 0 ? (
                        <div style={{ color: 'rgba(255,255,255,0.3)' }}>No recordings found</div>
                    ) : (
                        files.map(file => (
                            <div
                                key={file.name}
                                onClick={() => setSelectedFile(file)}
                                style={{
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    background: selectedFile?.name === file.name ? 'rgba(0, 255, 128, 0.1)' : 'rgba(255,255,255,0.05)',
                                    border: selectedFile?.name === file.name ? '1px solid var(--primary)' : 'none',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}
                            >
                                <div>
                                    <div style={{ fontWeight: '500', marginBottom: '4px' }}>
                                        {new Date(file.timestamp * 1000).toLocaleString()}
                                    </div>
                                    <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)' }}>
                                        {file.size_mb} MB
                                    </div>
                                </div>
                                <div style={{ fontSize: '1.2rem', opacity: 0.5 }}>▶</div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default RecordingsView;
