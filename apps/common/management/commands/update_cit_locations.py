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

        # 1. Update CampusLocation records
        self.stdout.write("1. Updating Campus Geographic Landmarks to CIT...")
        landmarks = CAMPUS_CONFIG['landmarks']
        
        # Mapping existing seeded codes to CIT landmarks
        code_map = {
            "BLK-A": "cse_block",
            "BLK-B": "ai_lab",
            "BLK-C": "mech_civil_eee",
            "LAB-AI": "ai_lab",
            "AUD-MAIN": "auditorium",
            "CAN-MAIN": "canteen",
            "PKG-NORTH": "parking_north",
            "PKG-EAST": "parking_east",
            "STOP-GATE1": "bus_terminal",
            "LIB-HUB": "library",
        }

        updated_locs = 0
        for code, lmark_key in code_map.items():
            info = landmarks.get(lmark_key)
            if not info:
                continue
            loc = CampusLocation.objects.filter(code=code).first()
            if loc:
                loc.name = info['name']
                loc.latitude = info['latitude']
                loc.longitude = info['longitude']
                loc.description = info.get('description', '')
                loc.save()
                updated_locs += 1

        # Also add any new landmarks if not present (Admin block, Sports, Hostel)
        for key in ["admin_block", "hostel", "sports", "parking_south"]:
            info = landmarks[key]
            CampusLocation.objects.update_or_create(
                code=info['code'],
                defaults={
                    'name': info['name'],
                    'category': info['category'],
                    'latitude': info['latitude'],
                    'longitude': info['longitude'],
                    'description': info.get('description', ''),
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f"   [OK] CampusLocation records updated to CIT campus ({updated_locs} updated)."))

        # 2. Update ParkingLot coordinates
        self.stdout.write("2. Updating Smart Parking Lots to CIT...")
        parking_coords = {
            "PKG-NORTH": (landmarks['parking_north']['latitude'], landmarks['parking_north']['longitude']),
            "PKG-EAST": (landmarks['parking_east']['latitude'], landmarks['parking_east']['longitude']),
            "PKG-AUDI": (landmarks['parking_south']['latitude'], landmarks['parking_south']['longitude']),
        }
        for code, (lat, lng) in parking_coords.items():
            lot = ParkingLot.objects.filter(code=code).first()
            if lot:
                lot.latitude = lat
                lot.longitude = lng
                lot.save()

        self.stdout.write(self.style.SUCCESS("   [OK] ParkingLot coordinates updated to CIT bays."))

        # 3. Update Transport Routes, Stops, and Vehicle Registration Plates
        self.stdout.write("3. Updating Bus Routes to Coimbatore corridors & TN-38 plates...")
        routes_config = CAMPUS_CONFIG['bus_routes']

        for r_data in routes_config:
            route = BusRoute.objects.filter(code=r_data['code']).first()
            if route:
                route.name = r_data['name']
                route.start_point = r_data['start']
                route.end_point = r_data['end']
                route.distance_km = r_data['distance_km']
                route.estimated_duration_mins = r_data['duration_mins']
                route.save()
            else:
                route = BusRoute.objects.create(
                    code=r_data['code'],
                    name=r_data['name'],
                    start_point=r_data['start'],
                    end_point=r_data['end'],
                    distance_km=r_data['distance_km'],
                    estimated_duration_mins=r_data['duration_mins']
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
