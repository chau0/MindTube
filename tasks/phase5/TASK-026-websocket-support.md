# TASK-026: WebSocket Support

## Task Information
- **ID**: TASK-026
- **Phase**: 5 - REST API
- **Estimate**: 75 minutes
- **Dependencies**: TASK-025
- **Status**: 🔴 Backlog

## Description
Implement WebSocket endpoints for real-time progress updates during video analysis operations. This allows clients to receive live updates on processing status, progress, and results.

## Acceptance Criteria
- [ ] Create WebSocket connection manager
- [ ] Implement progress broadcasting
- [ ] Add real-time status updates
- [ ] Handle connection lifecycle
- [ ] Implement message queuing
- [ ] Add error broadcasting
- [ ] Create WebSocket tests
- [ ] Add connection authentication
- [ ] Implement graceful disconnection
- [ ] Add progress persistence

## Implementation Details

### WebSocket Connection Manager
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
import asyncio
import json
import uuid
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_tasks: Dict[str, str] = {}  # connection_id -> task_id
        
    async def connect(self, websocket: WebSocket, client_id: str) -> str:
        """Accept WebSocket connection and return connection ID."""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_tasks:
            del self.connection_tasks[connection_id]
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection_id)
    
    async def broadcast_task_update(self, task_id: str, message: dict):
        """Broadcast update to all connections following a task."""
        for connection_id, conn_task_id in self.connection_tasks.items():
            if conn_task_id == task_id:
                await self.send_personal_message(message, connection_id)

manager = ConnectionManager()
```

### WebSocket Endpoints
```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from mindtube.core.engine import MindTubeEngine
from mindtube.core.progress import ProgressTracker

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for real-time updates."""
    connection_id = await manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "start_analysis":
                await handle_analysis_request(message, connection_id)
            elif message["type"] == "subscribe_task":
                await handle_task_subscription(message, connection_id)
            elif message["type"] == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        await manager.send_personal_message({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        manager.disconnect(connection_id)

async def handle_analysis_request(message: dict, connection_id: str):
    """Handle video analysis request via WebSocket."""
    try:
        url = message["url"]
        options = message.get("options", {})
        
        # Create task ID
        task_id = str(uuid.uuid4())
        manager.connection_tasks[connection_id] = task_id
        
        # Send task started message
        await manager.send_personal_message({
            "type": "task_started",
            "task_id": task_id,
            "url": url,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        # Start analysis with progress tracking
        engine = MindTubeEngine()
        progress_tracker = ProgressTracker(task_id, manager)
        
        result = await engine.analyze_video_with_progress(
            url=url,
            options=options,
            progress_tracker=progress_tracker
        )
        
        # Send completion message
        await manager.send_personal_message({
            "type": "task_completed",
            "task_id": task_id,
            "result": result.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
    except Exception as e:
        await manager.send_personal_message({
            "type": "task_failed",
            "task_id": task_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)

async def handle_task_subscription(message: dict, connection_id: str):
    """Handle subscription to existing task updates."""
    task_id = message["task_id"]
    manager.connection_tasks[connection_id] = task_id
    
    await manager.send_personal_message({
        "type": "subscribed",
        "task_id": task_id,
        "timestamp": datetime.utcnow().isoformat()
    }, connection_id)
```

### Progress Tracker Integration
```python
class ProgressTracker:
    def __init__(self, task_id: str, connection_manager: ConnectionManager):
        self.task_id = task_id
        self.manager = connection_manager
        self.start_time = datetime.utcnow()
        
    async def update_progress(self, stage: str, progress: float, message: str = ""):
        """Send progress update."""
        await self.manager.broadcast_task_update(self.task_id, {
            "type": "progress_update",
            "task_id": self.task_id,
            "stage": stage,
            "progress": progress,
            "message": message,
            "elapsed_time": (datetime.utcnow() - self.start_time).total_seconds(),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def stage_completed(self, stage: str, result: dict = None):
        """Send stage completion update."""
        await self.manager.broadcast_task_update(self.task_id, {
            "type": "stage_completed",
            "task_id": self.task_id,
            "stage": stage,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def error_occurred(self, stage: str, error: str):
        """Send error update."""
        await self.manager.broadcast_task_update(self.task_id, {
            "type": "error",
            "task_id": self.task_id,
            "stage": stage,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })
```

### Message Types
```python
# Client -> Server Messages
class StartAnalysisMessage(BaseModel):
    type: str = "start_analysis"
    url: str
    options: Optional[dict] = {}

class SubscribeTaskMessage(BaseModel):
    type: str = "subscribe_task"
    task_id: str

class PingMessage(BaseModel):
    type: str = "ping"

# Server -> Client Messages
class ConnectionEstablishedMessage(BaseModel):
    type: str = "connection_established"
    connection_id: str
    timestamp: str

class TaskStartedMessage(BaseModel):
    type: str = "task_started"
    task_id: str
    url: str
    timestamp: str

class ProgressUpdateMessage(BaseModel):
    type: str = "progress_update"
    task_id: str
    stage: str
    progress: float  # 0.0 to 1.0
    message: str
    elapsed_time: float
    timestamp: str

class StageCompletedMessage(BaseModel):
    type: str = "stage_completed"
    task_id: str
    stage: str
    result: Optional[dict]
    timestamp: str

class TaskCompletedMessage(BaseModel):
    type: str = "task_completed"
    task_id: str
    result: dict
    timestamp: str

class TaskFailedMessage(BaseModel):
    type: str = "task_failed"
    task_id: str
    error: str
    timestamp: str

class ErrorMessage(BaseModel):
    type: str = "error"
    message: str
    timestamp: str
```

### Connection Authentication
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_websocket_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Verify WebSocket connection token."""
    # Implement token verification logic
    if not credentials or not verify_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials.credentials

@router.websocket("/ws/{client_id}")
async def authenticated_websocket_endpoint(
    websocket: WebSocket, 
    client_id: str,
    token: str = Depends(verify_websocket_token)
):
    """Authenticated WebSocket endpoint."""
    # Connection logic here
    pass
```

### Progress Persistence
```python
import redis
from typing import Optional

class ProgressStore:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def save_progress(self, task_id: str, progress_data: dict):
        """Save progress data to Redis."""
        key = f"progress:{task_id}"
        await self.redis.setex(
            key, 
            3600,  # 1 hour TTL
            json.dumps(progress_data)
        )
    
    async def get_progress(self, task_id: str) -> Optional[dict]:
        """Get progress data from Redis."""
        key = f"progress:{task_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def delete_progress(self, task_id: str):
        """Delete progress data."""
        key = f"progress:{task_id}"
        await self.redis.delete(key)
```

### File Structure
```
mindtube/api/websocket/manager.py
mindtube/api/websocket/handlers.py
mindtube/api/websocket/messages.py
mindtube/core/progress.py
tests/unit/api/test_websocket.py
tests/integration/api/test_websocket_flow.py
```

## Testing Requirements
- Test WebSocket connection establishment
- Test message broadcasting
- Test progress updates
- Test error handling
- Test connection cleanup
- Test authentication
- Test concurrent connections
- Integration tests with real analysis
- Load testing for multiple connections

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] WebSocket protocol documented
- [ ] Error handling comprehensive
- [ ] Performance meets requirements
- [ ] Code follows project standards
- [ ] Connection management robust