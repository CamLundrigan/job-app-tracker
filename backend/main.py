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

                
                
                
            

    return jsonify({
        "message": "Job saved successfully!",
        "job": data
    }), 201





# GET route

@app.route("/jobs")
def get_jobs():
    # Read the optional “status” query parameter
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
                    deadline,
                FROM jobs;
                WHERE status = ?;
                    
                    """, requested_status)
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



    
@app.route("/ping")
def ping():
    print(" /ping route hit")
    return "pong", 200


# DEBUG: list all registered routes on startup
print("== Registered routes ==")
print(app.url_map)
print("========================")

if __name__ == "__main__":
    # this lets you run `python main.py` directly
    app.run(debug=True)
