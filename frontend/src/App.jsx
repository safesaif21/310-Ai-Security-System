import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CameraGrid from './components/CameraGrid';

import Navigation from './components/Navigation';
import RecordingsView from './components/RecordingsView';
import LogsView from './components/LogsView';
import './index.css';

function Dashboard() {
  const { user, logout } = useAuth();
  const [cameras, setCameras] = useState([]);
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null);
  const [detectionEnabled, setDetectionEnabled] = useState(false);
  const [stats, setStats] = useState({
    people_count: 0,
    weapon_detected: false,
    threat_level: 0
  });
  const [camerasActive, setCamerasActive] = useState(true);
  const [systemStatus, setSystemStatus] = useState('OFFLINE');
  const [recordingEnabled, setRecordingEnabled] = useState(false);
  const [logs, setLogs] = useState([]);
  const [currentView, setCurrentView] = useState('interface');

  // Determine Backend URL dynamically
  // If loaded from localhost, use localhost. If network IP, use compatible IP.
  // Port 8000 is hardcoded for backend.
  const BACKEND_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;
  // const BACKEND_URL = 'http://localhost:8000';

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch cameras
        const camerasRes = await fetch(`${BACKEND_URL}/cameras`);
        const camerasData = await camerasRes.json();
        const camerasWithUrl = camerasData.cameras.map(cam => ({
          ...cam,
          url: `${BACKEND_URL}${cam.url}`
        }));
        setCameras(camerasWithUrl);
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

  // Poll for logs
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/logs`);
        const data = await response.json();
        setLogs(data.logs);
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };

    // Initial fetch
    fetchLogs();

    // Poll every 2 seconds
    const interval = setInterval(fetchLogs, 2000);

    return () => clearInterval(interval);
  }, []);

  // Monitor system status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        await fetch(`${BACKEND_URL}/`);
        setSystemStatus('ONLINE');
      } catch (error) {
        setSystemStatus('OFFLINE');
      }
    };

    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <Header
        cameraCount={cameras.length}
        systemStatus={systemStatus}
        user={user}
        onLogout={logout}
      />

      <main className="main-content" style={{
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        overflow: 'hidden',
        minHeight: 0
      }}>
        <Navigation currentView={currentView} onViewChange={setCurrentView} />

        {currentView === 'interface' && (
          <CameraGrid
            cameras={cameras}
            camerasActive={camerasActive}
          />
        )}

        {currentView === 'recordings' && (
          <RecordingsView
            cameras={cameras}
            backendUrl={BACKEND_URL}
          />
        )}

        {currentView === 'logs' && (
          <LogsView
            backendUrl={BACKEND_URL}
          />
        )}
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

function AppContent() {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#0a0b0f'
      }}>
        <div style={{ color: 'white', fontSize: '1.25rem' }}>Loading...</div>
      </div>
    );
  }

  // Add key to force remount on login/logout - fixes camera state issues
  return isAuthenticated ? <Dashboard key={user?.id || 'dashboard'} /> : <Login />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
