import requests

url = "https://www.strava.com/oauth/token"

payload = {
    "client_id": "67174",
    "client_secret": "e6b45fcea5836d356bb3c81908b5dbdaa363b1ed",
    "refresh_token": "a8f6357b7a455bd2d980d05dcd7c072b1b4501e2",
    "grant_type": "refresh_token"
}

response = requests.post(url, data=payload)

if response.status_code == 200:
    print("Token refreshed successfully!")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)