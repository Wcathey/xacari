from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app.models.workout import (
    WorkoutSession,
    WorkoutSessionCreate,
    SessionStatus,
    ExerciseMetrics,
    PoseData,
    PoseAnalysisResult,
    ExerciseType,
)
from app.core.exceptions import WorkoutSessionException, ResourceNotFoundException
from app.core.logging import logger, log_with_context
from app.core.config import settings
import uuid


class WorkoutSessionService:
    """
    Service for managing workout sessions.
    Handles session lifecycle, state management, and coordination.
    """

    def __init__(self):
        # In-memory storage for sessions (will be replaced with database)
        self.sessions: Dict[str, WorkoutSession] = {}

    def create_session(self, session_data: WorkoutSessionCreate) -> WorkoutSession:
        """
        Create a new workout session.

        Args:
            session_data: Session creation data

        Returns:
            Created workout session

        Raises:
            WorkoutSessionException: If session creation fails
        """
        session_id = str(uuid.uuid4())

        # Create exercise metrics for each exercise
        exercises = []
        for idx, exercise_type in enumerate(session_data.exercises):
            reps_target = None
            if session_data.reps_per_exercise and idx < len(session_data.reps_per_exercise):
                reps_target = session_data.reps_per_exercise[idx]

            exercises.append(
                ExerciseMetrics(
                    exercise_type=exercise_type,
                    reps_target=reps_target,
                )
            )

        session = WorkoutSession(
            session_id=session_id,
            user_id=session_data.user_id,
            workout_type=session_data.workout_type,
            exercises=exercises,
        )

        self.sessions[session_id] = session

        log_with_context(
            logger,
            "info",
            "Workout session created",
            session_id=session_id,
            user_id=session_data.user_id,
            workout_type=session_data.workout_type,
        )

        return session

    def get_session(self, session_id: str) -> WorkoutSession:
        """
        Retrieve a workout session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Workout session

        Raises:
            ResourceNotFoundException: If session not found
        """
        if session_id not in self.sessions:
            raise ResourceNotFoundException("WorkoutSession", session_id)

        return self.sessions[session_id]

    def start_session(self, session_id: str) -> WorkoutSession:
        """
        Start a workout session.

        Args:
            session_id: Session identifier

        Returns:
            Updated workout session

        Raises:
            WorkoutSessionException: If session cannot be started
        """
        session = self.get_session(session_id)

        if session.status != SessionStatus.PENDING:
            raise WorkoutSessionException(
                f"Cannot start session in {session.status} state",
                details={"session_id": session_id, "current_status": session.status},
            )

        session.status = SessionStatus.ACTIVE
        session.started_at = datetime.utcnow()

        # Start the first exercise
        if session.exercises:
            session.exercises[0].started_at = datetime.utcnow()

        log_with_context(
            logger,
            "info",
            "Workout session started",
            session_id=session_id,
        )

        return session

    def pause_session(self, session_id: str) -> WorkoutSession:
        """
        Pause an active workout session.

        Args:
            session_id: Session identifier

        Returns:
            Updated workout session
        """
        session = self.get_session(session_id)

        if session.status != SessionStatus.ACTIVE:
            raise WorkoutSessionException(
                f"Cannot pause session in {session.status} state",
                details={"session_id": session_id, "current_status": session.status},
            )

        session.status = SessionStatus.PAUSED
        session.pause_count += 1

        log_with_context(
            logger,
            "info",
            "Workout session paused",
            session_id=session_id,
        )

        return session

    def resume_session(self, session_id: str) -> WorkoutSession:
        """
        Resume a paused workout session.

        Args:
            session_id: Session identifier

        Returns:
            Updated workout session
        """
        session = self.get_session(session_id)

        if session.status != SessionStatus.PAUSED:
            raise WorkoutSessionException(
                f"Cannot resume session in {session.status} state",
                details={"session_id": session_id, "current_status": session.status},
            )

        session.status = SessionStatus.ACTIVE

        log_with_context(
            logger,
            "info",
            "Workout session resumed",
            session_id=session_id,
        )

        return session

    def complete_session(self, session_id: str) -> WorkoutSession:
        """
        Complete a workout session.

        Args:
            session_id: Session identifier

        Returns:
            Updated workout session
        """
        session = self.get_session(session_id)

        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.utcnow()

        if session.started_at:
            session.total_duration_seconds = (
                session.ended_at - session.started_at
            ).total_seconds()

        # Complete current exercise if not already completed
        if session.exercises and session.current_exercise_index < len(session.exercises):
            current_exercise = session.exercises[session.current_exercise_index]
            if not current_exercise.completed_at:
                current_exercise.completed_at = datetime.utcnow()

        log_with_context(
            logger,
            "info",
            "Workout session completed",
            session_id=session_id,
            duration_seconds=session.total_duration_seconds,
        )

        return session

    def next_exercise(self, session_id: str) -> WorkoutSession:
        """
        Move to the next exercise in the workout.

        Args:
            session_id: Session identifier

        Returns:
            Updated workout session
        """
        session = self.get_session(session_id)

        if session.status != SessionStatus.ACTIVE:
            raise WorkoutSessionException(
                "Session must be active to switch exercises",
                details={"session_id": session_id, "current_status": session.status},
            )

        # Complete current exercise
        if session.current_exercise_index < len(session.exercises):
            current_exercise = session.exercises[session.current_exercise_index]
            current_exercise.completed_at = datetime.utcnow()

            if current_exercise.started_at:
                current_exercise.duration_seconds = (
                    current_exercise.completed_at - current_exercise.started_at
                ).total_seconds()

        # Move to next exercise
        session.current_exercise_index += 1

        # Start next exercise if available
        if session.current_exercise_index < len(session.exercises):
            next_exercise = session.exercises[session.current_exercise_index]
            next_exercise.started_at = datetime.utcnow()

            log_with_context(
                logger,
                "info",
                "Moved to next exercise",
                session_id=session_id,
                exercise_index=session.current_exercise_index,
                exercise_type=next_exercise.exercise_type,
            )
        else:
            # No more exercises, complete the session
            self.complete_session(session_id)

        return session

    def update_exercise_metrics(
        self,
        session_id: str,
        reps_completed: Optional[int] = None,
        form_score: Optional[float] = None,
        correction: Optional[str] = None,
    ) -> WorkoutSession:
        """
        Update metrics for the current exercise.

        Args:
            session_id: Session identifier
            reps_completed: Number of reps completed
            form_score: Form quality score
            correction: Form correction to add

        Returns:
            Updated workout session
        """
        session = self.get_session(session_id)

        if session.current_exercise_index >= len(session.exercises):
            raise WorkoutSessionException(
                "No active exercise to update",
                details={"session_id": session_id},
            )

        current_exercise = session.exercises[session.current_exercise_index]

        if reps_completed is not None:
            current_exercise.reps_completed = reps_completed

        if form_score is not None:
            current_exercise.form_score = form_score

        if correction:
            current_exercise.corrections_given.append(correction)

        return session

    def get_current_exercise(self, session_id: str) -> Optional[ExerciseMetrics]:
        """
        Get the current exercise being performed.

        Args:
            session_id: Session identifier

        Returns:
            Current exercise metrics or None if no active exercise
        """
        session = self.get_session(session_id)

        if session.current_exercise_index < len(session.exercises):
            return session.exercises[session.current_exercise_index]

        return None

    def list_user_sessions(self, user_id: str) -> List[WorkoutSession]:
        """
        List all sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of workout sessions
        """
        return [
            session
            for session in self.sessions.values()
            if session.user_id == user_id
        ]


# Global service instance
workout_session_service = WorkoutSessionService()
