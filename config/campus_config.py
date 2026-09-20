"""
Centralized Campus Configuration for CampusPulse AI
Single Source of Truth for Coimbatore Institute of Technology (CIT)
Contains:
- Campus Metadata
- Boundary Polygon (CIT Campus Area)
- 27 Dedicated Campus Buildings & Facilities (Category, Coords, Details, Icons)
- Campus Road & Walkway Waypoint Graph for Building-to-Building Navigation
- Precomputed Main Gate -> Building Routes with distance & walk time
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
    "latitude": 11.02752,
    "longitude": 77.02724,
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
        [11.0298, 77.0252],  # NW corner (Avinashi Road near Hope College signal)
        [11.0304, 77.0282],  # N boundary along Avinashi Road
        [11.0299, 77.0305],  # NE corner near Civil Aerodrome Post
        [11.0268, 77.0310],  # E boundary (Sports / Campus periphery)
        [11.0245, 77.0302],  # SE corner (Hostel & Ground back)
        [11.0242, 77.0270],  # S boundary (Residential perimeter)
        [11.0250, 77.0252],  # SW corner
        [11.0276, 77.0250],  # W boundary along Hope College corridor
    ],
    "boundary_label": "CIT Campus Area",

    # Campus Road & Walkway Waypoints for realistic routing without crossing building walls
    "waypoints": {
        "WP_GATE": [11.0291, 77.0268],           # Main Gate on Avinashi Road
        "WP_ADMIN_ROUND": [11.0283, 77.0271],    # North-Central Roundabout near Admin
        "WP_QUAD_CENTRE": [11.0276, 77.0271],    # Central Campus Crossroad / Quad
        "WP_EAST_AVENUE": [11.0276, 77.0283],    # East Engineering Corridor
        "WP_AUDI_LANE": [11.0284, 77.0283],      # Auditorium & Visitor Parking Lane
        "WP_SOUTH_SPINE": [11.0266, 77.0271],    # South Dining & Living Spine
        "WP_HOSTEL_JUNC": [11.0254, 77.0275],    # Residential Living Junction
        "WP_SPORTS_ROAD": [11.0260, 77.0285],    # Sports Ground & Courts Road
        "WP_WEST_PARK_LANE": [11.0288, 77.0262]  # West Student Parking Lane
    },

    # 27 Dedicated Campus Locations & Buildings
    "locations": [
        {
            "id": "main_gate",
            "name": "CIT Main Entrance Gate",
            "code": "GATE-MAIN",
            "category": "TRANSPORT",
            "type": "entrance",
            "latitude": 11.0292,
            "longitude": 77.0268,
            "floor_count": 1,
            "capacity": 500,
            "description": "Main campus gate on Avinashi Road (Hope College side) with 24/7 security and RFID entry.",
            "icon": "🚪",
            "is_verified": True,
            "status": "Operational",
            "nearest_waypoint": "WP_GATE"
        },
        {
            "id": "admin_block",
            "name": "CIT Administrative Block",
            "code": "ADMIN-BLK",
            "category": "ADMINISTRATION",
            "type": "admin",
            "latitude": 11.0285,
            "longitude": 77.0272,
            "floor_count": 4,
            "capacity": 450,
            "description": "Principal's Office, Deaneries, Registrar, Controller of Examinations & Admissions.",
            "icon": "🏛️",
            "is_verified": True,
            "status": "Open (9 AM - 5 PM)",
            "nearest_waypoint": "WP_ADMIN_ROUND"
        },
        {
            "id": "acad_block_1",
            "name": "Academic Block I (Main Quad)",
            "code": "ACAD-1",
            "category": "ACADEMIC",
            "type": "academic",
            "latitude": 11.0282,
            "longitude": 77.0264,
            "floor_count": 4,
            "capacity": 800,
            "description": "Undergraduate lecture halls, smart audiovisual auditoriums, and tutorial complexes.",
            "icon": "🏫",
            "is_verified": False,
            "is_simulated": True,
            "status": "Active Classes",
            "nearest_waypoint": "WP_ADMIN_ROUND"
        },
        {
            "id": "cse_dept",
            "name": "CSE Department (Computing Complex)",
            "code": "DEPT-CSE",
            "category": "DEPARTMENT",
            "type": "department",
            "latitude": 11.0278,
            "longitude": 77.0266,
            "floor_count": 5,
            "capacity": 900,
            "description": "Department of Computer Science & Engineering, NVIDIA GPU Labs, and Software Studios.",
            "icon": "💻",
            "is_verified": True,
            "status": "842 Students Enrolled",
            "nearest_waypoint": "WP_QUAD_CENTRE"
        },
        {
            "id": "it_dept",
            "name": "Information Technology Department",
            "code": "DEPT-IT",
            "category": "DEPARTMENT",
            "type": "department",
            "latitude": 11.0275,
            "longitude": 77.0263,
            "floor_count": 4,
            "capacity": 650,
            "description": "Department of Information Technology, Cloud Computing & Cybersecurity research suites.",
            "icon": "🖥️",
            "is_verified": False,
            "is_simulated": True,
            "status": "Active Labs",
            "nearest_waypoint": "WP_QUAD_CENTRE"
        },
        {
            "id": "ai_centre",
            "name": "Centre for Artificial Intelligence & IoT",
            "code": "CENTRE-AI",
            "category": "RESEARCH",
            "type": "research",
            "latitude": 11.0279,
            "longitude": 77.0270,
            "floor_count": 3,
            "capacity": 250,
            "description": "High Performance AI Computing Cluster, Edge Devices & CampusPulse AI Telemetry Center.",
            "icon": "🤖",
            "is_verified": True,
            "status": "Telemetry Online",
            "nearest_waypoint": "WP_QUAD_CENTRE"
        },
        {
            "id": "ece_dept",
            "name": "ECE Department (Electronics Complex)",
            "code": "DEPT-ECE",
            "category": "DEPARTMENT",
            "type": "department",
            "latitude": 11.0274,
            "longitude": 77.0278,
            "floor_count": 4,
            "capacity": 750,
            "description": "Electronics & Communication Engineering, VLSI Design, Embedded Systems & Signal Labs.",
            "icon": "📡",
            "is_verified": True,
            "status": "Optimal",
            "nearest_waypoint": "WP_EAST_AVENUE"
        },
        {
            "id": "eee_dept",
            "name": "EEE Department (Electrical Sciences)",
            "code": "DEPT-EEE",
            "category": "DEPARTMENT",
            "type": "department",
            "latitude": 11.0271,
            "longitude": 77.0279,
            "floor_count": 3,
            "capacity": 600,
            "description": "Electrical & Electronics Engineering, Smart Grid Microgrid Station, and High Voltage Wing.",
            "icon": "⚡",
            "is_verified": True,
            "status": "Grid Active",
            "nearest_waypoint": "WP_EAST_AVENUE"
        },
        {
            "id": "mech_dept",
            "name": "Mechanical Engineering Department",
            "code": "DEPT-MECH",
            "category": "DEPARTMENT",
            "type": "department",
            "latitude": 11.0268,
            "longitude": 77.0282,
            "floor_count": 3,
            "capacity": 700,
            "description": "Mechanical Engineering, CAD/CAM Design Center, Robotics, Thermodynamics and Metallurgy Labs.",
            "icon": "⚙️",
            "is_verified": True,
            "status": "Workshops Active",
            "nearest_waypoint": "WP_EAST_AVENUE"
        },
        {
            "id": "civil_dept",
            "name": "Civil Engineering Department",
            "code": "DEPT-CIVIL",
            "category": "DEPARTMENT",
            "type": "department",
            "latitude": 11.0266,
            "longitude": 77.0277,
            "floor_count": 3,
            "capacity": 550,
            "description": "Civil Engineering, Structural Testing Lab, Soil Mechanics, Surveying & Environmental Lab.",
            "icon": "🏗️",
            "is_verified": True,
            "status": "Active",
            "nearest_waypoint": "WP_SOUTH_SPINE"
        },
        {
            "id": "library",
            "name": "Central Library & Digital Knowledge Centre",
            "code": "LIB-CENTRAL",
            "category": "LIBRARY",
            "type": "library",
            "latitude": 11.0277,
            "longitude": 77.0274,
            "floor_count": 4,
            "capacity": 850,
            "description": "Autonomous library with RFID self-issue, 65,000+ print volumes, IEEE/Elsevier e-resources, quiet zones.",
            "icon": "📚",
            "is_verified": True,
            "status": "Quiet Zone (310/850 Occupied)",
            "nearest_waypoint": "WP_QUAD_CENTRE"
        },
        {
            "id": "canteen",
            "name": "Smart Campus Canteen & Cafeteria",
            "code": "CAN-MAIN",
            "category": "FOOD",
            "type": "food",
            "latitude": 11.0263,
            "longitude": 77.0267,
            "floor_count": 2,
            "capacity": 600,
            "description": "Central student & staff food court with AI demand-driven meal management and hygienic dining.",
            "icon": "🍽️",
            "is_verified": True,
            "status": "Peak Lunch (65% Full)",
            "nearest_waypoint": "WP_SOUTH_SPINE"
        },
        {
            "id": "auditorium",
            "name": "Golden Jubilee Auditorium",
            "code": "AUDI-MAIN",
            "category": "EVENT",
            "type": "auditorium",
            "latitude": 11.0286,
            "longitude": 77.0283,
            "floor_count": 2,
            "capacity": 1500,
            "description": "Premier air-conditioned cultural auditorium, international conferences and graduation ceremonies.",
            "icon": "🎭",
            "is_verified": True,
            "status": "Ready for Events",
            "nearest_waypoint": "WP_AUDI_LANE"
        },
        {
            "id": "seminar_hall",
            "name": "Conference & Seminar Hall Complex",
            "code": "SEM-HALL",
            "category": "EVENT",
            "type": "seminar",
            "latitude": 11.0283,
            "longitude": 77.0278,
            "floor_count": 2,
            "capacity": 350,
            "description": "Acoustically treated multi-media seminar hall for guest lectures, workshops and symposiums.",
            "icon": "🎙️",
            "is_verified": False,
            "is_simulated": True,
            "status": "Workshop Scheduled (2 PM)",
            "nearest_waypoint": "WP_AUDI_LANE"
        },
        {
            "id": "parking_student",
            "name": "Main Gate Student Parking (Lot A)",
            "code": "PKG-STUDENT",
            "category": "PARKING",
            "type": "parking",
            "latitude": 11.0290,
            "longitude": 77.0261,
            "floor_count": 1,
            "capacity": 150,
            "description": "Covered two-wheeler and four-wheeler bays with ultrasonic spot sensor monitoring.",
            "icon": "🏍️",
            "is_verified": True,
            "status": "68% Occupied (Sensor Monitored)",
            "nearest_waypoint": "WP_WEST_PARK_LANE"
        },
        {
            "id": "parking_faculty",
            "name": "East Engineering Faculty Parking (Lot B)",
            "code": "PKG-FACULTY",
            "category": "PARKING",
            "type": "parking",
            "latitude": 11.0276,
            "longitude": 77.0288,
            "floor_count": 1,
            "capacity": 75,
            "description": "Designated faculty parking bays and dedicated EV charging stations.",
            "icon": "🚗",
            "is_verified": True,
            "status": "Available",
            "nearest_waypoint": "WP_EAST_AVENUE"
        },
        {
            "id": "parking_visitor",
            "name": "Auditorium Visitor Parking (Lot C)",
            "code": "PKG-VISITOR",
            "category": "PARKING",
            "type": "parking",
            "latitude": 11.0287,
            "longitude": 77.0288,
            "floor_count": 1,
            "capacity": 65,
            "description": "Visitor and dignitary parking zone directly adjacent to Golden Jubilee Auditorium.",
            "icon": "🅿️",
            "is_verified": True,
            "status": "Open",
            "nearest_waypoint": "WP_AUDI_LANE"
        },
        {
            "id": "transit_hub",
            "name": "CIT Hope College Transit Hub",
            "code": "TRANSIT-HUB",
            "category": "TRANSPORT",
            "type": "transit",
            "latitude": 11.0293,
            "longitude": 77.0271,
            "floor_count": 1,
            "capacity": 300,
            "description": "Central boarding bay on Avinashi Road for campus fleet (TN-38) connecting to Gandhipuram, Airport & Central Station.",
            "icon": "🚌",
            "is_verified": True,
            "status": "12 Buses Active",
            "nearest_waypoint": "WP_GATE"
        },
        {
            "id": "boys_hostel_1",
            "name": "Boys Hostel 1",
            "code": "BH-1",
            "category": "HOSTEL",
            "type": "boys_hostel",
            "hostel_type": "boys_hostel",
            "gender_category": "boys",
            "latitude": 11.0253,
            "longitude": 77.0268,
            "floor_count": 5,
            "capacity": 420,
            "description": "CIT Boys Residential Hostel Block 1 with Wi-Fi, RO water, common study halls, and 24/7 power backup.",
            "icon": "🏠",
            "is_verified": True,
            "status": "Active (Residents Only)",
            "nearest_waypoint": "WP_HOSTEL_JUNC",
            "facilities": ["High-Speed Wi-Fi", "RO Drinking Water", "Study Hall", "Power Backup", "Mess Access", "Security Desk"]
        },
        {
            "id": "boys_hostel_2",
            "name": "Boys Hostel 2",
            "code": "BH-2",
            "category": "HOSTEL",
            "type": "boys_hostel",
            "hostel_type": "boys_hostel",
            "gender_category": "boys",
            "latitude": 11.0248,
            "longitude": 77.0270,
            "floor_count": 4,
            "capacity": 380,
            "description": "CIT Boys Residential Hostel Block 2 featuring reading rooms, recreation area, and dining mess access.",
            "icon": "🏠",
            "is_verified": True,
            "status": "Active (Residents Only)",
            "nearest_waypoint": "WP_HOSTEL_JUNC",
            "facilities": ["Wi-Fi Campus LAN", "Recreation Area", "RO Water", "Laundry Area", "Mess Access", "CCTV Surveillance"]
        },
        {
            "id": "girls_hostel_1",
            "name": "Girls Hostel 1",
            "code": "GH-1",
            "category": "HOSTEL",
            "type": "girls_hostel",
            "hostel_type": "girls_hostel",
            "gender_category": "girls",
            "latitude": 11.0252,
            "longitude": 77.0280,
            "floor_count": 5,
            "capacity": 350,
            "description": "CIT Girls Residential Hostel Block 1 equipped with biometric access, study lounge, medical desk, and high-speed Wi-Fi.",
            "icon": "🏡",
            "is_verified": True,
            "status": "Active (Residents Only)",
            "nearest_waypoint": "WP_HOSTEL_JUNC",
            "facilities": ["Biometric Security", "High-Speed Wi-Fi", "Health Desk", "Reading Lounge", "RO Water", "24/7 Power"]
        },
        {
            "id": "girls_hostel_2",
            "name": "Girls Hostel 2",
            "code": "GH-2",
            "category": "HOSTEL",
            "type": "girls_hostel",
            "hostel_type": "girls_hostel",
            "gender_category": "girls",
            "latitude": 11.0247,
            "longitude": 77.0283,
            "floor_count": 4,
            "capacity": 320,
            "description": "CIT Girls Residential Hostel Block 2 with indoor badminton court, reading rooms, laundry stations, and CCTV surveillance.",
            "icon": "🏡",
            "is_verified": True,
            "status": "Active (Residents Only)",
            "nearest_waypoint": "WP_HOSTEL_JUNC",
            "facilities": ["Indoor Recreation", "Study Cubicles", "Wi-Fi Access", "Laundry Stations", "RO Drinking Water", "CCTV Security"]
        },
        {
            "id": "sports_ground",
            "name": "CIT Main Sports Ground & Track",
            "code": "SPORTS-GROUND",
            "category": "SPORTS",
            "type": "sports",
            "latitude": 11.0255,
            "longitude": 77.0294,
            "floor_count": 1,
            "capacity": 2500,
            "description": "Standard 400m athletic track, football pitch, cricket nets, and stadium pavilion.",
            "icon": "⚽",
            "is_verified": True,
            "status": "Green Zone",
            "nearest_waypoint": "WP_SPORTS_ROAD"
        },
        {
            "id": "sports_courts",
            "name": "Basketball, Volleyball & Tennis Courts",
            "code": "SPORTS-COURTS",
            "category": "SPORTS",
            "type": "sports",
            "latitude": 11.0262,
            "longitude": 77.0292,
            "floor_count": 1,
            "capacity": 400,
            "description": "Floodlit basketball, volleyball and synthetic tennis courts with sports equipment store.",
            "icon": "🏀",
            "is_verified": False,
            "is_simulated": True,
            "status": "Open",
            "nearest_waypoint": "WP_SPORTS_ROAD"
        },
        {
            "id": "lab_central",
            "name": "Central Computing & Electrical Labs",
            "code": "LAB-CENTRAL",
            "category": "LABORATORY",
            "type": "lab",
            "latitude": 11.0272,
            "longitude": 77.0269,
            "floor_count": 3,
            "capacity": 400,
            "description": "Inter-departmental computing labs, digital logic laboratories, and microprocessor training centers.",
            "icon": "🔬",
            "is_verified": False,
            "is_simulated": True,
            "status": "Practical Sessions",
            "nearest_waypoint": "WP_QUAD_CENTRE"
        },
        {
            "id": "innovation_hub",
            "name": "Innovation & Incubation Research Centre",
            "code": "INNOVATION-HUB",
            "category": "RESEARCH",
            "type": "research",
            "latitude": 11.0280,
            "longitude": 77.0275,
            "floor_count": 3,
            "capacity": 200,
            "description": "Student startup incubator, patent facilitation cell, prototype development labs, and 3D printing studio.",
            "icon": "💡",
            "is_verified": True,
            "status": "8 Active Startups",
            "nearest_waypoint": "WP_ADMIN_ROUND"
        },
        {
            "id": "workshop_mech",
            "name": "Mechanical & Production Workshops",
            "code": "WORKSHOP-MECH",
            "category": "FACILITIES",
            "type": "workshop",
            "latitude": 11.0264,
            "longitude": 77.0286,
            "floor_count": 2,
            "capacity": 300,
            "description": "Machine shop, foundry, welding bay, CNC machining centers and automotive teardown floor.",
            "icon": "🔧",
            "is_verified": True,
            "status": "Operational",
            "nearest_waypoint": "WP_EAST_AVENUE"
        },
        {
            "id": "health_centre",
            "name": "Campus Health & Medical Centre",
            "code": "HEALTH-CENTRE",
            "category": "FACILITIES",
            "type": "medical",
            "latitude": 11.0258,
            "longitude": 77.0264,
            "floor_count": 1,
            "capacity": 50,
            "description": "Resident campus physician, emergency first-aid beds, pharmacy, and 24/7 ambulance tie-up with KMCH.",
            "icon": "🏥",
            "is_verified": True,
            "status": "Duty Doctor Available",
            "nearest_waypoint": "WP_SOUTH_SPINE"
        },
        {
            "id": "security_post",
            "name": "Campus Security Post & Gate Office",
            "code": "SECURITY-POST",
            "category": "FACILITIES",
            "type": "security",
            "latitude": 11.0291,
            "longitude": 77.0266,
            "floor_count": 1,
            "capacity": 30,
            "description": "Central surveillance CCTV console, lost & found desk, visitor pass issuing and vehicle access gate.",
            "icon": "🛡️",
            "is_verified": True,
            "status": "Live CCTV Surveillance",
            "nearest_waypoint": "WP_GATE"
        }
    ],

    # Internal Road Network Edges (Waypoints Graph Connections)
    "internal_road_edges": [
        ("WP_GATE", "WP_ADMIN_ROUND"),
        ("WP_GATE", "WP_WEST_PARK_LANE"),
        ("WP_ADMIN_ROUND", "WP_QUAD_CENTRE"),
        ("WP_ADMIN_ROUND", "WP_AUDI_LANE"),
        ("WP_QUAD_CENTRE", "WP_EAST_AVENUE"),
        ("WP_QUAD_CENTRE", "WP_SOUTH_SPINE"),
        ("WP_AUDI_LANE", "WP_EAST_AVENUE"),
        ("WP_EAST_AVENUE", "WP_SPORTS_ROAD"),
        ("WP_SOUTH_SPINE", "WP_HOSTEL_JUNC"),
        ("WP_SOUTH_SPINE", "WP_SPORTS_ROAD"),
        ("WP_HOSTEL_JUNC", "WP_SPORTS_ROAD")
    ],

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
                {"name": "CIT Main Gate Terminal", "lat": 11.0292, "lng": 77.0268}
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
                {"name": "CIT Main Gate Terminal", "lat": 11.0292, "lng": 77.0268}
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
                {"name": "CIT Main Gate Terminal", "lat": 11.0292, "lng": 77.0268}
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
                {"name": "CIT Main Gate Terminal", "lat": 11.0292, "lng": 77.0268}
            ]
        }
    ]
}
