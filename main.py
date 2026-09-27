import logging
from typing import List, Optional
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import settings
import database
from models import (
    EquipmentCreate, EquipmentResponse,
    WorkerCreate, WorkerResponse,
    PolicyMatchRequest, PolicyMatchResponse,
    CropYieldPredictRequest, CropYieldPredictResponse
)
from policy_matcher import get_policy_matches
from ml_service import yield_predictor

# -------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("farmconnect.api")

# -------------------------------------------------------------------
# FastAPI App Initialization
# -------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade Backend API Service, ML Yield Predictor & AI Policy Matcher for FarmConnect",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -------------------------------------------------------------------
# CORS Middleware Configuration
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Global Exception Handlers
# -------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
            "code": f"HTTP_{exc.status_code}",
            "detail": str(exc.detail)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "code": "INTERNAL_SERVER_ERROR",
            "detail": "An unexpected error occurred. Please try again later."
        }
    )

# -------------------------------------------------------------------
# Application Startup Event
# -------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    logger.info("Initializing database tables and indexes on startup...")
    database.init_db()

# -------------------------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Check System & DB Health")
def health_check():
    """Checks service operational status and SQLite database connectivity."""
    db_status = "unhealthy"
    try:
        with database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            if cursor.fetchone():
                db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check DB ping failed: {e}")

    return {
        "status": "online" if db_status == "healthy" else "degraded",
        "database": db_status,
        "app": settings.APP_NAME,
        "environment": settings.ENV,
        "ml_model": "active" if yield_predictor.is_trained else "offline"
    }

@app.get("/", tags=["Health"], include_in_schema=False)
def read_root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "docs_url": "/docs",
        "health_url": "/health"
    }

# -------------------------------------------------------------------
# APIRouter v1
# -------------------------------------------------------------------
api_v1_router = APIRouter(prefix="/api/v1")

# Equipment Endpoints
@api_v1_router.get(
    "/equipment",
    response_model=List[EquipmentResponse],
    tags=["Equipment"],
    summary="List and filter registered equipment"
)
def get_equipment_v1(
    location: Optional[str] = Query(None, description="Filter by city or location"),
    category: Optional[str] = Query(None, alias="type", description="Filter by equipment category/type")
):
    """Retrieve all available agricultural equipment with optional location & type filtering."""
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, name, type, purpose, condition, rent_per_day, location, contact, vendor_name, image_url, available, created_at, updated_at FROM equipment WHERE 1=1"
        params = []

        if location and location.strip():
            query += " AND LOWER(location) LIKE ?"
            params.append(f"%{location.strip().lower()}%")

        if category and category.strip():
            query += " AND LOWER(type) LIKE ?"
            params.append(f"%{category.strip().lower()}%")

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        result = [dict(row) for row in rows]
        for item in result:
            item["available"] = bool(item["available"])
        return result

@api_v1_router.post(
    "/equipment",
    status_code=status.HTTP_201_CREATED,
    tags=["Equipment"],
    summary="Register new equipment listing"
)
def create_equipment_v1(data: EquipmentCreate):
    """Registers new agricultural machinery into the database."""
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO equipment (name, type, purpose, condition, rent_per_day, location, contact, vendor_name, image_url, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.name,
            data.type,
            data.purpose,
            data.condition,
            data.rent_per_day,
            data.location,
            data.contact,
            data.vendor_name,
            data.image_url,
            1 if data.availability else 0
        ))
        new_id = cursor.lastrowid
        logger.info(f"Registered new equipment item ID {new_id}: {data.name}")
        return {"success": True, "id": new_id}

# Worker Endpoints
@api_v1_router.get(
    "/workers",
    response_model=List[WorkerResponse],
    tags=["Workers"],
    summary="List and filter agricultural workers"
)
def get_workers_v1(
    location: Optional[str] = Query(None, description="Filter by city or location"),
    skill: Optional[str] = Query(None, description="Filter by skill")
):
    """Retrieve registered agricultural laborers with optional location & skill filtering."""
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, name, skill, experience, daily_wage, location, contact, image_url, available_from, available_to, created_at, updated_at FROM workers WHERE 1=1"
        params = []

        if location and location.strip():
            query += " AND LOWER(location) LIKE ?"
            params.append(f"%{location.strip().lower()}%")

        if skill and skill.strip():
            query += " AND LOWER(skill) LIKE ?"
            params.append(f"%{skill.strip().lower()}%")

        query += " ORDER BY id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

@api_v1_router.post(
    "/workers",
    status_code=status.HTTP_201_CREATED,
    tags=["Workers"],
    summary="Register new worker listing"
)
def create_worker_v1(data: WorkerCreate):
    """Registers new agricultural laborer or labor group into the database."""
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workers (name, skill, experience, daily_wage, location, contact, image_url, available_from, available_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.name,
            data.skill,
            data.experience,
            data.daily_wage,
            data.location,
            data.contact,
            data.image_url,
            data.available_from,
            data.available_to
        ))
        new_id = cursor.lastrowid
        logger.info(f"Registered new worker ID {new_id}: {data.name}")
        return {"success": True, "id": new_id}

# Policy Matcher Endpoint
@api_v1_router.post(
    "/policy-match",
    response_model=PolicyMatchResponse,
    tags=["Policy Matcher"],
    summary="Match eligible government agricultural schemes"
)
def policy_match_v1(data: PolicyMatchRequest):
    """Evaluates crop, land size, income, and state to return eligible government schemes via Gemini AI."""
    logger.info(f"Received policy match request for {data.crop_type} in {data.state}")
    res = get_policy_matches(
        crop_type=data.crop_type,
        land_size=data.land_size,
        income_range=data.income_range,
        state=data.state
    )
    return res

# Supervised Machine Learning Yield Predictor Endpoint
@api_v1_router.post(
    "/predict-yield",
    response_model=CropYieldPredictResponse,
    tags=["Machine Learning"],
    summary="Predict crop yield and revenue using Supervised ML"
)
def predict_crop_yield_v1(data: CropYieldPredictRequest):
    """Predicts agricultural crop yield (in tons) and revenue (in INR) using a Supervised Random Forest Regressor ML Model trained on ICAR benchmarks."""
    logger.info(f"Received ML yield prediction request for {data.crop_type} on {data.land_size_acres} acres")
    res = yield_predictor.predict(
        crop_type=data.crop_type,
        land_size_acres=data.land_size_acres,
        soil_type=data.soil_type or "alluvial",
        rainfall_mm=data.rainfall_mm or 1800.0,
        temperature_c=data.temperature_c or 28.0
    )
    return res

# Include Router v1
app.include_router(api_v1_router)

# -------------------------------------------------------------------
# Backward-Compatible Legacy Route Aliases
# -------------------------------------------------------------------
app.add_api_route("/api/equipment", get_equipment_v1, methods=["GET"], response_model=List[EquipmentResponse], include_in_schema=False)
app.add_api_route("/api/equipment", create_equipment_v1, methods=["POST"], status_code=status.HTTP_201_CREATED, include_in_schema=False)
app.add_api_route("/api/workers", get_workers_v1, methods=["GET"], response_model=List[WorkerResponse], include_in_schema=False)
app.add_api_route("/api/workers", create_worker_v1, methods=["POST"], status_code=status.HTTP_201_CREATED, include_in_schema=False)
app.add_api_route("/api/policy-match", policy_match_v1, methods=["POST"], response_model=PolicyMatchResponse, include_in_schema=False)
app.add_api_route("/api/predict-yield", predict_crop_yield_v1, methods=["POST"], response_model=CropYieldPredictResponse, include_in_schema=False)
