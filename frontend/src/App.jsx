import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import CameraGrid from './components/CameraGrid';

import Navigation from './components/Navigation';
import RecordingsView from './components/RecordingsView';
import LogsView from './components/LogsView';
import api from './utils/api';
import './index.css';

function Dashboard() {
  const { user, logout } = useAuth();
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMobile = windowWidth <= 1024;
  const isSmartphone = windowWidth <= 768;

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

  // Persistent state for Recordings View
  const [selectedRecordingCamera, setSelectedRecordingCamera] = useState(null);
  const [selectedRecordingFile, setSelectedRecordingFile] = useState(null);

  // Persistent state for Logs View
  const [selectedLogDate, setSelectedLogDate] = useState('');

  // Persistent scroll position for Recordings View
  const [recordingScrollTop, setRecordingScrollTop] = useState(0);

  // Determine Backend URL dynamically
  // If loaded from localhost, use localhost. If network IP, use compatible IP.
  // Port 8040 is hardcoded for backend.
  // Port 8040 is hardcoded for backend (Auth).
  const BACKEND_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8040`;

  // Fetch initial data and poll for cameras if missing
  useEffect(() => {
    const fetchCameras = async () => {
      try {
        // Fetch cameras from Camera Service
        const camerasData = await api.camera.get('/cameras');
        if (camerasData.cameras && camerasData.cameras.length > 0) {
          const camerasWithUrl = camerasData.cameras.map(cam => ({
            ...cam,
            // POINT TO ANALYSIS SERVICE FOR ANNOTATED FEED
            url: `${api.SERVICES.ANALYSIS}/annotated/${cam.id}`
          }));
          setCameras(camerasWithUrl);
          setSystemStatus('ONLINE');
        }
      } catch (error) {
        console.error('Error fetching cameras:', error);
        setSystemStatus('OFFLINE');
      }
    };

    const fetchModels = async () => {
      try {
        // Fetch models from Analysis Service
        const modelsData = await api.analysis.get('/models');
        setModels(modelsData.models);
        setCurrentModel(modelsData.current_model);
        setDetectionEnabled(modelsData.detection_enabled);
      } catch (error) {
        console.error('Error fetching models:', error);
      }
    };

    // Initial load
    fetchCameras();
    fetchModels();

    // Retry loop: If no cameras are found, keep looking every 10 seconds
    // This handles the case where the frontend starts before the camera server
    const interval = setInterval(() => {
      if (cameras.length === 0) {
        fetchCameras();
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [cameras.length]); // Re-evaluate if camera count changes

  // Poll for stats from Analysis Service
  useEffect(() => {
    let interval;
    if (detectionEnabled && camerasActive) {
      interval = setInterval(async () => {
        try {
          const data = await api.analysis.get('/stats');
          setStats({
            people_count: data.people_count,
            weapon_detected: data.weapon_detected,
            threat_level: data.threat_level
          });
        } catch (error) {
          console.error('Error fetching stats:', error);
        }
      }, isSmartphone ? 2000 : 500); // Slower polling on mobile to unblock streams
    } else {
      setStats(prev => ({ ...prev, people_count: 0, weapon_detected: false, threat_level: 0 }));
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [detectionEnabled, camerasActive, isSmartphone]);

  // Poll for logs from DVR Service
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await api.dvr.get('/logs');
        setLogs(data.logs);
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, isSmartphone ? 5000 : 2000);
    return () => clearInterval(interval);
  }, [isSmartphone]); // Re-run if device type changes

  // Monitor system status (Auth Service)
  useEffect(() => {
    const checkStatus = async () => {
      try {
        await fetch(`${api.SERVICES.AUTH}/health`);
        setSystemStatus('ONLINE');
      } catch (error) {
        setSystemStatus('OFFLINE');
      }
    };

    const interval = setInterval(checkStatus, isSmartphone ? 10000 : 5000);
    return () => clearInterval(interval);
  }, [isSmartphone]);

  return (
    <div className="app-container">
      <Header
        cameraCount={cameras.length}
        systemStatus={systemStatus}
        user={user}
        onLogout={logout}
      />

      <main className="main-content" style={{
        padding: isSmartphone ? '1rem' : '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        overflow: isMobile ? 'visible' : 'hidden',
        minHeight: 0
      }}>
        <Navigation currentView={currentView} onViewChange={setCurrentView} />

        {currentView === 'interface' && (
          <CameraGrid
            cameras={cameras}
            camerasActive={camerasActive}
            isSmartphone={isSmartphone}
          />
        )}

        {currentView === 'recordings' && (
          <RecordingsView
            cameras={cameras}
            isSmartphone={isSmartphone}
            selectedCamera={selectedRecordingCamera}
            setSelectedCamera={setSelectedRecordingCamera}
            selectedFile={selectedRecordingFile}
            setSelectedFile={setSelectedRecordingFile}
            scrollTop={recordingScrollTop}
            setScrollTop={setRecordingScrollTop}
          />
        )}

        {currentView === 'logs' && (
          <LogsView
            selectedDate={selectedLogDate}
            setSelectedDate={setSelectedLogDate}
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
