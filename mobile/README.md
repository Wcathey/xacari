# Xacari Mobile App

React Native + Expo mobile application for the Xacari AI workout coach.

## Project Status

✅ **Phase 2 Foundation - COMPLETE**

Core infrastructure is ready for development!

### Completed
- ✅ React Native + Expo setup
- ✅ TypeScript configuration
- ✅ Folder structure created
- ✅ Supabase client configured
- ✅ Navigation (React Navigation)
- ✅ State management (Zustand)
- ✅ WebSocket service
- ✅ API service (REST)
- ✅ Pose detection abstraction layer
- ✅ Authentication store
- ✅ Workout store

### Next Steps
- [ ] Update configuration (local IP, Supabase credentials)
- [ ] Implement auth screens
- [ ] Add camera component
- [ ] Implement skeleton rendering
- [ ] Integrate RTMPose/custom model

## Quick Start

### 1. Install Dependencies

Dependencies are already installed. If you need to reinstall:

```bash
cd mobile
npm install
```

### 2. Configure the App

Edit `src/config/index.ts`:

```typescript
// Find your local IP
// Mac/Linux: ifconfig | grep "inet "
// Windows: ipconfig

const getLocalIP = () => {
  return '192.168.1.100'; // Replace with YOUR actual IP
};

export const CONFIG = {
  SUPABASE: {
    URL: 'https://xxxxx.supabase.co', // Your Supabase URL
    ANON_KEY: 'your-anon-key-here',   // Your Supabase anon key
  },
  // ... rest of config
};
```

### 3. Start the App

```bash
# Start Expo dev server
npx expo start

# Then choose your platform:
# Press 'a' for Android emulator
# Press 'i' for iOS simulator (Mac only)
# Scan QR code with Expo Go app on iPhone
```

### 4. Make Sure Backend is Running

```bash
# In another terminal, from the backend directory:
cd ../backend
source xacari_env/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
mobile/
├── src/
│   ├── components/         # Reusable components
│   │   ├── common/        # Generic UI components
│   │   ├── pose/          # Pose detection components
│   │   └── workout/       # Workout-specific components
│   ├── config/            # Configuration
│   │   ├── index.ts       # Main config (UPDATE THIS!)
│   │   └── supabase.ts    # Supabase client
│   ├── navigation/        # Navigation setup
│   ├── screens/           # App screens
│   │   ├── auth/          # Login, SignUp
│   │   ├── workout/       # Workout screens
│   │   ├── profile/       # Profile screens
│   │   └── WelcomeScreen.tsx
│   ├── services/          # Business logic
│   │   ├── api.ts         # REST API service
│   │   ├── websocket.ts   # WebSocket service
│   │   └── poseDetection/ # Pose detection models
│   │       ├── BasePoseModel.ts
│   │       ├── XacariPoseModel.ts  # Custom model placeholder
│   │       └── index.ts
│   ├── stores/            # State management (Zustand)
│   │   ├── useAuthStore.ts
│   │   └── useWorkoutStore.ts
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   └── utils/             # Utility functions
├── App.tsx                # App entry point
├── package.json
└── README.md
```

## Key Features

### 1. Pose Detection Abstraction

The app uses an abstraction layer for pose detection models, making it easy to swap between different models:

```typescript
// Currently uses XacariPoseModel (placeholder)
// Easy to add RTMPose or other models

import PoseDetectionService from './services/poseDetection';

const model = await PoseDetectionService.getModel();
const poseData = await model.estimatePose(videoFrame);
```

**Files:**
- `src/services/poseDetection/BasePoseModel.ts` - Base class
- `src/services/poseDetection/XacariPoseModel.ts` - Your custom model (currently mock)

### 2. Real-time Communication

WebSocket service for real-time pose data streaming and feedback:

```typescript
import websocketService from './services/websocket';

// Connect
await websocketService.connect(sessionId, userId);

// Send pose data
websocketService.sendPoseData(poseData);

// Receive feedback
websocketService.onMessage((message) => {
  if (message.type === 'feedback') {
    console.log('Received feedback:', message.message);
  }
});
```

### 3. State Management

Zustand stores for clean state management:

```typescript
// Auth
import { useAuthStore } from './stores/useAuthStore';
const { user, signIn, signOut } = useAuthStore();

// Workout
import { useWorkoutStore } from './stores/useWorkoutStore';
const { currentSession, startSession, updatePoseData } = useWorkoutStore();
```

### 4. API Service

REST API client for backend communication:

```typescript
import apiService from './services/api';

// Create workout session
const response = await apiService.createWorkoutSession(
  userId,
  'strength',
  ['squat', 'pushup'],
  [10, 15]
);

// Start session
await apiService.startWorkoutSession(sessionId);
```

## Integrating Your Custom Model (RTMPose)

The app is designed to make custom model integration easy. You have several options:

### Option 1: ONNX Runtime (Recommended)

```bash
npm install onnxruntime-react-native
```

Update `src/services/poseDetection/XacariPoseModel.ts`:

```typescript
import { InferenceSession } from 'onnxruntime-react-native';

export class XacariPoseModel extends BasePoseModel {
  private session: InferenceSession | null = null;

  async load(): Promise<void> {
    // Load your RTMPose ONNX model
    this.session = await InferenceSession.create('path/to/rtmpose.onnx');
    this.isLoaded = true;
  }

  async estimatePose(videoFrame: any): Promise<PoseData | null> {
    // Run inference
    const input = await this.preprocessFrame(videoFrame);
    const output = await this.session.run(input);
    return this.postprocessOutput(output);
  }
}
```

### Option 2: Backend Processing

Send frames to your FastAPI backend for processing:

```typescript
async estimatePose(videoFrame: any): Promise<PoseData | null> {
  // Convert frame to base64
  const base64Frame = await this.frameToBase64(videoFrame);

  // Send to backend
  const response = await fetch(`${CONFIG.API.BASE_URL}/api/pose/analyze`, {
    method: 'POST',
    body: JSON.stringify({ frame: base64Frame }),
  });

  return await response.json();
}
```

### Option 3: Custom Native Module

Build a React Native bridge to your model (advanced):

```bash
# Create native module that wraps your Python/C++ RTMPose code
# Then use it in React Native
```

## Environment Variables

Create a `.env` file (not tracked in git):

```bash
EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
EXPO_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-key-here
```

## Testing Backend Connection

The Welcome screen automatically tests the backend connection on startup.

You should see:
- ✅ Backend Connected (with version number)

If you see an error:
1. Check that backend is running (`uvicorn app.main:app --reload`)
2. Verify `CONFIG.API.BASE_URL` has your correct local IP
3. Make sure phone/emulator is on same network as dev machine

## Development Tips

### Hot Reload
- Press `r` in Expo CLI to reload
- Shake device to open dev menu
- Code changes auto-reload

### Debugging
```typescript
// Console logs appear in Expo CLI
console.log('Debug info:', data);

// Use React Native Debugger
// Or Chrome DevTools (press 'm' in Expo, then "Debug remote JS")
```

### Testing API Endpoints

Use the Swagger UI at `http://localhost:8000/docs` to test backend endpoints.

## Common Issues

### Issue: "Cannot connect to backend"

**Solution:**
1. Find your local IP:
   ```bash
   # Mac/Linux
   ifconfig | grep "inet "

   # Windows
   ipconfig
   ```
2. Update `src/config/index.ts` with your IP
3. Restart Expo server

### Issue: "Module not found"

**Solution:**
```bash
npm install
# Then restart Expo
```

### Issue: "Supabase errors"

**Solution:**
1. Check that you've added credentials to `src/config/index.ts`
2. Verify credentials are correct in Supabase Dashboard
3. Make sure database schema is created

## Next Development Steps

### 1. Configuration (Required First!)

Edit `src/config/index.ts`:
- Add your local IP address
- Add Supabase credentials

### 2. Authentication Screens

Create:
- `src/screens/auth/LoginScreen.tsx`
- `src/screens/auth/SignUpScreen.tsx`

Add to App.tsx navigation.

### 3. Camera Component

```bash
# Expo Camera is already installed
```

Create:
- `src/components/pose/CameraView.tsx`
- Request camera permissions
- Capture frames for pose detection

### 4. Skeleton Rendering

Create:
- `src/components/pose/SkeletonOverlay.tsx`
- Draw keypoints and connections
- Color-code by confidence

### 5. Custom Model Integration

Update `src/services/poseDetection/XacariPoseModel.ts`:
- Load your RTMPose model (ONNX or backend)
- Implement actual inference
- Process and return keypoints

## Resources

- [Expo Docs](https://docs.expo.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Supabase Docs](https://supabase.com/docs)
- [Zustand](https://github.com/pmndrs/zustand)
- [RTMPose](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmpose)
- [ONNX Runtime](https://onnxruntime.ai/docs/tutorials/mobile/react-native.html)

## Scripts

```bash
# Start development server
npx expo start

# Run on Android
npx expo start --android

# Run on iOS (Mac only)
npx expo start --ios

# Clear cache
npx expo start -c

# Type check
npx tsc --noEmit

# Build for production (later)
eas build --platform ios
eas build --platform android
```

## Support

See main project documentation:
- `/QUICKSTART.md` - Quick start guide
- `/PROJECT_STATUS.md` - Full project status
- `/POSE_DETECTION_ANALYSIS.md` - Model comparison

---

**Status**: Mobile foundation complete! Ready for feature development.

**Next**: Configure app, then build auth screens and camera component.
