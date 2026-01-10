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
