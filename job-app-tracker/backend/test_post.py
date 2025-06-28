import requests

url = "http://127.0.0.1:5000/save-job"

job = {
    "title": "Python Developer",
    "company": "OpenAI",
    "location": "Remote",
    "apply_link": "https://openai.com/careers/python-dev"
}

response = requests.post(url, json=job)

print("Status Code:", response.status_code)
print("Response:", response.text)
