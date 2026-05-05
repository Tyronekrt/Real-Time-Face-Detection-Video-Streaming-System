import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [currentROI, setCurrentROI] = useState(null);
  const [frameNumber, setFrameNumber] = useState(0);
  const [videoStats, setVideoStats] = useState({
    fps: 0,
    totalFrames: 0,
    detectedFaces: 0,
  });
  const [lastMessage, setLastMessage] = useState('');
  const canvasRef = useRef(null);
  const videoInputRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE_URL}/api/video/upload`, formData);
      setLastMessage(`File uploaded: ${response.data.video_session_id}`);
    } catch (error) {
      console.error('Error uploading video:', error);
      setLastMessage(`Error uploading video: ${error.message}`);
    }
  };

  const startWebcamStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      // Generate random session ID
      const sessionId = Math.random().toString(36).substring(7);
      
      // Connect to WebSocket
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${API_BASE_URL.split('://')[1]}/api/video/ws/${sessionId}`;
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setLastMessage('Connected to video stream');
        
        // Start sending frames
        const sendFrame = () => {
          if (video.readyState === video.HAVE_ENOUGH_DATA && ws.readyState === WebSocket.OPEN) {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            canvas.toBlob((blob) => {
              if (ws.readyState === WebSocket.OPEN) {
                ws.send(blob);
              }
            }, 'image/jpeg', 0.8);
          }
          
          if (ws.readyState === WebSocket.OPEN) {
            requestAnimationFrame(sendFrame);
          }
        };
        
        sendFrame();
      };

      ws.onmessage = (event) => {
        // Parse JSON metadata
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const metadata = JSON.parse(e.target.result);
            setFrameNumber(metadata.frame_number);
            setVideoStats(prev => ({
              ...prev,
              totalFrames: metadata.frame_number + 1,
            }));
            
            if (metadata.roi) {
              setCurrentROI(metadata.roi);
              setVideoStats(prev => ({
                ...prev,
                detectedFaces: prev.detectedFaces + 1,
              }));
            }
          } catch (error) {
            console.error('Error parsing metadata:', error);
          }
        };
        
        reader.readAsText(event.data);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setLastMessage('WebSocket error');
      };

      ws.onclose = () => {
        setIsConnected(false);
        setLastMessage('Disconnected from video stream');
        stream.getTracks().forEach(track => track.stop());
      };

    } catch (error) {
      console.error('Error accessing webcam:', error);
      setLastMessage(`Error accessing webcam: ${error.message}`);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎥 Real-Time Face Detection</h1>
        <p>Video Streaming & ROI Tracking System</p>
      </header>

      <div className="container">
        <section className="video-section">
          <div className="video-container">
            <canvas 
              ref={canvasRef}
              className="video-canvas"
              width={640}
              height={480}
            />
            {currentROI && (
              <div className="roi-overlay">
                <div 
                  className="roi-box"
                  style={{
                    left: `${currentROI.x_min}px`,
                    top: `${currentROI.y_min}px`,
                    width: `${currentROI.x_max - currentROI.x_min}px`,
                    height: `${currentROI.y_max - currentROI.y_min}px`,
                  }}
                />
              </div>
            )}
          </div>

          <div className="controls">
            <div className="control-group">
              <label htmlFor="fileInput" className="file-label">
                📁 Upload Video
              </label>
              <input
                id="fileInput"
                type="file"
                accept="video/*"
                onChange={handleFileUpload}
                className="file-input"
              />
            </div>

            <button 
              onClick={startWebcamStream}
              disabled={isConnected}
              className="control-button"
            >
              {isConnected ? '🔴 Streaming' : '▶ Start Webcam'}
            </button>
          </div>
        </section>

        <section className="stats-section">
          <h2>📊 Statistics</h2>
          
          <div className="status-indicator">
            <div className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Frame Number</div>
              <div className="stat-value">{frameNumber}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Total Frames</div>
              <div className="stat-value">{videoStats.totalFrames}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Faces Detected</div>
              <div className="stat-value">{videoStats.detectedFaces}</div>
            </div>

            <div className="stat-card">
              <div className="stat-label">Average FPS</div>
              <div className="stat-value">{videoStats.fps}</div>
            </div>
          </div>

          {currentROI && (
            <div className="roi-details">
              <h3>Current Face ROI</h3>
              <ul>
                <li><strong>X-Min:</strong> {currentROI.x_min.toFixed(0)}px</li>
                <li><strong>Y-Min:</strong> {currentROI.y_min.toFixed(0)}px</li>
                <li><strong>X-Max:</strong> {currentROI.x_max.toFixed(0)}px</li>
                <li><strong>Y-Max:</strong> {currentROI.y_max.toFixed(0)}px</li>
                <li><strong>Confidence:</strong> {(currentROI.confidence * 100).toFixed(1)}%</li>
              </ul>
            </div>
          )}

          {lastMessage && (
            <div className="message-box">
              {lastMessage}
            </div>
          )}
        </section>
      </div>

      <footer className="app-footer">
        <p>AI-Powered Face Detection System • Backend: {API_BASE_URL}</p>
      </footer>
    </div>
  );
}

export default App;
