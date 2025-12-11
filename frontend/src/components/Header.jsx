import React from 'react';
import { Shield, Radio } from 'lucide-react';

const Header = ({ cameraCount, systemStatus, user, onLogout }) => {
    const isOnline = systemStatus === 'ONLINE';

    return (
        <header style={{
            gridColumn: '1 / -1',
            background: 'linear-gradient(135deg, rgba(21, 24, 35, 0.95) 0%, rgba(15, 17, 23, 0.98) 100%)',
            backdropFilter: 'blur(20px)',
            padding: '1rem 1.5rem',
            borderBottom: '1px solid rgba(99, 102, 241, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4), 0 0 40px rgba(99, 102, 241, 0.1)'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%)',
                    padding: '0.5rem',
                    borderRadius: '0.5rem',
                    color: 'var(--primary)',
                    boxShadow: '0 0 20px rgba(99, 102, 241, 0.2)',
                    border: '1px solid rgba(99, 102, 241, 0.3)'
                }}>
                    <Shield size={24} />
                </div>
                <div>
                    <h1 style={{
                        fontSize: '1.25rem',
                        fontWeight: '600',
                        color: 'var(--text-main)',
                        letterSpacing: '-0.025em'
                    }}>
                        Safe Security System
                    </h1>
                    <div style={{
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <Radio size={12} />
                        <span>{cameraCount} camera(s) detected</span>
                    </div>
                </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                {/* User Info */}
                {user && (
                    <div style={{
                        padding: '0.5rem 1rem',
                        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%)',
                        borderRadius: '2rem',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <div style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: '600',
                            fontSize: '0.75rem'
                        }}>
                            {user.username.charAt(0).toUpperCase()}
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ fontSize: '0.875rem', fontWeight: '500', color: 'var(--text-main)' }}>
                                {user.username}
                            </span>
                            <span style={{ fontSize: '0.625rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                                {user.role}
                            </span>
                        </div>
                    </div>
                )}

                {/* Logout Button */}
                {onLogout && (
                    <button
                        onClick={onLogout}
                        style={{
                            padding: '0.5rem 1rem',
                            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%)',
                            color: 'var(--danger)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            borderRadius: '2rem',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={(e) => {
                            e.target.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(239, 68, 68, 0.15) 100%)';
                            e.target.style.transform = 'translateY(-2px)';
                        }}
                        onMouseLeave={(e) => {
                            e.target.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%)';
                            e.target.style.transform = 'translateY(0)';
                        }}
                    >
                        Logout
                    </button>
                )}

                {/* System Status */}
                <div style={{
                    padding: '0.5rem 1rem',
                    background: isOnline
                        ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%)'
                        : 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%)',
                    color: isOnline ? 'var(--success)' : 'var(--danger)',
                    borderRadius: '2rem',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    border: `1px solid ${isOnline ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                    boxShadow: `0 0 15px ${isOnline ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
                }}>
                    <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'currentColor',
                        boxShadow: '0 0 8px currentColor'
                    }} />
                    {isOnline ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
                </div>
            </div>
        </header>
    );
};

export default Header;
