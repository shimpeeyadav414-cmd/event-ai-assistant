from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# --- Problem-Solution Database ---
ROLE_DATA = {
    "Manager": {
        "problems": [
            {"p": "Venue Overbooking", "s": "AI checks Google Calendar and suggests 3 alternative slots."},
            {"p": "Low Attendee Engagement", "s": "Gmail Automation triggers personalized invites to top 50 VIPs."},
            {"p": "Budget Leakage", "s": "Google Sheets logic flags expenses exceeding 15% of category limit."},
            {"p": "Vendor Delay", "s": "AI sends automated 'Urgent' follow-ups via Tasks integration."}
        ]
    },
    "Volunteer": {
        "problems": [
            {"p": "Job Confusion", "s": "Personalized Task list fetched from Google Tasks with priority tags."},
            {"p": "Lost at Venue", "s": "Indoor mapping via Google Maps API highlights assigned zone."},
            {"p": "Shift Overlap", "s": "AI reshuffles schedule to ensure 30-min break between tasks."},
            {"p": "Inventory Shortage", "s": "Quick-form update alerts Manager via Gmail instantly."}
        ]
    },
    "Attendee": {
        "problems": [
            {"p": "Traffic Delay", "s": "Maps API suggests fastest route and nearby parking in real-time."},
            {"p": "Missing Schedule", "s": "Digital itinerary synced to local Calendar with push alerts."},
            {"p": "Food Preference", "s": "AI filters stall locations based on pre-filled dietary tags."},
            {"p": "Networking Gap", "s": "AI suggests 3 people to meet based on shared LinkedIn interests."}
        ]
    },
    "Security": {
        "problems": [
            {"p": "Crowd Bottleneck", "s": "Heatmap logic identifies Gate 2 congestion; redirects to Gate 4."},
            {"p": "Unauthorized Entry", "s": "Instant alert sent to all Security Tasks with ID photo."},
            {"p": "Emergency Exit Block", "s": "Real-time verification request sent to nearest Volunteer."},
            {"p": "Lost & Found", "s": "AI logs item photo and notifies all Attendees via Gmail."}
        ]
    }
}

# --- Frontend with Visual Dashboard ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Visual Event AI Solver</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #eef2f7; margin: 0; }
        .nav { background: #1a73e8; color: white; padding: 1rem; text-align: center; font-weight: bold; }
        .container { max-width: 1000px; margin: 2rem auto; padding: 1rem; }
        .login-screen { text-align: center; background: white; padding: 3rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .role-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .card { background: white; padding: 1.5rem; border-radius: 10px; border-top: 5px solid #1a73e8; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .problem-tag { color: #d93025; font-weight: bold; font-size: 0.9rem; }
        .solution-tag { color: #188038; background: #e6f4ea; padding: 5px; border-radius: 4px; display: block; margin-top: 5px; }
        select, button { padding: 12px; width: 250px; border-radius: 6px; border: 1px solid #ddd; margin: 10px; }
        button { background: #1a73e8; color: white; border: none; cursor: pointer; font-weight: bold; }
        .btn-solve { width: 100%; margin-top: 10px; background: #34a853; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="nav">🚀 GOOGLE ANTIGRAVITY EVENT SOLVER</div>
    
    <div class="container">
        <div id="login" class="login-screen">
            <h1>Welcome to AI Control</h1>
            <p>Select your role to view 4 key solutions</p>
            <select id="roleSelect">
                <option value="Manager">Event Manager</option>
                <option value="Volunteer">Volunteer</option>
                <option value="Attendee">Attendee</option>
                <option value="Security">Security Team</option>
            </select><br>
            <button onclick="showDashboard()">Launch Visual Dashboard</button>
        </div>

        <div id="dashboard" class="hidden">
            <h2 id="roleTitle"></h2>
            <div id="cardsContainer" class="role-grid"></div>
            <button onclick="location.reload()" style="background:#5f6368; width:100%; margin-top:20px;">Back to Roles</button>
        </div>
    </div>

    <script>
        const data = """ + str(ROLE_DATA) + """;
        
        function showDashboard() {
            const role = document.getElementById('roleSelect').value;
            document.getElementById('login').classList.add('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
            document.getElementById('roleTitle').innerText = role + " Strategy Dashboard";
            
            let cardsHtml = "";
            data[role].problems.forEach(item => {
                cardsHtml += `
                    <div class="card">
                        <span class="problem-tag">🚩 PROBLEM:</span>
                        <div>${item.p}</div>
                        <span class="solution-tag">💡 AI SOLUTION:</span>
                        <div>${item.s}</div>
                        <button class="btn-solve" onclick="alert('Solution deployed via Google Antigravity Logic!')">Deploy Fix</button>
                    </div>
                `;
            });
            document.getElementById('cardsContainer').innerHTML = cardsHtml;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)