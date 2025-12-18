
import React from 'react';

const Navigation = ({ currentView, onViewChange }) => {
    const tabs = [
        { id: 'interface', label: 'INTERFACE' },
        { id: 'recordings', label: 'RECORDINGS' },
        { id: 'logs', label: 'LOGS' }
    ];

    return (
        <div style={{
            display: 'flex',
            gap: '1rem',
            padding: '0 1.5rem',
            marginBottom: '1rem'
        }}>
            {tabs.map(tab => (
                <button
                    key={tab.id}
                    onClick={() => onViewChange(tab.id)}
                    style={{
                        background: currentView === tab.id ? 'var(--primary)' : 'rgba(255, 255, 255, 0.05)',
                        padding: '0.75rem 2rem',
                        borderRadius: '8px',
                        color: 'white',
                        fontWeight: '600',
                        letterSpacing: '1px',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                        flex: 1,
                        boxShadow: currentView === tab.id ? '0 4px 12px rgba(0, 255, 128, 0.2)' : 'none',
                        border: currentView === tab.id ? 'none' : '1px solid rgba(255, 255, 255, 0.1)'
                    }}
                >
                    {tab.label}
                </button>
            ))}
        </div>
    );
};

export default Navigation;
