
import React, { useState, useEffect } from 'react';

const LogsView = ({ backendUrl }) => {
    const [dates, setDates] = useState([]);
    const [selectedDate, setSelectedDate] = useState(null);
    const [logContent, setLogContent] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetch(`${backendUrl}/logs/dates`)
            .then(res => res.json())
            .then(data => {
                setDates(data.dates);
                if (data.dates.length > 0) setSelectedDate(data.dates[0]);
            })
            .catch(console.error);
    }, [backendUrl]);

    useEffect(() => {
        if (selectedDate) {
            setLoading(true);
            fetch(`${backendUrl}/logs/${selectedDate}`)
                .then(res => res.json())
                .then(data => {
                    setLogContent(data.content || '');
                    setLoading(false);
                })
                .catch(err => {
                    console.error(err);
                    setLoading(false);
                });
        }
    }, [selectedDate, backendUrl]);

    const getLogColor = (line) => {
        if (line.includes('[ERROR]')) return '#ff4444';
        if (line.includes('[WARNING]')) return '#ffbb33';
        if (line.includes('[SUCCESS]')) return '#00C851';
        if (line.includes('[DETECTION]')) return '#33b5e5';
        return 'inherit';
    };

    return (
        <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Date Selector */}
            <div style={{ padding: '1rem', background: 'rgba(20, 21, 25, 0.8)', borderRadius: '12px', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <span style={{ fontWeight: '600', color: 'var(--text-secondary)' }}>Select Date:</span>
                <select
                    value={selectedDate || ''}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    style={{
                        padding: '0.5rem 1rem',
                        borderRadius: '6px',
                        background: '#1a1b20',
                        color: 'white',
                        border: '1px solid rgba(255,255,255,0.2)',
                        minWidth: '200px',
                        cursor: 'pointer',
                        outline: 'none'
                    }}
                >
                    {dates.map(date => (
                        <option key={date} value={date} style={{ background: '#1a1b20', color: 'white' }}>{date}</option>
                    ))}
                </select>
            </div>

            {/* Log Content */}
            <div style={{
                flex: 1,
                background: 'rgba(0, 0, 0, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem',
                paddingBottom: '4rem', // Extra space at bottom to prevent cut-off
                overflowY: 'auto',
                fontFamily: 'monospace',
                border: '1px solid rgba(255,255,255,0.1)'
            }}>
                {loading ? (
                    <div>Loading logs...</div>
                ) : (
                    logContent.split('\n').map((line, i) => (
                        <div key={i} style={{
                            color: getLogColor(line),
                            marginBottom: '4px',
                            borderBottom: '1px solid rgba(255,255,255,0.02)',
                            paddingBottom: '2px'
                        }}>
                            {line}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default LogsView;
