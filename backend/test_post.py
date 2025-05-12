import requests

url = "http://127.0.0.1:5000/jobs"

job_data = {
    "title": "Python Developer",
    "company": "NerdTech",
    "status": "Applied",
    "deadline": "2025-06-30"
}

response = requests.post(url,json=job_data)

print("Status code:", response.status_code)
print("Response JSON:", response.json())