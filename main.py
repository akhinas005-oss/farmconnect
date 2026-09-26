from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from dotenv import load_dotenv

import database
from models import (
    EquipmentCreate, EquipmentResponse,
    WorkerCreate, WorkerResponse,
    PolicyMatchRequest, PolicyMatchResponse
)
from policy_matcher import get_policy_matches

# Load environment variables (.env)
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="FarmConnect API",
    description="Backend API service for FarmConnect hackathon project",
    version="1.0.0"
)

# Enable CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.init_db()


@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "FarmConnect Backend API",
        "docs_url": "/docs"
    }

# -------------------------------------------------------------------
# 1. Equipment Endpoints
# -------------------------------------------------------------------

@app.get("/api/equipment", response_model=List[EquipmentResponse])
def get_equipment(
    location: Optional[str] = Query(None, description="City/Location filter"),
    category: Optional[str] = Query(None, alias="type", description="Category or Type filter")
):
    conn = database.get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, name, type, purpose, condition, rent_per_day, location, contact, vendor_name, image_url, available FROM equipment WHERE 1=1"
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
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "name": row["name"],
            "type": row["type"],
            "purpose": row["purpose"],
            "condition": row["condition"],
            "rent_per_day": row["rent_per_day"],
            "location": row["location"],
            "contact": row["contact"],
            "vendor_name": row["vendor_name"],
            "image_url": row["image_url"],
            "available": bool(row["available"])
        })
    return result


@app.post("/api/equipment")
def create_equipment(data: EquipmentCreate):
    conn = database.get_db_connection()
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

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"success": True, "id": new_id}


# -------------------------------------------------------------------
# 2. Worker Endpoints
# -------------------------------------------------------------------

@app.get("/api/workers", response_model=List[WorkerResponse])
def get_workers(
    location: Optional[str] = Query(None, description="City/Location filter"),
    skill: Optional[str] = Query(None, description="Skill filter")
):
    conn = database.get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, name, skill, experience, daily_wage, location, contact, image_url, available_from, available_to FROM workers WHERE 1=1"
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
    conn.close()

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "name": row["name"],
            "skill": row["skill"],
            "experience": row["experience"],
            "daily_wage": row["daily_wage"],
            "location": row["location"],
            "contact": row["contact"],
            "image_url": row["image_url"],
            "available_from": row["available_from"],
            "available_to": row["available_to"]
        })
    return result


@app.post("/api/workers")
def create_worker(data: WorkerCreate):
    conn = database.get_db_connection()
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

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"success": True, "id": new_id}


# -------------------------------------------------------------------
# 3. Policy Matcher Endpoint
# -------------------------------------------------------------------

@app.post("/api/policy-match", response_model=PolicyMatchResponse)
def policy_match(data: PolicyMatchRequest):
    res = get_policy_matches(
        crop_type=data.crop_type,
        land_size=data.land_size,
        income_range=data.income_range,
        state=data.state
    )
    return res
