import React from 'react';
import { Target, AlertTriangle, ShieldAlert, Users, Activity, RefreshCw } from 'lucide-react';

const Sidebar = ({
    models,
    currentModel,
    setCurrentModel,
    detectionEnabled,
    setDetectionEnabled,
    stats,
    systemStatus
}) => {
    const BACKEND_URL = 'http://localhost:8000';

    const loadModel = async (modelName) => {
        if (!modelName) return;
        try {
            const response = await fetch(`${BACKEND_URL}/model/load?model_name=${modelName}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                setCurrentModel(modelName);
                setDetectionEnabled(true);
            } else {
                alert(`Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error loading model:', error);
            alert('Failed to load model');
        }
    };

    const toggleDetection = async () => {
        if (!currentModel) {
            alert('Please select and load a model first!');
            return;
        }
        try {
            const newState = !detectionEnabled;
            const response = await fetch(`${BACKEND_URL}/detection/toggle?enabled=${newState}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (data.success) {
                setDetectionEnabled(newState);
            }
        } catch (error) {
            console.error('Error toggling detection:', error);
        }
    };

    return (
        <aside style={{
            height: '100%',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            background: 'var(--bg-sidebar)',
            borderLeft: '1px solid var(--border)'
        }}>
            <div className="sidebar-content" style={{
                padding: '1.5rem',
                overflowY: 'auto',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem'
            }}>
                {/* Main Control Panel */}
                <div className="card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>

                    {/* Model Selection Section */}
                    <div>
                        <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Target size={16} color="var(--primary)" />
                            YOLO Model Configuration
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            <select
                                value={currentModel || ''}
                                onChange={(e) => loadModel(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '0.75rem',
                                    background: 'var(--bg-dark)',
                                    border: '1px solid var(--border)',
                                    borderRadius: '0.5rem',
                                    color: 'var(--text-main)',
                                    fontSize: '0.875rem',
                                    outline: 'none',
                                    transition: 'all 0.2s',
                                    cursor: 'pointer'
                                }}
                            >
                                <option value="">Select a YOLO model...</option>
                                {models.map(model => (
                                    <option key={model.name} value={model.name}>
                                        {model.name} ({model.size_mb} MB)
                                    </option>
                                ))}
                            </select>

                            <button
                                className={`btn ${detectionEnabled ? 'btn-danger' : 'btn-success'}`}
                                onClick={toggleDetection}
                                disabled={!currentModel}
                                style={{ justifyContent: 'center', width: '100%' }}
                            >
                                {detectionEnabled ? 'Disable Detection' : 'Enable Detection'}
                            </button>

                            <div style={{
                                padding: '0.75rem',
                                borderRadius: '0.5rem',
                                background: detectionEnabled ? 'rgba(16, 185, 129, 0.1)' : 'rgba(156, 163, 175, 0.1)',
                                border: `1px solid ${detectionEnabled ? 'rgba(16, 185, 129, 0.2)' : 'var(--border)'}`,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontSize: '0.75rem',
                                color: detectionEnabled ? 'var(--success)' : 'var(--text-muted)'
                            }}>
                                <div style={{
                                    width: '6px',
                                    height: '6px',
                                    borderRadius: '50%',
                                    background: 'currentColor'
                                }} />
                                Status: {detectionEnabled ? 'Active' : 'Inactive'}
                            </div>
                        </div>
                    </div>

                    <div style={{ height: '1px', background: 'var(--border)' }}></div>

                    {/* Threat Level Section */}
                    <div style={{ textAlign: 'center' }}>
                        <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                            <AlertTriangle size={16} color="var(--warning)" />
                            Current Threat Level
                        </h3>
                        <div style={{
                            fontSize: '4rem',
                            fontWeight: '700',
                            color: stats.threat_level > 5 ? 'var(--danger)' : 'var(--success)',
                            lineHeight: 1,
                            textShadow: stats.threat_level > 5 ? '0 0 30px var(--danger-glow)' : '0 0 30px var(--success-glow)',
                            transition: 'all 0.3s',
                            marginBottom: '0.5rem'
                        }}>
                            {stats.threat_level}/10
                        </div>
                        <div style={{
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            letterSpacing: '0.1em',
                            color: stats.threat_level > 5 ? 'var(--danger)' : 'var(--success)'
                        }}>
                            {stats.threat_level > 7 ? 'CRITICAL' : stats.threat_level > 3 ? 'MODERATE' : 'LOW'}
                        </div>
                    </div>

                    <div style={{ height: '1px', background: 'var(--border)' }}></div>

                    {/* Weapon Detection Section */}
                    <div>
                        <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <ShieldAlert size={16} color="var(--danger)" />
                            Security Alerts
                        </h3>
                        <div style={{
                            padding: '1rem',
                            borderRadius: '0.5rem',
                            background: stats.weapon_detected ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.1)',
                            border: `1px solid ${stats.weapon_detected ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.2)'}`,
                            color: stats.weapon_detected ? 'var(--danger)' : 'var(--success)',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            fontSize: '0.875rem',
                            transition: 'all 0.3s'
                        }}>
                            <div style={{
                                width: '8px',
                                height: '8px',
                                borderRadius: '50%',
                                background: 'currentColor',
                                boxShadow: '0 0 8px currentColor'
                            }} />
                            {stats.weapon_detected ? 'WEAPON DETECTED' : 'No Active Threats'}
                        </div>
                    </div>

                    <div style={{ height: '1px', background: 'var(--border)' }}></div>

                    {/* Statistics Section */}
                    <div>
                        <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Activity size={16} color="var(--text-muted)" />
                            Live Statistics
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <div style={{
                                background: 'var(--bg-dark)',
                                padding: '1rem',
                                borderRadius: '0.5rem',
                                border: '1px solid var(--border)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '1rem'
                            }}>
                                <Users size={24} color="var(--text-muted)" />
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>People Count</div>
                                    <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{stats.people_count}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
