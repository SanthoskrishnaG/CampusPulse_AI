"""
Management command to update existing database location records to
Coimbatore Institute of Technology (CIT), Coimbatore in-place.
Preserves all students, faculty, events, complaints, and ML models.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from config.campus_config import CAMPUS_CONFIG
from apps.common.models import CampusLocation, WeatherCache
from apps.parking.models import ParkingLot
from apps.transport.models import BusRoute, BusStop, Bus

class Command(BaseCommand):
    help = "Update existing database records to Coimbatore Institute of Technology (CIT) coordinates and routes"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Updating CampusPulse AI Locations to CIT (Coimbatore) ==="))

        # 1. Update/Create all 27 CampusLocation records from CAMPUS_CONFIG['locations']
        self.stdout.write("1. Synchronizing 27 CIT Campus Buildings & Facilities...")
        locations = CAMPUS_CONFIG.get('locations', [])

        # Legacy seed code mapping to smooth in-place update
        legacy_code_map = {
            "BLK-A": "DEPT-CSE",
            "BLK-B": "CENTRE-AI",
            "BLK-C": "DEPT-ECE",
            "LAB-AI": "LAB-CENTRAL",
            "AUD-MAIN": "AUDI-MAIN",
            "CAN-MAIN": "CAN-MAIN",
            "PKG-NORTH": "PKG-STUDENT",
            "PKG-EAST": "PKG-FACULTY",
            "STOP-GATE1": "TRANSIT-HUB",
            "LIB-HUB": "LIB-CENTRAL",
        }

        # First update any matching legacy locations
        for old_code, new_code in legacy_code_map.items():
            loc_data = next((l for l in locations if l['code'] == new_code), None)
            if loc_data:
                CampusLocation.objects.filter(code=old_code).update(
                    code=new_code,
                    name=loc_data['name'],
                    category=loc_data['category'],
                    latitude=loc_data['latitude'],
                    longitude=loc_data['longitude'],
                    floor_count=loc_data.get('floor_count', 1),
                    capacity=loc_data.get('capacity', 100),
                    description=loc_data.get('description', ''),
                    is_active=True
                )

        # Now update_or_create all 27 locations
        synced_count = 0
        for loc in locations:
            CampusLocation.objects.update_or_create(
                code=loc['code'],
                defaults={
                    'name': loc['name'],
                    'category': loc['category'],
                    'latitude': loc['latitude'],
                    'longitude': loc['longitude'],
                    'floor_count': loc.get('floor_count', 1),
                    'capacity': loc.get('capacity', 100),
                    'description': loc.get('description', ''),
                    'is_active': True
                }
            )
            synced_count += 1

        self.stdout.write(self.style.SUCCESS(f"   [OK] {synced_count} CampusLocation records synchronized to CIT."))

        # 2. Update ParkingLot coordinates to designated CIT bays
        self.stdout.write("2. Updating Smart Parking Lots to CIT...")
        parking_lots_data = [
            ("PKG-STUDENT", "Main Gate Student Parking (Lot A)", 11.0290, 77.0261, 150),
            ("PKG-FACULTY", "East Engineering Faculty Parking (Lot B)", 11.0276, 77.0288, 75),
            ("PKG-VISITOR", "Auditorium Visitor Parking (Lot C)", 11.0287, 77.0288, 65),
        ]

        # Rename / update existing lots if they had old codes
        old_parking_map = {"PKG-NORTH": "PKG-STUDENT", "PKG-EAST": "PKG-FACULTY", "PKG-AUDI": "PKG-VISITOR"}
        for old_c, new_c in old_parking_map.items():
            ParkingLot.objects.filter(code=old_c).update(code=new_c)

        for code, name, lat, lng, slots in parking_lots_data:
            ParkingLot.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'latitude': lat,
                    'longitude': lng,
                    'total_slots': slots,
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS("   [OK] ParkingLot coordinates updated to CIT bays."))

        # 3. Update Transport Routes, Stops, and Vehicle Registration Plates
        self.stdout.write("3. Updating Bus Routes to Coimbatore corridors & TN-38 plates...")
        routes_config = CAMPUS_CONFIG['bus_routes']

        for r_data in routes_config:
            route, _ = BusRoute.objects.update_or_create(
                code=r_data['code'],
                defaults={
                    'name': r_data['name'],
                    'start_point': r_data['start'],
                    'end_point': r_data['end'],
                    'distance_km': r_data['distance_km'],
                    'estimated_duration_mins': r_data['duration_mins'],
                    'is_active': True
                }
            )

            # Update / recreate stops
            BusStop.objects.filter(route=route).delete()
            for seq, s in enumerate(r_data['stops'], start=1):
                BusStop.objects.create(
                    route=route,
                    sequence=seq,
                    name=s['name'],
                    latitude=s['lat'],
                    longitude=s['lng'],
                    estimated_offset_mins=seq * 5
                )

        # Update bus numbers from KA-01 to TN-38-CIT
        buses = Bus.objects.all()
        for idx, b in enumerate(buses, start=1):
            rcode = b.route.code[2:] if b.route else "01"
            b.bus_number = f"TN-38-CIT-{rcode}{idx:02d}"
            b.save()

        self.stdout.write(self.style.SUCCESS(f"   [OK] {len(routes_config)} Routes and {buses.count()} Buses updated with TN-38-CIT plates."))

        # 4. Clear Weather Cache to force immediate Coimbatore weather fetch
        WeatherCache.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("   [OK] WeatherCache reset for live Coimbatore Open-Meteo polling."))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] CampusPulse AI successfully mapped to Coimbatore Institute of Technology (CIT)!"))
