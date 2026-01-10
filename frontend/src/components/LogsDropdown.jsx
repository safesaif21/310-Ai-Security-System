import React, { useState, useEffect, useRef } from 'react';
import { Scroll, Bell, AlertTriangle, Info, CheckCircle, Calendar } from 'lucide-react';
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
            setAvailableDates(data.dates || []);
            if (data.dates?.length > 0 && !selectedDate) {
                setSelectedDate(data.dates[0]);
            }
        } catch (err) {
            console.error("Error fetching log dates:", err);
        }
    };

    const fetchHistoricalLogs = async (date) => {
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
                    fontWeight: 500
                }}
            >
                <Scroll size={16} />
                <span>Logs</span>
                {realTimeLogs.length > 0 && view === 'recent' && (
                    <span style={{ background: 'var(--primary)', color: 'white', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '1rem' }}>
                        {realTimeLogs.length}
                    </span>
                )}
            </button>

            {isOpen && (
                <div style={{
                    position: 'absolute', top: '120%', right: 0, width: '380px', maxHeight: '500px',
                    background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '0.75rem',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.5)', zIndex: 100, display: 'flex', flexDirection: 'column', overflow: 'hidden'
                }}>
                    {/* Header with View Toggle */}
                    <div style={{ padding: '0.75rem', borderBottom: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)', display: 'flex', gap: '0.5rem' }}>
                        <button
                            onClick={() => setView('recent')}
                            style={{
                                flex: 1, padding: '0.4rem', borderRadius: '4px', border: 'none',
                                background: view === 'recent' ? 'var(--primary)' : 'transparent',
                                color: view === 'recent' ? 'white' : 'var(--text-muted)', cursor: 'pointer', fontSize: '0.75rem'
                            }}
                        >
                            Recent
                        </button>
                        <button
                            onClick={() => setView('historical')}
                            style={{
                                flex: 1, padding: '0.4rem', borderRadius: '4px', border: 'none',
                                background: view === 'historical' ? 'var(--primary)' : 'transparent',
                                color: view === 'historical' ? 'white' : 'var(--text-muted)', cursor: 'pointer', fontSize: '0.75rem'
                            }}
                        >
                            History
                        </button>
                    </div>

                    {/* Date Selector for Historical View */}
                    {view === 'historical' && (
                        <div style={{ padding: '0.75rem', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Calendar size={14} color="var(--text-muted)" />
                            <select
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                style={{ flex: 1, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', borderRadius: '4px', color: 'white', padding: '0.2rem' }}
                            >
                                {availableDates.map(date => <option key={date} value={date}>{date}</option>)}
                            </select>
                        </div>
                    )}

                    <div style={{ overflowY: 'auto', flex: 1, minHeight: '300px' }}>
                        {loading ? (
                            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading logs...</div>
                        ) : displayLogs.length === 0 ? (
                            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No logs for this view</div>
                        ) : (
                            displayLogs.map((log) => (
                                <div key={log.id} style={{ padding: '0.6rem 1rem', borderBottom: '1px solid var(--border)', display: 'flex', gap: '0.75rem', fontSize: '0.8rem' }}>
                                    <div style={{ marginTop: '2px' }}>{getIcon(log.type)}</div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ color: 'var(--text-main)', lineHeight: '1.4' }}>{log.message}</div>
                                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>{log.timestamp}</div>
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
