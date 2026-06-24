import React from 'react';
import './App.css';
import PoseDetector from './components/PoseDetector';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🏋️ Xacari RTMPose Testing</h1>
        <p>React + Webcam + RTMPose Backend</p>
      </header>
      <PoseDetector />
    </div>
  );
}

export default App;
