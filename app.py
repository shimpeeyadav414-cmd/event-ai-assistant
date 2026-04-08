from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os

app = Flask(__name__)

# --- State Management (Database Simulation) ---
LIVE_EVENTS = [
    {"id": 1, "name": "Keynote: AI Future", "status": "LIVE", "time": "14:00", "color": "#d93025"},
    {"id": 2, "name": "Workshop: Cloud Sync", "status": "UPCOMING", "time": "16:00", "color": "#f4b400"},
]
VOLUNTEER_TASKS = [
    {"id": 1, "task": "Check Hall A Mic", "assigned_to": "Rahul", "status": "Pending"},
    {"id": 2, "task": "Water for VIPs", "assigned_to": "Anjali", "status": "Done"},
]
ALERTS = ["Crowd density high at Gate 1", "Speaker arrived at VIP Lounge"]

# --- Logic Functions ---
def get_ai_prediction():
    return "AI Predicts 85% Crowd at Hall A in 20 mins. Recommendation: Open Hall B for buffer."

# --- Frontend with All New Modules ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Venue OS - Enterprise Edition</title>
    <style>
        :root { --blue: #1a73e8; --red: #ea4335; --green: #34a853; --dark: #202124; }
        body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        
        /* Layout */
        .nav { background: white; padding: 15px 30px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center; }
        .main-content { display: flex; flex: 1; overflow: hidden; }
        .sidebar { width: 250px; background: white; border-right: 1px solid #ddd; padding: 20px; }
        .dashboard { flex: 1; padding: 30px; overflow-y: auto; }

        /* Role-Specific Cards */
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px; border-top: 5px solid var(--blue); }
        .btn { padding: 8px 15px; border-radius: 6px; border: none; cursor: pointer; font-weight: bold; transition: 0.2s; }
        .btn-edit { background: #e8f0fe; color: var(--blue); }
        .btn-delete { background: #fce8e6; color: var(--red); }
        
        /* Interactive Elements */
        .heat-map { height: 150px; background: linear-gradient(90deg, #34a853, #fbbc05, #ea4335); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
        .hidden { display: none; }
        .badge { font-size: 11px; padding: 3px 8px; border-radius: 10px; color: white; }
    </style>
</head>
<body>

    <div id="login-overlay" style="position:fixed; inset:0; background:rgba(0,0,0,0.9); z-index:1000; display:flex; align-items:center; justify-content:center;">
        <div style="background:white; padding:40px; border-radius:15px; text-align:center; width:350px;">
            <h2>🔐 Secure Access</h2>
            <select id="userRole" style="width:100%; padding:10px; margin:20px 0;">
                <option value="Manager">Manager</option>
                <option value="Volunteer">Volunteer</option>
                <option value="Security">Security</option>
                <option value="Attendee">Attendee</option>
            </select>
            <button onclick="startOS()" style="width:100%; padding:10px; background:var(--blue); color:white; border:none; border-radius:5px;">Launch Dashboard</button>
        </div>
    </div>

    <div class="nav">
        <h3>🏛️ VenueOS - v2.0</h3>
        <div id="role-tag" class="badge" style="background:var(--blue)">Role: Undefined</div>
    </div>

    <div class="main-content">
        <div class="sidebar">
            <h4>Live Alerts</h4>
            <ul id="alert-list" style="font-size:13px; color:var(--red); padding-left:15px;">
                {% for a in alerts %}<li>{{a}}</li>{% endfor %}
            </ul>
            <hr>
            <h4>AI Insights</h4>
            <p style="font-size:12px; color:var(--green)">{{ai_prediction}}</p>
        </div>

        <div class="dashboard">
            <section id="manager-panel" class="role-section hidden">
                <h2>Admin Control</h2>
                <div class="card" style="background:#e8f0fe">
                    <h4>Add/Edit Event</h4>
                    <form action="/manage_event" method="POST">
                        <input type="hidden" name="action" value="add">
                        <input type="text" name="name" placeholder="Event Name" required style="padding:10px; margin:5px;">
                        <input type="text" name="time" placeholder="Time" required style="padding:10px; margin:5px;">
                        <button type="submit" class="btn" style="background:var(--blue); color:white">Submit</button>
                    </form>
                </div>
            </section>

            <h2>Live Itinerary</h2>
            <div class="grid" id="event-grid" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:20px;">
                {% for e in events %}
                <div class="card">
                    <div style="display:flex; justify-content:space-between">
                        <span class="badge" style="background:{{e.color}}">{{e.status}}</span>
                        <div class="mgr-only hidden">
                            <a href="/delete_event/{{e.id}}" class="btn btn-delete" style="text-decoration:none">Delete</a>
                        </div>
                    </div>
                    <h4>{{e.name}}</h4>
                    <p>🕒 {{e.time}}</p>
                </div>
                {% endfor %}
            </div>

            <section id="volunteer-panel" class="role-section hidden">
                <h2>Staff Tasks</h2>
                <div class="card">
                    {% for t in tasks %}
                    <div style="padding:10px; border-bottom:1px solid #eee">
                        <b>{{t.task}}</b> - Assigned to: {{t.assigned_to}} (<i>{{t.status}}</i>)
                    </div>
                    {% endfor %}
                </div>
            </section>

            <section id="security-panel" class="role-section hidden">
                <h2>Security Heatmap</h2>
                <div class="heat-map">GATE 1 - CONGESTION: 85%</div>
            </section>
        </div>
    </div>

    <script>
        function startOS() {
            const role = document.getElementById('userRole').value;
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('role-tag').innerText = "Role: " + role;

            // Role-Specific UI Logic
            document.querySelectorAll('.role-section').forEach(s => s.classList.add('hidden'));
            if(role === 'Manager') {
                document.getElementById('manager-panel').classList.remove('hidden');
                document.querySelectorAll('.mgr-only').forEach(m => m.classList.remove('hidden'));
            } else if(role === 'Volunteer') {
                document.getElementById('volunteer-panel').classList.remove('hidden');
            } else if(role === 'Security') {
                document.getElementById('security-panel').classList.remove('hidden');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    prediction = get_ai_prediction()
    return render_template_string(HTML_TEMPLATE, 
                                 events=LIVE_EVENTS, 
                                 tasks=VOLUNTEER_TASKS, 
                                 alerts=ALERTS,
                                 ai_prediction=prediction)

@app.route('/manage_event', methods=['POST'])
def manage_event():
    name = request.form.get('name')
    time = request.form.get('time')
    new_id = len(LIVE_EVENTS) + 1
    LIVE_EVENTS.append({"id": new_id, "name": name, "status": "UPCOMING", "time": time, "color": "#1a73e8"})
    return redirect(url_for('home'))

@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    global LIVE_EVENTS
    LIVE_EVENTS = [e for e in LIVE_EVENTS if e['id'] != event_id]
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)