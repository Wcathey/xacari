# Xacari Quick Start Guide

This guide will help you get Xacari up and running quickly.

## What's Been Done ✅

**Phase 1 (Backend) - COMPLETE:**
- ✅ FastAPI backend with WebSocket support
- ✅ Structured logging and error handling
- ✅ Workout session management API
- ✅ Docker configuration
- ✅ All tested and working

**Phase 2 (Planning) - COMPLETE:**
- ✅ Supabase database schema designed
- ✅ MoveNet pose detection model selected
- ✅ Architecture documented

## What You Need to Do Next 🔄

### Step 1: Set Up Supabase (15 minutes)

1. **Get your Supabase credentials:**
   - Go to https://app.supabase.com
   - Select your Xacari project
   - Go to Settings → API
   - Copy:
     - Project URL → `SUPABASE_URL`
     - anon public key → `SUPABASE_ANON_KEY`
     - service_role key → `SUPABASE_SERVICE_ROLE_KEY`

2. **Add to backend environment:**
   ```bash
   cd backend
   nano .env  # or use any text editor
   ```

   Replace these values:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

3. **Create database schema:**
   - Open Supabase Dashboard → SQL Editor
   - Click "New Query"
   - Copy all contents from `supabase_schema.sql`
   - Click "Run" to execute

4. **Create storage buckets:**
   - Go to Storage in Supabase Dashboard
   - Create these buckets (see SUPABASE_SETUP.md for details):
     - `avatars`
     - `workout-videos`
     - `pose-snapshots`
     - `voice-feedback`

### Step 2: Test Backend (5 minutes)

```bash
cd backend
source xacari_env/bin/activate
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to see the API documentation.

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status": "healthy", "service": "xacari-api"}
```

### Step 3: Create Mobile App (30 minutes)

```bash
# From the xacari root directory
npx create-expo-app mobile --template blank-typescript

cd mobile

# Install core dependencies
npm install @supabase/supabase-js
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context

# Install TensorFlow and pose detection
npm install @tensorflow/tfjs @tensorflow/tfjs-react-native
npm install @react-native-async-storage/async-storage
npm install expo-gl expo-camera

# Install UI components (optional)
npm install react-native-paper
```

### Step 4: Configure Mobile App

Create `mobile/src/config/supabase.ts`:
```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseAnonKey = 'YOUR_SUPABASE_ANON_KEY';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

Create `mobile/src/config/api.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: 'http://YOUR_LOCAL_IP:8000',  // e.g., http://192.168.1.100:8000
  WS_URL: 'ws://YOUR_LOCAL_IP:8000/ws',
};
```

### Step 5: Create Basic Folder Structure

```bash
cd mobile
mkdir -p src/{components,screens,navigation,services,hooks,utils,config}
mkdir -p src/screens/{auth,workout,profile}
```

### Step 6: Run Mobile App

```bash
cd mobile
npx expo start
```

Choose your platform:
- Press `i` for iOS Simulator (Mac only)
- Press `a` for Android Emulator
- Scan QR code with Expo Go app on iPhone

## File Locations Reference

```
xacari/
├── backend/                    # ✅ Phase 1 Complete
│   ├── app/                   # FastAPI application
│   ├── .env                   # 🔄 Add Supabase credentials here
│   └── README.md              # Backend documentation
│
├── mobile/                     # 🔄 Create this in Step 3
│   ├── src/
│   │   ├── screens/           # App screens
│   │   ├── components/        # Reusable components
│   │   ├── navigation/        # Navigation config
│   │   ├── services/          # API & WebSocket services
│   │   └── config/            # Configuration files
│   └── package.json
│
├── supabase_schema.sql        # ✅ Run this in Supabase
├── SUPABASE_SETUP.md          # ✅ Detailed Supabase guide
├── POSE_DETECTION_ANALYSIS.md # ✅ Model comparison
├── PROJECT_STATUS.md          # ✅ Full project status
└── QUICKSTART.md              # ✅ This file
```

## Testing Your Setup

### 1. Test Backend
```bash
curl http://localhost:8000/health
curl http://localhost:8000/version
```

### 2. Test Supabase Connection
Create a test file `backend/test_supabase.py`:
```python
from app.core.config import settings
print(f"Supabase URL: {settings.SUPABASE_URL}")
print(f"Anon Key: {settings.SUPABASE_ANON_KEY[:20]}...")
print("✅ Supabase configured!")
```

Run it:
```bash
cd backend
source xacari_env/bin/activate
python test_supabase.py
```

### 3. Test Mobile App
Once you've created the mobile app, verify:
- App launches without errors
- You can navigate between screens
- Camera permissions work (if you've added camera)

## Common Issues & Solutions

### Issue: Can't connect to backend from mobile
**Solution:** Use your computer's local IP address (not localhost):
```bash
# Find your IP
# Mac/Linux:
ifconfig | grep "inet "
# Windows:
ipconfig
```
Use this IP in your mobile app config: `http://192.168.x.x:8000`

### Issue: TensorFlow.js errors in React Native
**Solution:** Make sure to install peer dependencies:
```bash
npm install @react-native-async-storage/async-storage
npm install expo-gl
```

### Issue: Expo Go can't find Metro bundler
**Solution:** Make sure your phone/emulator is on the same WiFi network as your dev machine.

### Issue: WebSocket connection fails
**Solution:**
1. Check backend is running
2. Use correct IP address (not localhost)
3. Make sure firewall allows port 8000

## Development Tips

### Hot Reload
- **Backend**: FastAPI auto-reloads on code changes when using `--reload` flag
- **Mobile**: Expo auto-reloads on save (press `r` to reload manually)

### Debugging
- **Backend logs**: Structured JSON logs in console
- **Mobile logs**: Use `console.log()` and view in Expo dev tools
- **API testing**: Use http://localhost:8000/docs (Swagger UI)

### Git Workflow
```bash
# Don't commit these files:
backend/.env
backend/xacari_env/
mobile/node_modules/
mobile/.expo/
```

## Next Steps After Setup

Once you have the basic setup working:

1. **Implement Authentication** (Day 1-2)
   - Login/Signup screens
   - Supabase auth integration
   - Protected routes

2. **Add Camera & Pose Detection** (Day 3-4)
   - Camera screen
   - Load MoveNet model
   - Display skeleton overlay

3. **WebSocket Integration** (Day 5)
   - Connect to backend
   - Send pose data
   - Receive feedback

4. **Workout Flow** (Day 6-7)
   - Create workout session
   - Start/pause/complete
   - Display metrics

## Resources

### Getting Help
- **Backend issues**: Check `backend/README.md`
- **Supabase setup**: See `SUPABASE_SETUP.md`
- **Model info**: Read `POSE_DETECTION_ANALYSIS.md`
- **Full project status**: Check `PROJECT_STATUS.md`

### External Docs
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Supabase Getting Started](https://supabase.com/docs/guides/getting-started)
- [Expo Tutorial](https://docs.expo.dev/tutorial/introduction/)
- [MoveNet Guide](https://www.tensorflow.org/hub/tutorials/movenet)

## Quick Command Reference

```bash
# Backend
cd backend && source xacari_env/bin/activate && uvicorn app.main:app --reload

# Mobile
cd mobile && npx expo start

# Docker
cd backend && docker-compose up --build

# Install new Python package
cd backend && source xacari_env/bin/activate && pip install package_name && pip freeze > requirements.txt

# Install new npm package
cd mobile && npm install package_name
```

## Support

If you get stuck:
1. Check the relevant documentation file
2. Review error messages in logs
3. Verify all dependencies are installed
4. Make sure environment variables are set correctly

## You're Ready! 🚀

Your backend is complete and tested. Now:
1. Set up Supabase (15 min)
2. Create the mobile app (30 min)
3. Start building features!

Good luck with Xacari! 💪
