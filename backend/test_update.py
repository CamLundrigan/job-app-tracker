import requests

# 1) Change these as needed:
JOB_ID = 1
NEW_STATUS = "Applied"

url = f"http://127.0.0.1:5000/jobs/{JOB_ID}"
payload = {"status": NEW_STATUS}

response = requests.put(url, json=payload)
print("Status code:", response.status_code)
print("Response JSON:", response.json())

# 2) Optionally, fetch all jobs to confirm:
response2 = requests.get("http://127.0.0.1:5000/jobs")
print("All jobs:", response2.json())
