from flask import Flask, jsonify, request
import requests
app = Flask(__name__)

# GET route
@app.route("/jobs")
def get_jobs():
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
        return jsonify(response.json()), 200  # Send results to the browser
    else:
        return jsonify({"error": "Failed to fetch jobs"}), response.status_code