/**
 * Core TypeScript types for Xacari mobile app
 */

// ==================== User & Auth ====================

export interface User {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Profile extends User {
  preferred_language: string;
  units_system: 'metric' | 'imperial';
  voice_enabled: boolean;
  notifications_enabled: boolean;
  total_workouts: number;
  total_workout_duration_seconds: number;
  streak_days: number;
  last_workout_date?: string;
}

// ==================== Workout ====================

export type WorkoutType = 'strength' | 'cardio' | 'flexibility' | 'balance' | 'custom';

export type ExerciseType =
  | 'squat'
  | 'pushup'
  | 'plank'
  | 'lunge'
  | 'deadlift'
  | 'bicep_curl'
  | 'shoulder_press'
  | 'jumping_jack'
  | 'burpee'
  | 'custom';

export type SessionStatus = 'pending' | 'active' | 'paused' | 'completed' | 'cancelled';

export interface WorkoutSession {
  id: string;
  user_id: string;
  workout_type: WorkoutType;
  status: SessionStatus;
  started_at?: string;
  ended_at?: string;
  total_duration_seconds: number;
  pause_count: number;
  current_exercise_index: number;
  exercises: Exercise[];
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Exercise {
  id: string;
  session_id: string;
  exercise_type: ExerciseType;
  exercise_order: number;
  reps_completed: number;
  reps_target?: number;
  duration_seconds: number;
  form_score: number;
  corrections_given: string[];
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

// ==================== Pose Detection ====================

export interface Keypoint {
  x: number; // Normalized 0-1
  y: number; // Normalized 0-1
  confidence: number; // 0-1
  name: string;
}

export interface PoseData {
  keypoints: Keypoint[];
  timestamp: string;
  frame_number: number;
  overall_confidence: number;
}

export interface PoseAnalysisResult {
  is_correct: boolean;
  confidence: number;
  corrections: string[];
  form_score: number;
  rep_counted: boolean;
  exercise_type: ExerciseType;
  timestamp: string;
}

// ==================== WebSocket Messages ====================

export type WebSocketMessageType =
  | 'pose_data'
  | 'command'
  | 'ping'
  | 'pong'
  | 'heartbeat'
  | 'feedback'
  | 'error'
  | 'pose_data_received'
  | 'command_acknowledged';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  [key: string]: any;
}

export interface PoseDataMessage extends WebSocketMessage {
  type: 'pose_data';
  keypoints: Keypoint[];
  timestamp: string;
  frame_number: number;
  overall_confidence: number;
}

export interface CommandMessage extends WebSocketMessage {
  type: 'command';
  command: 'start' | 'pause' | 'resume' | 'stop';
}

export interface FeedbackMessage extends WebSocketMessage {
  type: 'feedback';
  message: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  audio_url?: string;
  timestamp: string;
}

// ==================== Navigation ====================

export type RootStackParamList = {
  Welcome: undefined;
  Login: undefined;
  SignUp: undefined;
  Home: undefined;
  WorkoutSetup: undefined;
  WorkoutSession: {
    sessionId: string;
  };
  WorkoutSummary: {
    sessionId: string;
  };
  Profile: undefined;
  Settings: undefined;
};

// ==================== Camera ====================

export interface CameraConfig {
  fps: number;
  quality: number;
  facing: 'front' | 'back';
}

// ==================== Pose Model Abstraction ====================

export interface PoseDetectionModel {
  name: string;
  load(): Promise<void>;
  estimatePose(videoFrame: any): Promise<PoseData | null>;
  dispose(): void;
}

// ==================== API Responses ====================

export interface ApiResponse<T = any> {
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
}

export interface WorkoutSessionCreateRequest {
  user_id: string;
  workout_type: WorkoutType;
  exercises: ExerciseType[];
  reps_per_exercise?: number[];
}
