from flask import Flask, jsonify, request, render_template
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
    #  Read the search term (“query”) from the URL 
    # If no ?query=… is provided, default to "data scientist".
    query = request.args.get("query", "data scientist")

    #  Read the “page” from the URL 
    # If no ?page=… is provided, default to the integer 1.
    # We’ll parse it as an int and then force it to be at least 1.
    raw_page = request.args.get("page", "1")  # This is a string, e.g. "2"
    try:
        page = int(raw_page)  # Convert it to an integer
    except ValueError:
        # If someone passed ?page=abc (not a number), we fallback to 1
        page = 1

    # Now ensure page is at least 1. If page is 0 or negative, set page = 1.
    if page < 1:
        page = 1

    #  Build the JSearch request parameters 
    # We only want exactly one page (num_pages = "1").
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {
        "query":     query,
        "page":      str(page),   # Convert back to string because JSearch expects strings
        "num_pages": "1"
    }

    #  Provide JSearch with our RapidAPI key and host 
    headers = {
        "X-RapidAPI-Key":  "1f98f4ce5emshdef3c3943476506p128946jsn71c63",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    #  Call JSearch (make an HTTP GET)
    response = requests.get(url, headers=headers, params=querystring)

    # If JSearch returns 200 OK, process the result 
    if response.status_code == 200:
        payload = response.json()
        results = payload.get("data", [])  # This is an array of ~10 job dicts

        # “Clean” each job to include only the fields we need
        cleaned = []
        for job in results:
            cleaned.append({
                "title":      job.get("job_title"),
                "company":    job.get("employer_name"),
                "location":   job.get("job_city"),
                "posted":     job.get("job_posted_at_datetime_utc"),
                "apply_link": job.get("job_apply_link")
            })

        # Return exactly one page of results, plus metadata 
        return jsonify({
            "query": query,
            "page":  page,
            "count": len(cleaned),  # Usually ≈10, but could be fewer on the last page
            "jobs":  cleaned
        }), 200

    #  If JSearch fails, forward an error 
    return jsonify({"error": "Failed to fetch jobs from JSearch"}), response.status_code

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
    
    return "pong", 200


# DEBUG: list all registered routes on startup
print("== Registered routes ==")
print(app.url_map)
print("========================")






if __name__ == "__main__":
   
    app.run(debug=True)
