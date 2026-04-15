document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Initialize Interactive Particles Background (if container exists)
    if (document.getElementById('particles-js')) {
        particlesJS("particles-js", {
            "particles": {
                "number": { "value": 80, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#0ea5e9" }, // Cyber Blue
                "shape": { "type": "circle" },
                "opacity": { "value": 0.5, "random": false },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#0ea5e9", "opacity": 0.4, "width": 1 },
                "move": { "enable": true, "speed": 2, "direction": "none", "random": false, "straight": false, "out_mode": "out", "bounce": false }
            },
            "interactivity": {
                "detect_on": "window",
                "events": { 
                    "onhover": { "enable": true, "mode": "grab" }, 
                    "onclick": { "enable": true, "mode": "push" }, 
                    "resize": true 
                },
                "modes": { 
                    "grab": { "distance": 140, "line_linked": { "opacity": 1 } }
                }
            },
            "retina_detect": true
        });
    }

    // 2. Global Toast Notification Function
    window.showToast = function(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'info-circle';
        if(type === 'success') icon = 'check-circle';
        if(type === 'error') icon = 'exclamation-circle';
        
        toast.innerHTML = `<i class="fa-solid fa-${icon}"></i> <span>${message}</span>`;
        container.appendChild(toast);
        
        // Slide in animation
        requestAnimationFrame(() => {
            setTimeout(() => toast.classList.add('show'), 10);
        });
        
        // Remove after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    };

    // 3. Centralized Async Form Handler (for Login and others)
    const asyncForms = document.querySelectorAll('.async-form');
    asyncForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const btn = form.querySelector('button[type="submit"]');
            if (btn) btn.classList.add('loading');
            
            // Gather JSON data
            const formData = new FormData(form);
            const dataObj = Object.fromEntries(formData.entries());
            
            try {
                const response = await fetch(form.action, {
                    method: form.method || 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dataObj)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast(result.message || 'Success!', 'success');
                    if (result.redirect) {
                        setTimeout(() => window.location.href = result.redirect, 1000);
                    }
                } else {
                    showToast(result.message || 'Error executing request.', 'error');
                    if (btn) btn.classList.remove('loading');
                }
            } catch (err) {
                console.error(err);
                showToast('Network error while executing request.', 'error');
                if (btn) btn.classList.remove('loading');
            }
        });
    });

    // 4. Real Docker Deployment Streaming Orchestrator
    const triggerBtn = document.getElementById('trigger-btn');
    if (triggerBtn) {
        triggerBtn.addEventListener('click', async () => {
            // UI Switch to Loading State
            triggerBtn.classList.add('loading');
            triggerBtn.disabled = true;
            
            const logsList = document.getElementById('logs-list');
            if (logsList) {
                logsList.innerHTML = `<li class="log-entry" style="color:var(--accent)"><i class="fa-solid fa-rocket"></i> Orchestrator pipeline initialized...</li>`;
            }
            
            showToast('Triggering Server Rebuild...', 'info');

            // Hit the trigger POST API
            try {
                const res = await fetch('/api/trigger', { method: 'POST' });
                const json = await res.json();
                
                if (!res.ok || !json.success) {
                    throw new Error(json.message || "Failed to trigger pipeline");
                }
                
                // If trigger was successful, open Server-Sent Events stream for LIVE bash logs
                const sse = new EventSource('/api/logs/stream');
                
                sse.onmessage = function(event) {
                    if (event.data === "[EOF]") {
                        // The stream is completely finished
                        sse.close();
                        triggerBtn.classList.remove('loading');
                        triggerBtn.disabled = false;
                        showToast('Deployment finished successfully!', 'success');
                        
                        if (logsList) {
                            logsList.innerHTML += `<li class="log-entry text-success"><i class="fa-solid fa-check"></i> [SYSTEM] Server is now running the latest origin/main containers.</li>`;
                            // Scroll to bottom
                            const terminalWindow = document.querySelector('.terminal-window');
                            terminalWindow.scrollTop = terminalWindow.scrollHeight;
                        }
                        return;
                    }

                    // Append real bash output line to the terminal
                    if (logsList) {
                        logsList.innerHTML += `<li class="log-entry"><span style="color:#d1d5db">> ${event.data}</span></li>`;
                        // Scroll to bottom dynamically
                        const terminalWindow = document.querySelector('.terminal-window');
                        terminalWindow.scrollTop = terminalWindow.scrollHeight;
                    }
                };

                sse.onerror = function() {
                    sse.close();
                    triggerBtn.classList.remove('loading');
                    triggerBtn.disabled = false;
                    showToast('Log stream connection dropped.', 'error');
                };

            } catch (err) {
                triggerBtn.classList.remove('loading');
                triggerBtn.disabled = false;
                showToast(err.message, 'error');
                if (logsList) {
                    logsList.innerHTML += `<li class="log-entry text-danger"><i class="fa-solid fa-triangle-exclamation"></i> [ERROR] ${err.message}</li>`;
                }
            }
        });
    }
});
