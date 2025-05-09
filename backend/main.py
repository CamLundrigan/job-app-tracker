from flask import Flask, jsonify

app= Flask(__name__)

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