from pydantic import BaseModel
from typing import List, Optional

# --- Equipment Schemas ---
class EquipmentCreate(BaseModel):
    name: str
    type: str
    purpose: Optional[str] = "General Farming"
    condition: Optional[str] = "Good"
    rent_per_day: float
    location: str
    contact: str
    vendor_name: Optional[str] = "Equipment Vendor"
    image_url: Optional[str] = None
    availability: Optional[bool] = True

class EquipmentResponse(BaseModel):
    id: int
    name: str
    type: str
    purpose: Optional[str] = None
    condition: Optional[str] = None
    rent_per_day: float
    location: str
    contact: str
    vendor_name: Optional[str] = None
    image_url: Optional[str] = None
    available: bool

# --- Worker Schemas ---
class WorkerCreate(BaseModel):
    name: str
    skill: str
    experience: Optional[str] = "1 year"
    daily_wage: float
    location: str
    contact: str
    image_url: Optional[str] = None
    available_from: Optional[str] = "2024-01-01"
    available_to: Optional[str] = "2024-12-31"

class WorkerResponse(BaseModel):
    id: int
    name: str
    skill: str
    experience: Optional[str] = None
    daily_wage: float
    location: str
    contact: str
    image_url: Optional[str] = None
    available_from: Optional[str] = None
    available_to: Optional[str] = None

# --- Policy Matcher Schemas ---
class PolicyMatchRequest(BaseModel):
    crop_type: str
    land_size: str
    income_range: str
    state: str

class SchemeItem(BaseModel):
    name: str
    description: str
    benefit: str
    how_to_apply: str

class PolicyMatchResponse(BaseModel):
    schemes: List[SchemeItem]
