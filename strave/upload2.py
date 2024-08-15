import requests
import json
import csv
from datetime import datetime, timezone

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
    print(access_token)
    return access_token

def read_gps_data(filename):
    gps_data = []
    with open(filename, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            gps_data.append({
                'time': row['timestamp'],
                'lat': float(row['latitude']),
                'lng': float(row['longitude']),
                'elevation': float(row['elevation'])
            })
    return gps_data

def create_activity_data(gps_data):
    start_time = datetime.fromisoformat(gps_data[0]['time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(gps_data[-1]['time'].replace('Z', '+00:00'))
    duration = (end_time - start_time).total_seconds()

    activity_data = {
        "name": f"Running Activity on {start_time.strftime('%Y-%m-%d')}",
        "type": "Run",
        "start_date_local": start_time.isoformat(),
        "elapsed_time": int(duration),
        "description": "A test activity uploaded via API with GPS data",
    }

    return activity_data

def upload_activity(access_token, activity_data, gps_data):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Convert GPS data to Strava's expected format
    streams = {
        "time": [],
        "latlng": [],
        "altitude": []
    }
    for point in gps_data:
        streams["time"].append(int((datetime.fromisoformat(point['time'].replace('Z', '+00:00')) - datetime.fromisoformat(gps_data[0]['time'].replace('Z', '+00:00'))).total_seconds()))
        streams["latlng"].append([point['lat'], point['lng']])
        streams["altitude"].append(point['elevation'])

    activity_data["streams"] = streams

    response = requests.post(UPLOAD_URL, json=activity_data, headers=headers)
    return response

def main():
    print("Starting Strava upload with GPS data...")
    
    # Get access token
    access_token = get_access_token()
    print("Access token obtained.")

    # Read GPS data
    gps_data = read_gps_data('gps_data.csv')
    print(f"Loaded {len(gps_data)} GPS points.")

    # Create activity data
    activity_data = create_activity_data(gps_data)
    print("Activity data created:", json.dumps(activity_data, indent=2))

    # Upload activity with GPS data
    response = upload_activity(access_token, activity_data, gps_data)
    
    if response.status_code == 201:
        print("Activity uploaded successfully!")
        print("Response:", json.dumps(response.json(), indent=2))
    else:
        print("Failed to upload activity.")
        print("Status code:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    main()