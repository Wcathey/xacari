# Pose Detection Model Analysis: MoveNet vs RTMPose

## Executive Summary

**Recommendation: MoveNet Thunder** for Xacari workout coach application.

Given your hardware constraints (8GB RAM, GTX 4GB GPU) and requirement for real-time mobile pose detection, MoveNet offers the best balance of accuracy, performance, and ease of integration.

## Comparison Table

| Feature | MoveNet Thunder | MoveNet Lightning | RTMPose |
|---------|----------------|-------------------|---------|
| **Accuracy** | High (⭐⭐⭐⭐⭐) | Medium-High (⭐⭐⭐⭐) | Very High (⭐⭐⭐⭐⭐) |
| **Speed (FPS)** | 25-30 FPS | 50+ FPS | 15-20 FPS |
| **Model Size** | ~12 MB | ~6 MB | ~30-50 MB |
| **RAM Usage** | ~500 MB | ~300 MB | ~1-2 GB |
| **GPU Required** | Optional | Optional | Recommended |
| **Mobile Support** | ✅ Excellent | ✅ Excellent | ⚠️ Limited |
| **TFLite Support** | ✅ Yes | ✅ Yes | ❌ No (ONNX) |
| **React Native** | ✅ Easy | ✅ Easy | ⚠️ Difficult |
| **Keypoints** | 17 | 17 | 17-133 |
| **Open Source** | ✅ Yes (Apache 2.0) | ✅ Yes (Apache 2.0) | ✅ Yes (Apache 2.0) |

## Detailed Analysis

### MoveNet (Google TensorFlow)

**Pros:**
- ✅ **Optimized for mobile**: Designed specifically for on-device inference
- ✅ **TensorFlow Lite support**: Runs directly on mobile devices
- ✅ **Small model size**: 6-12 MB, easy to package with app
- ✅ **Low resource usage**: Works well with limited RAM/GPU
- ✅ **React Native integration**: Excellent library support (@tensorflow/tfjs-react-native)
- ✅ **Real-time performance**: 25-50 FPS on mobile devices
- ✅ **Single-person optimized**: Perfect for workout coaching
- ✅ **Good documentation**: Extensive tutorials and examples
- ✅ **Maintained by Google**: Regular updates and support

**Cons:**
- ❌ **Limited keypoints**: Only 17 keypoints (but sufficient for most exercises)
- ❌ **Single-person only**: Cannot track multiple people simultaneously
- ❌ **Less accurate than RTMPose**: But difference is marginal for workout use cases

**Two Variants:**
1. **Lightning**: 6 MB, 50+ FPS, slightly lower accuracy - ideal for real-time feedback
2. **Thunder**: 12 MB, 25-30 FPS, higher accuracy - better for form analysis

### RTMPose (MMPose)

**Pros:**
- ✅ **State-of-the-art accuracy**: Best-in-class pose estimation
- ✅ **Multiple keypoint models**: 17-133 keypoints available
- ✅ **Multi-person support**: Can track multiple people
- ✅ **Flexible architecture**: Many model variants
- ✅ **Active development**: Latest research from OpenMMLab

**Cons:**
- ❌ **Larger models**: 30-50 MB+ model files
- ❌ **Higher resource usage**: Requires 1-2 GB RAM minimum
- ❌ **Complex deployment**: Harder to deploy on mobile
- ❌ **Limited mobile support**: Primarily designed for server/edge computing
- ❌ **ONNX format**: Requires additional conversion for mobile
- ❌ **React Native integration**: No official support, requires custom bridge
- ❌ **Overkill for single-person**: Extra capabilities not needed for workout coaching

## Hardware Compatibility

### Your Setup (8GB RAM, GTX 4GB GPU)

**MoveNet:**
- ✅ **Backend (Python)**: Will run smoothly on CPU
- ✅ **Mobile (React Native)**: Will run at 25-30 FPS on most smartphones
- ✅ **Low GPU requirements**: Can run entirely on CPU if needed

**RTMPose:**
- ⚠️ **Backend**: Possible but tight on RAM (1-2 GB for model)
- ❌ **Mobile**: Challenging to deploy, performance issues likely
- ⚠️ **GPU helpful**: Benefits from GPU acceleration

## Mobile Integration

### MoveNet with React Native

```bash
# Easy installation
npm install @tensorflow/tfjs @tensorflow/tfjs-react-native
npm install @react-native-community/async-storage
expo install expo-gl expo-camera

# Pre-built libraries available
npm install react-native-pose-detection
```

**Implementation complexity**: ⭐⭐ (Easy)

### RTMPose with React Native

```bash
# Complex setup required
# Need to:
# 1. Convert model to ONNX
# 2. Build custom native module
# 3. Create bridge between React Native and ONNX Runtime
# 4. Handle dependencies manually
```

**Implementation complexity**: ⭐⭐⭐⭐⭐ (Very Difficult)

## Use Case Fit for Xacari

### Requirements:
- ✅ Real-time pose tracking during workouts
- ✅ Form correction feedback
- ✅ Rep counting
- ✅ Single-person tracking
- ✅ Mobile device deployment
- ✅ Low latency (<100ms)
- ✅ Works on limited hardware

### MoveNet Coverage:
- ✅ **17 keypoints** sufficient for all major exercises:
  - Squats: hips, knees, ankles
  - Push-ups: shoulders, elbows, wrists
  - Planks: shoulders, hips, knees
  - Lunges: hips, knees, ankles
  - Deadlifts: hips, knees, back
  - All upper body: shoulders, elbows, wrists

### RTMPose Coverage:
- ✅ Same keypoints + face/hand details (not needed for workouts)
- ❌ Overkill for the use case

## Recommended Architecture

### Option 1: Mobile-First (Recommended)
```
Mobile App (React Native + Expo)
  ↓
MoveNet Thunder (TFLite)
  ↓ (skeleton data via WebSocket)
Backend (FastAPI)
  ↓ (form analysis)
Voice Feedback + Storage
```

**Pros:**
- Lowest latency (on-device inference)
- Works offline
- Reduced backend load
- Better user experience

### Option 2: Hybrid
```
Mobile App (React Native)
  ↓ (video frames via WebSocket)
Backend (FastAPI + MoveNet)
  ↓
Pose Analysis + Voice Feedback
  ↓
Mobile App
```

**Pros:**
- Easier to update model
- Centralized processing
- Better for analytics

**Cons:**
- Higher latency
- Requires constant connection
- More backend resources needed

## Implementation Recommendation

### Phase 2A: Mobile App Setup
1. Set up React Native with Expo
2. Install TensorFlow.js and MoveNet
3. Implement camera capture
4. Run MoveNet inference on-device
5. Send skeleton data (not video) to backend via WebSocket

### Phase 2B: Backend Integration
1. Receive skeleton keypoints from mobile
2. Analyze form based on exercise type
3. Generate corrections and feedback
4. Send voice feedback to mobile
5. Store session data in Supabase

### Phase 3: Advanced Features
1. Rep counting algorithm
2. Form scoring system
3. Exercise detection (auto-detect exercise type)
4. Progress tracking and analytics

## Code Example: MoveNet in React Native

```javascript
import * as tf from '@tensorflow/tfjs';
import * as posedetection from '@tensorflow-models/pose-detection';
import { Camera } from 'expo-camera';

// Load MoveNet model
const detector = await posedetection.createDetector(
  posedetection.SupportedModels.MoveNet,
  {
    modelType: posedetection.movenet.modelType.SINGLEPOSE_THUNDER,
    enableSmoothing: true,
    minPoseScore: 0.3
  }
);

// Run inference
const poses = await detector.estimatePoses(videoFrame);
const keypoints = poses[0].keypoints;

// Send to backend via WebSocket
websocket.send(JSON.stringify({
  type: 'pose_data',
  keypoints: keypoints,
  timestamp: Date.now(),
  frame_number: frameCount
}));
```

## Resources

### MoveNet
- [TensorFlow Hub](https://tfhub.dev/google/movenet/)
- [Official Guide](https://www.tensorflow.org/hub/tutorials/movenet)
- [React Native Example](https://github.com/tensorflow/tfjs-models/tree/master/pose-detection)
- [Expo + TensorFlow](https://docs.expo.dev/versions/latest/sdk/gl-view/)

### RTMPose
- [GitHub](https://github.com/open-mmlab/mmpose/tree/main/projects/rtmpose)
- [Documentation](https://mmpose.readthedocs.io/)
- [Paper](https://arxiv.org/abs/2303.07399)

## Final Recommendation

**Use MoveNet Thunder** for the following reasons:

1. ✅ **Perfect fit for hardware**: Works smoothly on your 8GB RAM, 4GB GPU setup
2. ✅ **Mobile-optimized**: Runs directly on smartphones via TensorFlow Lite
3. ✅ **Easy integration**: Excellent React Native support
4. ✅ **Real-time performance**: 25-30 FPS is sufficient for workout coaching
5. ✅ **Sufficient accuracy**: 17 keypoints cover all major exercises
6. ✅ **Small footprint**: 12 MB model size, ~500 MB RAM usage
7. ✅ **Proven technology**: Used by Google Fit, Nike Training Club, and others
8. ✅ **Open source**: Apache 2.0 license, free to use commercially

**When to consider RTMPose:**
- ❌ Need hand/face tracking (not required for workouts)
- ❌ Multi-person tracking (not needed for solo workouts)
- ❌ Research/academic use (MoveNet is production-ready)
- ❌ Server-only deployment (but then why not use MoveNet anyway?)

## Next Steps

1. ✅ Set up React Native project with Expo
2. ✅ Install TensorFlow.js and MoveNet dependencies
3. ✅ Implement camera capture and pose detection
4. ✅ Create skeleton rendering visualization
5. ✅ Set up WebSocket communication with backend
6. ✅ Implement form analysis algorithms
7. ✅ Add voice feedback system

This will be covered in the remaining Phase 2 tasks.
