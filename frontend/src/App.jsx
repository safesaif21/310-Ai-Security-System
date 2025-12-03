import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CameraGrid from './components/CameraGrid';
import Controls from './components/Controls';
import './index.css';

function App() {
  const [cameras, setCameras] = useState([]);
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null);
  const [detectionEnabled, setDetectionEnabled] = useState(false);
  const [stats, setStats] = useState({
    people_count: 0,
    weapon_detected: false,
    threat_level: 0
  });
  const [camerasActive, setCamerasActive] = useState(false);
  const [systemStatus, setSystemStatus] = useState('OFFLINE');
  const [recordingEnabled, setRecordingEnabled] = useState(false);

  const BACKEND_URL = 'http://localhost:8000';

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch cameras
        const camerasRes = await fetch(`${BACKEND_URL}/cameras`);
        const camerasData = await camerasRes.json();
        setCameras(camerasData.cameras);
        setSystemStatus('ONLINE');
      } catch (error) {
        console.error('Error fetching cameras:', error);
        setSystemStatus('OFFLINE');
      }

      try {
        // Fetch models
        const modelsRes = await fetch(`${BACKEND_URL}/models`);
        const modelsData = await modelsRes.json();
        setModels(modelsData.models);
        setCurrentModel(modelsData.current_model);
        setDetectionEnabled(modelsData.detection_enabled);
      } catch (error) {
        console.error('Error fetching models:', error);
      }
    };

    fetchData();
  }, []);

  // Poll for stats
  useEffect(() => {
    let interval;
    if (detectionEnabled && camerasActive) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${BACKEND_URL}/stats`);
          const data = await response.json();
          setStats({
            people_count: data.people_count,
            weapon_detected: data.weapon_detected,
            threat_level: data.threat_level
          });
        } catch (error) {
          console.error('Error fetching stats:', error);
        }
      }, 500);
    } else {
      // Reset stats when detection is off
      setStats(prev => ({ ...prev, people_count: 0, weapon_detected: false, threat_level: 0 }));
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [detectionEnabled, camerasActive]);

  return (
    <div className="app-container">
      <Header cameraCount={cameras.length} />

      <main className="main-content" style={{
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        overflow: 'hidden',
        minHeight: 0
      }}>
        <Controls
          camerasActive={camerasActive}
          setCamerasActive={setCamerasActive}
          detectionEnabled={detectionEnabled}
          recordingEnabled={recordingEnabled}
          setRecordingEnabled={setRecordingEnabled}
        />
        <CameraGrid
          cameras={cameras}
          camerasActive={camerasActive}
        />
      </main>

      <Sidebar
        models={models}
        currentModel={currentModel}
        setCurrentModel={setCurrentModel}
        detectionEnabled={detectionEnabled}
        setDetectionEnabled={setDetectionEnabled}
        stats={stats}
        systemStatus={systemStatus}
      />
    </div>
  );
}

export default App;
