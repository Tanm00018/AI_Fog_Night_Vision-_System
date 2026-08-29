import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [mode, setMode] = useState('normal')
  const [fogStrength, setFogStrength] = useState(50)
  const [brightness, setBrightness] = useState(50)
  const [contrast, setContrast] = useState(50)
  const [splitScreen, setSplitScreen] = useState(false)
  const [edgeHighlight, setEdgeHighlight] = useState(false)
  
  const [fps, setFps] = useState(30)
  const [speed, setSpeed] = useState(65)
  const [heading, setHeading] = useState('NNE')
  
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  
  // Real-time clock for the HUD
  const [time, setTime] = useState(new Date().toLocaleTimeString())

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // Mock telemetry data simulation
  useEffect(() => {
    const telemetryTimer = setInterval(() => {
      setSpeed(prev => {
        const change = Math.floor(Math.random() * 5) - 2;
        return Math.max(0, Math.min(120, prev + change));
      });
      const headings = ['N', 'NNE', 'NE', 'NNE', 'N'];
      setHeading(headings[Math.floor(Math.random() * headings.length)]);
      setFps(Math.floor(Math.random() * 5) + 28);
    }, 2000);
    return () => clearInterval(telemetryTimer);
  }, []);

  // Update backend when settings change
  useEffect(() => {
    const updateSettings = async () => {
      try {
        await fetch('/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            mode,
            fog_strength: fogStrength,
            brightness,
            contrast,
            split_screen: splitScreen,
            edge_highlight: edgeHighlight
          }),
        })
      } catch (err) {
        console.error("Failed to update settings:", err)
      }
    }
    
    updateSettings()
  }, [mode, fogStrength, brightness, contrast, splitScreen, edgeHighlight])

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      const response = await fetch('/upload_video?filename=' + encodeURIComponent(file.name), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/octet-stream'
        },
        body: file,
      });
      const result = await response.json();
      if (result.status === 'success') {
        setUploadStatus('Upload Complete');
      } else {
        setUploadStatus('Upload Failed');
      }
    } catch (err) {
      console.error("Upload error:", err);
      setUploadStatus('Upload Error');
    } finally {
      setIsUploading(false);
      // Clear status after 3 seconds
      setTimeout(() => setUploadStatus(''), 3000);
      // Reset the file input
      event.target.value = null;
    }
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header glass-panel">
        <div className="logo">
          <span className="logo-icon">◎</span>
          <h1>AeroVision Dashcam</h1>
        </div>
        <div className="status-indicators">
          {uploadStatus && <span className="indicator battery">{uploadStatus}</span>}
          <label className="upload-button indicator">
            {isUploading ? 'Uploading...' : 'Upload Video'}
            <input 
              type="file" 
              accept="video/*" 
              onChange={handleFileUpload} 
              disabled={isUploading}
              style={{ display: 'none' }} 
            />
          </label>
          <span className="indicator live">● LIVE</span>
        </div>
      </header>

      <div className="dashboard-main">
        {/* Main Video View */}
        <div className="video-section glass-panel">
          <div className="video-container">
            {/* The scanline effect overlay */}
            <div className="scanlines"></div>
            
            {/* The MJPEG stream from the backend */}
            <img 
              src="/video_feed" 
              alt="Live Video Feed" 
              className={`video-stream ${mode}`}
              onError={(e) => {
                e.target.onerror = null; 
                e.target.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='480' fill='%23333'><rect width='100%25' height='100%25'/><text x='50%25' y='50%25' fill='%23666' font-size='24' font-family='sans-serif' text-anchor='middle'>Stream Unavailable</text></svg>";
              }}
            />
            
            {/* HUD Overlays */}
            <div className="hud-overlay top-left">
              <div className="hud-item">{time}</div>
            </div>
            <div className="hud-overlay top-right">
              <div className="hud-item mode-indicator">
                {edgeHighlight ? 'ADAS MODE' : `MODE: ${mode.toUpperCase()}`}
              </div>
            </div>
            <div className="hud-overlay bottom-left">
              <div className="hud-item telemetry">
                <div>SPD: {speed} km/h</div>
                <div>HDG: {heading}</div>
                <div>FPS: {fps}</div>
              </div>
            </div>
            <div className="hud-overlay bottom-right">
              <div className="hud-item rec">REC</div>
            </div>
          </div>
        </div>

        {/* Control Panel */}
        <div className="control-panel glass-panel">
          <h2>Vision Controls</h2>
          
          <div className="control-group">
            <label>Operating Mode</label>
            <div className="mode-buttons">
              <button 
                className={mode === 'normal' ? 'active' : ''} 
                onClick={() => setMode('normal')}
              >
                <span>Normal</span>
              </button>
              <button 
                className={mode === 'fog' ? 'active' : ''} 
                onClick={() => setMode('fog')}
              >
                <span>Fog Vision</span>
              </button>
              <button 
                className={mode === 'night' ? 'active' : ''} 
                onClick={() => setMode('night')}
              >
                <span>Night Vision</span>
              </button>
            </div>
          </div>

          <div className="control-group">
            <label>Advanced Features</label>
            <div className="toggle-container">
              <span className="toggle-label">Split Screen (Raw vs AI)</span>
              <label className="switch">
                <input type="checkbox" checked={splitScreen} onChange={(e) => setSplitScreen(e.target.checked)} />
                <span className="slider round"></span>
              </label>
            </div>
            <div className="toggle-container">
              <span className="toggle-label">ADAS Edge Detection</span>
              <label className="switch">
                <input type="checkbox" checked={edgeHighlight} onChange={(e) => setEdgeHighlight(e.target.checked)} />
                <span className="slider round"></span>
              </label>
            </div>
          </div>

          {mode === 'fog' && (
            <div className="control-group fade-in">
              <label>Dehaze Strength: {fogStrength}</label>
              <input 
                type="range" 
                min="0" max="100" 
                value={fogStrength} 
                onChange={(e) => setFogStrength(Number(e.target.value))}
              />
            </div>
          )}

          <div className="control-group">
            <label>Brightness: {brightness}</label>
            <input 
              type="range" 
              min="0" max="100" 
              value={brightness} 
              onChange={(e) => setBrightness(Number(e.target.value))}
            />
          </div>

          <div className="control-group">
            <label>Contrast: {contrast}</label>
            <input 
              type="range" 
              min="0" max="100" 
              value={contrast} 
              onChange={(e) => setContrast(Number(e.target.value))}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
