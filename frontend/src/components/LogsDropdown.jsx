import React, { useState, useEffect, useRef } from 'react';
import { Scroll, Bell, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const LogsDropdown = ({ logs }) => {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const getIcon = (type) => {
        switch (type) {
            case 'warning': return <AlertTriangle size={14} color="var(--warning)" />;
            case 'error': return <AlertTriangle size={14} color="var(--danger)" />;
            case 'success': return <CheckCircle size={14} color="var(--success)" />;
            case 'detection': return <Bell size={14} color="var(--primary)" />;
            default: return <Info size={14} color="var(--text-muted)" />;
        }
    };

    const getColor = (type) => {
        switch (type) {
            case 'warning': return 'var(--warning)';
            case 'error': return 'var(--danger)';
            case 'success': return 'var(--success)';
            case 'detection': return 'var(--primary)';
            default: return 'var(--text-muted)';
        }
    };

    return (
        <div className="logs-dropdown" ref={dropdownRef} style={{ position: 'relative' }}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    color: 'var(--text-main)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    transition: 'all 0.2s'
                }}
            >
                <Scroll size={16} />
                <span>System Logs</span>
                {logs.length > 0 && (
                    <span style={{
                        background: 'var(--primary)',
                        color: 'white',
                        fontSize: '0.7rem',
                        padding: '0.1rem 0.4rem',
                        borderRadius: '1rem',
                        marginLeft: '0.25rem'
                    }}>
                        {logs.length}
                    </span>
                )}
            </button>

            {isOpen && (
                <div style={{
                    position: 'absolute',
                    top: '120%',
                    right: 0,
                    width: '350px',
                    maxHeight: '400px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '0.75rem',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
                    zIndex: 100,
                    display: 'flex',
                    flexDirection: 'column',
                    overflow: 'hidden'
                }}>
                    <div style={{
                        padding: '1rem',
                        borderBottom: '1px solid var(--border)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        background: 'rgba(0,0,0,0.2)'
                    }}>
                        <h3 style={{ margin: 0, fontSize: '0.875rem', fontWeight: 600 }}>Activity Log</h3>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Last 50 events</span>
                    </div>

                    <div style={{ overflowY: 'auto', flex: 1 }}>
                        {logs.length === 0 ? (
                            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                No logs available
                            </div>
                        ) : (
                            logs.map((log) => (
                                <div key={log.id} style={{
                                    padding: '0.75rem 1rem',
                                    borderBottom: '1px solid var(--border)',
                                    display: 'flex',
                                    gap: '0.75rem',
                                    alignItems: 'flex-start',
                                    fontSize: '0.875rem'
                                }}>
                                    <div style={{ marginTop: '2px' }}>{getIcon(log.type)}</div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ marginBottom: '0.25rem', color: 'var(--text-main)' }}>
                                            {log.message}
                                        </div>
                                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                            {log.timestamp}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default LogsDropdown;
