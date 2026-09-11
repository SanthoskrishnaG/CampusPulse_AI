// CampusPulse AI - Real-Time Dashboard & Simulation Controller

document.addEventListener('DOMContentLoaded', () => {
    initSimulationControls();
});

function initSimulationControls() {
    const speedButtons = document.querySelectorAll('.sim-btn[data-speed]');
    speedButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const speed = parseFloat(btn.getAttribute('data-speed'));
            speedButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            try {
                const resp = await fetch('/api/simulation-control/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'set_speed', speed: speed })
                });
                const data = await resp.json();
                console.log("Simulation updated:", data);
            } catch (err) {
                console.error("Failed to update simulation speed:", err);
            }
        });
    });
}
