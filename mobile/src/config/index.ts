/**
 * Application configuration
 *
 * IMPORTANT: Replace these values with your actual credentials
 * - Get your local IP with: ifconfig (Mac/Linux) or ipconfig (Windows)
 * - Get Supabase credentials from your Supabase Dashboard
 */

// Find your local IP address for development
// Mac/Linux: ifconfig | grep "inet "
// Windows: ipconfig

const getLocalIP = () => {
  // REPLACE THIS with your actual local IP address
  // Example: '192.168.1.100'
  return 'YOUR_LOCAL_IP_HERE';
};

export const CONFIG = {
  // Backend API Configuration
  API: {
    BASE_URL: __DEV__
      ? `http://${getLocalIP()}:8000`
      : 'https://your-production-api.com',
    WS_URL: __DEV__
      ? `ws://${getLocalIP()}:8000/ws`
      : 'wss://your-production-api.com/ws',
    TIMEOUT: 10000, // 10 seconds
  },

  // Supabase Configuration
  // Get these from: https://app.supabase.com → Your Project → Settings → API
  SUPABASE: {
    URL: 'YOUR_SUPABASE_URL', // e.g., 'https://xxxxx.supabase.co'
    ANON_KEY: 'YOUR_SUPABASE_ANON_KEY',
  },

  // Pose Detection Configuration
  POSE: {
    // Start with null - we'll add the model later
    MODEL: null as 'movenet' | 'rtmpose' | null,
    FPS: 10, // Frames per second for pose analysis
    CONFIDENCE_THRESHOLD: 0.5,
  },

  // Camera Configuration
  CAMERA: {
    FPS: 30,
    QUALITY: 0.7,
  },

  // App Configuration
  APP: {
    NAME: 'Xacari',
    VERSION: '0.1.0',
  },
};

export default CONFIG;
