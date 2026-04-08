from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- Live Venue Data ---
LIVE_EVENTS = [
    {"name": "Keynote: AI Future", "status": "LIVE", "time": "14:00 - 15:30", "color": "#d93025"},
    {"name": "Workshop: Cloud Sync", "status": "UPCOMING", "time": "16:00 - 17:30", "color": "#f4b400"},
    {"name": "Inauguration Ceremony", "status": "ENDED", "time": "10:00 - 11:30", "color": "#34a853"}
]

# --- Frontend with Graphics & Interactive Maps ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Venue Command Center</title>
    <style>
        :root { --google-blue: #1a73e8; --google-red: #ea4335; --google-green: #34a853; --google-yellow: #fbbc05; }
        body { font-family: 'Segoe UI', sans-serif; background: #f1f3f4; margin: 0; padding-bottom: 50px; }
        .nav { background: white; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .container { max-width: 1100px; margin: 20px auto; padding: 0 15px; }
        
        /* Common Dashboard */
        .live-board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px; }
        .event-card { background: white; padding: 15px; border-radius: 8px; border-left: 8px solid; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .status-badge { font-size: 10px; padding: 3px 8px; border-radius: 10px; color: white; font-weight: bold; }

        /* Role Selection */
        .role-nav { display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; padding: 10px 0; }
        .role-btn { padding: 10px 20px; border: none; border-radius: 20px; background: white; cursor: pointer; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .role-btn.active { background: var(--google-blue); color: white; }

        /* Problem Solving Area */
        .solution-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .problem-card { background: white; padding: 20px; border-radius: 12px; position: relative; overflow: hidden; }
        .problem-card h4 { margin: 0 0 10px 0; color: var(--google-red); }
        
        /* Interactive Visuals */
        .visual-display { display: none; margin-top: 15px; padding: 15px; background: #f8f9fa; border: 1px dashed #ccc; border-radius: 8px; animation: fadeIn 0.5s; }
        .map-box { width: 100%; height: 100px; background: #e8eaed; display: flex; align-items: center; justify-content: center; position: relative; }
        .seat { width: 20px; height: 20px; margin: 2px; display: inline-block; border-radius: 3px; }
        
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>
    <div class="nav">
        <span style="color: var(--google-blue)">● SMART VENUE LIVE</span>
        <button onclick="location.reload()" style="background: none; border: 1px solid #ccc; border-radius: 4px; padding: 5px 10px;">Refresh Feed</button>
    </div>

    <div class="container">
        <h3>📢 Live Event Notifications</h3>
        <div class="live-board">
            {% for event in events %}
            <div class="event-card" style="border-color: {{event.color}}">
                <span class="status-badge" style="background: {{event.color}}">{{event.status}}</span>
                <h4 style="margin: 10px 0 5px 0;">{{event.name}}</h4>
                <small>{{event.time}}</small>
            </div>
            {% endfor %}
        </div>

        <hr>

        <h3>🛠️ On-Site Problem Solver</h3>
        <div class="role-nav">
            <button class="role-btn active" onclick="setRole('Attendee', this)">Attendee</button>
            <button class="role-btn" onclick="setRole('Volunteer', this)">Volunteer</button>
            <button class="role-btn" onclick="setRole('Security', this)">Security</button>
            <button class="role-btn" onclick="setRole('Manager', this)">Manager</button>
        </div>

        <div id="solver-container" class="solution-grid"></div>
    </div>

    <script>
        const problems = {
            Attendee: [
                { p: "Where is the nearest Washroom?", s: "View Washroom Map", type: "map", data: "Floor 1, North Wing (2 min walk)" },
                { p: "Is the Main Hall full?", s: "Check Empty Seats", type: "seats", data: "14 Empty Seats in Row H" },
                { p: "How to reach Cafeteria?", s: "Navigate Venue", type: "map", data: "Direct Path: Exit Hall, Turn Right" }
            ],
            Volunteer: [
                { p: "Water Shortage at Hall B", s: "Alert Supply Team", type: "alert", data: "Water truck dispatched to Hall B" },
                { p: "Crowd at Entry Gate", s: "View Gate Heatmap", type: "map", data: "Red Zone: Gate 1 | Clear: Gate 3" }
            ],
            Security: [
                { p: "Suspect Package Found", s: "Isolate & Alert", type: "alert", data: "Protocol A-1 activated. Area isolated." },
                { p: "VIP Arrival Route", s: "Clear Path 7", type: "map", data: "Clearance Level: Green" }
            ]
        };

        function setRole(role, btn) {
            document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderProblems(role);
        }

        function renderProblems(role) {
            let html = "";
            (problems[role] || []).forEach((item, index) => {
                html += `
                <div class="problem-card">
                    <h4>🚩 ${item.p}</h4>
                    <button onclick="showSolution(${index})" style="width:100%; background:var(--google-blue); color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">${item.s}</button>
                    <div id="sol-${index}" class="visual-display">
                        <strong>Action:</strong> ${item.data}<br><br>
                        ${renderGraphic(item.type)}
                    </div>
                </div>`;
            });
            document.getElementById('solver-container').innerHTML = html;
        }

        function renderGraphic(type) {
            if(type === 'map') return '<div class="map-box">🗺️ [VENUE MAP VIEW: NORTH WING]</div>';
            if(type === 'seats') return '<div style="text-align:center;">' + '<div class="seat" style="background:#ccc"></div>'.repeat(10) + '<br><div class="seat" style="background:var(--google-green)"></div>'.repeat(5) + '</div>';
            return '<div style="color:var(--google-red); font-weight:bold;">⚠️ DISPATCHING AI BOT...</div>';
        }

        function showSolution(index) {
            document.querySelectorAll('.visual-display').forEach(d => d.style.display = 'none');
            document.getElementById('sol-' + index).style.display = 'block';
        }

        // Initial load
        renderProblems('Attendee');
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