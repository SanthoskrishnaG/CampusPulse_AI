"""
Centralized Campus Configuration for CampusPulse AI
Single Source of Truth for Coimbatore Institute of Technology (CIT)
"""
import os

CAMPUS_CONFIG = {
    "name": "Coimbatore Institute of Technology",
    "short_name": "CIT",
    "tagline": "CIT Smart Campus • Coimbatore",
    "city": "Coimbatore",
    "locality": "Hope College / Peelamedu",
    "state": "Tamil Nadu",
    "country": "India",
    "postal_code": "641014",
    "address": "Civil Aerodrome Post, Coimbatore, Tamil Nadu - 641014",
    
    # Official / Map-verified Center Point (Civil Aerodrome Post / Avinashi Road)
    "latitude": float(os.environ.get('CAMPUS_LAT', 11.02752)),
    "longitude": float(os.environ.get('CAMPUS_LNG', 77.02724)),
    "default_zoom": 17,
    "regional_lat": 11.0168,
    "regional_lng": 76.9558,
    "regional_zoom": 12,
    "locality_lat": 11.0275,
    "locality_lng": 77.0180,
    "locality_zoom": 15,

    # Approximate visual boundary polygon of CIT Campus for demo rendering
    # (Along Avinashi Road / Civil Aerodrome corridor - clearly labeled approximate area)
    "boundary_approx": [
        [11.0302, 77.0250],
        [11.0306, 77.0295],
        [11.0252, 77.0301],
        [11.0246, 77.0255],
    ],
    "boundary_label": "CIT Campus Area",

    # Configurable Campus Building / Landmark Coordinates
    "landmarks": {
        "main_gate": {
            "name": "CIT Main Entrance Gate",
            "code": "CIT-GATE1",
            "category": "BUS_STOP",
            "latitude": 11.0287,
            "longitude": 77.0268,
            "description": "Main campus gate on Avinashi Road (Hope College side)"
        },
        "admin_block": {
            "name": "CIT Administrative Block",
            "code": "CIT-ADMIN",
            "category": "ADMIN_BLOCK",
            "latitude": 11.0281,
            "longitude": 77.0272,
            "description": "Principal Office, Deanery & Central Admissions"
        },
        "auditorium": {
            "name": "Golden Jubilee Auditorium",
            "code": "CIT-AUDI",
            "category": "AUDITORIUM",
            "latitude": 11.0283,
            "longitude": 77.0282,
            "description": "Main campus cultural and international conference auditorium"
        },
        "cse_block": {
            "name": "Computing & IT Complex (CSE/IT)",
            "code": "CIT-CSE",
            "category": "ACADEMIC_BLOCK",
            "latitude": 11.0276,
            "longitude": 77.0267,
            "description": "Computer Science, AI & Information Technology Labs"
        },
        "mech_civil_eee": {
            "name": "Core Engineering Block (ECE/EEE/Mech/Civil)",
            "code": "CIT-ENGG",
            "category": "ACADEMIC_BLOCK",
            "latitude": 11.0271,
            "longitude": 77.0279,
            "description": "Engineering research laboratories and workshops"
        },
        "ai_lab": {
            "name": "CIT Centre for Artificial Intelligence & IoT",
            "code": "CIT-AI",
            "category": "LABORATORY",
            "latitude": 11.0278,
            "longitude": 77.0269,
            "description": "High Performance GPU Clusters & CampusPulse AI Telemetry Center"
        },
        "library": {
            "name": "Central Library & Digital Knowledge Centre",
            "code": "CIT-LIB",
            "category": "ACADEMIC_BLOCK",
            "latitude": 11.0274,
            "longitude": 77.0273,
            "description": "Autonomous library with RFID borrowing and 60,000+ volumes"
        },
        "canteen": {
            "name": "Smart Campus Canteen & Cafeteria",
            "code": "CIT-CAN",
            "category": "CANTEEN",
            "latitude": 11.0266,
            "longitude": 77.0264,
            "description": "Student food court with AI demand-driven meal management"
        },
        "parking_north": {
            "name": "Main Gate Student Parking (Lot A)",
            "code": "PKG-NORTH",
            "category": "PARKING",
            "latitude": 11.0288,
            "longitude": 77.0262,
            "total_slots": 80,
            "description": "Two-wheeler and four-wheeler covered parking bays"
        },
        "parking_east": {
            "name": "East Engineering Faculty Parking (Lot B)",
            "code": "PKG-EAST",
            "category": "PARKING",
            "latitude": 11.0274,
            "longitude": 77.0289,
            "total_slots": 75,
            "description": "Faculty and EV charging vehicle bays"
        },
        "parking_south": {
            "name": "Auditorium Visitor Parking (Lot C)",
            "code": "PKG-AUDI",
            "category": "PARKING",
            "latitude": 11.0285,
            "longitude": 77.0287,
            "total_slots": 65,
            "description": "Guest and visitor parking zone"
        },
        "bus_terminal": {
            "name": "CIT Hope College Transit Hub",
            "code": "STOP-CIT",
            "category": "BUS_STOP",
            "latitude": 11.0289,
            "longitude": 77.0270,
            "description": "Designated boarding bay for campus shuttle and town fleet"
        },
        "hostel": {
            "name": "Student Residential Hostels",
            "code": "CIT-HOSTEL",
            "category": "HOSTEL",
            "latitude": 11.0256,
            "longitude": 77.0276,
            "description": "Undergraduate and postgraduate on-campus residences"
        },
        "sports": {
            "name": "CIT Sports Pavilion & Track",
            "code": "CIT-SPORTS",
            "category": "SPORTS",
            "latitude": 11.0260,
            "longitude": 77.0286,
            "description": "Athletics track, basketball complex and outdoor grounds"
        }
    },

    # Coimbatore Bus Fleet Simulated Routes
    "bus_routes": [
        {
            "name": "Route 1 - Gandhipuram Central Express",
            "code": "R-01",
            "start": "Gandhipuram Central Bus Stand",
            "end": "CIT Main Gate Terminal",
            "distance_km": 7.2,
            "duration_mins": 22,
            "stops": [
                {"name": "Gandhipuram Central", "lat": 11.0182, "lng": 76.9678},
                {"name": "Lakshmi Mills Junction", "lat": 11.0205, "lng": 76.9850},
                {"name": "Nava India Signal", "lat": 11.0232, "lng": 77.0010},
                {"name": "Peelamedu / Hope College", "lat": 11.0275, "lng": 77.0180},
                {"name": "CIT Main Gate Terminal", "lat": 11.0287, "lng": 77.0268}
            ]
        },
        {
            "name": "Route 2 - Coimbatore Junction Railway Connector",
            "code": "R-02",
            "start": "Coimbatore Railway Junction",
            "end": "CIT Main Gate Terminal",
            "distance_km": 8.8,
            "duration_mins": 26,
            "stops": [
                {"name": "Coimbatore Railway Junction", "lat": 10.9985, "lng": 76.9660},
                {"name": "Collectorate & District Court", "lat": 11.0060, "lng": 76.9740},
                {"name": "VOC Park / Stadium", "lat": 11.0110, "lng": 76.9810},
                {"name": "Fun Republic Mall / Krishnammal", "lat": 11.0260, "lng": 77.0120},
                {"name": "CIT Main Gate Terminal", "lat": 11.0287, "lng": 77.0268}
            ]
        },
        {
            "name": "Route 3 - Singanallur & Trichy Road Shuttle",
            "code": "R-03",
            "start": "Singanallur Bus Stand",
            "end": "CIT Main Gate Terminal",
            "distance_km": 6.1,
            "duration_mins": 19,
            "stops": [
                {"name": "Singanallur Bus Stand", "lat": 11.0020, "lng": 77.0260},
                {"name": "Kallimadai Junction", "lat": 11.0120, "lng": 77.0280},
                {"name": "Tidel Park / Civil Aerodrome Road", "lat": 11.0230, "lng": 77.0310},
                {"name": "CIT East Gate", "lat": 11.0275, "lng": 77.0285},
                {"name": "CIT Main Gate Terminal", "lat": 11.0287, "lng": 77.0268}
            ]
        },
        {
            "name": "Route 4 - Airport & Sitra Link",
            "code": "R-04",
            "start": "Coimbatore International Airport",
            "end": "CIT Main Gate Terminal",
            "distance_km": 4.5,
            "duration_mins": 14,
            "stops": [
                {"name": "Coimbatore International Airport (CJB)", "lat": 11.0300, "lng": 77.0434},
                {"name": "Sitra Junction", "lat": 11.0312, "lng": 77.0380},
                {"name": "KMCH Medical Center", "lat": 11.0295, "lng": 77.0330},
                {"name": "Civil Aerodrome Post Office", "lat": 11.0282, "lng": 77.0295},
                {"name": "CIT Main Gate Terminal", "lat": 11.0287, "lng": 77.0268}
            ]
        }
    ]
}
