import React, { useRef, useEffect, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { PoseData, DetectionStats, AlertMessage } from '../types';
import { SKELETON_CONNECTIONS, getConfidenceColor } from '../utils/skeletonConnections';
import './PoseDetector.css';

const BACKEND_URL = 'http://localhost:8000';
const CONFIDENCE_THRESHOLD = 0.3;

const PoseDetector: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const requestRef = useRef<number | undefined>(undefined);
  const frameCountRef = useRef<number>(0);
  const lastFrameTimeRef = useRef<number>(0);

  const [isDetecting, setIsDetecting] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const [alerts, setAlerts] = useState<AlertMessage[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<string>('squat');
  const [formFeedback, setFormFeedback] = useState<string[]>([]);
  const [formScore, setFormScore] = useState<number>(0);
  const [stats, setStats] = useState<DetectionStats>({
    fps: 0,
    framesProcessed: 0,
    avgConfidence: 0,
    keypointsDetected: 0,
    inFrame: true,
  });
  const [fpsLimit, setFpsLimit] = useState(10);

  const addAlert = useCallback((type: AlertMessage['type'], message: string) => {
    const newAlert: AlertMessage = {
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date(),
    };
    setAlerts((prev) => [newAlert, ...prev].slice(0, 10));
  }, []);

  // Check backend connection
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/health`);
        if (response.status === 200) {
          setBackendConnected(true);
          addAlert('success', 'Backend connected successfully');
        }
      } catch (error) {
        setBackendConnected(false);
        addAlert('error', 'Backend not connected. Make sure server is running.');
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, [addAlert]);

  // Draw skeleton on canvas
  const drawSkeleton = useCallback((pose: PoseData) => {
    const canvas = canvasRef.current;
    const video = webcamRef.current?.video;

    if (!canvas || !video) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const { keypoints } = pose;

    // Create keypoint map for easy lookup
    const keypointMap = new Map(keypoints.map(kp => [kp.name, kp]));

    // Draw skeleton connections
    ctx.lineWidth = 3;
    SKELETON_CONNECTIONS.forEach(([point1, point2]) => {
      const kp1 = keypointMap.get(point1);
      const kp2 = keypointMap.get(point2);

      if (kp1 && kp2 && kp1.confidence > CONFIDENCE_THRESHOLD && kp2.confidence > CONFIDENCE_THRESHOLD) {
        const x1 = kp1.x * canvas.width;
        const y1 = kp1.y * canvas.height;
        const x2 = kp2.x * canvas.width;
        const y2 = kp2.y * canvas.height;

        const avgConfidence = (kp1.confidence + kp2.confidence) / 2;
        ctx.strokeStyle = getConfidenceColor(avgConfidence);

        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    });

    // Draw keypoints (excluding face keypoints)
    const faceKeypoints = ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear'];
    keypoints.forEach((kp) => {
      // Skip face keypoints
      if (faceKeypoints.includes(kp.name)) return;

      if (kp.confidence > CONFIDENCE_THRESHOLD) {
        const x = kp.x * canvas.width;
        const y = kp.y * canvas.height;

        // Draw outer circle
        ctx.fillStyle = getConfidenceColor(kp.confidence);
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, 2 * Math.PI);
        ctx.fill();

        // Draw inner circle
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
      }
    });

    // Draw frame indicator if out of frame
    if (!pose.in_frame) {
      ctx.strokeStyle = '#ff4444';
      ctx.lineWidth = 10;
      ctx.strokeRect(5, 5, canvas.width - 10, canvas.height - 10);

      ctx.fillStyle = 'rgba(255, 68, 68, 0.2)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw warning text
      ctx.fillStyle = '#ff4444';
      ctx.font = 'bold 48px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('OUT OF FRAME', canvas.width / 2, canvas.height / 2);
    }
  }, []);

  // Process frame
  const processFrame = useCallback(async () => {
    if (!isDetecting || !webcamRef.current || !backendConnected) {
      return;
    }

    const now = Date.now();
    const elapsed = now - lastFrameTimeRef.current;
    const targetInterval = 1000 / fpsLimit;

    if (elapsed < targetInterval) {
      requestRef.current = requestAnimationFrame(processFrame);
      return;
    }

    lastFrameTimeRef.current = now;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) {
      requestRef.current = requestAnimationFrame(processFrame);
      return;
    }

    try {
      // Send frame to backend with selected exercise
      const response = await axios.post(`${BACKEND_URL}/api/pose/analyze`, {
        frame: imageSrc.split(',')[1], // Remove data:image/jpeg;base64, prefix
        confidence_threshold: CONFIDENCE_THRESHOLD,
        exercise_type: selectedExercise,
      });

      const poseData: PoseData = response.data;

      // Update form feedback if exercise validation is present
      if (poseData.exercise_validation) {
        setFormFeedback(poseData.exercise_validation.feedback || []);
        setFormScore(poseData.exercise_validation.form_score || 0);
      }

      // Draw skeleton
      drawSkeleton(poseData);

      // Update stats
      frameCountRef.current++;
      const validKeypoints = poseData.keypoints.filter(kp => kp.confidence > CONFIDENCE_THRESHOLD).length;

      setStats({
        fps: Math.round(1000 / elapsed),
        framesProcessed: frameCountRef.current,
        avgConfidence: poseData.overall_confidence,
        keypointsDetected: validKeypoints,
        inFrame: poseData.in_frame,
      });

    } catch (error) {
      console.error('Error processing frame:', error);
      if (axios.isAxiosError(error)) {
        addAlert('error', `Backend error: ${error.message}`);
      }
    }

    requestRef.current = requestAnimationFrame(processFrame);
  }, [isDetecting, backendConnected, fpsLimit, drawSkeleton, addAlert, stats.inFrame, selectedExercise]);

  // Start/stop detection
  useEffect(() => {
    if (isDetecting) {
      requestRef.current = requestAnimationFrame(processFrame);
    } else {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    }

    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [isDetecting, processFrame]);

  const handleStartDetection = () => {
    if (!backendConnected) {
      addAlert('error', 'Backend not connected!');
      return;
    }
    frameCountRef.current = 0;
    lastFrameTimeRef.current = Date.now();
    setIsDetecting(true);
    addAlert('success', 'Pose detection started');
  };

  const handleStopDetection = () => {
    setIsDetecting(false);
    addAlert('info', 'Pose detection stopped');

    // Clear canvas
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  return (
    <div className="pose-detector">
      <div className="main-content">
        <div className="video-section">
          <div className="video-container">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={{
                width: 1280,
                height: 720,
                facingMode: 'user',
              }}
              className="webcam"
            />
            <canvas ref={canvasRef} className="canvas-overlay" />
            <div className="fps-badge">{stats.fps} FPS</div>
          </div>
        </div>

        <div className="controls-section">
          <div className="status-badges">
            <span className={`badge ${backendConnected ? 'connected' : 'disconnected'}`}>
              {backendConnected ? '✓ Backend' : '✗ Backend'}
            </span>
            <span className={`badge ${isDetecting ? 'detecting' : 'idle'}`}>
              {isDetecting ? '🔴 Detecting' : '⚫ Idle'}
            </span>
          </div>

          <div className="control-group">
            <h3>Exercise</h3>
            <div className="setting">
              <label>
                Select Exercise:
                <select
                  value={selectedExercise}
                  onChange={(e) => setSelectedExercise(e.target.value)}
                  className="exercise-select"
                >
                  <option value="squat">Squat</option>
                  <option value="pushup">Push-up</option>
                  <option value="plank">Plank</option>
                  <option value="lunge">Lunge</option>
                </select>
              </label>
            </div>
          </div>

          <div className="control-group">
            <h3>Controls</h3>
            <button
              onClick={handleStartDetection}
              disabled={isDetecting || !backendConnected}
              className="btn btn-primary"
            >
              Start Detection
            </button>
            <button
              onClick={handleStopDetection}
              disabled={!isDetecting}
              className="btn btn-danger"
            >
              Stop Detection
            </button>
          </div>

          {isDetecting && formFeedback.length > 0 && (
            <div className="control-group">
              <h3>Form Feedback</h3>
              <div className="form-score">
                <span>Form Score: </span>
                <span className={`score ${formScore >= 80 ? 'good' : formScore >= 60 ? 'medium' : 'bad'}`}>
                  {formScore}/100
                </span>
              </div>
              <div className="feedback-list">
                {formFeedback.map((feedback, idx) => (
                  <div key={idx} className="feedback-item">
                    {feedback}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="control-group">
            <h3>Settings</h3>
            <div className="setting">
              <label>
                Frame Rate: {fpsLimit} FPS
                <input
                  type="range"
                  min="5"
                  max="30"
                  step="5"
                  value={fpsLimit}
                  onChange={(e) => setFpsLimit(Number(e.target.value))}
                />
              </label>
            </div>
          </div>

          <div className="control-group">
            <h3>Statistics</h3>
            <div className="stats">
              <div className="stat-row">
                <span>FPS</span>
                <span className="value">{stats.fps}</span>
              </div>
              <div className="stat-row">
                <span>Frames Processed</span>
                <span className="value">{stats.framesProcessed}</span>
              </div>
              <div className="stat-row">
                <span>Confidence</span>
                <span className={`value ${stats.avgConfidence > 0.7 ? 'good' : stats.avgConfidence > 0.4 ? 'medium' : 'bad'}`}>
                  {(stats.avgConfidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="stat-row">
                <span>Keypoints</span>
                <span className="value">{stats.keypointsDetected}/17</span>
              </div>
              <div className="stat-row">
                <span>In Frame</span>
                <span className={`value ${stats.inFrame ? 'good' : 'bad'}`}>
                  {stats.inFrame ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          <div className="control-group">
            <h3>Alerts</h3>
            <div className="alerts">
              {alerts.length === 0 ? (
                <div className="alert info">No alerts yet...</div>
              ) : (
                alerts.map((alert) => (
                  <div key={alert.id} className={`alert ${alert.type}`}>
                    {alert.message}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PoseDetector;
