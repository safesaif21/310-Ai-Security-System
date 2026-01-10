
import React, { useState, useEffect } from 'react';
import api from '../utils/api';

const LogsView = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [availableDates, setAvailableDates] = useState([]);
    const [selectedDate, setSelectedDate] = useState(''); // Stores 'YYYY-MM-DD'

    // Fetch available log dates on mount
    useEffect(() => {
        const fetchDates = async () => {
            try {
                const data = await api.dvr.get('/logs/dates');
                const dates = data.dates || [];
                setAvailableDates(dates);

                // Default to latest date if not set
                if (dates.length > 0 && !selectedDate) {
                    setSelectedDate(dates[0]);
                } else if (dates.length === 0) {
                    // Fallback to today if no files found yet
                    const today = new Date().toISOString().split('T')[0];
                    setSelectedDate(today);
                }
            } catch (err) {
                console.error("Error fetching log dates:", err);
            }
        };
        fetchDates();
    }, []);

    // Polling effect: only active when the selected date is the newest one (Live mode)
    useEffect(() => {
        if (!selectedDate || (availableDates.length > 0 && selectedDate !== availableDates[0])) {
            return;
        }

        const fetchLiveLogs = async () => {
            if (logs.length === 0) setLoading(true);
            try {
                const data = await api.dvr.get('/logs');
                setLogs(data.logs || []);
            } catch (err) {
                console.error("Error loading live logs:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchLiveLogs();
        const interval = setInterval(fetchLiveLogs, 2000);
        return () => clearInterval(interval);
    }, [selectedDate, availableDates, logs.length]);

    // History fetch effect: only active when an older date is selected
    useEffect(() => {
        if (!selectedDate || (availableDates.length > 0 && selectedDate === availableDates[0])) {
            return;
        }

        const fetchHistoricalLogs = async () => {
            setLoading(true);
            try {
                const data = await api.dvr.get(`/logs/by-date/${selectedDate}`);
                setLogs(data.logs || []);
            } catch (err) {
                console.error("Error loading historical logs:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchHistoricalLogs();
    }, [selectedDate, availableDates.length]);

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
                alignItems: 'center',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <span style={{ fontWeight: '600', color: 'var(--text-secondary)' }}>System Activity</span>
                    <select
                        value={selectedDate}
                        onChange={(e) => setSelectedDate(e.target.value)}
                        style={{
                            background: 'rgba(255,255,255,0.05)',
                            color: 'white',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '6px',
                            padding: '0.4rem 0.8rem',
                            fontSize: '0.85rem',
                            outline: 'none',
                            cursor: 'pointer'
                        }}
                    >
                        {availableDates.length === 0 && selectedDate && (
                            <option value={selectedDate}>{selectedDate} (Active)</option>
                        )}
                        {availableDates.map((filename, idx) => (
                            <option key={filename} value={filename}>
                                {filename} {idx === 0 ? '(Active)' : ''}
                            </option>
                        ))}
                    </select>
                </div>
                <span style={{ fontSize: '0.8rem', opacity: 0.5 }}>
                    {availableDates.length > 0 && selectedDate === availableDates[0] ? 'Updating every 2s' : `${logs.length} archived events`}
                </span>
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
