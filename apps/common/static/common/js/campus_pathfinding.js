/**
 * A* Pathfinding Algorithm for CIT Campus Routes
 * Connects CampusNodes loaded from /api/campus-routing/
 */

function heuristic(nodeA, nodeB) {
    // Haversine distance heuristic
    const R = 6371e3; // metres
    const rL1 = nodeA.latitude * Math.PI/180;
    const rL2 = nodeB.latitude * Math.PI/180;
    const dL = (nodeB.latitude - nodeA.latitude) * Math.PI/180;
    const dLo = (nodeB.longitude - nodeA.longitude) * Math.PI/180;

    const a = Math.sin(dL/2) * Math.sin(dL/2) +
              Math.cos(rL1) * Math.cos(rL2) *
              Math.sin(dLo/2) * Math.sin(dLo/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function calculateCampusRoute(startNodeId, endNodeId) {
    if (!window.campusNodes || !window.campusEdges) {
        console.error("Campus graph not loaded yet.");
        return null;
    }
    
    // Simple mock return for now until full UI integration
    console.log(`Calculating A* route from ${startNodeId} to ${endNodeId}...`);
    return {
        path: [startNodeId, endNodeId],
        distance: 120,
        estimated_time: "2 mins"
    };
}
