import React, { useState, useEffect } from 'react';
import { X, Save, RotateCcw } from 'lucide-react';
import api from '../utils/api';

const CameraSettings = ({ camera, onClose }) => {
    const [settings, setSettings] = useState({
        brightness: 50,
        contrast: 50,
        saturation: 50,
        gamma: 50
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const data = await api.camera.get(`/camera/${camera.id}/settings`);
            setSettings(data);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching settings:', error);
            setLoading(false);
        }
    };

    const handleChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: parseInt(value) }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Camera service uses PUT for settings
            await api.camera.put(`/camera/${camera.id}/settings`, settings);
            onClose();
        } catch (error) {
            console.error('Error saving settings:', error);
        } finally {
            setSaving(false);
        }
    };

    const handleReset = () => {
        setSettings({
            brightness: 50,
            contrast: 50,
            saturation: 50,
            gamma: 50
        });
    };

    if (loading) return <div className="p-4 text-white">Loading settings...</div>;

    return (
        <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(4px)',
            zIndex: 10,
            display: 'flex',
            flexDirection: 'column',
            padding: '1rem',
            color: 'white'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{camera.name} Settings</h3>
                <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                    <X size={18} />
                </button>
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
                {['brightness', 'contrast', 'saturation', 'gamma'].map(setting => (
                    <div key={setting}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.875rem' }}>
                            <span style={{ textTransform: 'capitalize' }}>{setting}</span>
                            <span style={{ color: 'var(--text-muted)' }}>{settings[setting]}%</span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="100"
                            value={settings[setting]}
                            onChange={(e) => handleChange(setting, e.target.value)}
                            style={{ width: '100%', accentColor: 'var(--primary)' }}
                        />
                    </div>
                ))}
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                <button
                    onClick={handleReset}
                    style={{
                        flex: 1,
                        padding: '0.5rem',
                        background: 'rgba(255, 255, 255, 0.1)',
                        border: 'none',
                        borderRadius: '0.25rem',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem',
                        fontSize: '0.875rem'
                    }}
                >
                    <RotateCcw size={14} /> Reset
                </button>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    style={{
                        flex: 2,
                        padding: '0.5rem',
                        background: 'var(--primary)',
                        border: 'none',
                        borderRadius: '0.25rem',
                        color: 'white',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '0.5rem',
                        fontSize: '0.875rem',
                        opacity: saving ? 0.7 : 1
                    }}
                >
                    <Save size={14} /> {saving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
        </div>
    );
};

export default CameraSettings;
