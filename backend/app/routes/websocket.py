from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from app.core.websocket_manager import manager
from app.core.logging import logger, log_with_context
import json

router = APIRouter()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    user_id: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time workout session communication.

    Args:
        websocket: WebSocket connection
        session_id: Unique identifier for the workout session
        user_id: User identifier (optional, can be from auth)
    """
    # If no user_id provided, use anonymous
    if not user_id:
        user_id = f"anonymous_{session_id}"

    await manager.connect(websocket, session_id, user_id)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")

                log_with_context(
                    logger,
                    "debug",
                    f"Received WebSocket message: {message_type}",
                    session_id=session_id,
                    user_id=user_id,
                    message_type=message_type,
                )

                # Handle different message types
                if message_type == "pose_data":
                    # Process pose data (will be handled by workout session service)
                    await handle_pose_data(session_id, message)

                elif message_type == "ping":
                    # Respond to ping
                    await manager.send_personal_message(
                        {"type": "pong", "timestamp": message.get("timestamp")},
                        session_id,
                    )

                elif message_type == "command":
                    # Handle commands (start, pause, stop, etc.)
                    await handle_command(session_id, message)

                else:
                    # Echo unknown messages back for debugging
                    await manager.send_personal_message(
                        {"type": "echo", "original": message},
                        session_id,
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"},
                    session_id,
                )

    except WebSocketDisconnect:
        await manager.disconnect(session_id)
        log_with_context(
            logger,
            "info",
            "Client disconnected",
            session_id=session_id,
            user_id=user_id,
        )

    except Exception as e:
        log_with_context(
            logger,
            "error",
            f"WebSocket error: {str(e)}",
            session_id=session_id,
            user_id=user_id,
        )
        await manager.disconnect(session_id)


async def handle_pose_data(session_id: str, message: dict) -> None:
    """
    Handle incoming pose data from the client.

    Args:
        session_id: Session identifier
        message: Message containing pose data
    """
    # This will be integrated with the workout session service
    # For now, just acknowledge receipt
    await manager.send_personal_message(
        {
            "type": "pose_data_received",
            "timestamp": message.get("timestamp"),
        },
        session_id,
    )


async def handle_command(session_id: str, message: dict) -> None:
    """
    Handle workout session commands.

    Args:
        session_id: Session identifier
        message: Command message
    """
    command = message.get("command")

    # This will be integrated with the workout session service
    # For now, just acknowledge the command
    await manager.send_personal_message(
        {
            "type": "command_acknowledged",
            "command": command,
        },
        session_id,
    )


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status.
    """
    return {
        "active_connections": manager.get_connection_count(),
        "active_sessions": manager.get_active_sessions(),
    }
