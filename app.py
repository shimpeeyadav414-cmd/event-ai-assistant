from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "google_antigravity_secret"

# --- Database Simulation ---
LIVE_EVENTS = [
    {"id": 1, "name": "AI Keynote", "status": "LIVE", "time": "14:00", "color": "#d93025"},
    {"id": 2, "name": "Dev Workshop", "status": "UPCOMING", "time": "16:00", "color": "#fbbc05"},
]
TASKS = [
    {"id": 1, "task": "Stage Mic Check", "status": "Pending", "pts": 50},
    {"id": 2, "task": "VIP Escort", "status": "Pending", "pts": 100},
]
FEEDBACKS = [{"msg": "Great event!", "sentiment": "Positive"}]

# --- UI Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VenueOS v3.0 | Enterprise AI</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root { --mgr: #1a73e8; --vol: #34a853; --sec: #ea4335; --atn: #fbbc05; --dark: #202124; }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f1f3f4; overflow-x: hidden; }
        
        /* Glassmorphism Login */
        .overlay { position: fixed; inset: 0; background: var(--dark); z-index: 2000; display: flex; align-items: center; justify-content: center; }
        .login-card { background: white; padding: 40px; border-radius: 20px; width: 350px; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        
        /* Profile Header */
        .profile-bar { background: white; padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ddd; }
        .user-chip { background: #e8f0fe; padding: 5px 15px; border-radius: 20px; font-weight: bold; color: var(--mgr); }

        /* Character Selection */
        .char-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 50px; }
        .char-card { background: white; padding: 30px; border-radius: 20px; text-align: center; cursor: pointer; transition: 0.3s; border-bottom: 8px solid #ccc; }
        .char-card:hover { transform: translateY(-10px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); }

        /* Role Dashboards */
        .dashboard { padding: 30px; max-width: 1200px; margin: auto; display: none; animation: fadeIn 0.5s; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
        
        .btn { padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer; font-weight: bold; color: white; margin: 5px 0; }
        .mgr-bg { background: var(--mgr); } .vol-bg { background: var(--vol); } 
        .sec-bg { background: var(--sec); } .atn-bg { background: var(--atn); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    {% if not session.user %}
    <div class="overlay">
        <div class="login-card">
            <h2 style="color: var(--mgr)"><i class="fas fa-microchip"></i> VenueOS Login</h2>
            <form action="/login" method="POST">
                <input type="text" name="name" placeholder="Full Name" required style="width:100%; padding:10px; margin:10px 0; border-radius:8px; border:1px solid #ddd;">
                <input type="email" name="email" placeholder="Email Address" required style="width:100%; padding:10px; margin:10px 0; border-radius:8px; border:1px solid #ddd;">
                <input type="number" name="age" placeholder="Age" required style="width:100%; padding:10px; margin:10px 0; border-radius:8px; border:1px solid #ddd;">
                <button type="submit" class="btn mgr-bg" style="width:100%">Access System</button>
            </form>
        </div>
    </div>
    {% endif %}

    {% if session.user %}
    <div class="profile-bar">
        <h3>🏛️ VenueOS v3.0</h3>
        <div class="user-chip">
            <i class="fas fa-user-circle"></i> {{session.user.name}} ({{session.user.age}})
            <a href="/logout" style="margin-left:10px; color:var(--sec); text-decoration:none;"><i class="fas fa-sign-out-alt"></i></a>
        </div>
    </div>

    <div id="selection-screen">
        <h2 style="text-align:center; margin-top:40px;">Choose Your Role</h2>
        <div class="char-grid">
            <div class="char-card" style="border-color: var(--mgr)" onclick="openRole('Manager')">
                <i class="fas fa-user-tie fa-4x" style="color: var(--mgr)"></i>
                <h3>Manager</h3>
                <p>Full Control & AI Insights</p>
            </div>
            <div class="char-card" style="border-color: var(--vol)" onclick="openRole('Volunteer')">
                <i class="fas fa-hands-helping fa-4x" style="color: var(--vol)"></i>
                <h3>Volunteer</h3>
                <p>Tasks & Rewards</p>
            </div>
            <div class="char-card" style="border-color: var(--sec)" onclick="openRole('Security')">
                <i class="fas fa-shield-alt fa-4x" style="color: var(--sec)"></i>
                <h3>Security</h3>
                <p>Safety & Heatmaps</p>
            </div>
            <div class="char-card" style="border-color: var(--atn)" onclick="openRole('Attendee')">
                <i class="fas fa-ticket-alt fa-4x" style="color: var(--atn)"></i>
                <h3>Attendee</h3>
                <p>Schedule & Feedback</p>
            </div>
        </div>
    </div>

    <div id="role-container">
        <button class="btn mgr-bg" onclick="goBack()" style="margin: 20px 50px;"><i class="fas fa-arrow-left"></i> Back to Selection</button>
        
        <div id="Manager-db" class="dashboard role-view">
            <h1 style="color:var(--mgr)">👔 Manager Command Center</h1>
            <div class="grid">
                <div class="card">
                    <h4>Add Event</h4>
                    <form action="/add_event" method="POST">
                        <input type="text" name="name" placeholder="Event Name" style="width:90%; padding:8px; margin-bottom:10px;">
                        <button class="btn mgr-bg" style="width:100%">Create Event</button>
                    </form>
                </div>
                <div class="card">
                    <h4>AI Crowd Prediction</h4>
                    <canvas id="crowdChart"></canvas>
                </div>
            </div>
        </div>

        <div id="Volunteer-db" class="dashboard role-view">
            <h1 style="color:var(--vol)">🛠️ Staff Workspace</h1>
            <div class="grid">
                <div class="card">
                    <h4>Your Points: <span style="color:var(--vol)">450 XP</span></h4>
                    <div style="height:10px; background:#eee; border-radius:5px;"><div style="width:70%; height:100%; background:var(--vol); border-radius:5px;"></div></div>
                </div>
                <div class="card">
                    <h4>Active Tasks</h4>
                    {% for t in tasks %}
                    <div style="border-bottom:1px solid #eee; padding:10px 0; display:flex; justify-content:space-between;">
                        <span>{{t.task}}</span>
                        <button class="btn vol-bg" style="font-size:10px;">Done (+{{t.pts}})</button>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div id="Security-db" class="dashboard role-view">
            <h1 style="color:var(--sec)">🛡️ Security Grid</h1>
            <div class="card" style="text-align:center; background:#ffebee;">
                <h3 style="color:var(--sec)"><i class="fas fa-exclamation-triangle pulse"></i> ALERT: UNUSUAL CROWD AT GATE 2</h3>
            </div>
            <div class="card" style="margin-top:20px; height:300px; background: url('https://upload.wikimedia.org/wikipedia/commons/9/9a/Sample_Floorplan.jpg') center/cover;">
                <div style="width:50px; height:50px; background:rgba(234,67,53,0.6); border-radius:50%; margin:100px; border:2px solid red;"></div>
            </div>
        </div>

        <div id="Attendee-db" class="dashboard role-view">
            <h1 style="color:var(--atn)">🎟️ Attendee Experience</h1>
            <div class="grid">
                <div class="card">
                    <h4>Live Feedback</h4>
                    <canvas id="sentimentChart"></canvas>
                </div>
                <div class="card">
                    <h4>AI Suggestions</h4>
                    <p><i class="fas fa-coffee"></i> Free Coffee at Hall B - Low Crowd Now!</p>
                    <p><i class="fas fa-star"></i> Recommended: AI Ethics Keynote at 16:00</p>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <script>
        function openRole(role) {
            document.getElementById('selection-screen').classList.add('hidden');
            document.getElementById('role-container').classList.remove('hidden');
            document.querySelectorAll('.role-view').forEach(v => v.style.display = 'none');
            document.getElementById(role + '-db').style.display = 'block';
            if(role === 'Manager') initManagerChart();
            if(role === 'Attendee') initSentimentChart();
        }

        function goBack() {
            document.getElementById('selection-screen').classList.remove('hidden');
            document.getElementById('role-container').classList.add('hidden');
        }

        function initManagerChart() {
            new Chart(document.getElementById('crowdChart'), {
                type: 'line',
                data: {
                    labels: ['10am', '12pm', '2pm', '4pm', '6pm'],
                    datasets: [{ label: 'Crowd %', data: [20, 45, 85, 60, 30], borderColor: '#1a73e8', tension: 0.4 }]
                }
            });
        }

        function initSentimentChart() {
            new Chart(document.getElementById('sentimentChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Happy', 'Neutral', 'Sad'],
                    datasets: [{ data: [70, 20, 10], backgroundColor: ['#34a853', '#fbbc05', '#ea4335'] }]
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, tasks=TASKS, events=LIVE_EVENTS)

@app.route('/login', methods=['POST'])
def login():
    session['user'] = {
        "name": request.form.get('name'),
        "email": request.form.get('email'),
        "age": request.form.get('age')
    }
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/add_event', methods=['POST'])
def add_event():
    name = request.form.get('name')
    LIVE_EVENTS.append({"id": len(LIVE_EVENTS)+1, "name": name, "status": "UPCOMING", "time": "TBD", "color": "#1a73e8"})
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)