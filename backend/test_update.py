import requests

JOB_ID = 1
url = f"http://127.0.0.1:5000/jobs/{JOB_ID}"
payload = {"status": "Applied"}

response = requests.put(url, json=payload)

print("Status code:", response.status_code)
print("Response text:")
print(response.text)   # raw HTML or JSON

# If it really is JSON, show the parsed JSON
if response.headers.get("Content-Type", "").startswith("application/json"):
    print("Response JSON:", response.json())

