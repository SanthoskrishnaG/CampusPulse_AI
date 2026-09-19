// CampusPulse AI - Modern Light AI-Tech Interaction Engine

document.addEventListener('DOMContentLoaded', () => {
    initSimulationControls();
    init3DCardHoverEffects();
    initNumberCountUp();
});

// Simulation Speed Controller (1x, 2x, 5x, 10x)
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
                console.log("Simulation speed updated to:", speed, data);
            } catch (err) {
                console.error("Failed to update simulation speed:", err);
            }
        });
    });
}

// 3D Card Hover Tilt Micro-Interactions
function init3DCardHoverEffects() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    const cards = document.querySelectorAll('.module-card-3d, .kpi-card-light');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const deltaX = (x - centerX) / centerX;
            const deltaY = (y - centerY) / centerY;
            
            const rotateX = -deltaY * 3.5;
            const rotateY = deltaX * 3.5;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-3px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        });
    });
}

// Number Count-Up Animation
function initNumberCountUp() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    const values = document.querySelectorAll('.kpi-value');
    values.forEach(el => {
        const text = el.innerText.trim();
        const num = parseFloat(text.replace(/[^0-9.-]+/g, ""));
        if (!isNaN(num) && num > 0 && num < 100000 && !text.includes('%') && !text.includes('.')) {
            let start = 0;
            const end = num;
            const duration = 800;
            const stepTime = 20;
            const steps = duration / stepTime;
            const increment = end / steps;
            
            const timer = setInterval(() => {
                start += increment;
                if (start >= end) {
                    el.innerText = Math.round(end).toLocaleString();
                    clearInterval(timer);
                } else {
                    el.innerText = Math.round(start).toLocaleString();
                }
            }, stepTime);
        }
    });
}
