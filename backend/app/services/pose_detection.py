"""
Pose Detection Service

This service handles pose detection from image frames using MediaPipe.
"""

import base64
import io
import numpy as np
from PIL import Image
from typing import Dict, List, Any
import logging
import cv2

logger = logging.getLogger(__name__)

# MediaPipe Pose landmark names mapped to COCO format
MEDIAPIPE_TO_COCO = {
    0: "nose",
    2: "left_eye",
    5: "right_eye",
    7: "left_ear",
    8: "right_ear",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
}

KEYPOINT_NAMES = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]


class PoseDetector:
    """
    Pose detection using MediaPipe Pose.
    """

    def __init__(self):
        self.model_loaded = False
        self.frame_count = 0
        self.mp_pose = None
        self.pose = None
        logger.info("Initializing MediaPipe pose detector...")

    async def load_model(self):
        """Load the MediaPipe pose detection model"""
        try:
            logger.info("Loading MediaPipe Pose model...")
            import mediapipe as mp
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.model_loaded = True
            logger.info("✅ MediaPipe Pose model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load MediaPipe pose model: {e}")
            raise

    def decode_image(self, base64_image: str) -> np.ndarray:
        """Decode base64 image to numpy array"""
        try:
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))
            return np.array(image)
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            raise

    def check_person_in_frame(self, keypoints: List[Dict]) -> bool:
        """
        Check if person is fully in frame.
        Returns False if critical keypoints are at edges or missing.
        """
        # Check if we have enough visible keypoints
        visible_keypoints = [kp for kp in keypoints if kp["confidence"] > 0.3]

        if len(visible_keypoints) < 10:  # Need at least 10 keypoints
            return False

        # Check if keypoints are too close to edges (0.1 margin on each side)
        edge_margin = 0.1
        for kp in visible_keypoints:
            x, y = kp["x"], kp["y"]
            if (
                x < edge_margin
                or x > (1.0 - edge_margin)
                or y < edge_margin
                or y > (1.0 - edge_margin)
            ):
                return False

        return True

    async def detect_pose(
        self, image: np.ndarray, confidence_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Detect pose from image using MediaPipe.
        """
        self.frame_count += 1

        # Convert RGB to BGR for MediaPipe
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Process the image
        results = self.pose.process(image_bgr)

        # Initialize keypoints list
        keypoints = []

        if results.pose_landmarks:
            # Extract keypoints in COCO format
            height, width = image.shape[:2]

            for mp_idx, coco_name in MEDIAPIPE_TO_COCO.items():
                landmark = results.pose_landmarks.landmark[mp_idx]

                keypoints.append({
                    "name": coco_name,
                    "x": landmark.x,  # Already normalized 0-1
                    "y": landmark.y,  # Already normalized 0-1
                    "confidence": landmark.visibility
                })

            # Calculate overall confidence
            overall_confidence = sum(kp["confidence"] for kp in keypoints) / len(keypoints)

            # Always true - skeleton tracking is enough
            in_frame = True
        else:
            # No person detected
            keypoints = []
            for name in KEYPOINT_NAMES:
                keypoints.append({
                    "name": name,
                    "x": 0.5,
                    "y": 0.5,
                    "confidence": 0.0
                })
            overall_confidence = 0.0
            in_frame = False

        result = {
            "keypoints": keypoints,
            "timestamp": None,  # Will be set by the endpoint
            "frame_number": self.frame_count,
            "overall_confidence": overall_confidence,
            "in_frame": in_frame,
        }

        logger.info(
            f"Frame {self.frame_count}: confidence={overall_confidence:.2f}, "
            f"in_frame={in_frame}, keypoints={len(keypoints)}"
        )

        return result


# Global pose detector instance
pose_detector = PoseDetector()
