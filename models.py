from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# --- Enums ---
class EquipmentCondition(str, Enum):
    BRAND_NEW = "Brand New"
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"

class EquipmentType(str, Enum):
    TRACTOR = "Tractor"
    HARVESTER = "Harvester"
    TILLER = "Tiller"
    SPRAYER = "Sprayer"
    OTHER = "Other"

# --- Equipment Schemas ---
class EquipmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Name of the equipment")
    type: str = Field(..., min_length=2, max_length=50, description="Equipment type/category")
    purpose: Optional[str] = Field("General Farming", max_length=200, description="Use case or purpose")
    condition: Optional[str] = Field("Good", max_length=50, description="Condition of machine")
    rent_per_day: float = Field(..., gt=0, description="Rent per day in INR")
    location: str = Field(..., min_length=2, max_length=100, description="Location/City")
    contact: str = Field(..., min_length=7, max_length=15, description="Contact phone number")
    vendor_name: Optional[str] = Field("Equipment Vendor", max_length=100, description="Vendor or Owner Name")
    image_url: Optional[str] = Field(None, description="Image URL")
    availability: Optional[bool] = Field(True, description="Availability flag")

class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    type: Optional[str] = Field(None, min_length=2, max_length=50)
    purpose: Optional[str] = Field(None, max_length=200)
    condition: Optional[str] = Field(None, max_length=50)
    rent_per_day: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    contact: Optional[str] = Field(None, min_length=7, max_length=15)
    vendor_name: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None)
    available: Optional[bool] = Field(None)

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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# --- Worker Schemas ---
class WorkerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Worker or Team Name")
    skill: str = Field(..., min_length=2, max_length=100, description="Agricultural skill")
    experience: Optional[str] = Field("1 year", max_length=100, description="Years or description of experience")
    daily_wage: float = Field(..., gt=0, description="Daily wage in INR")
    location: str = Field(..., min_length=2, max_length=100, description="Location/City")
    contact: str = Field(..., min_length=7, max_length=15, description="Contact phone number")
    image_url: Optional[str] = Field(None, description="Profile Image URL")
    available_from: Optional[str] = Field("2024-01-01", description="Availability start date")
    available_to: Optional[str] = Field("2024-12-31", description="Availability end date")

class WorkerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    skill: Optional[str] = Field(None, min_length=2, max_length=100)
    experience: Optional[str] = Field(None, max_length=100)
    daily_wage: Optional[float] = Field(None, gt=0)
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    contact: Optional[str] = Field(None, min_length=7, max_length=15)
    image_url: Optional[str] = Field(None)
    available_from: Optional[str] = Field(None)
    available_to: Optional[str] = Field(None)

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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# --- Policy Matcher Schemas ---
class PolicyMatchRequest(BaseModel):
    crop_type: str = Field(..., min_length=2, max_length=100, example="Paddy")
    land_size: str = Field(..., min_length=1, max_length=50, example="2 Acres")
    income_range: str = Field(..., min_length=1, max_length=50, example="< 2 Lakhs")
    state: str = Field(..., min_length=2, max_length=100, example="Kerala")

class SchemeItem(BaseModel):
    name: str
    description: str
    benefit: str
    how_to_apply: List[str]

class PolicyMatchResponse(BaseModel):
    schemes: List[SchemeItem]

# --- Supervised ML Yield Predictor Schemas ---
class CropYieldPredictRequest(BaseModel):
    crop_type: str = Field(..., min_length=2, max_length=100, example="Paddy")
    land_size_acres: float = Field(..., gt=0, example=2.5, description="Land size in Acres")
    soil_type: Optional[str] = Field("Alluvial", example="Alluvial")
    rainfall_mm: Optional[float] = Field(1800.0, gt=0, example=1800.0)
    temperature_c: Optional[float] = Field(28.0, gt=5.0, lt=60.0, example=28.0)

class CropYieldPredictResponse(BaseModel):
    crop_type: str
    land_size_acres: float
    predicted_yield_tons: float
    yield_per_acre_tons: float
    estimated_revenue_inr: float
    ml_model: str
    model_r2_accuracy: float
    recommendation: str
