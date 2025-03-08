from flask import Flask, request, jsonify, render_template
import sqlite3
import time

# Initialize Flask app
app = Flask(__name__)

# Create database
conn = sqlite3.connect("ig_tracker.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS following (
        username TEXT,
        timestamp TEXT
    )
""")
conn.commit()

# Home route (serves the frontend)
@app.route('/')
def home():
    return render_template('index.html')  # Ensure index.html exists in the root

# Store a new IG username
@app.route("/track", methods=["POST"])
def track_user():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "No username provided"}), 400

    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO following VALUES (?, ?)", (username, timestamp))
    conn.commit()

    return jsonify({"message": f"Tracking started for {username}!"})

# Retrieve following list
@app.route("/following")
def get_following():
    cursor.execute("SELECT * FROM following")
    data = cursor.fetchall()
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
