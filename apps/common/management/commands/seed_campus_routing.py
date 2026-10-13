import math
from django.core.management.base import BaseCommand
from config.campus_config import CAMPUS_CONFIG
from apps.common.models import CampusNode, CampusEdge

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

class Command(BaseCommand):
    help = "Seeds comprehensive CampusNode and CampusEdge pedestrian pathways for CIT"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing CIT Campus Routing Graph Seeding..."))

        # 1. Clear existing edges and nodes to ensure clean graph
        CampusEdge.objects.all().delete()
        CampusNode.objects.all().delete()

        created_nodes = {}

        # 2. Seed Waypoints
        waypoints = CAMPUS_CONFIG.get("waypoints", {})
        for wp_id, coords in waypoints.items():
            lat, lng = coords[0], coords[1]
            node = CampusNode.objects.create(
                node_id=wp_id,
                latitude=lat,
                longitude=lng,
                node_type="junction"
            )
            created_nodes[wp_id] = node
        self.stdout.write(f"  [+] Created {len(waypoints)} waypoint junction nodes.")

        # 3. Seed Location / Facility Nodes
        locations = CAMPUS_CONFIG.get("locations", [])
        for loc in locations:
            loc_id = f"LOC_{loc['code'].replace('-', '_').upper()}"
            node = CampusNode.objects.create(
                node_id=loc_id,
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                node_type=loc.get("type", "building")
            )
            created_nodes[loc_id] = node
        self.stdout.write(f"  [+] Created {len(locations)} building/facility nodes.")

        edges_to_create = []

        def add_bidirectional_edge(from_id, to_id, path_type="Walkway", is_accessible=True):
            if from_id not in created_nodes or to_id not in created_nodes:
                return
            node_a = created_nodes[from_id]
            node_b = created_nodes[to_id]
            dist = max(5.0, haversine_distance_meters(node_a.latitude, node_a.longitude, node_b.latitude, node_b.longitude))
            # Walking speed: 1.2 m/s
            est_seconds = max(10, int(dist / 1.2))

            edges_to_create.append(CampusEdge(
                from_node=node_a,
                to_node=node_b,
                distance=dist,
                path_type=path_type,
                is_accessible=is_accessible,
                estimated_time=est_seconds
            ))
            edges_to_create.append(CampusEdge(
                from_node=node_b,
                to_node=node_a,
                distance=dist,
                path_type=path_type,
                is_accessible=is_accessible,
                estimated_time=est_seconds
            ))

        # 4. Connect Waypoint Graph Edges
        road_edges = CAMPUS_CONFIG.get("internal_road_edges", [])
        for edge in road_edges:
            wp_from, wp_to = edge[0], edge[1]
            add_bidirectional_edge(wp_from, wp_to, path_type="Main Walkway / Road", is_accessible=True)
        self.stdout.write(f"  [+] Connected {len(road_edges)} internal waypoint corridors.")

        # 5. Connect Each Building to its Nearest Waypoint
        for loc in locations:
            loc_id = f"LOC_{loc['code'].replace('-', '_').upper()}"
            nearest_wp = loc.get("nearest_waypoint")
            if nearest_wp and nearest_wp in created_nodes:
                add_bidirectional_edge(loc_id, nearest_wp, path_type="Paved Corridor", is_accessible=True)

        # 6. Interconnect nearby key buildings directly for intuitive walking
        direct_pairs = [
            ("LOC_GATE_MAIN", "LOC_SECURITY_POST"),
            ("LOC_GATE_MAIN", "LOC_TRANSIT_HUB"),
            ("LOC_ADMIN_BLK", "LOC_LIB_CENTRAL"),
            ("LOC_ACAD_1", "LOC_ACAD_2"),
            ("LOC_DEPT_CSE", "LOC_CENTRE_AI"),
            ("LOC_DEPT_CSE", "LOC_DEPT_IT"),
            ("LOC_DEPT_ECE", "LOC_DEPT_EEE"),
            ("LOC_DEPT_MECH", "LOC_WORKSHOP_MECH"),
            ("LOC_CAN_MAIN", "LOC_HOSTEL_DINING"),
            ("LOC_HOSTEL_BOYS_1", "LOC_HOSTEL_BOYS_2"),
            ("LOC_HOSTEL_GIRLS_1", "LOC_HOSTEL_GIRLS_2"),
            ("LOC_HOSTEL_BOYS_1", "LOC_HOSTEL_DINING"),
            ("LOC_HOSTEL_GIRLS_1", "LOC_HOSTEL_DINING"),
            ("LOC_SPORTS_COMPLEX", "LOC_GROUND_MAIN"),
            ("LOC_SPORTS_COMPLEX", "LOC_COURTS_TENNIS"),
            ("LOC_AUDI_MAIN", "LOC_AUDI_OPENAIR"),
        ]

        for b1, b2 in direct_pairs:
            add_bidirectional_edge(b1, b2, path_type="Pedestrian Walkway", is_accessible=True)

        CampusEdge.objects.bulk_create(edges_to_create)

        node_count = CampusNode.objects.count()
        edge_count = CampusEdge.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f"\n[SUCCESS] CIT Campus Pedestrian Graph seeded successfully!\n"
            f"          Total Nodes: {node_count}\n"
            f"          Total Edges: {edge_count} (bidirectional)\n"
        ))
