from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.workout import (
    WorkoutSession,
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
)
from app.services.workout_session import workout_session_service
from app.core.logging import logger, log_with_context

router = APIRouter(prefix="/api/workout", tags=["workout"])


@router.post("/sessions", response_model=WorkoutSession, status_code=status.HTTP_201_CREATED)
async def create_workout_session(session_data: WorkoutSessionCreate):
    """
    Create a new workout session.
    """
    session = workout_session_service.create_session(session_data)
    return session


@router.get("/sessions/{session_id}", response_model=WorkoutSession)
async def get_workout_session(session_id: str):
    """
    Retrieve a workout session by ID.
    """
    session = workout_session_service.get_session(session_id)
    return session


@router.post("/sessions/{session_id}/start", response_model=WorkoutSession)
async def start_workout_session(session_id: str):
    """
    Start a workout session.
    """
    session = workout_session_service.start_session(session_id)
    return session


@router.post("/sessions/{session_id}/pause", response_model=WorkoutSession)
async def pause_workout_session(session_id: str):
    """
    Pause a workout session.
    """
    session = workout_session_service.pause_session(session_id)
    return session


@router.post("/sessions/{session_id}/resume", response_model=WorkoutSession)
async def resume_workout_session(session_id: str):
    """
    Resume a paused workout session.
    """
    session = workout_session_service.resume_session(session_id)
    return session


@router.post("/sessions/{session_id}/complete", response_model=WorkoutSession)
async def complete_workout_session(session_id: str):
    """
    Complete a workout session.
    """
    session = workout_session_service.complete_session(session_id)
    return session


@router.post("/sessions/{session_id}/next", response_model=WorkoutSession)
async def next_exercise(session_id: str):
    """
    Move to the next exercise in the workout.
    """
    session = workout_session_service.next_exercise(session_id)
    return session


@router.get("/sessions/user/{user_id}", response_model=List[WorkoutSession])
async def list_user_sessions(user_id: str):
    """
    List all workout sessions for a user.
    """
    sessions = workout_session_service.list_user_sessions(user_id)
    return sessions
