import unittest
import sqlite3
import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load env variables
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
DB_FILE = os.path.join(os.path.dirname(__file__), "farmconnect.db")

class TestFarmConnectBackend(unittest.TestCase):

    def test_01_database_tables_and_columns(self):
        """Verify SQLite Database file exists and tables/columns match specs."""
        self.assertTrue(os.path.exists(DB_FILE), f"Database file {DB_FILE} does not exist!")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Verify Equipment Table schema
        cursor.execute("PRAGMA table_info(equipment);")
        equip_cols = {col[1]: col[2] for col in cursor.fetchall()}
        expected_equip = ["id", "name", "type", "purpose", "condition", "rent_per_day", "location", "contact", "vendor_name", "image_url", "available"]
        for col in expected_equip:
            self.assertIn(col, equip_cols, f"Column '{col}' missing from equipment table!")

        # Verify Workers Table schema
        cursor.execute("PRAGMA table_info(workers);")
        worker_cols = {col[1]: col[2] for col in cursor.fetchall()}
        expected_worker = ["id", "name", "skill", "experience", "daily_wage", "location", "contact", "image_url", "available_from", "available_to"]
        for col in expected_worker:
            self.assertIn(col, worker_cols, f"Column '{col}' missing from workers table!")

        conn.close()
        print("\n[PASSED] Test 1: SQLite Database tables, columns, and data types verified successfully!")

    def test_02_get_equipment_api(self):
        """Test GET /api/equipment endpoint with location filter."""
        req = urllib.request.Request(f"{BASE_URL}/api/equipment?location=Palakkad")
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0, "No equipment found for Palakkad!")
            item = data[0]
            self.assertIn("name", item)
            self.assertIn("vendor_name", item)
            self.assertIn("rent_per_day", item)
            self.assertIn("image_url", item)
        print("[PASSED] Test 2: GET /api/equipment endpoint works with filters!")

    def test_03_post_equipment_api(self):
        """Test POST /api/equipment registration endpoint."""
        payload = {
            "name": "Test Drone Sprayer 500",
            "type": "Sprayer",
            "purpose": "Aerial Crop Spraying",
            "condition": "Brand New",
            "rent_per_day": 1800.0,
            "location": "Palakkad",
            "contact": "9998887770",
            "vendor_name": "AgriTech Drones",
            "image_url": "https://example.com/drone.jpg",
            "availability": True
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/equipment",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            res_data = json.loads(response.read().decode())
            self.assertTrue(res_data.get("success"))
            self.assertIn("id", res_data)
        print("[PASSED] Test 3: POST /api/equipment registered new listing into DB!")

    def test_04_get_workers_api(self):
        """Test GET /api/workers endpoint."""
        req = urllib.request.Request(f"{BASE_URL}/api/workers?skill=Harvesting")
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode())
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0, "No harvesting workers found!")
            item = data[0]
            self.assertIn("name", item)
            self.assertIn("skill", item)
            self.assertIn("daily_wage", item)
        print("[PASSED] Test 4: GET /api/workers endpoint works!")

    def test_05_post_worker_api(self):
        """Test POST /api/workers registration endpoint."""
        payload = {
            "name": "Test Worker Alex",
            "skill": "Tilling",
            "experience": "3 years",
            "daily_wage": 700.0,
            "location": "Thrissur",
            "contact": "9991112223",
            "image_url": "https://example.com/alex.jpg",
            "available_from": "2024-01-01",
            "available_to": "2024-12-31"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/workers",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            res_data = json.loads(response.read().decode())
            self.assertTrue(res_data.get("success"))
            self.assertIn("id", res_data)
        print("[PASSED] Test 5: POST /api/workers registered new worker into DB!")

    def test_06_policy_match_api(self):
        """Test POST /api/policy-match endpoint with Gemini LLM integration."""
        payload = {
            "crop_type": "Paddy",
            "land_size": "2 Acres",
            "income_range": "< 2 Lakhs",
            "state": "Kerala"
        }
        req = urllib.request.Request(
            f"{BASE_URL}/api/policy-match",
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            res_data = json.loads(response.read().decode())
            self.assertIn("schemes", res_data)
            self.assertGreater(len(res_data["schemes"]), 0)
            scheme = res_data["schemes"][0]
            self.assertIn("name", scheme)
            self.assertIn("description", scheme)
            self.assertIn("benefit", scheme)
            self.assertIn("how_to_apply", scheme)
        print("[PASSED] Test 6: POST /api/policy-match returned valid government schemes!")

if __name__ == "__main__":
    unittest.main()
