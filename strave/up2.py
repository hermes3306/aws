import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime, timedelta
import gpxpy
import gpxpy.gpx
import time
import random

# Strava API settings
CLIENT_ID = "67174"
CLIENT_SECRET = "e6b45fcea5836d356bb3c81908b5dbdaa363b1ed"
REDIRECT_URI = "http://localhost:8000"
SCOPE = "activity:write,activity:read_all"

AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
TOKEN_URL = "https://www.strava.com/oauth/token"
UPLOAD_URL = "https://www.strava.com/api/v3/uploads"
ACTIVITIES_URL = "https://www.strava.com/api/v3/activities"

auth_code = None

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urlparse(self.path).query
        query_components = parse_qs(query)
        if 'code' in query_components:
            auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window now.")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

def get_authorization():
    with socketserver.TCPServer(("", 8000), OAuthHandler) as httpd:
        print("Please authorize the app by visiting:", AUTH_URL)
        webbrowser.open(AUTH_URL)
        httpd.handle_request()
    
    if not auth_code:
        raise Exception("Failed to get authorization code")
    
    response = requests.post(TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code'
    })
    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.content}")
    return response.json()['access_token']

def get_recent_activities(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'after': int((datetime.now() - timedelta(days=1)).timestamp()),
        'per_page': 30
    }
    response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve recent activities: {response.content}")

def is_duplicate_activity(recent_activities, start_time, distance):
    for activity in recent_activities:
        activity_start = datetime.strptime(activity['start_date'], "%Y-%m-%dT%H:%M:%SZ")
        if abs((activity_start - start_time).total_seconds()) < 300 and abs(activity['distance'] - distance) < 100:
            return True
    return False

def generate_random_gps_data(duration_minutes=10, interval_seconds=30):
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Random start time within the last week
    start_time = datetime.now() - timedelta(days=random.randint(0, 7))
    start_time = start_time.replace(hour=random.randint(6, 20), minute=random.randint(0, 59), second=0, microsecond=0)

    # Starting point (somewhere in Seoul, South Korea)
    lat, lon = 37.5665 + random.uniform(-0.05, 0.05), 126.9780 + random.uniform(-0.05, 0.05)
    ele = 10  # Starting elevation

    total_distance = 0
    prev_point = None

    for i in range(0, duration_minutes * 60, interval_seconds):
        current_time = start_time + timedelta(seconds=i)
        
        # Simulate movement
        lat += random.uniform(-0.0002, 0.0002)
        lon += random.uniform(-0.0002, 0.0002)
        ele += random.uniform(-1, 1)  # Small changes in elevation

        point = gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=ele, time=current_time)
        gpx_segment.points.append(point)

        if prev_point:
            total_distance += point.distance_2d(prev_point)
        prev_point = point

    return gpx, start_time, total_distance

def upload_to_strava(access_token, gpx_content):
    files = {'file': ('activity.gpx', gpx_content)}
    data = {
        'data_type': 'gpx',
        'activity_type': 'run'
    }
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.post(UPLOAD_URL, files=files, data=data, headers=headers)
    if response.status_code != 201:
        raise Exception(f"Failed to upload activity: {response.content}")
    return response.json()

def check_upload_status(access_token, upload_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    for _ in range(60):  # Check for up to 5 minutes (60 * 5 seconds)
        response = requests.get(f"{UPLOAD_URL}/{upload_id}", headers=headers)
        if response.status_code == 200:
            status = response.json()
            if status['status'] == 'Your activity is ready.':
                return status['activity_id']
            elif status['error'] is not None:
                raise Exception(f"Upload failed: {status['error']}")
        time.sleep(5)  # Wait 5 seconds before checking again
    
    raise Exception("Upload processing timed out")

def get_activity_details(access_token, activity_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(f"{ACTIVITIES_URL}/{activity_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve activity details: {response.content}")

def main():
    try:
        access_token = get_authorization()
        print("Authorization successful!")

        print("Generating random GPS data...")
        gpx, start_time, distance = generate_random_gps_data()
        gpx_content = gpx.to_xml()

        print("Checking for recent activities...")
        recent_activities = get_recent_activities(access_token)
        
        if is_duplicate_activity(recent_activities, start_time, distance):
            print("A similar activity already exists. Skipping upload to avoid duplication.")
            return

        print("Uploading activity to Strava...")
        upload_response = upload_to_strava(access_token, gpx_content)
        upload_id = upload_response['id']
        print(f"Upload initiated. Upload ID: {upload_id}")

        print("Checking upload status...")
        activity_id = check_upload_status(access_token, upload_id)
        print(f"Upload successful! Activity ID: {activity_id}")

        print("Retrieving activity details...")
        activity_details = get_activity_details(access_token, activity_id)
        
        print("\nActivity Details:")
        print(f"Name: {activity_details['name']}")
        print(f"Type: {activity_details['type']}")
        print(f"Distance: {activity_details['distance']} meters")
        print(f"Moving Time: {activity_details['moving_time']} seconds")
        print(f"Elapsed Time: {activity_details['elapsed_time']} seconds")
        print(f"Total Elevation Gain: {activity_details['total_elevation_gain']} meters")
        print(f"Start Date: {activity_details['start_date_local']}")
        print(f"Activity URL: https://www.strava.com/activities/{activity_id}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()