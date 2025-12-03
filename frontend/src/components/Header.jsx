import React from 'react';
import { Shield, Radio } from 'lucide-react';

const Header = ({ cameraCount }) => {
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
                        AI Security System
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

            <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{
                    padding: '0.5rem 1rem',
                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%)',
                    color: 'var(--success)',
                    borderRadius: '2rem',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    boxShadow: '0 0 15px rgba(16, 185, 129, 0.2)'
                }}>
                    <div style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: 'currentColor',
                        boxShadow: '0 0 8px currentColor'
                    }} />
                    SYSTEM ONLINE
                </div>
            </div>
        </header>
    );
};

export default Header;
