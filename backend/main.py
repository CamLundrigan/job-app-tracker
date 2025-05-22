from flask import Flask, jsonify, request
import requests
import sqlite3

app = Flask(__name__)

def get_db_connection():
    #create or open jobs.db
    conn = sqlite3.connect('jobs.db')

    conn.row_factory = sqlite3.Row

    return conn

conn = sqlite3.connect('jobs.db')
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        apply_link TEXT,
        status TEXT DEFAULT 'Saved',
        deadline TEXT
    );
""")
conn.commit()
cur.close()
conn.close()



jobs = [
        {
            "id": 1,
            "title": "Data Analyst",
            "company": "TechCorp",
            "status": "Applied",
            "deadline": "2025-05-10"
        },
        {
            "id": 2,
            "title": "Business Analyst",
            "company": "BizGroup",
            "status": "Interviewing",
            "deadline": "2025-05-15"
        }
    ]
#POST Route
@app.route("/save-job", methods=["POST"])
def save_job():
    print("✅ /save-job route hit")
    data = request.get_json()
    print("Received data:", data)

    if not data:
        return jsonify({"error": "No job data provided"}), 400

    new_id = max([job["id"] for job in jobs], default=0) + 1
    data["id"] = new_id

    if "status" not in data:
        data["status"] = "Saved"

    jobs.append(data)

    return jsonify({
        "message": "Job saved successfully!",
        "job": data
    }), 201





# GET route
@app.route("/jobs")
def get_jobs():
    return jsonify(jobs)

#  POST route
@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()
    return jsonify({
        "message": "Job received!",
        "job": data
    }), 201

@app.route("/live-jobs")  # Define a new route
def get_live_jobs():
    url = "https://jsearch.p.rapidapi.com/search"  # API endpoint

    query = request.args.get("query", "data analyst in Canada")

    querystring = {  # Search terms
        "query": query,
        "page": "1",
        "num_pages": "1"
    }

    headers = {  # Auth + host info for the API
        "X-RapidAPI-Key": "1f98f4ce5emshdef3c3943476506p128946jsn71c315b17f63",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)  # Make the request

    if response.status_code == 200:
        results = response.json().get("data",[])

        cleaned = []
        for job in results:
            cleaned.append({
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_city"),
            "posted": job.get("job_posted_at_datetime_utc"),
            "apply_link": job.get("job_apply_link")
        })

        return jsonify(cleaned), 200
    
    else:
        return jsonify({"error": "Failed to fetch jobs"}), response.status_code
    
@app.route("/ping")
def ping():
    print("✅ /ping route hit")
    return "pong", 200

if __name__ == "__main__":
    # this lets you run `python main.py` directly
    app.run(debug=True)
