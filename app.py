from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)

# Mock logic for integrations
def add_calendar_event(name, date):
    return f"📅 Event '{name}' scheduled for {date}."

def send_gmail_invite(email):
    return f"📩 Invite sent to {email}."

# HTML Template (Directly inside Python for simplicity)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Event AI Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; background: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input { padding: 10px; width: 80%; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #4285f4; color: white; border: none; border-radius: 5px; cursor: pointer; }
        #result { margin-top: 20px; font-weight: bold; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🤖 Smart Event AI</h1>
        <p>Manage your events with Google Antigravity Logic</p>
        
        <input type="text" id="eventName" placeholder="Event Name (e.g. Birthday Party)">
        <input type="date" id="eventDate">
        <button onclick="scheduleEvent()">Schedule Event</button>
        <br><br>
        <input type="email" id="email" placeholder="Attendee Email">
        <button onclick="sendInvite()" style="background: #db4437;">Send Invite</button>
        
        <div id="result"></div>
    </div>

    <script>
        async function scheduleEvent() {
            const name = document.getElementById('eventName').value;
            const date = document.getElementById('eventDate').value;
            const res = await fetch(`/api/schedule?name=${name}&date=${date}`);
            const data = await res.json();
            document.getElementById('result').innerText = data.message;
        }

        async function sendInvite() {
            const email = document.getElementById('email').value;
            const res = await fetch(`/api/invite?email=${email}`);
            const data = await res.json();
            document.getElementById('result').innerText = data.message;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/schedule')
def schedule():
    name = request.args.get('name', 'General Meeting')
    date = request.args.get('date', 'Today')
    return jsonify({"message": add_calendar_event(name, date)})

@app.route('/api/invite')
def invite():
    email = request.args.get('email', 'guest@example.com')
    return jsonify({"message": send_gmail_invite(email)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)