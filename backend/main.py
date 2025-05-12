from flask import Flask, jsonify, request

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
