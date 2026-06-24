export interface Keypoint {
  name: string;
  x: number;
  y: number;
  confidence: number;
}

export interface ExerciseValidation {
  valid: boolean;
  feedback: string[];
  voice_feedback?: string[];
  form_score: number;
}

export interface PoseData {
  keypoints: Keypoint[];
  timestamp: string;
  frame_number: number;
  overall_confidence: number;
  in_frame: boolean;
  exercise_validation?: ExerciseValidation;
}

export interface DetectionStats {
  fps: number;
  framesProcessed: number;
  avgConfidence: number;
  keypointsDetected: number;
  inFrame: boolean;
}

export interface AlertMessage {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  timestamp: Date;
}
