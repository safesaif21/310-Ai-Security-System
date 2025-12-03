import React, { useState } from 'react';
import { Maximize, Video, VideoOff, MoreHorizontal } from 'lucide-react';
import CameraSettings from './CameraSettings';

const CameraCard = ({ camera, active }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const [showSettings, setShowSettings] = useState(false);

    const handleLoad = () => {
        setLoading(false);
        setError(false);
    };

    const handleError = () => {
        setLoading(false);
        setError(true);
    };

    const openFullscreen = () => {
        const win = window.open('', '_blank', 'width=1024,height=768');
        if (win) {
            win.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${camera.name} - Fullscreen</title>
            <style>
                body { margin: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }
                img { max-width: 100%; max-height: 100%; object-fit: contain; }
            </style>
        </head>
        <body>
            <img src="${camera.url}" alt="${camera.name}">
        </body>
        </html>
      `);
        }
    };

    return (
        <div className="card" style={{
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            border: '2px solid var(--border)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            position: 'relative',
            overflow: 'hidden'
        }}
            onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(99, 102, 241, 0.5)';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.4), 0 0 40px rgba(99, 102, 241, 0.15)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '';
            }}
        >
            <div style={{
                padding: '0.75rem 1rem',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
                borderBottom: '1px solid var(--border)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                backdropFilter: 'blur(10px)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                    <Video size={16} color={active ? 'var(--success)' : 'var(--text-muted)'} />
                    <span style={{ fontWeight: '500' }}>{camera.name}</span>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        onClick={() => setShowSettings(true)}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--text-muted)',
                            cursor: 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.2s'
                        }}
                        title="Settings"
                        onMouseEnter={(e) => {
                            e.target.style.color = 'var(--primary)';
                            e.target.style.transform = 'scale(1.1)';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.color = 'var(--text-muted)';
                            e.target.style.transform = 'scale(1)';
                        }}
                    >
                        <MoreHorizontal size={16} />
                    </button>
                    <button
                        onClick={openFullscreen}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--text-muted)',
                            cursor: 'pointer',
                            padding: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            fontSize: '0.75rem',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            e.target.style.color = 'var(--primary)';
                            e.target.style.transform = 'scale(1.05)';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.color = 'var(--text-muted)';
                            e.target.style.transform = 'scale(1)';
                        }}
                    >
                        <Maximize size={14} />
                        Fullscreen
                    </button>
                </div>
            </div>

            <div style={{
                flex: 1,
                background: '#000',
                position: 'relative',
                minHeight: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                {active ? (
                    <>
                        {loading && (
                            <div style={{
                                position: 'absolute',
                                color: 'var(--text-muted)',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}>
                                <div className="spinner" style={{
                                    width: '30px',
                                    height: '30px',
                                    border: '2px solid var(--border)',
                                    borderTopColor: 'var(--primary)',
                                    borderRadius: '50%',
                                    animation: 'spin 1s linear infinite'
                                }} />
                                <span style={{ fontSize: '0.875rem' }}>Connecting...</span>
                            </div>
                        )}
                        <img
                            src={camera.url}
                            alt={camera.name}
                            style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'contain',
                                display: loading ? 'none' : 'block'
                            }}
                            onLoad={handleLoad}
                            onError={handleError}
                        />
                        {error && (
                            <div style={{
                                position: 'absolute',
                                color: 'var(--danger)',
                                textAlign: 'center',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: '0.5rem'
                            }}>
                                <VideoOff size={32} />
                                <span style={{ fontWeight: '600' }}>Signal Lost</span>
                            </div>
                        )}
                    </>
                ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                        Feed Paused
                    </div>
                )}

                {showSettings && (
                    <CameraSettings
                        camera={camera}
                        onClose={() => setShowSettings(false)}
                    />
                )}
            </div>
            <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
};

export default CameraCard;
