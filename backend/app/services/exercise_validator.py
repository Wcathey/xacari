"""
Exercise Form Validation

Validates proper form for various exercises based on pose keypoints.
"""

import math
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_angle(point1: Dict, point2: Dict, point3: Dict) -> float:
    """
    Calculate angle between three points (in degrees).
    point2 is the vertex of the angle.
    """
    # Convert to vectors
    v1 = (point1["x"] - point2["x"], point1["y"] - point2["y"])
    v2 = (point3["x"] - point2["x"], point3["y"] - point2["y"])

    # Calculate angle using dot product
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

    if mag1 == 0 or mag2 == 0:
        return 0

    cos_angle = dot / (mag1 * mag2)
    cos_angle = max(-1, min(1, cos_angle))  # Clamp to [-1, 1]
    angle = math.acos(cos_angle)

    return math.degrees(angle)


def get_keypoint(keypoints: List[Dict], name: str) -> Optional[Dict]:
    """Get a specific keypoint by name."""
    for kp in keypoints:
        if kp["name"] == name and kp["confidence"] > 0.3:
            return kp
    return None


class ExerciseValidator:
    """Validates exercise form based on pose keypoints."""

    @staticmethod
    def validate_squat(keypoints: List[Dict]) -> Dict:
        """
        Validate squat form.
        Checks:
        - Knee angle (should be < 90 degrees at bottom)
        - Back straightness
        - Hip hinge
        """
        feedback = []
        form_score = 100

        # Get required keypoints
        left_hip = get_keypoint(keypoints, "left_hip")
        left_knee = get_keypoint(keypoints, "left_knee")
        left_ankle = get_keypoint(keypoints, "left_ankle")
        left_shoulder = get_keypoint(keypoints, "left_shoulder")

        if not all([left_hip, left_knee, left_ankle, left_shoulder]):
            return {
                "valid": False,
                "feedback": ["Cannot see full body - adjust position"],
                "form_score": 0,
            }

        # Check knee angle
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

        voice_feedback = []

        if knee_angle < 70:
            feedback.append("Good depth! Knees at proper angle")
            voice_feedback.append("good_depth")
        elif knee_angle < 90:
            feedback.append("Go slightly deeper for full range")
            form_score -= 10
            voice_feedback.append("not_deep_enough")
        else:
            feedback.append("Squat deeper - knees should bend more")
            form_score -= 20
            voice_feedback.append("not_deep_enough")

        # Check if knees go past toes (x position)
        if left_knee["x"] > left_ankle["x"] + 0.05:
            feedback.append("⚠️ Knees going too far forward")
            form_score -= 15
            voice_feedback.append("knee_forward")

        # Check back angle (should be relatively upright)
        back_angle = calculate_angle(left_shoulder, left_hip, left_knee)
        if back_angle < 70:
            feedback.append("⚠️ Keep chest up and back straight")
            form_score -= 15
            voice_feedback.append("back_angle")

        return {
            "valid": True,
            "feedback": feedback,
            "voice_feedback": voice_feedback,
            "form_score": max(0, form_score),
            "knee_angle": knee_angle,
        }

    @staticmethod
    def validate_pushup(keypoints: List[Dict]) -> Dict:
        """
        Validate pushup form.
        Checks:
        - Elbow angle
        - Body alignment (plank position)
        - Depth
        """
        feedback = []
        form_score = 100
        voice_feedback = []

        # Get required keypoints
        left_shoulder = get_keypoint(keypoints, "left_shoulder")
        left_elbow = get_keypoint(keypoints, "left_elbow")
        left_wrist = get_keypoint(keypoints, "left_wrist")
        left_hip = get_keypoint(keypoints, "left_hip")
        left_ankle = get_keypoint(keypoints, "left_ankle")

        if not all([left_shoulder, left_elbow, left_wrist, left_hip, left_ankle]):
            return {
                "valid": False,
                "feedback": ["Cannot see full body - adjust camera angle"],
                "voice_feedback": [],
                "form_score": 0,
            }

        # Check elbow angle
        elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

        if elbow_angle < 90:
            feedback.append("Good depth! Elbows at proper angle")
            voice_feedback.append("good_depth")
        elif elbow_angle < 120:
            feedback.append("Go slightly lower for full range")
            form_score -= 10
            voice_feedback.append("elbow_angle")
        else:
            feedback.append("Lower your body more")
            form_score -= 20
            voice_feedback.append("elbow_angle")

        # Check body alignment (should be straight line)
        body_angle = abs(
            calculate_angle(left_shoulder, left_hip, left_ankle) - 180
        )
        if body_angle > 20:
            feedback.append("⚠️ Keep body straight - don't sag hips")
            form_score -= 15
            voice_feedback.append("body_sag")

        # Check elbow flare (elbows should be tucked)
        # This would require comparing left/right positions

        return {
            "valid": True,
            "feedback": feedback,
            "voice_feedback": voice_feedback,
            "form_score": max(0, form_score),
            "elbow_angle": elbow_angle,
        }

    @staticmethod
    def validate_plank(keypoints: List[Dict]) -> Dict:
        """
        Validate plank form.
        Checks:
        - Body alignment
        - Hip position
        - Head/neck alignment
        """
        feedback = []
        form_score = 100
        voice_feedback = []

        # Get required keypoints
        nose = get_keypoint(keypoints, "nose")
        left_shoulder = get_keypoint(keypoints, "left_shoulder")
        left_hip = get_keypoint(keypoints, "left_hip")
        left_ankle = get_keypoint(keypoints, "left_ankle")

        if not all([nose, left_shoulder, left_hip, left_ankle]):
            return {
                "valid": False,
                "feedback": ["Cannot see full body"],
                "voice_feedback": [],
                "form_score": 0,
            }

        # Check body alignment
        body_angle = abs(calculate_angle(left_shoulder, left_hip, left_ankle) - 180)

        if body_angle < 10:
            feedback.append("Perfect alignment!")
            voice_feedback.append("perfect_form")
        elif body_angle < 20:
            feedback.append("Good form - keep it steady")
            form_score -= 5
        else:
            feedback.append("⚠️ Keep hips level with shoulders")
            form_score -= 20
            voice_feedback.append("body_alignment")

        # Check if hips are sagging
        if left_hip["y"] > left_shoulder["y"] + 0.1:
            feedback.append("⚠️ Hips too low - engage core")
            form_score -= 15
            voice_feedback.append("hips_low")

        # Check if hips are too high
        if left_hip["y"] < left_shoulder["y"] - 0.05:
            feedback.append("⚠️ Lower hips slightly")
            form_score -= 10
            voice_feedback.append("hips_high")

        return {
            "valid": True,
            "feedback": feedback,
            "voice_feedback": voice_feedback,
            "form_score": max(0, form_score),
            "body_alignment": 180 - body_angle,
        }

    @staticmethod
    def validate_lunge(keypoints: List[Dict]) -> Dict:
        """
        Validate lunge form.
        Checks:
        - Front knee angle (should be ~90 degrees)
        - Back knee position
        - Upright torso
        """
        feedback = []
        form_score = 100
        voice_feedback = []

        # Get required keypoints
        left_hip = get_keypoint(keypoints, "left_hip")
        left_knee = get_keypoint(keypoints, "left_knee")
        left_ankle = get_keypoint(keypoints, "left_ankle")
        right_knee = get_keypoint(keypoints, "right_knee")
        left_shoulder = get_keypoint(keypoints, "left_shoulder")

        if not all([left_hip, left_knee, left_ankle, left_shoulder]):
            return {
                "valid": False,
                "feedback": ["Cannot see full body"],
                "voice_feedback": [],
                "form_score": 0,
            }

        # Check front knee angle
        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

        if 80 <= knee_angle <= 100:
            feedback.append("Perfect knee angle!")
            voice_feedback.append("good_form")
        elif 70 <= knee_angle <= 110:
            feedback.append("Good depth")
            form_score -= 5
        else:
            feedback.append("Adjust depth - aim for 90 degree knee angle")
            form_score -= 15
            voice_feedback.append("depth")

        # Check if knee goes past toes
        if left_knee["x"] > left_ankle["x"] + 0.05:
            feedback.append("⚠️ Front knee past toes")
            form_score -= 15
            voice_feedback.append("knee_forward")

        # Check torso upright
        torso_angle = calculate_angle(left_shoulder, left_hip, left_knee)
        if torso_angle < 70:
            feedback.append("⚠️ Keep torso upright")
            form_score -= 10
            voice_feedback.append("torso_lean")

        return {
            "valid": True,
            "feedback": feedback,
            "voice_feedback": voice_feedback,
            "form_score": max(0, form_score),
            "knee_angle": knee_angle,
        }


# Exercise catalog
EXERCISES = {
    "squat": {
        "name": "Squat",
        "description": "Lower body strength exercise",
        "validator": ExerciseValidator.validate_squat,
    },
    "pushup": {
        "name": "Push-up",
        "description": "Upper body pressing exercise",
        "validator": ExerciseValidator.validate_pushup,
    },
    "plank": {
        "name": "Plank",
        "description": "Core stability exercise",
        "validator": ExerciseValidator.validate_plank,
    },
    "lunge": {
        "name": "Lunge",
        "description": "Single leg strength exercise",
        "validator": ExerciseValidator.validate_lunge,
    },
}


def validate_exercise(exercise_type: str, keypoints: List[Dict]) -> Dict:
    """
    Validate exercise form.

    Args:
        exercise_type: Type of exercise (squat, pushup, plank, lunge)
        keypoints: List of pose keypoints

    Returns:
        Validation result with feedback and form score
    """
    if exercise_type not in EXERCISES:
        return {
            "valid": False,
            "feedback": [f"Unknown exercise: {exercise_type}"],
            "form_score": 0,
        }

    exercise = EXERCISES[exercise_type]
    return exercise["validator"](keypoints)
