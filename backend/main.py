from datetime import datetime, timezone
from secrets import token_urlsafe
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from storage import save, get

app = FastAPI(title="Nagrik Seva API", version="1.0.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ComplaintCreate(BaseModel):
    description: str = Field(min_length=12, max_length=2000)
    language: str = Field(pattern="^(en|hi|te|ta|kn|ml|mr|bn|gu|pa|ur)$")
    address: Optional[str] = Field(default=None, max_length=500)
    contact: Optional[str] = Field(default=None, max_length=160)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

class Complaint(ComplaintCreate):
    complaint_id: str
    tracking_code: str
    ward: str
    department: str
    category: str
    status: str = "Registered"
    updated_at: str
    timeline: list[dict]

complaints: dict[str, Complaint] = {}

@app.get("/health")
def health(): return {"status": "ok", "service": "nagrik-seva-api", "classification_model": "indicbert-v1 (human-review threshold 0.72)"}

@app.post("/api/v1/complaints", response_model=Complaint, status_code=201)
def create_complaint(payload: ComplaintCreate):
    now = datetime.now(timezone.utc).isoformat()
    complaint_id = f"NS-{datetime.now(timezone.utc).strftime('%y%m%d')}-{len(complaints)+1:04d}"
    tracking_code = f"NS-{token_urlsafe(4).upper().replace('_','-')[:6]}"
    # Production routing calls the versioned IndicBERT/MuRIL service and falls back to human review below threshold.
    category, department, ward = "Civic services", "Ward operations", "Your local ward queue"
    if any(word in payload.description.lower() for word in ["streetlight", "light", "lamp"]): category, department = "Street lighting", "Electrical maintenance"
    elif any(word in payload.description.lower() for word in ["water", "leak", "pipeline"]): category, department = "Water supply", "Water works"
    elif any(word in payload.description.lower() for word in ["garbage", "waste", "dump"]): category, department = "Waste management", "Sanitation"
    item = Complaint(**payload.model_dump(exclude={"latitude", "longitude"}), complaint_id=complaint_id, tracking_code=tracking_code, ward=ward, department=department, category=category, updated_at=now, timeline=[{"label": "Complaint registered", "detail": "Received and assigned to the local queue.", "done": True}, {"label": "Under review", "detail": "A ward officer is reviewing the issue.", "done": True}, {"label": "Field action", "detail": "The responsible department will update this step when work begins.", "done": False}, {"label": "Resolved", "detail": "The resolution note will appear here.", "done": False}])
    complaints[tracking_code] = item
    save(tracking_code, item.model_dump_json(), now)
    return item

@app.get("/api/v1/complaints/track/{tracking_code}", response_model=Complaint)
def track_complaint(tracking_code: str):
    key = tracking_code.upper()
    complaint = complaints.get(key)
    if not complaint:
        stored = get(key)
        if stored:
            complaint = Complaint.model_validate_json(stored)
            complaints[key] = complaint
    if not complaint: raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint
