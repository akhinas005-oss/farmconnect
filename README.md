# 🌾 FarmConnect - Backend & API Service

Official Python FastAPI Backend & AI Policy Matcher for **FarmConnect** (Hackathon PS2 - Agriculture).

---

## 📁 Repository Clean Structure

* `main.py` — FastAPI application & CORS-enabled API routes
* `database.py` — SQLite connection & schema initialization
* `models.py` — Pydantic validation schemas
* `policy_matcher.py` — Google Gemini 3.5 Flash LLM integration + rules fallback engine
* `seed.py` — Seeding script for sample tractors, harvesters, sprayers, and workers
* `requirements.txt` — Python dependencies
* `.env.example` — Environment variables template

---

## ⚡ Quick 1-Minute Setup Guide for Frontend Integration

### 1. Clone & Set up Virtual Environment
```bash
git clone https://github.com/YOUR_USERNAME/farmconnect.git
cd farmconnect
py -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Database & Start Server
```bash
python seed.py
python -m uvicorn main:app --reload --port 8000
```
Your backend will run live on **`http://127.0.0.1:8000`** with interactive Swagger API docs at **`http://127.0.0.1:8000/docs`**.

---

## 📡 API Contract (Frontend ↔ Backend)

| Endpoint | Method | Query / Body Params | Response Description |
| :--- | :--- | :--- | :--- |
| `/api/equipment` | `GET` | `location={city}`, `type={category}` | List of equipment cards with vendor name, rent/day, contact, & images |
| `/api/equipment` | `POST` | `{ name, type, purpose, condition, rent_per_day, location, contact, vendor_name, image_url }` | Registers new equipment listing (`{ success: true, id: X }`) |
| `/api/workers` | `GET` | `location={city}`, `skill={skill}` | List of skilled agricultural workers with daily wage, contact, & images |
| `/api/workers` | `POST` | `{ name, skill, experience, daily_wage, location, contact, image_url }` | Registers new worker listing (`{ success: true, id: X }`) |
| `/api/policy-match` | `POST` | `{ crop_type, land_size, income_range, state }` | Returns eligible government schemes via Gemini LLM |
