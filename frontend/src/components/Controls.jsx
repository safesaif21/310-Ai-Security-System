import React from 'react';
import { Play, Square, Video, VideoOff } from 'lucide-react';
import LogsDropdown from './LogsDropdown';
import api from '../utils/api';

const Controls = ({ camerasActive, setCamerasActive, detectionEnabled, recordingEnabled, setRecordingEnabled, logs }) => {
    const toggleCameras = () => {
        setCamerasActive(!camerasActive);
    };

    const toggleRecording = async () => {
        // Recording is now automatic via the DVR service polling the Analysis service.
        // This button now acts as a manual refresh/status check.
        console.log("Recording is automatically managed by the DVR service.");
    };

    return (
        <div className="animate-fade-in" style={{
            gridColumn: '1 / -1',
            display: 'flex',
            gap: '1rem',
            marginBottom: '1rem',
            alignItems: 'center',
            background: 'rgba(255,255,255,0.02)',
            padding: '0.75rem',
            borderRadius: '1rem',
            border: '1px solid var(--border)'
        }}>
            <button
                className={`btn ${camerasActive ? 'btn-danger' : 'btn-success'} glass-panel`}
                onClick={toggleCameras}
                style={{ flex: 1, justifyContent: 'center', padding: '1rem', borderRadius: '0.75rem' }}
            >
                {camerasActive ? <Square size={20} /> : <Play size={20} />}
                <span style={{ fontWeight: 600 }}>{camerasActive ? 'Stop System' : 'Start System'}</span>
            </button>

            <button
                className={`btn ${recordingEnabled ? 'btn-danger' : 'btn-primary'} glass-panel`}
                onClick={toggleRecording}
                disabled={!camerasActive}
                style={{ flex: 1, justifyContent: 'center', padding: '1rem', borderRadius: '0.75rem' }}
            >
                {recordingEnabled ? <VideoOff size={20} /> : <Video size={20} />}
                <span style={{ fontWeight: 600 }}>{recordingEnabled ? 'DVR Active' : 'DVR Auto-Start'}</span>
            </button>

            <div style={{ marginLeft: 'auto', paddingRight: '0.5rem' }}>
                <LogsDropdown logs={logs} />
            </div>
        </div>
    );
};

export default Controls;
