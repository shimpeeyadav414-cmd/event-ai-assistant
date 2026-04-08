from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Event AI Assistant is Live!"

if __name__ == "__main__":
    # Render sets the PORT environment variable automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)