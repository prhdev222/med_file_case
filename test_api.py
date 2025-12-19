import requests
import json

# Test the login API - Use Flask server port
url = "http://127.0.0.1:5000/api/admin/auth/login"
headers = {"Content-Type": "application/json"}
data = {"username": "admin", "password": "admin123"}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")