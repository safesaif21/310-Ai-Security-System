import React from 'react';
import { Play, Square, Video, VideoOff } from 'lucide-react';
import LogsDropdown from './LogsDropdown';
import api from '../utils/api';

const Controls = ({ camerasActive, setCamerasActive, detectionEnabled, recordingEnabled, setRecordingEnabled, logs }) => {
    const toggleCameras = () => {
        setCamerasActive(!camerasActive);
    };

    const toggleRecording = async () => {
        try {
            const newState = !recordingEnabled;
            const data = await api.post(`/recording/toggle?enabled=${newState}`);
            if (data.success) {
                setRecordingEnabled(newState);
            }
        } catch (error) {
            console.error('Error toggling recording:', error);
        }
    };

    return (
        <div style={{
            gridColumn: '1 / -1',
            display: 'flex',
            gap: '1rem',
            marginBottom: '1rem',
            alignItems: 'center'
        }}>
            <button
                className={`btn ${camerasActive ? 'btn-danger' : 'btn-success'}`}
                onClick={toggleCameras}
                style={{ flex: 1, justifyContent: 'center', padding: '1rem' }}
            >
                {camerasActive ? <Square size={20} /> : <Play size={20} />}
                {camerasActive ? 'Stop All Cameras' : 'Start All Cameras'}
            </button>

            <button
                className={`btn ${recordingEnabled ? 'btn-danger' : 'btn-primary'}`}
                onClick={toggleRecording}
                disabled={!camerasActive}
                style={{ flex: 1, justifyContent: 'center', padding: '1rem' }}
            >
                {recordingEnabled ? <VideoOff size={20} /> : <Video size={20} />}
                {recordingEnabled ? 'Stop Recording' : 'Start Recording'}
            </button>

            <div style={{ marginLeft: 'auto' }}>
                <LogsDropdown logs={logs} />
            </div>
        </div>
    );
};

export default Controls;
