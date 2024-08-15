import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse, parse_qs
import requests
from datetime import datetime
import gpxpy
import gpxpy.gpx
import io

# Strava API settings
CLIENT_ID = "67174"
CLIENT_SECRET = "e6b45fcea5836d356bb3c81908b5dbdaa363b1ed"
REDIRECT_URI = "http://localhost:8000"
SCOPE = "activity:write,activity:read_all"

AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
TOKEN_URL = "https://www.strava.com/oauth/token"
UPLOAD_URL = "https://www.strava.com/api/v3/uploads"

auth_code = None

# Embedded GPS data
GPS_DATA = """timestamp,latitude,longitude,elevation
2023-08-15T07:00:00+09:00,37.52415,126.93407,10
2023-08-15T07:00:30+09:00,37.52428,126.93461,10
2023-08-15T07:01:00+09:00,37.52441,126.93515,11
2023-08-15T07:01:30+09:00,37.52454,126.93569,11
2023-08-15T07:02:00+09:00,37.52467,126.93623,12
2023-08-15T07:02:30+09:00,37.52480,126.93677,12
2023-08-15T07:03:00+09:00,37.52493,126.93731,13
2023-08-15T07:03:30+09:00,37.52506,126.93785,13
2023-08-15T07:04:00+09:00,37.52519,126.93839,14
2023-08-15T07:04:30+09:00,37.52532,126.93893,14
2023-08-15T07:05:00+09:00,37.52545,126.93947,15
2023-08-15T07:05:30+09:00,37.52558,126.94001,15
2023-08-15T07:06:00+09:00,37.52571,126.94055,16
2023-08-15T07:06:30+09:00,37.52584,126.94109,16
2023-08-15T07:07:00+09:00,37.52597,126.94163,17
2023-08-15T07:07:30+09:00,37.52610,126.94217,17
2023-08-15T07:08:00+09:00,37.52623,126.94271,18
2023-08-15T07:08:30+09:00,37.52636,126.94325,18
2023-08-15T07:09:00+09:00,37.52649,126.94379,19
2023-08-15T07:09:30+09:00,37.52662,126.94433,19
2023-08-15T07:10:00+09:00,37.52675,126.94487,20"""

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

def create_gpx_from_data():
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    csv_file = io.StringIO(GPS_DATA)
    next(csv_file)  # Skip the header row
    for line in csv_file:
        timestamp, lat, lon, ele = line.strip().split(',')
        time = datetime.fromisoformat(timestamp)
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(float(lat), float(lon), elevation=float(ele), time=time))

    return gpx

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

def main():
    try:
        access_token = get_authorization()
        print("Authorization successful!")

        print("Creating GPX file from embedded data...")
        gpx = create_gpx_from_data()
        gpx_content = gpx.to_xml()

        print("Uploading activity to Strava...")
        upload_response = upload_to_strava(access_token, gpx_content)
        print(f"Upload successful! Activity ID: {upload_response['id']}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()