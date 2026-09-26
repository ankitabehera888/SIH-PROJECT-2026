import asyncio
import logging
from typing import Any, Dict, Optional
import socketio

logger = logging.getLogger("healthcare_platform.socketio")

# Create Async Socket.IO server with permissive CORS for development/production web apps
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)

socket_app = socketio.ASGIApp(
    socketio_server=sio,
    socketio_path="socket.io",
)


@sio.event
async def connect(sid, environ, auth=None):
    logger.info(f"[Socket.IO] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    logger.info(f"[Socket.IO] Client disconnected: {sid}")


@sio.event
async def join_consultation_room(sid, data):
    room = data.get("room")
    if room:
        await sio.enter_room(sid, room)
        logger.info(f"[Socket.IO] Client {sid} joined room {room}")
        await sio.emit("room_joined", {"room": room, "status": "OK"}, to=sid)


def broadcast_event(event_name: str, data: Dict[str, Any], room: Optional[str] = None):
    """Synchronous helper allowing FastAPI sync routes and services to broadcast Socket.IO events."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        asyncio.create_task(sio.emit(event_name, data, room=room))
    else:
        loop.run_until_complete(sio.emit(event_name, data, room=room))
    logger.info(f"[Socket.IO Broadcast] Event '{event_name}' emitted to room '{room}' with data: {data}")
