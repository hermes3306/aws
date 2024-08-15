import requests
import json
from datetime import datetime, timedelta

# Strava API endpoints
AUTH_URL = "https://www.strava.com/oauth/token"
UPLOAD_URL = "https://www.strava.com/api/v3/activities"

# Your Strava API credentials
CLIENT_ID = "67174"
CLIENT_SECRET = "e6b45fcea5836d356bb3c81908b5dbdaa363b1ed"
REFRESH_TOKEN = "a8f6357b7a455bd2d980d05dcd7c072b1b4501e2"
ACCENT_TOKEN = "7d69beef5cb4e4e86588f04542bbdcdc67c12eda"

def get_access_token():
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    response = requests.post(AUTH_URL, data=payload)
    access_token = response.json()['access_token']
    return access_token

def create_activity_data():
    # Create a sample activity (a 5km run)
    start_time = datetime.now() - timedelta(hours=1)
    activity_data = {
        "name": "Morning Run",
        "type": "Run",
        "start_date_local": start_time.isoformat(),
        "elapsed_time": 1800,  # 30 minutes in seconds
        "description": "A test activity uploaded via API",
        "distance": 5000,  # 5km in meters
    }
    return activity_data

def upload_activity(access_token, activity_data):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(UPLOAD_URL, json=activity_data, headers=headers)
    return response

def main():
    print("Starting Strava upload test...")
    
    # Get access token
    access_token = get_access_token()
    print("Access token obtained.")

    # Create mock activity data
    activity_data = create_activity_data()
    print("Activity data created:", json.dumps(activity_data, indent=2))

    # Upload activity
    response = upload_activity(access_token, activity_data)
    
    if response.status_code == 201:
        print("Activity uploaded successfully!")
        print("Response:", json.dumps(response.json(), indent=2))
    else:
        print("Failed to upload activity.")
        print("Status code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    main()