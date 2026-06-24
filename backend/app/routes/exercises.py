"""
Exercise Catalog API Routes
"""

from fastapi import APIRouter
from app.services.exercise_validator import EXERCISES

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


@router.get("/")
async def list_exercises():
    """Get list of available exercises."""
    return {
        "exercises": [
            {
                "id": exercise_id,
                "name": exercise["name"],
                "description": exercise["description"],
            }
            for exercise_id, exercise in EXERCISES.items()
        ]
    }


@router.get("/{exercise_id}")
async def get_exercise(exercise_id: str):
    """Get details about a specific exercise."""
    if exercise_id not in EXERCISES:
        return {"error": "Exercise not found"}

    exercise = EXERCISES[exercise_id]
    return {
        "id": exercise_id,
        "name": exercise["name"],
        "description": exercise["description"],
    }
