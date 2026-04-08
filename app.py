from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "ai_architect_secret_key"

# --- Shared Data State ---
LIVE_EVENTS = []
TASKS = []
AI_LOGS = ["VenueOS AI: System initialized. Waiting for Architect inputs..."]

# --- UI Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VenueOS v4.0 | AI Architect</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --mgr: #1a73e8; --vol: #34a853; --sec: #ea4335; --atn: #fbbc05; --dark: #202124; }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f8f9fa; }
        
        .overlay { position: fixed; inset: 0; background: var(--dark); z-index: 2000; display: flex; align-items: center; justify-content: center; }
        .setup-card { background: white; padding: 40px; border-radius: 20px; width: 450px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); animation: slideUp 0.5s; }
        
        .nav { background: white; padding: 15px 30px; display: flex; justify-content: space-between; border-bottom: 2px solid #eee; }
        .char-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 50px; }
        .char-card { background: white; padding: 30px; border-radius: 20px; text-align: center; cursor: pointer; transition: 0.3s; }
        
        .dashboard { padding: 30px; display: none; max-width: 1200px; margin: auto; }
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); margin-bottom: 20px; }
        
        .ai-chat { background: #f1f3f4; border-radius: 10px; padding: 15px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 13px; }
        .btn { padding: 12px 25px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; color: white; transition: 0.2s; }
        
        input, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }
        .hidden { display: none !important; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    {% if not session.user %}
    <div class="overlay">
        <div class="setup-card">
            <h2 style="color:var(--mgr)"><i class="fas fa-robot"></i> Initialize Identity</h2>
            <form action="/login" method="POST">
                <input type="text" name="name" placeholder="Your Name" required>
                <input type="email" name="email" placeholder="Email" required>
                <button type="submit" class="btn" style="background:var(--mgr); width:100%">Access VenueOS</button>
            </form>
        </div>
    </div>
    {% endif %}

    {% if session.user %}
    <div class="nav">
        <h3>🏛️ VenueOS <span style="font-weight:100">AI Architect</span></h3>
        <div>Welcome, <b>{{session.user.name}}</b> | <a href="/logout">Exit</a></div>
    </div>

    <div id="selection-screen">
        <div class="char-grid">
            <div class="char-card" style="border-bottom: 8px solid var(--mgr)" onclick="openSetup('Manager')">
                <i class="fas fa-user-tie fa-4x" style="color: var(--mgr)"></i>
                <h3>Manager</h3>
                <p>Architect the Event</p>
            </div>
            <div class="char-card" style="border-bottom: 8px solid var(--vol)" onclick="openSetup('Volunteer')">
                <i class="fas fa-hands-helping fa-4x" style="color: var(--vol)"></i>
                <h3>Volunteer</h3>
                <p>Deploy Workforce</p>
            </div>
            <div class="char-card" style="border-bottom: 8px solid var(--sec)" onclick="openSetup('Security')">
                <i class="fas fa-shield-alt fa-4x" style="color: var(--sec)"></i>
                <h3>Security</h3>
                <p>Setup Surveillance</p>
            </div>
            <div class="char-card" style="border-bottom: 8px solid var(--atn)" onclick="openSetup('Attendee')">
                <i class="fas fa-ticket-alt fa-4x" style="color: var(--atn)"></i>
                <h3>Attendee</h3>
                <p>Join the Experience</p>
            </div>
        </div>
    </div>

    <div id="setup-container" class="overlay hidden">
        <div class="setup-card">
            <h2 id="setup-title">Setup</h2>
            <div id="setup-form-content"></div>
            <button class="btn" onclick="completeSetup()" style="background:var(--dark); width:100%; margin-top:10px;">Build Dashboard</button>
        </div>
    </div>

    <div id="main-dashboards">
        <button class="btn" onclick="goBack()" style="margin: 20px 50px; background:#ddd; color:black;"><i class="fas fa-arrow-left"></i> Selection</button>
        
        <div id="Manager-db" class="dashboard">
            <h1 style="color:var(--mgr)">👔 AI Event Strategy</h1>
            <div class="card" id="mgr-summary"></div>
            <div class="card">
                <h4>AI Simulation: Crowd Flow</h4>
                <canvas id="mgrChart"></canvas>
            </div>
        </div>

        <div id="Volunteer-db" class="dashboard">
            <h1 style="color:var(--vol)">🛠️ Workforce Grid</h1>
            <div class="card" id="vol-summary"></div>
            <div class="card">
                <h4>Smart Task List (Auto-Generated)</h4>
                <div id="task-list"></div>
            </div>
        </div>

        <div id="Security-db" class="dashboard">
            <h1 style="color:var(--sec)">🛡️ Sentinel View</h1>
            <div class="card" id="sec-summary"></div>
            <div class="card" style="background:var(--dark); color:#0f0; padding:20px; font-family:monospace;">
                >> BOOTING SURVEILLANCE...<br>
                >> SCANNING ZONES...<br>
                >> <span id="sec-status">ACTIVE</span>
            </div>
        </div>

        <div id="Attendee-db" class="dashboard">
            <h1 style="color:var(--atn)">🎟️ Live Experience</h1>
            <div class="card">
                <h4><i class="fas fa-robot"></i> Ask Venue AI</h4>
                <div class="ai-chat" id="ai-messages">
                    {% for log in logs %}<p>{{log}}</p>{% endfor %}
                </div>
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <input type="text" id="ai-input" placeholder="Ask about events, food, or exits...">
                    <button class="btn" style="background:var(--atn)" onclick="askAI()">Send</button>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        let currentRole = "";
        let setupData = {};

        function openSetup(role) {
            currentRole = role;
            if(role === 'Attendee') { showDashboard(); return; }
            
            const content = document.getElementById('setup-form-content');
            let formHtml = "";
            
            if(role === 'Manager') {
                formHtml = `
                    <input type="text" id="event_name" placeholder="Event Name (e.g. TechFest 2026)">
                    <input type="number" id="capacity" placeholder="Expected Crowd Size">
                    <select id="event_type"><option>Conference</option><option>Music Fest</option><option>Workshop</option></select>
                `;
            } else if(role === 'Volunteer') {
                formHtml = `
                    <input type="number" id="v_count" placeholder="Number of Volunteers">
                    <select id="v_dept"><option>Logistics</option><option>Technical</option><option>Hospitality</option></select>
                `;
            } else if(role === 'Security') {
                formHtml = `
                    <input type="number" id="zones" placeholder="Number of Zones to Monitor">
                    <select id="risk_level"><option>Low Risk</option><option>Medium Risk</option><option>High Alert</option></select>
                `;
            }
            
            content.innerHTML = formHtml;
            document.getElementById('setup-title').innerText = "Architect " + role;
            document.getElementById('setup-container').classList.remove('hidden');
        }

        function completeSetup() {
            document.getElementById('setup-container').classList.add('hidden');
            document.getElementById('selection-screen').classList.add('hidden');
            showDashboard();
        }

        function showDashboard() {
            document.querySelectorAll('.dashboard').forEach(d => d.style.display = 'none');
            const db = document.getElementById(currentRole + '-db');
            db.style.display = 'block';

            if(currentRole === 'Manager') {
                const name = document.getElementById('event_name').value || "Unnamed Event";
                const cap = document.getElementById('capacity').value || "0";
                document.getElementById('mgr-summary').innerHTML = `<h3>Event: ${name}</h3><p>AI Goal: Optimize for ${cap} attendees.</p>`;
                new Chart(document.getElementById('mgrChart'), {
                    type: 'bar',
                    data: { labels: ['Gate A', 'Hall 1', 'Food Court'], datasets: [{label: 'Predicted Density', data: [30, 80, 50], backgroundColor: '#1a73e8'}] }
                });
            }
            
            if(currentRole === 'Volunteer') {
                const dept = document.getElementById('v_dept').value;
                document.getElementById('vol-summary').innerHTML = `<h3>Department: ${dept}</h3>`;
                document.getElementById('task-list').innerHTML = `<ul><li>Setup ${dept} counters</li><li>Brief Staff</li><li>Sync Comm Channels</li></ul>`;
            }

            if(currentRole === 'Security') {
                const risk = document.getElementById('risk_level').value;
                document.getElementById('sec-summary').innerHTML = `<h3>Risk Status: ${risk}</h3>`;
                document.getElementById('sec-status').innerText = risk === 'High Alert' ? 'CRITICAL SCANNING' : 'NORMAL MONITORING';
            }
        }

        function askAI() {
            const input = document.getElementById('ai-input');
            const chat = document.getElementById('ai-messages');
            if(!input.value) return;

            chat.innerHTML += `<p style="color:var(--mgr)"><b>You:</b> ${input.value}</p>`;
            
            // AI Logic Simulation
            let response = "I'm analyzing your request...";
            if(input.value.toLowerCase().includes('food')) response = "AI: Food court is in Hall C. Current wait time: 5 mins.";
            else if(input.value.toLowerCase().includes('event')) response = "AI: The main Keynote starts at 14:00 in the Grand Ballroom.";
            else response = "AI: System is optimized. No issues detected in your vicinity.";

            setTimeout(() => {
                chat.innerHTML += `<p style="color:var(--vol)"><b>Venue AI:</b> ${response}</p>`;
                chat.scrollTop = chat.scrollHeight;
            }, 800);
            input.value = "";
        }

        function goBack() {
            document.getElementById('selection-screen').classList.remove('hidden');
            document.querySelectorAll('.dashboard').forEach(d => d.style.display = 'none');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, logs=AI_LOGS)

@app.route('/login', methods=['POST'])
def login():
    session['user'] = {"name": request.form.get('name')}
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)