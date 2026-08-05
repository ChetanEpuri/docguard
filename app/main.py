import logging
import uuid
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("docguard_api")

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DocGuard API is starting up...")
    yield
    logger.info("DocGuard API is shutting down...")

# --- OpenAPI Metadata ---
description = """
DocGuard API is the core backend for a Self-Healing Documentation Intelligence Platform. 
It ingests documentation drift events from CI/CD pipelines, tracks document health, and manages users. 
By analyzing code changes against existing documentation, DocGuard helps ensure your docs are always up-to-date.
This API provides the necessary endpoints to manage users, documents, and drift events in real-time.
"""

tags_metadata = [
    {
        "name": "Health",
        "description": "System health check endpoints.",
    },
    {
        "name": "Users",
        "description": "Operations with users.",
    },
    {
        "name": "Documents",
        "description": "Operations with documents.",
    },
    {
        "name": "Drift Events",
        "description": "Manage documentation drift events detected by CI pipelines.",
    },
]

app = FastAPI(
    title="DocGuard API",
    description=description,
    version="1.0.0",
    contact={
        "name": "DocGuard Team",
        "email": "hello@docguard.example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info(f"Incoming request: {request.method} {request.url} - RequestID: {request_id}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Completed request: {request.method} {request.url} - Status: {response.status_code} - Duration: {process_time:.4f}s")
    
    return response

# --- Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": True, "message": "Internal Server Error"},
    )

# --- Pydantic Models ---

# Users
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    role: str = Field(default="viewer", description="User role (admin, editor, viewer)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "role": "editor"
            }
        }
    )

class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the user")
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    role: str = Field(..., description="User role")
    created_at: datetime = Field(..., description="Timestamp of user creation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "role": "editor",
                "created_at": "2023-10-01T12:00:00Z"
            }
        }
    )

# Documents
class DocStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    OUTDATED = "outdated"

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Title of the document")
    content: str = Field(..., min_length=10, description="Markdown content of the document")
    author_id: uuid.UUID = Field(..., description="UUID of the author")
    status: DocStatus = Field(default=DocStatus.DRAFT, description="Current status of the document")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "API Gateway Authentication",
                "content": "# Authentication\n\nAll API requests must include a valid JWT token...",
                "author_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "published"
            }
        }
    )

class DocumentResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    content: str = Field(..., description="Markdown content of the document")
    author_id: uuid.UUID = Field(..., description="UUID of the author")
    status: DocStatus = Field(..., description="Current status of the document")
    updated_at: datetime = Field(..., description="Timestamp of last update")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "987e6543-e21b-12d3-a456-426614174000",
                "title": "API Gateway Authentication",
                "content": "# Authentication\n\nAll API requests must include a valid JWT token...",
                "author_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "published",
                "updated_at": "2023-10-02T14:30:00Z"
            }
        }
    )

# Drift Events
class DriftSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DriftEventCreate(BaseModel):
    document_id: uuid.UUID = Field(..., description="UUID of the document that drifted")
    commit_hash: str = Field(..., min_length=7, max_length=40, description="Git commit hash causing the drift")
    description: str = Field(..., description="Description of what changed in the code vs docs")
    severity: DriftSeverity = Field(..., description="Severity of the documentation drift")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "987e6543-e21b-12d3-a456-426614174000",
                "commit_hash": "a1b2c3d",
                "description": "Auth middleware removed JWT token validation, but docs still say it's required.",
                "severity": "high"
            }
        }
    )

class DriftEventResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the event")
    document_id: uuid.UUID = Field(..., description="UUID of the document that drifted")
    commit_hash: str = Field(..., description="Git commit hash causing the drift")
    description: str = Field(..., description="Description of the drift")
    severity: DriftSeverity = Field(..., description="Severity of the drift")
    detected_at: datetime = Field(..., description="Timestamp of when the drift was detected")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "111e2222-e33b-12d3-a456-426614174000",
                "document_id": "987e6543-e21b-12d3-a456-426614174000",
                "commit_hash": "a1b2c3d",
                "description": "Auth middleware removed JWT token validation, but docs still say it's required.",
                "severity": "high",
                "detected_at": "2023-10-03T09:15:00Z"
            }
        }
    )

# --- In-Memory Data Store ---
db_users: Dict[uuid.UUID, UserResponse] = {}
db_documents: Dict[uuid.UUID, DocumentResponse] = {}
db_drift_events: Dict[uuid.UUID, DriftEventResponse] = {}

# Seed Data
def seed_data():
    u1_id = uuid.uuid4()
    u2_id = uuid.uuid4()
    u3_id = uuid.uuid4()
    
    db_users[u1_id] = UserResponse(id=u1_id, name="Alice Admin", email="alice@example.com", role="admin", created_at=datetime.now(timezone.utc))
    db_users[u2_id] = UserResponse(id=u2_id, name="Bob Builder", email="bob@example.com", role="editor", created_at=datetime.now(timezone.utc))
    db_users[u3_id] = UserResponse(id=u3_id, name="Charlie Checker", email="charlie@example.com", role="viewer", created_at=datetime.now(timezone.utc))

    d1_id = uuid.uuid4()
    d2_id = uuid.uuid4()
    d3_id = uuid.uuid4()
    
    db_documents[d1_id] = DocumentResponse(id=d1_id, title="Architecture Overview", content="The system consists of microservices...", author_id=u1_id, status=DocStatus.PUBLISHED, updated_at=datetime.now(timezone.utc))
    db_documents[d2_id] = DocumentResponse(id=d2_id, title="Setup Guide", content="To setup the project, run `make install`...", author_id=u2_id, status=DocStatus.OUTDATED, updated_at=datetime.now(timezone.utc))
    db_documents[d3_id] = DocumentResponse(id=d3_id, title="Deployment Runbook", content="Deployment requires admin access...", author_id=u1_id, status=DocStatus.DRAFT, updated_at=datetime.now(timezone.utc))

seed_data()

# --- Endpoints ---

# Health
class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    version: str

start_time = time.time()

@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health_check():
    """
    Check the system health.
    Returns service status, uptime, and API version.
    """
    return HealthResponse(
        status="ok",
        uptime_seconds=time.time() - start_time,
        version="1.0.0"
    )

# Users
@app.get("/api/v1/users", tags=["Users"], response_model=List[UserResponse])
async def list_users(page: int = 1, limit: int = 10):
    """
    List all users with pagination.
    
    - **page**: Page number (default 1)
    - **limit**: Number of items per page (default 10)
    """
    users_list = list(db_users.values())
    start = (page - 1) * limit
    end = start + limit
    return users_list[start:end]

@app.post("/api/v1/users", tags=["Users"], response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user.
    Validates email format and required fields.
    """
    user_id = uuid.uuid4()
    new_user = UserResponse(
        id=user_id,
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=datetime.now(timezone.utc)
    )
    db_users[user_id] = new_user
    logger.info(f"User created: {user_id}")
    return new_user

@app.get("/api/v1/users/{user_id}", tags=["Users"], response_model=UserResponse)
async def get_user(user_id: uuid.UUID):
    """
    Retrieve a specific user by their UUID.
    """
    if user_id not in db_users:
        raise HTTPException(status_code=404, detail="User not found")
    return db_users[user_id]

# Documents
@app.get("/api/v1/documents", tags=["Documents"], response_model=List[DocumentResponse])
async def list_documents(status_filter: Optional[DocStatus] = None, author_id: Optional[uuid.UUID] = None):
    """
    List documents with optional filtering.
    
    - **status_filter**: Filter by document status (draft, published, outdated)
    - **author_id**: Filter by the UUID of the author
    """
    docs = list(db_documents.values())
    if status_filter:
        docs = [d for d in docs if d.status == status_filter]
    if author_id:
        docs = [d for d in docs if d.author_id == author_id]
    return docs

@app.post("/api/v1/documents", tags=["Documents"], response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(doc: DocumentCreate):
    """
    Create a new document.
    """
    if doc.author_id not in db_users:
        raise HTTPException(status_code=400, detail="Author ID does not exist")
        
    doc_id = uuid.uuid4()
    new_doc = DocumentResponse(
        id=doc_id,
        title=doc.title,
        content=doc.content,
        author_id=doc.author_id,
        status=doc.status,
        updated_at=datetime.now(timezone.utc)
    )
    db_documents[doc_id] = new_doc
    logger.info(f"Document created: {doc_id}")
    return new_doc

@app.get("/api/v1/documents/{doc_id}", tags=["Documents"], response_model=DocumentResponse)
async def get_document(doc_id: uuid.UUID):
    """
    Retrieve a specific document by its UUID.
    """
    if doc_id not in db_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_documents[doc_id]

# Drift Events
@app.get("/api/v1/drift-events", tags=["Drift Events"], response_model=List[DriftEventResponse])
async def list_drift_events():
    """
    List all documentation drift events detected by the CI pipeline.
    """
    return list(db_drift_events.values())

@app.post("/api/v1/drift-events", tags=["Drift Events"], response_model=DriftEventResponse, status_code=status.HTTP_201_CREATED)
async def record_drift_event(event: DriftEventCreate):
    """
    Record a new documentation drift event.
    Typically called by a CI/CD pipeline webhook when code changes drift from documentation.
    """
    if event.document_id not in db_documents:
        raise HTTPException(status_code=400, detail="Document ID does not exist")
        
    event_id = uuid.uuid4()
    new_event = DriftEventResponse(
        id=event_id,
        document_id=event.document_id,
        commit_hash=event.commit_hash,
        description=event.description,
        severity=event.severity,
        detected_at=datetime.now(timezone.utc)
    )
    db_drift_events[event_id] = new_event
    
    # Update document status to outdated when a drift event is recorded
    db_documents[event.document_id].status = DocStatus.OUTDATED
    db_documents[event.document_id].updated_at = datetime.now(timezone.utc)
    
    logger.info(f"Drift event recorded: {event_id} for document {event.document_id}")
    return new_event
