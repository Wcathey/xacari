// RTMPose skeleton connections (17 keypoints - COCO format)
export const SKELETON_CONNECTIONS = [
  // Face
  ['nose', 'left_eye'],
  ['nose', 'right_eye'],
  ['left_eye', 'left_ear'],
  ['right_eye', 'right_ear'],

  // Upper body
  ['left_shoulder', 'right_shoulder'],
  ['left_shoulder', 'left_elbow'],
  ['right_shoulder', 'right_elbow'],
  ['left_elbow', 'left_wrist'],
  ['right_elbow', 'right_wrist'],

  // Torso
  ['left_shoulder', 'left_hip'],
  ['right_shoulder', 'right_hip'],
  ['left_hip', 'right_hip'],

  // Lower body
  ['left_hip', 'left_knee'],
  ['right_hip', 'right_knee'],
  ['left_knee', 'left_ankle'],
  ['right_knee', 'right_ankle'],
];

export const KEYPOINT_NAMES = [
  'nose',
  'left_eye',
  'right_eye',
  'left_ear',
  'right_ear',
  'left_shoulder',
  'right_shoulder',
  'left_elbow',
  'right_elbow',
  'left_wrist',
  'right_wrist',
  'left_hip',
  'right_hip',
  'left_knee',
  'right_knee',
  'left_ankle',
  'right_ankle',
];

export const CONFIDENCE_COLORS = {
  high: '#00ff88',    // > 0.7
  medium: '#ffaa00',  // 0.4 - 0.7
  low: '#ff4444',     // < 0.4
};

export function getConfidenceColor(confidence: number): string {
  if (confidence > 0.7) return CONFIDENCE_COLORS.high;
  if (confidence > 0.4) return CONFIDENCE_COLORS.medium;
  return CONFIDENCE_COLORS.low;
}
