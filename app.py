from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- Live Data ---
LIVE_EVENTS = [
    {"name": "Keynote: AI Future", "status": "LIVE", "time": "14:00 - 15:30", "color": "#d93025"},
    {"name": "Workshop: Cloud Sync", "status": "UPCOMING", "time": "16:00 - 17:30", "color": "#f4b400"},
    {"name": "Inauguration Ceremony", "status": "ENDED", "time": "10:00 - 11:30", "color": "#34a853"}
]

# --- UI with Chief Guest, Login, and Role Graphics ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Grand Event Command Center</title>
    <style>
        :root { --g-blue: #1a73e8; --g-red: #ea4335; --g-green: #34a853; --g-yellow: #fbbc05; }
        body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; margin: 0; }
        
        /* Login Overlay */
        #login-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 1000; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px); }
        .login-card { background: white; padding: 40px; border-radius: 20px; text-align: center; width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        .header { background: white; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        
        /* Chief Guest Section */
        .chief-guest-box { background: linear-gradient(135deg, #1a73e8, #0d47a1); color: white; border-radius: 15px; padding: 25px; display: flex; align-items: center; gap: 20px; margin-bottom: 30px; position: relative; overflow: hidden; }
        .guest-img { width: 100px; height: 100px; border-radius: 50%; border: 4px solid white; object-fit: cover; background: #eee; }
        .live-dot { position: absolute; top: 15px; right: 15px; background: #ff5252; padding: 5px 15px; border-radius: 20px; font-size: 12px; animation: blink 1.5s infinite; }
        
        /* Dashboard Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        
        /* Task Solver */
        .btn-solve { width: 100%; padding: 12px; margin-top: 10px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; background: var(--g-blue); color: white; transition: 0.3s; }
        .visual-result { display: none; margin-top: 15px; padding: 15px; background: #f0f7ff; border-radius: 8px; border-left: 5px solid var(--g-blue); }
        .venue-pic { width: 100%; height: 150px; border-radius: 8px; margin-top: 10px; background: url('https://picsum.photos/seed/venue/400/200') center/cover; }
        
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
    </style>
</head>
<body>

    <div id="login-overlay">
        <div class="login-card">
            <h1 style="color: var(--g-blue)">Welcome to Prompt Wars</h1>
            <p>Select your authorized role to enter venue dashboard</p>
            <select id="userRole" style="width: 100%; padding: 12px; margin-bottom: 20px; border-radius: 8px; border: 1px solid #ddd;">
                <option value="Manager">Event Manager</option>
                <option value="Attendee">Attendee</option>
                <option value="Volunteer">Volunteer</option>
                <option value="Security">Security Personnel</option>
            </select>
            <button onclick="enterDashboard()" class="btn-solve">Enter Command Center</button>
        </div>
    </div>

    <div class="header">
        <h2 style="margin:0; color: var(--g-blue);">🏛️ SMART VENUE CONTROL</h2>
    </div>

    <div class="container">
        <div class="chief-guest-box">
            <div class="live-dot">● CHIEF GUEST ARRIVED</div>
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Chief Guest" class="guest-img">
            <div>
                <h2 style="margin: 0;">Prof. Alan Turing Jr.</h2>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Global Lead, AI Ethics & Robotics | Delivering Keynote</p>
            </div>
        </div>

        <h3>📢 Live Venue Feed</h3>
        <div class="grid" style="margin-bottom: 30px;">
            {% for e in events %}
            <div class="card" style="border-top: 5px solid {{e.color}}">
                <span style="background:{{e.color}}; color:white; padding:2px 8px; border-radius:5px; font-size:10px;">{{e.status}}</span>
                <h4 style="margin:10px 0 5px 0">{{e.name}}</h4>
                <small>{{e.time}}</small>
            </div>
            {% endfor %}
        </div>

        <h3 id="roleHeading">🛠️ AI Assistant Tools</h3>
        <div id="solver-container" class="grid"></div>
    </div>

    <script>
        const tasks = {
            Manager: [
                { p: "VIP Late Arrival Logic", s: "Reschedule Keynote & Notify VIP", data: "AI rescheduled Calendar by 15 mins. Notifications sent via Gmail." },
                { p: "Food Court Congestion", s: "Reroute with Discount Coupons", data: "Sending 10% off vouchers to Stall 3 to clear Stall 1 crowd." },
                { p: "Resource Analytics", s: "Predict Resource Depletion", data: "Warning: Water bottles will finish in 40 mins. Ordering more via Task Bot." }
            ],
            Attendee: [
                { p: "Where is the Chief Guest?", s: "Track Guest Location", data: "Guest is currently at Hall A, Stage 1. [See Photo Below]" },
                { p: "Available Charging Stations", s: "Check Socket Status", data: "3 Sockets free at Lounge Area (Level 2)." },
                { p: "Washroom Empty Map", s: "Show Nearest Facility", data: "Main Hall East washrooms are clear. [See Interior Preview]" }
            ],
            Volunteer: [
                { p: "Entry Gate Overload", s: "Activate Backup Scanning", data: "Open Gate 4. Diverting 50% traffic via Maps logic." },
                { p: "Water Supply Hall B", s: "Dispatch Supply Bot", data: "Volunteer Team 2 notified. Water crates arriving in 5 mins." }
            ],
            Security: [
                { p: "Unauthorized Area Access", s: "Seal Sector 4", data: "Digital locks engaged for Sector 4. Security team 1 dispatched." },
                { p: "Emergency Medical Kit", s: "Locate Nearest First-Aid", data: "Kit found at Reception Desk. Quickest path marked on device." }
            ]
        };

        function enterDashboard() {
            const role = document.getElementById('userRole').value;
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('roleHeading').innerText = "🛠️ " + role + " Control Panel";
            renderTasks(role);
        }

        function renderTasks(role) {
            let html = "";
            tasks[role].forEach((item, idx) => {
                html += `
                <div class="card">
                    <h4 style="color:var(--g-red)">🚩 ${item.p}</h4>
                    <button class="btn-solve" onclick="showSolution(${idx})">${item.s}</button>
                    <div id="sol-${idx}" class="visual-display">
                        <div class="visual-result">
                            <strong>System Logic:</strong> ${item.data}
                            <div class="venue-pic" style="background-image: url('https://picsum.photos/seed/${role}${idx}/400/200')"></div>
                        </div>
                    </div>
                </div>`;
            });
            document.getElementById('solver-container').innerHTML = html;
        }

        function showSolution(id) {
            let el = document.getElementById('sol-' + id).children[0];
            el.parentElement.style.display = (el.parentElement.style.display === 'block') ? 'none' : 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, events=LIVE_EVENTS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)