
import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const LogsView = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchLogs = async () => {
            setLoading(true);
            try {
                const data = await api.dvr.get('/logs');
                setLogs(data.logs || []);
            } catch (err) {
                console.error("Error loading logs:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchLogs();
        const interval = setInterval(fetchLogs, 2000);
        return () => clearInterval(interval);
    }, []);

    const getLogColor = (type) => {
        switch (type?.toLowerCase()) {
            case 'error': return '#ff4444';
            case 'warning': return '#ffbb33';
            case 'success': return '#00C851';
            case 'detection': return '#33b5e5';
            case 'info': return '#ffffff';
            default: return '#ffffff';
        }
    };

    return (
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div style={{
                padding: '1rem',
                background: 'rgba(20, 21, 25, 0.8)',
                borderRadius: '12px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <span style={{ fontWeight: '600', color: 'var(--text-secondary)' }}>Live System Events</span>
                <span style={{ fontSize: '0.8rem', opacity: 0.5 }}>Updates every 2s</span>
            </div>

            {/* Log Content */}
            <div style={{
                flex: 1,
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem',
                overflowY: 'auto',
                fontFamily: 'monospace',
                border: '1px solid rgba(255,255,255,0.1)'
            }}>
                {loading && logs.length === 0 ? (
                    <div>Loading logs...</div>
                ) : logs.length === 0 ? (
                    <div style={{ color: 'rgba(255,255,255,0.2)' }}>No logs found.</div>
                ) : (
                    logs.map((log) => (
                        <div key={log.id} style={{
                            marginBottom: '8px',
                            borderBottom: '1px solid rgba(255,255,255,0.02)',
                            paddingBottom: '4px',
                            fontSize: '0.9rem'
                        }}>
                            <span style={{ color: 'rgba(255,255,255,0.4)', marginRight: '10px' }}>[{log.timestamp}]</span>
                            <span style={{ color: getLogColor(log.type), fontWeight: 'bold', marginRight: '10px' }}>[{log.type.toUpperCase()}]</span>
                            <span style={{ color: 'var(--text-main)' }}>{log.message}</span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default LogsView;
