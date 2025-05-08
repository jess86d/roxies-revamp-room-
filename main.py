import firebase_admin
from firebase_admin import credentials, firestore, storage
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()

# Initialize Firebase
cred = credentials.Certificate("C:/Users/Assistant/ROXI/firebase key.json")
firebase_admin.initialize_app(cred,'storageBucket': '
roxies-revampd-rooms.appspot.com'
})
db = firestore.client()
bucket = storage.bucket()

# Pydantic models
class User(BaseModel):
    email: str
    name: str

class Room(BaseModel):
    user_id: str
    name: str
    room_scan_url: str = None

class Design(BaseModel):
    user_id: str
    room_id: str
    furniture_list: List[str]

# Routes

@app.post("/users/")
async def create_user(user: User):
    user_ref = db.collection('users').document()
    user_ref.set(user.dict())
    return {"message": "User created", "user_id": user_ref.id}

@app.post("/rooms/")
async def upload_room(user_id: str, name: str, file: UploadFile = File(...)):
    file_name = f"rooms/{uuid.uuid4()}_{file.filename}"
    blob = bucket.blob(file_name)
    blob.upload_from_file(file.file, content_type=file.content_type)
    blob.make_public()
    room_data = {
        "user_id": user_id,
        "name": name,
        "room_scan_url": blob.public_url
    }
    room_ref = db.collection('rooms').document()
    room_ref.set(room_data)
    return {"message": "Room uploaded", "room_id": room_ref.id, "url": blob.public_url}

@app.get("/rooms/{user_id}")
async def list_rooms(user_id: str):
    rooms = db.collection('rooms').where('user_id', '==', user_id).stream()
    return [r.to_dict() for r in rooms]

@app.post("/designs/")
async def save_design(design: Design):
    design_ref = db.collection('designs').document()
    design_ref.set(design.dict())
    return {"message": "Design saved", "design_id": design_ref.id}

@app.get("/roxie/recommendations/{room_type}")
async def get_recommendations(room_type: str):
    recommendations = {
        "rv": ["Compact foldable bed", "Wall-mounted storage"],
        "shed": ["Workbench", "Pegboard wall"],
        "van": ["Convertible sofa", "Roof rack"]
    }
    return recommendations.get(room_type.lower(), ["No recommendations available"])

@app.get("/")
async def root():
    return {"message": "Welcome to Roxie's Revamped Rooms API"}
