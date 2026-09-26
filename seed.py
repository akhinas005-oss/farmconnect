import database

def seed_data():
    # 1. Drop existing tables to re-apply schema with timestamps cleanly
    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS equipment;")
        cursor.execute("DROP TABLE IF EXISTS workers;")

    # 2. Re-initialize DB tables & indexes
    database.init_db()

    # 3. Seed Equipment Data
    equipment_items = [
        (
            "John Deere 5050D Tractor", 
            "Tractor", 
            "Heavy Plowing & Soil Preparation", 
            "Excellent", 
            1500.0, 
            "Palakkad", 
            "9876543210", 
            "Kerala Agro Machinery Vendors", 
            "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=600&auto=format&fit=crop&q=80", 
            1
        ),
        (
            "Mahindra 575 DI Tractor", 
            "Tractor", 
            "Land Tilling & Hauling", 
            "Good", 
            1400.0, 
            "Thrissur", 
            "9876543211", 
            "Thrissur Farm Solutions", 
            "https://images.unsplash.com/photo-1562684844-0e0dd0f4a25c?w=600&auto=format&fit=crop&q=80", 
            1
        ),
        (
            "Kubota Paddy Harvester", 
            "Harvester", 
            "Fast Paddy Crop Harvesting", 
            "Brand New", 
            2500.0, 
            "Palakkad", 
            "9876543212", 
            "Palakkad Harvesting Tech", 
            "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=600&auto=format&fit=crop&q=80", 
            1
        ),
        (
            "Power Tiller 15HP", 
            "Tiller", 
            "Wetland Paddy Field Preparation", 
            "Good", 
            800.0, 
            "Wayanad", 
            "9876543213", 
            "Wayanad Farmers Guild", 
            "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=600&auto=format&fit=crop&q=80", 
            1
        ),
        (
            "High-Pressure Battery Sprayer", 
            "Sprayer", 
            "Pesticide & Fertilizer Spraying", 
            "Good", 
            400.0, 
            "Thrissur", 
            "9876543214", 
            "GreenCare Agro Services", 
            "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=600&auto=format&fit=crop&q=80", 
            1
        ),
        (
            "Class Crop Combine Harvester", 
            "Harvester", 
            "Multi-Crop Grains Harvesting", 
            "Fair", 
            3000.0, 
            "Coimbatore", 
            "9876543215", 
            "Coimbatore Harvesters Ltd", 
            "https://images.unsplash.com/photo-1535379453347-1ffd615e2e08?w=600&auto=format&fit=crop&q=80", 
            0
        )
    ]

    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO equipment (name, type, purpose, condition, rent_per_day, location, contact, vendor_name, image_url, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, equipment_items)

    # 4. Seed Worker Data
    worker_items = [
        (
            "Rajan K", 
            "Harvesting", 
            "8 years in Paddy & Coconut Harvesting", 
            800.0, 
            "Thrissur", 
            "9876543220", 
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80", 
            "2024-01-10", 
            "2024-01-20"
        ),
        (
            "Suresh Kumar", 
            "Tilling", 
            "5 years operating Power Tillers", 
            750.0, 
            "Palakkad", 
            "9876543221", 
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80", 
            "2024-01-05", 
            "2024-01-25"
        ),
        (
            "Binu P", 
            "Pesticide Spraying", 
            "4 years in Certified Spraying & Pest Control", 
            700.0, 
            "Palakkad", 
            "9876543222", 
            "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80", 
            "2024-01-01", 
            "2024-01-30"
        ),
        (
            "Mani & Team (4 Workers)", 
            "Harvesting", 
            "10 years experienced Paddy Harvesting Crew", 
            3200.0, 
            "Palakkad", 
            "9876543223", 
            "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400&auto=format&fit=crop&q=80", 
            "2024-01-12", 
            "2024-01-22"
        ),
        (
            "Venu M", 
            "Sowing & Planting", 
            "6 years in Paddy Nursery & Sapling Planting", 
            650.0, 
            "Wayanad", 
            "9876543224", 
            "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&auto=format&fit=crop&q=80", 
            "2024-01-08", 
            "2024-01-18"
        )
    ]

    with database.get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO workers (name, skill, experience, daily_wage, location, contact, image_url, available_from, available_to)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, worker_items)

    print("[SUCCESS] Database schema updated and seeded cleanly using context managers!")

if __name__ == "__main__":
    seed_data()
