document.addEventListener('DOMContentLoaded', () => {

    // 1. Initial State Fetching
    updateSystemStatus();
    
    // Poll every 5 seconds
    setInterval(updateSystemStatus, 5000);

    // 2. Terminal Logic (if on dashboard)
    const terminal = document.getElementById('terminal-output');
    const triggerBtn = document.getElementById('trigger-btn');

    if (terminal) {
        addLogLine('System initialized. Awaiting CI/CD events...', 'info');
    }

    if (triggerBtn) {
        triggerBtn.addEventListener('click', async () => {
            triggerBtn.disabled = true;
            triggerBtn.textContent = 'Deploying...';
            
            if(terminal) terminal.innerHTML = '';
            addLogLine('Triggering manual deployment webhook...', 'info');
            
            try {
                const res = await fetch('/api/trigger', { method: 'POST' });
                const data = await res.json();
                
                if (data.status === 'success') {
                    simulateBuildLogs();
                } else {
                    addLogLine('Error triggering pipeline!', 'error');
                    triggerBtn.disabled = false;
                    triggerBtn.textContent = 'Deploy Now';
                }
            } catch (e) {
                addLogLine('Network error triggering pipeline!', 'error');
                triggerBtn.disabled = false;
                triggerBtn.textContent = 'Deploy Now';
            }
        });
    }

    // --- Helper Functions ---

    async function updateSystemStatus() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            
            const statusVal = document.getElementById('status-val');
            const deployVal = document.getElementById('deploy-count-val');
            
            if (statusVal) statusVal.textContent = data.status === 'ok' ? 'Online' : 'Degraded';
            if (deployVal) deployVal.textContent = data.total_deployments;
            
        } catch (e) {
            console.error('Failed to fetch status');
        }
    }

    function addLogLine(text, level='info') {
        if (!terminal) return;
        const line = document.createElement('div');
        line.className = 'log-line';
        
        const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" });
        let colorClass = 'log-info';
        if (level === 'success') colorClass = 'log-success';
        if (level === 'warn') colorClass = 'log-warn';
        
        line.innerHTML = `<span class="log-time">[${time}]</span> <span class="${colorClass}">${text}</span>`;
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }

    function simulateBuildLogs() {
        const logs = [
            { t: "Cloning repository...", l: "info" },
            { t: "Resolving dependencies via pip...", l: "info" },
            { t: "Requirement already satisfied: flask in /usr/local/lib/python3.11/site-packages", l: "info" },
            { t: "Running pytest unit tests...", l: "info" },
            { t: "test_app.py::test_homepage PASSED", l: "success" },
            { t: "test_app.py::test_health_api PASSED", l: "success" },
            { t: "Building Docker image 'ttl-demo:latest'...", l: "info" },
            { t: "Successfully built image df6a782b1c", l: "success" },
            { t: "Restarting Gunicorn web server...", l: "warn" },
            { t: "Deployment successful. Traffic fully routed.", l: "success" }
        ];

        let index = 0;
        function showNextLog() {
            if (index < logs.length) {
                addLogLine(logs[index].t, logs[index].l);
                index++;
                // Random delay between 400ms and 1500ms
                setTimeout(showNextLog, Math.floor(Math.random() * 1100) + 400);
            } else {
                updateSystemStatus(); // update deploy count
                triggerBtn.disabled = false;
                triggerBtn.textContent = 'Deploy Now';
            }
        }
        
        setTimeout(showNextLog, 600);
    }
});
