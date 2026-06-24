from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkoutType(str, Enum):
    """Types of workouts available."""
    STRENGTH = "strength"
    CARDIO = "cardio"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    CUSTOM = "custom"


class ExerciseType(str, Enum):
    """Types of exercises."""
    SQUAT = "squat"
    PUSHUP = "pushup"
    PLANK = "plank"
    LUNGE = "lunge"
    DEADLIFT = "deadlift"
    BICEP_CURL = "bicep_curl"
    SHOULDER_PRESS = "shoulder_press"
    JUMPING_JACK = "jumping_jack"
    BURPEE = "burpee"
    CUSTOM = "custom"


class SessionStatus(str, Enum):
    """Workout session status."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PoseKeypoint(BaseModel):
    """Individual pose keypoint with coordinates and confidence."""
    x: float = Field(..., description="X coordinate (normalized 0-1)")
    y: float = Field(..., description="Y coordinate (normalized 0-1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    name: str = Field(..., description="Keypoint name (e.g., 'left_elbow')")


class PoseData(BaseModel):
    """Complete pose estimation data."""
    keypoints: List[PoseKeypoint] = Field(..., description="List of detected keypoints")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    frame_number: int = Field(..., description="Frame number in the video stream")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall pose confidence")


class ExerciseMetrics(BaseModel):
    """Metrics for a single exercise."""
    exercise_type: ExerciseType
    reps_completed: int = 0
    reps_target: Optional[int] = None
    duration_seconds: float = 0.0
    form_score: float = Field(0.0, ge=0.0, le=100.0, description="Form quality score (0-100)")
    corrections_given: List[str] = Field(default_factory=list, description="List of form corrections")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkoutSession(BaseModel):
    """Workout session model."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    workout_type: WorkoutType
    status: SessionStatus = SessionStatus.PENDING
    exercises: List[ExerciseMetrics] = Field(default_factory=list)
    current_exercise_index: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    pause_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkoutSessionCreate(BaseModel):
    """Request model for creating a workout session."""
    user_id: str
    workout_type: WorkoutType
    exercises: List[ExerciseType] = Field(..., min_length=1)
    reps_per_exercise: Optional[List[int]] = None


class WorkoutSessionUpdate(BaseModel):
    """Request model for updating a workout session."""
    status: Optional[SessionStatus] = None
    current_exercise_index: Optional[int] = None


class PoseAnalysisResult(BaseModel):
    """Result of pose analysis for form correction."""
    is_correct: bool = Field(..., description="Whether form is correct")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    corrections: List[str] = Field(default_factory=list, description="List of corrections needed")
    form_score: float = Field(..., ge=0.0, le=100.0, description="Form quality score")
    rep_counted: bool = Field(default=False, description="Whether a rep was counted")
    exercise_type: ExerciseType
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class VoiceFeedback(BaseModel):
    """Voice feedback to be sent to the user."""
    message: str = Field(..., description="Feedback message text")
    priority: str = Field(default="normal", description="Priority: low, normal, high, critical")
    audio_url: Optional[str] = Field(None, description="URL to generated audio file")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
