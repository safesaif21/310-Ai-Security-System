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
            paddingTop: 'calc(1rem + env(safe-area-inset-top, 0px))',
            borderBottom: '1px solid rgba(99, 102, 241, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4), 0 0 40px rgba(99, 102, 241, 0.1)'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{
                    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%)',
                    padding: '0.25rem',
                    borderRadius: '0.6rem',
                    boxShadow: '0 0 20px rgba(99, 102, 241, 0.2)',
                    border: '1px solid rgba(99, 102, 241, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden'
                }}>
                    <img src="/logo_t.png" alt="Logo" style={{ width: '32px', height: '32px', objectFit: 'contain' }} />
                </div>
                <div>
                    <h1 style={{
                        fontSize: '1.25rem',
                        fontWeight: '600',
                        color: 'var(--text-main)',
                        letterSpacing: '-0.025em'
                    }}>
                        Safe Security Camera Dashboard
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

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                {/* User Info - Compact on mobile */}
                {user && (
                    <div style={{
                        padding: '0.25rem 0.5rem',
                        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%)',
                        borderRadius: '2rem',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                    }}>
                        <div style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            fontWeight: '600',
                            fontSize: '0.65rem'
                        }}>
                            {user.username.charAt(0).toUpperCase()}
                        </div>
                        <span style={{ fontSize: '0.75rem', fontWeight: '500', color: 'var(--text-main)', display: window.innerWidth <= 768 ? 'none' : 'block' }}>
                            {user.username}
                        </span>
                    </div>
                )}

                {/* Logout Button */}
                {onLogout && (
                    <button
                        onClick={onLogout}
                        style={{
                            padding: '0.4rem 0.8rem',
                            background: 'rgba(239, 68, 68, 0.1)',
                            color: 'var(--danger)',
                            border: '1px solid rgba(239, 68, 68, 0.2)',
                            borderRadius: '2rem',
                            fontSize: '0.7rem',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}
                    >
                        {window.innerWidth <= 768 ? 'Exit' : 'Logout'}
                    </button>
                )}

                {/* System Status */}
                <div style={{
                    padding: '0.4rem 0.8rem',
                    background: isOnline ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: isOnline ? 'var(--success)' : 'var(--danger)',
                    borderRadius: '2rem',
                    fontSize: '0.65rem',
                    fontWeight: '700',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                    border: `1px solid ${isOnline ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
                }}>
                    <div style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'currentColor' }} />
                    {isOnline ? 'LIVE' : 'OFFLINE'}
                </div>
            </div>
        </header>
    );
};

export default Header;
