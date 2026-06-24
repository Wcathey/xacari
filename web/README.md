# Xacari Web Testing Interface

React-based web app for testing RTMPose integration with webcam.

## Setup

```bash
# Install dependencies
npm install

# Start the React app
npm start
```

The app will open at `http://localhost:3000`

## Backend Connection

Make sure the FastAPI backend is running:

```bash
cd ../backend
source xacari_venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Features

- ✅ Webcam capture using react-webcam
- ✅ Canvas overlay for skeleton rendering
- ✅ Real-time pose detection via backend API
- ✅ Out-of-frame detection and alerts
- ✅ FPS monitoring
- ✅ Confidence scoring
- ✅ Adjustable frame rate

## How It Works

1. **Webcam** captures video frames
2. **Frame extraction** converts to base64 JPEG
3. **HTTP POST** sends frame to backend `/api/pose/analyze`
4. **Backend** processes with pose model (currently mock data, will be RTMPose)
5. **Response** returns 17 keypoints with x, y, confidence
6. **Canvas overlay** draws skeleton on top of webcam feed
7. **Alerts** notify when user goes out of frame

## Next Steps

1. Test the connection end-to-end
2. Integrate actual RTMPose model in backend
3. Fine-tune skeleton rendering
4. Add more workout-specific features

## Current Status

- React app: ✅ Complete
- Backend endpoint: ✅ Complete with mock data  
- RTMPose integration: ⚠️ TODO (currently using mock keypoints)
