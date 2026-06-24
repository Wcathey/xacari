from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
from datetime import datetime
import json
import asyncio
from app.core.logging import logger, log_with_context
from app.core.exceptions import WebSocketException


class ConnectionManager:
    """
    Manages WebSocket connections for workout sessions.
    Handles connection lifecycle, message broadcasting, and session management.
    """

    def __init__(self):
        # Maps session_id to WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps session_id to user_id
        self.session_users: Dict[str, str] = {}
        # Heartbeat tasks for each connection
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str) -> None:
        """
        Accept a new WebSocket connection and register it.

        Args:
            websocket: WebSocket connection instance
            session_id: Unique session identifier
            user_id: User identifier
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_users[session_id] = user_id

        log_with_context(
            logger,
            "info",
            "WebSocket connection established",
            session_id=session_id,
            user_id=user_id,
        )

        # Start heartbeat task
        self.heartbeat_tasks[session_id] = asyncio.create_task(
            self._heartbeat(session_id)
        )

    async def disconnect(self, session_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            session_id: Session identifier to disconnect
        """
        if session_id in self.active_connections:
            # Cancel heartbeat task
            if session_id in self.heartbeat_tasks:
                self.heartbeat_tasks[session_id].cancel()
                del self.heartbeat_tasks[session_id]

            # Remove connection
            del self.active_connections[session_id]
            user_id = self.session_users.pop(session_id, None)

            log_with_context(
                logger,
                "info",
                "WebSocket connection closed",
                session_id=session_id,
                user_id=user_id,
            )

    async def send_personal_message(self, message: dict, session_id: str) -> None:
        """
        Send a message to a specific session.

        Args:
            message: Message data to send
            session_id: Target session identifier
        """
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                log_with_context(
                    logger,
                    "error",
                    f"Failed to send message to session {session_id}",
                    error=str(e),
                )
                await self.disconnect(session_id)

    async def broadcast(self, message: dict, exclude_session: Optional[str] = None) -> None:
        """
        Broadcast a message to all connected sessions.

        Args:
            message: Message data to broadcast
            exclude_session: Optional session_id to exclude from broadcast
        """
        disconnected = []

        for session_id, websocket in self.active_connections.items():
            if session_id == exclude_session:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                log_with_context(
                    logger,
                    "error",
                    f"Failed to broadcast to session {session_id}",
                    error=str(e),
                )
                disconnected.append(session_id)

        # Clean up disconnected sessions
        for session_id in disconnected:
            await self.disconnect(session_id)

    async def _heartbeat(self, session_id: str) -> None:
        """
        Send periodic heartbeat messages to keep connection alive.

        Args:
            session_id: Session to send heartbeat to
        """
        while session_id in self.active_connections:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                await self.send_personal_message(
                    {"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()},
                    session_id,
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_with_context(
                    logger,
                    "error",
                    f"Heartbeat failed for session {session_id}",
                    error=str(e),
                )
                break

    def get_active_sessions(self) -> List[str]:
        """
        Get list of all active session IDs.

        Returns:
            List of active session identifiers
        """
        return list(self.active_connections.keys())

    def get_connection_count(self) -> int:
        """
        Get the number of active connections.

        Returns:
            Number of active connections
        """
        return len(self.active_connections)

    def is_session_active(self, session_id: str) -> bool:
        """
        Check if a session is currently active.

        Args:
            session_id: Session identifier to check

        Returns:
            True if session is active, False otherwise
        """
        return session_id in self.active_connections


# Global connection manager instance
manager = ConnectionManager()
