from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/version")
async def get_version():
    """
    Returns API version information and build details.
    """
    return {
        "version": "0.1.0",
        "api_name": "Xacari Workout Coach API",
        "environment": "development",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "websocket": True,
            "pose_analysis": True,
            "voice_feedback": True
        }
    }
