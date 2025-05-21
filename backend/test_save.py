import requests

url = "http://127.0.0.1:5000/save-job"

job = {
    "title": "Python Developer",
    "company": "OpenAI",
    "location": "Remote",
    "apply_link": "https://openai.com/careers/python-dev"
}

try:
    response = requests.post(url, json=job)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("⚠️ ERROR:", e)
