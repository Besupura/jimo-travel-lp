from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import math
from jose import JWTError, jwt
from uuid import uuid4

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # For MVP only, should be env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

app = FastAPI(title="Digital Stamp Rally API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class TokenData(BaseModel):
    user_id: str
    is_admin: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: str
    display_name: str

class UserCreate(UserBase):
    password: str = "password"  # Default password for MVP

class User(UserBase):
    id: str
    is_admin: bool = False
    
    class Config:
        from_attributes = True

class RallyBase(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime

class Rally(RallyBase):
    id: str
    
    class Config:
        from_attributes = True

class CheckpointType(str, Enum):
    GPS = "gps"
    QR = "qr"
    QUIZ = "quiz"
    STEPS = "steps"
    PHOTO = "photo"

class CheckpointBase(BaseModel):
    rally_id: str
    name: str
    description: str
    type: str
    order: int = 0

class Checkpoint(CheckpointBase):
    id: str
    condition_data: Dict[str, Any]
    
    class Config:
        from_attributes = True

class CheckpointWithProgress(Checkpoint):
    acquired: bool = False
    acquired_at: Optional[datetime] = None

class StampProgressBase(BaseModel):
    user_id: str
    checkpoint_id: str
    acquired: bool = False
    acquired_at: Optional[datetime] = None

class StampProgress(StampProgressBase):
    id: str
    
    class Config:
        from_attributes = True

class GPSAttempt(BaseModel):
    latitude: float
    longitude: float

class QRAttempt(BaseModel):
    code: str

class QuizAttempt(BaseModel):
    answer: str

class StepsAttempt(BaseModel):
    steps: int

class PhotoAttempt(BaseModel):
    photo_url: str  # In MVP, we'll just accept a URL or base64 string

class AttemptResponse(BaseModel):
    success: bool
    message: str


db = {
    "users": {},
    "rallies": {},
    "checkpoints": {},
    "progress": {}
}

def init_db():
    sample_user = {
        "id": "user1",
        "email": "user@example.com",
        "display_name": "Demo User",
        "password": "password",  # In MVP only, never store plain passwords in production
        "is_admin": False
    }
    db["users"][sample_user["id"]] = sample_user
    
    admin_user = {
        "id": "admin",
        "email": "admin@example.com",
        "display_name": "Administrator",
        "password": "admin",  # In MVP only, never store plain passwords in production
        "is_admin": True
    }
    db["users"][admin_user["id"]] = admin_user
    
    rally_id = "rally1"
    sample_rally = {
        "id": rally_id,
        "name": "Tokyo City Tour",
        "description": "Explore the highlights of Tokyo with this digital stamp rally!",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    db["rallies"][rally_id] = sample_rally
    
    checkpoints = [
        {
            "id": "cp1",
            "rally_id": rally_id,
            "name": "Tokyo Tower",
            "description": "Visit the iconic Tokyo Tower",
            "type": "gps",
            "order": 1,
            "condition_data": {
                "latitude": 35.6586,
                "longitude": 139.7454,
                "radius": 100  # meters
            }
        },
        {
            "id": "cp2",
            "rally_id": rally_id,
            "name": "Meiji Shrine",
            "description": "Scan the QR code at Meiji Shrine entrance",
            "type": "qr",
            "order": 2,
            "condition_data": {
                "qrCode": "MEIJI-SHRINE-12345"
            }
        },
        {
            "id": "cp3",
            "rally_id": rally_id,
            "name": "Shibuya Crossing",
            "description": "Answer a quiz about Shibuya Crossing",
            "type": "quiz",
            "order": 3,
            "condition_data": {
                "question": "What is Shibuya Crossing also known as?",
                "options": ["Scramble Crossing", "Rainbow Crossing", "Tokyo Junction", "City Center"],
                "correctAnswer": "Scramble Crossing"
            }
        },
        {
            "id": "cp4",
            "rally_id": rally_id,
            "name": "Ueno Park",
            "description": "Walk 5000 steps in Ueno Park",
            "type": "steps",
            "order": 4,
            "condition_data": {
                "targetSteps": 5000
            }
        },
        {
            "id": "cp5",
            "rally_id": rally_id,
            "name": "Asakusa Temple",
            "description": "Take a photo of Sensoji Temple in Asakusa",
            "type": "photo",
            "order": 5,
            "condition_data": {
                "description": "Take a photo of the famous red lantern at the entrance"
            }
        }
    ]
    
    for checkpoint in checkpoints:
        db["checkpoints"][checkpoint["id"]] = checkpoint

init_db()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, is_admin=is_admin)
    except JWTError:
        raise credentials_exception
    
    user = db["users"].get(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371000  # Radius of earth in meters
    return c * r

def check_gps(user_location, checkpoint):
    """Check if user is within the specified radius of the checkpoint."""
    target_lat = checkpoint["condition_data"]["latitude"]
    target_lng = checkpoint["condition_data"]["longitude"]
    radius = checkpoint["condition_data"]["radius"]
    
    distance = haversine_distance(
        user_location.latitude, 
        user_location.longitude, 
        target_lat, 
        target_lng
    )
    return distance <= radius

def check_qr(scanned_code, checkpoint):
    """Check if scanned QR code matches the expected code."""
    return scanned_code.code == checkpoint["condition_data"]["qrCode"]

def check_quiz(answer, checkpoint):
    """Check if quiz answer is correct."""
    return answer.answer.strip().lower() == checkpoint["condition_data"]["correctAnswer"].lower()

def check_steps(step_count, checkpoint):
    """Check if step count meets or exceeds the target."""
    return step_count.steps >= checkpoint["condition_data"]["targetSteps"]

def check_photo(photo_data, checkpoint):
    """For MVP, just verify that a photo was submitted."""
    return True if photo_data.photo_url else False

check_handlers = {
    "gps": check_gps,
    "qr": check_qr,
    "quiz": check_quiz,
    "steps": check_steps,
    "photo": check_photo
}

def save_progress(user_id, checkpoint_id):
    """Save user's stamp acquisition progress."""
    progress_id = f"{user_id}_{checkpoint_id}"
    
    if progress_id in db["progress"]:
        return db["progress"][progress_id]
    
    progress = {
        "id": progress_id,
        "user_id": user_id,
        "checkpoint_id": checkpoint_id,
        "acquired": True,
        "acquired_at": datetime.now().isoformat()
    }
    db["progress"][progress_id] = progress
    return progress


@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for u in db["users"].values():
        if u["email"] == form_data.username:
            user = u
            break
    
    if not user:
        user_id = str(uuid4())
        user = {
            "id": user_id,
            "email": form_data.username,
            "display_name": form_data.username.split("@")[0],  # Use part before @ as display name
            "password": form_data.password,
            "is_admin": False
        }
        db["users"][user_id] = user
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "is_admin": user.get("is_admin", False)}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/admin/login", response_model=Token)
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Admin login endpoint with predefined credentials for MVP."""
    if form_data.username == "admin@example.com" and form_data.password == "admin":
        user_id = "admin"
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "is_admin": True}, 
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect admin credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/api/rallies", response_model=List[Rally])
async def get_rallies():
    """Get a list of all available stamp rallies."""
    return list(db["rallies"].values())

@app.get("/api/rallies/{rally_id}/checkpoints", response_model=List[CheckpointWithProgress])
async def get_rally_checkpoints(rally_id: str, current_user: dict = Depends(get_current_user)):
    """Get all checkpoints for a specific rally with user's progress."""
    checkpoints = [cp for cp in db["checkpoints"].values() if cp["rally_id"] == rally_id]
    
    result = []
    for cp in checkpoints:
        progress_id = f"{current_user['id']}_{cp['id']}"
        progress = db["progress"].get(progress_id)
        
        checkpoint_with_progress = cp.copy()
        checkpoint_with_progress["acquired"] = False
        checkpoint_with_progress["acquired_at"] = None
        
        if progress:
            checkpoint_with_progress["acquired"] = progress["acquired"]
            checkpoint_with_progress["acquired_at"] = progress["acquired_at"]
        
        result.append(checkpoint_with_progress)
    
    result.sort(key=lambda x: x["order"])
    return result

@app.get("/api/checkpoints/{checkpoint_id}", response_model=Checkpoint)
async def get_checkpoint(checkpoint_id: str):
    """Get detailed information for a specific checkpoint."""
    checkpoint = db["checkpoints"].get(checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint

@app.post("/api/checkpoints/{checkpoint_id}/attempt", response_model=AttemptResponse)
async def attempt_checkpoint(
    checkpoint_id: str, 
    gps_data: Optional[GPSAttempt] = None,
    qr_data: Optional[QRAttempt] = None,
    quiz_data: Optional[QuizAttempt] = None,
    steps_data: Optional[StepsAttempt] = None,
    photo_data: Optional[PhotoAttempt] = None,
    current_user: dict = Depends(get_current_user)
):
    """Attempt to acquire a stamp at a checkpoint."""
    checkpoint = db["checkpoints"].get(checkpoint_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    progress_id = f"{current_user['id']}_{checkpoint_id}"
    if progress_id in db["progress"]:
        return {"success": True, "message": "You've already acquired this stamp!"}
    
    checkpoint_type = checkpoint["type"]
    handler = check_handlers.get(checkpoint_type)
    
    if not handler:
        raise HTTPException(status_code=400, detail=f"Unsupported checkpoint type: {checkpoint_type}")
    
    data_map = {
        "gps": gps_data,
        "qr": qr_data,
        "quiz": quiz_data,
        "steps": steps_data,
        "photo": photo_data
    }
    
    user_input = data_map.get(checkpoint_type)
    if not user_input:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required data for checkpoint type: {checkpoint_type}"
        )
    
    success = handler(user_input, checkpoint)
    
    if success:
        save_progress(current_user["id"], checkpoint_id)
        return {"success": True, "message": "Congratulations! You've acquired a new stamp!"}
    else:
        return {"success": False, "message": "Condition not met. Please try again."}

@app.get("/api/progress", response_model=List[StampProgress])
async def get_user_progress(current_user: dict = Depends(get_current_user)):
    """Get all stamp progress for the current user."""
    user_progress = [
        progress for progress_id, progress in db["progress"].items()
        if progress["user_id"] == current_user["id"]
    ]
    return user_progress

@app.get("/api/rallies/{rally_id}/progress")
async def get_rally_progress(rally_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's progress for a specific rally."""
    rally_checkpoints = [cp for cp in db["checkpoints"].values() if cp["rally_id"] == rally_id]
    
    checkpoint_ids = [cp["id"] for cp in rally_checkpoints]
    user_progress = {}
    
    for checkpoint_id in checkpoint_ids:
        progress_id = f"{current_user['id']}_{checkpoint_id}"
        progress = db["progress"].get(progress_id)
        
        if progress:
            user_progress[checkpoint_id] = progress
        else:
            user_progress[checkpoint_id] = {
                "id": progress_id,
                "user_id": current_user["id"],
                "checkpoint_id": checkpoint_id,
                "acquired": False,
                "acquired_at": None
            }
    
    total_checkpoints = len(rally_checkpoints)
    acquired_checkpoints = sum(1 for p in user_progress.values() if p["acquired"])
    
    return {
        "rally_id": rally_id,
        "total_checkpoints": total_checkpoints,
        "acquired_checkpoints": acquired_checkpoints,
        "completion_percentage": (acquired_checkpoints / total_checkpoints * 100) if total_checkpoints > 0 else 0,
        "checkpoints": user_progress
    }

@app.get("/api/admin/rallies", response_model=List[Rally])
async def admin_get_rallies(current_admin: dict = Depends(get_current_admin)):
    """Get a list of all stamp rallies (admin only)."""
    return list(db["rallies"].values())

@app.post("/api/admin/rallies", response_model=Rally)
async def admin_create_rally(rally: RallyBase, current_admin: dict = Depends(get_current_admin)):
    """Create a new stamp rally (admin only)."""
    rally_id = f"rally_{uuid4()}"
    rally_data = rally.dict()
    rally_data["id"] = rally_id
    db["rallies"][rally_id] = rally_data
    return rally_data

@app.get("/api/admin/rallies/{rally_id}", response_model=Rally)
async def admin_get_rally(rally_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get a specific stamp rally by ID (admin only)."""
    if rally_id not in db["rallies"]:
        raise HTTPException(status_code=404, detail="Rally not found")
    return db["rallies"][rally_id]

@app.put("/api/admin/rallies/{rally_id}", response_model=Rally)
async def admin_update_rally(rally_id: str, rally: RallyBase, current_admin: dict = Depends(get_current_admin)):
    """Update a specific stamp rally (admin only)."""
    if rally_id not in db["rallies"]:
        raise HTTPException(status_code=404, detail="Rally not found")
    rally_data = rally.dict()
    rally_data["id"] = rally_id
    db["rallies"][rally_id] = rally_data
    return rally_data

@app.delete("/api/admin/rallies/{rally_id}", response_model=dict)
async def admin_delete_rally(rally_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a specific stamp rally (admin only)."""
    if rally_id not in db["rallies"]:
        raise HTTPException(status_code=404, detail="Rally not found")
    
    checkpoints_to_delete = [cp_id for cp_id, cp in db["checkpoints"].items() if cp["rally_id"] == rally_id]
    for cp_id in checkpoints_to_delete:
        del db["checkpoints"][cp_id]
    
    del db["rallies"][rally_id]
    
    return {"message": "Rally and associated checkpoints deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
