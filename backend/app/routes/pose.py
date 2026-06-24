"""
Pose Detection API Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.services.pose_detection import pose_detector
from app.services.exercise_validator import validate_exercise, EXERCISES
from app.core.logging import logger

router = APIRouter(prefix="/api/pose", tags=["pose"])


class PoseAnalysisRequest(BaseModel):
    frame: str  # Base64 encoded image
    confidence_threshold: float = 0.3
    exercise_type: str = None  # Optional: squat, pushup, plank, lunge


class PoseAnalysisResponse(BaseModel):
    keypoints: list
    timestamp: str
    frame_number: int
    overall_confidence: float
    in_frame: bool


@router.on_event("startup")
async def startup():
    """Initialize pose detector on startup"""
    logger.info("Pose detection service will load on first use")


@router.post("/analyze", response_model=PoseAnalysisResponse)
async def analyze_pose(request: PoseAnalysisRequest):
    """
    Analyze a frame and return pose keypoints.

    Args:
        request: Contains base64 encoded image frame and confidence threshold

    Returns:
        Pose keypoints with confidence scores and in-frame status
    """
    try:
        # Lazy load model on first use
        if not pose_detector.model_loaded:
            await pose_detector.load_model()

        # Decode image
        image = pose_detector.decode_image(request.frame)

        # Detect pose
        result = await pose_detector.detect_pose(
            image, confidence_threshold=request.confidence_threshold
        )

        # Add timestamp
        result["timestamp"] = datetime.now().isoformat()

        # Validate exercise form if exercise type provided
        if request.exercise_type:
            validation = validate_exercise(request.exercise_type, result["keypoints"])
            result["exercise_validation"] = validation

        return result

    except Exception as e:
        logger.error(f"Error analyzing pose: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing pose: {str(e)}")


@router.get("/status")
async def get_status():
    """Get pose detection service status"""
    return {
        "model_loaded": pose_detector.model_loaded,
        "frames_processed": pose_detector.frame_count,
        "service": "pose_detection",
        "status": "ready" if pose_detector.model_loaded else "not_ready",
    }
