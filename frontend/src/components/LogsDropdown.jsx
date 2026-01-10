import React, { useState, useEffect, useRef } from 'react';
import { Scroll, Bell, AlertTriangle, Info, CheckCircle, Calendar, ChevronDown, RefreshCcw } from 'lucide-react';
import api from '../utils/api';

const LogsDropdown = ({ logs: realTimeLogs }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [view, setView] = useState('recent'); // 'recent' or 'historical'
    const [availableDates, setAvailableDates] = useState([]);
    const [selectedDate, setSelectedDate] = useState('');
    const [historicalLogs, setHistoricalLogs] = useState([]);
    const [loading, setLoading] = useState(false);
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

    const fetchDates = async () => {
        try {
            const data = await api.dvr.get('/logs/dates');
            const dates = data.dates || [];
            setAvailableDates(dates);
            if (dates.length > 0 && !selectedDate) {
                setSelectedDate(dates[0]);
            }
        } catch (err) {
            console.error("Error fetching log dates:", err);
        }
    };

    const fetchHistoricalLogs = async (date) => {
        if (!date) return;
        setLoading(true);
        try {
            const data = await api.dvr.get(`/logs/by-date/${date}`);
            setHistoricalLogs(data.logs || []);
        } catch (err) {
            console.error("Error fetching historical logs:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen && view === 'historical') {
            fetchDates();
        }
    }, [isOpen, view]);

    useEffect(() => {
        if (selectedDate && view === 'historical') {
            fetchHistoricalLogs(selectedDate);
        }
    }, [selectedDate, view]);

    const getIcon = (type) => {
        switch (type) {
            case 'warning': return <AlertTriangle size={14} color="var(--warning)" />;
            case 'error': return <AlertTriangle size={14} color="var(--danger)" />;
            case 'success': return <CheckCircle size={14} color="var(--success)" />;
            case 'detection': return <Bell size={14} color="var(--primary)" />;
            default: return <Info size={14} color="var(--text-muted)" />;
        }
    };

    const displayLogs = view === 'recent' ? realTimeLogs : historicalLogs;

    return (
        <div className="logs-dropdown" ref={dropdownRef} style={{ position: 'relative' }}>
            {/* Main Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="btn glass-panel"
                style={{
                    padding: '0.6rem 1.2rem',
                    borderRadius: '0.75rem',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.6rem',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    fontWeight: 500,
                    border: isOpen ? '1px solid var(--primary)' : '1px solid var(--border)',
                    boxShadow: isOpen ? '0 0 15px var(--primary-glow)' : 'none'
                }}
            >
                <Scroll size={18} className={realTimeLogs.length > 0 ? "animate-pulse" : ""} />
                <span>Security Logs</span>
                <ChevronDown size={14} style={{
                    transition: 'transform 0.3s',
                    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    opacity: 0.5
                }} />
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div
                    className="card animate-slide-up"
                    style={{
                        position: 'absolute',
                        top: 'calc(100% + 10px)',
                        right: 0,
                        width: '400px',
                        maxHeight: '80vh',
                        background: 'var(--bg-card)',
                        display: 'flex',
                        flexDirection: 'column',
                        zIndex: 1000,
                        boxShadow: '0 20px 50px rgba(0,0,0,0.6)',
                        border: '1px solid var(--border)',
                        overflow: 'hidden'
                    }}
                >
                    {/* View Switcher Tabs */}
                    <div style={{
                        display: 'flex',
                        background: 'rgba(0,0,0,0.3)',
                        padding: '0.5rem',
                        gap: '0.25rem',
                        borderBottom: '1px solid var(--border)'
                    }}>
                        <button
                            onClick={() => setView('recent')}
                            style={{
                                flex: 1, padding: '0.6rem', borderRadius: '0.5rem', border: 'none',
                                background: view === 'recent' ? 'var(--primary)' : 'transparent',
                                color: view === 'recent' ? 'white' : 'var(--text-muted)',
                                cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
                                transition: 'all 0.2s'
                            }}
                        >
                            Real-time Activity
                        </button>
                        <button
                            onClick={() => setView('historical')}
                            style={{
                                flex: 1, padding: '0.6rem', borderRadius: '0.5rem', border: 'none',
                                background: view === 'historical' ? 'var(--primary)' : 'transparent',
                                color: view === 'historical' ? 'white' : 'var(--text-muted)',
                                cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
                                transition: 'all 0.2s'
                            }}
                        >
                            Historical Archive
                        </button>
                    </div>

                    {/* Controls Bar */}
                    <div style={{
                        padding: '0.8rem 1rem',
                        borderBottom: '1px solid var(--border)',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: '1rem',
                        background: 'rgba(255,255,255,0.02)'
                    }}>
                        {view === 'historical' ? (
                            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <Calendar size={16} color="var(--primary)" />
                                <select
                                    value={selectedDate}
                                    onChange={(e) => setSelectedDate(e.target.value)}
                                    style={{
                                        flex: 1,
                                        background: 'var(--bg-dark)',
                                        border: '1px solid var(--border)',
                                        borderRadius: '0.4rem',
                                        color: 'white',
                                        padding: '0.4rem',
                                        fontSize: '0.85rem',
                                        outline: 'none',
                                        cursor: 'pointer'
                                    }}
                                >
                                    {availableDates.length === 0 && <option>No dates found</option>}
                                    {availableDates.map(date => <option key={date} value={date}>{date}</option>)}
                                </select>
                            </div>
                        ) : (
                            <div style={{ flex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                                    Live Stream Events
                                </span>
                                <button
                                    onClick={() => setView('recent')} // Force refresh logic if needed
                                    style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                                >
                                    <RefreshCcw size={14} />
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Logs Content Area */}
                    <div style={{ overflowY: 'auto', flex: 1, scrollbarWidth: 'thin', minHeight: '350px' }}>
                        {loading ? (
                            <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
                                <RefreshCcw size={30} className="animate-spin" style={{ opacity: 0.3, marginBottom: '1rem' }} />
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Fetching records...</div>
                            </div>
                        ) : displayLogs.length === 0 ? (
                            <div style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                <Info size={30} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                                <div style={{ fontSize: '0.9rem' }}>No activity records found</div>
                            </div>
                        ) : (
                            displayLogs.map((log) => (
                                <div
                                    key={log.id}
                                    style={{
                                        padding: '1rem 1.2rem',
                                        borderBottom: '1px solid rgba(255,255,255,0.03)',
                                        display: 'flex',
                                        gap: '1rem',
                                        fontSize: '0.85rem',
                                        transition: 'background 0.2s'
                                    }}
                                    className="log-item"
                                >
                                    <div style={{ marginTop: '2px' }}>{getIcon(log.type)}</div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ color: 'var(--text-main)', lineHeight: '1.5' }}>{log.message}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem', fontFamily: 'monospace' }}>
                                            {log.timestamp}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            <style>{`
                .log-item:hover {
                    background: rgba(255,255,255,0.03);
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                .animate-spin {
                    animation: spin 1s linear infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                .animate-pulse {
                    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                }
            `}</style>
        </div>
    );
};

export default LogsDropdown;
