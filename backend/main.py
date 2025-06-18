from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

from flask import Flask, jsonify, request, render_template
import requests
import sqlite3
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY, SECRET_KEY

# ── Adzuna credentials moved to config.py ───────────────────────────────

app = Flask(__name__)

app.secret_key = SECRET_KEY



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

cur.execute("""
        CREATE TABLE IF NOT EXITS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
            
            
            );
            """)
conn.commit()
cur.close()
conn.close()

@app.route("/")
def home():
#home page shows our index.html file
    return render_template("index.html")


#POST Route
@app.route("/save-job", methods=["POST"])
def save_job():
    print(" /save-job route hit")
    data = request.get_json()
    print("Received data:", data)

    if not data:
        return jsonify({"error": "No job data provided"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # 1) Write your SQL with ? placeholders
    sql = """
    INSERT INTO jobs (title, company, location, apply_link, status, deadline)
    VALUES (?, ?, ?, ?, ?, ?)
"""

# 2) Prepare a tuple (or list) of values in the same order
    params = (
    data.get("title"),
    data.get("company"),
    data.get("location"),
    data.get("apply_link"),
    data.get("status", "Saved"),
    data.get("deadline")
)

# 3) Execute, passing both SQL and params
    cur.execute(sql, params)

    conn.commit()
    cur.close()
    conn.close()      
                
                
            

    return jsonify({
        "message": "Job saved successfully!",
        "job": data
    }), 201





# GET route

@app.route("/jobs")
def get_jobs():
    # Read the optional "status" query parameter
    requested_status = request.args.get("status")
    #  Open a new database connection
    conn = get_db_connection()

    #  Create a cursor for executing SQL
    cur = conn.cursor()
    
    # If the frontend provided ?status=…, only select those rows:
    if requested_status:
        cur.execute("""
                SELECT
                    id,
                    title,
                    company,
                    location,
                    apply_link,
                    status,
                    deadline
                FROM jobs
                WHERE status = ?;
                    
                    """, (requested_status,))
    #Otherwise return all jobs
    else:
     #  Execute a SELECT to fetch all columns from all rows
        cur.execute("""
            SELECT
                id,
                title,
                company,
                location,
                apply_link,
                status,
                deadline
            FROM jobs;
    """)

    #  Fetch all result rows into a list
    rows = cur.fetchall()

    # Clean up: close cursor and connection
    cur.close()
    conn.close()

    #  Transform sqlite3.Row objects into plain dicts
    jobs_list = []
    for row in rows:
        jobs_list.append({
            "id":        row["id"],
            "title":     row["title"],
            "company":   row["company"],
            "location":  row["location"],
            "apply_link":row["apply_link"],
            "status":    row["status"],
            "deadline":  row["deadline"],
        })

    # Return the list of jobs as JSON
    return jsonify(jobs_list)


    

#  POST route
@app.route("/jobs", methods=["POST"])
def add_job():
    data = request.get_json()
    return jsonify({
        "message": "Job received!",
        "job": data
    }), 201


@app.route("/live-jobs")
def get_live_jobs():
    # 1) Read the "query" and "page" parameters
    query = request.args.get("query", "").strip() or "data scientist"
    raw_page = request.args.get("page", "1")
    try:
        page = max(1, int(raw_page))
    except ValueError:
        page = 1

    # 2) Build the Adzuna URL and parameters
    url = f"https://api.adzuna.com/v1/api/jobs/ca/search/{page}"
    params = {
        "app_id":           ADZUNA_APP_ID,    # your Application ID
        "app_key":          ADZUNA_APP_KEY,   # your Application Key
        "what":             query,            # the search term
        "results_per_page": 10,               # limit to 10 results
        "sort_by":          "date"            # most recent first
    }

    # 3) Fetch from Adzuna
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return jsonify({"error": f"Adzuna error: {resp.status_code}"}), resp.status_code

    # 4) Parse the JSON and extract the "results" list
    data    = resp.json()
    results = data.get("results", [])

    # 5) Clean each result down to the fields we need
    cleaned = []
    for job in results:
        cleaned.append({
            "title":      job.get("title"),
            "company":    job.get("company", {}).get("display_name"),
            "location":   (job.get("location", {}).get("area") or [""])[-1],
            "posted":     job.get("created"),
            "apply_link": job.get("redirect_url")
        })

    # 6) Return exactly those 10 jobs
    return jsonify({
        "query": query,
        "page":  page,
        "count": len(cleaned),
        "jobs":  cleaned
    }), 200


@app.route("/jobs/<int:id>", methods=["DELETE"])
def delete_job(id):

    conn = get_db_connection()

    cur = conn.cursor()
    
    cur.execute("DELETE FROM jobs WHERE id = ?", (id,))

    if cur.rowcount ==0:
        cur.close()
        conn.close()
        return jsonify({"Error": "No existing job to delete" }),404

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Job {id} deleted"}), 200


@app.route("/jobs/<int:id>", methods=["PUT"])
def update_status(id):

    data = request.get_json()
    if not data or "status" not in data:
        return jsonify({" Error": "No Status provided or job not found"}),404
    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute("UPDATE jobs SET status= ? WHERE id= ?", (data["status"],id))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": f"Job {id} status updated to '{data['status']}'"}), 200


@app.route("/saved")
def saved_page():
    return render_template("saved.html")

    
@app.route("/ping")
def ping():
    
    return "pong", 200


# DEBUG: list all registered routes on startup
print("== Registered routes ==")
print(app.url_map)
print("========================")






if __name__ == "__main__":
   
    app.run(debug=True)
