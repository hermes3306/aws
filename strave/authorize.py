import requests
from urllib.parse import urlencode
import webbrowser

# Step 1: Set up your application's credentials
client_id = "67174"
client_secret = "e6b45fcea5836d356bb3c81908b5dbdaa363b1ed"
redirect_uri = "http://localhost"  # You can use this even without a local server

# Step 2: Construct the authorization URL
auth_url = "https://www.strava.com/oauth/authorize"
params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": "activity:write,activity:read_all"  # Include necessary scopes
}
auth_link = f"{auth_url}?{urlencode(params)}"

print(f"Please visit this URL to authorize the application: {auth_link}")
webbrowser.open(auth_link)

# Step 3: Get the authorization code from the redirected URL
auth_code = input("Enter the code from the redirected URL: ")

# Step 4: Exchange the authorization code for tokens
token_url = "https://www.strava.com/oauth/token"
data = {
    "client_id": "67174",
    "client_secret": "e6b45fcea5836d356bb3c81908b5dbdaa363b1ed",
    "code": "a8f6357b7a455bd2d980d05dcd7c072b1b4501e2",
    "grant_type": "authorization_code"
}


response = requests.post(token_url, data=data)

if response.status_code == 200:
    tokens = response.json()
    print("Authorization successful!")
    print(f"Access Token: {tokens['access_token']}")
    print(f"Refresh Token: {tokens['refresh_token']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)