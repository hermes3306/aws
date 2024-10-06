import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse, parse_qs
import requests
import json
import os
import time
from datetime import datetime, timedelta
import unicodedata
import re

# Strava API settings
CLIENT_ID = "67174"
CLIENT_SECRET = "11deb64d5fc70d28aed865992a6792f28edce3c6"
REDIRECT_URI = "http://localhost:8000"
SCOPE = "activity:read_all"
AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
ACTIVITY_STREAMS_URL = "https://www.strava.com/api/v3/activities/{}/streams"

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

def get_all_activities(access_token):
    all_activities = []
    page = 1
    per_page = 200

    while True:
        try:
            params = {'page': page, 'per_page': per_page}
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"Failed to retrieve activities on page {page}: {response.content}")
                break
            
            activities = response.json()
            if not activities:
                break
            
            all_activities.extend(activities)
            page += 1
            time.sleep(1)  # To avoid hitting rate limits
        except Exception as e:
            print(f"Error retrieving activities on page {page}: {str(e)}")
            break

    return all_activities

def get_activity_streams(access_token, activity_id):
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {'keys': 'time,latlng,altitude', 'key_by_type': 'true'}
        response = requests.get(ACTIVITY_STREAMS_URL.format(activity_id), headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to retrieve streams for activity {activity_id}: {response.content}")
            return None
        return response.json()
    except Exception as e:
        print(f"Error retrieving streams for activity {activity_id}: {str(e)}")
        return None

def create_gpx(activity, streams):
    gpx = ['<?xml version="1.0" encoding="UTF-8"?>']
    gpx.append('<gpx creator="Strava" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">')
    gpx.append(f'<metadata><time>{activity["start_date"]}</time></metadata>')
    gpx.append('<trk>')
    gpx.append(f'<name>{activity["name"]}</name>')
    gpx.append('<type>1</type>')
    gpx.append('<trkseg>')

    start_time = datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ")

    for i in range(len(streams['latlng']['data'])):
        lat, lng = streams['latlng']['data'][i]
        alt = streams['altitude']['data'][i] if 'altitude' in streams else 0
        time = start_time + timedelta(seconds=streams['time']['data'][i])
        gpx.append(f'<trkpt lat="{lat}" lon="{lng}">')
        gpx.append(f'<ele>{alt}</ele>')
        gpx.append(f'<time>{time.strftime("%Y-%m-%dT%H:%M:%SZ")}</time>')
        gpx.append('</trkpt>')

    gpx.append('</trkseg>')
    gpx.append('</trk>')
    gpx.append('</gpx>')

    return '\n'.join(gpx)

def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    return filename

def save_activities_and_gpx(access_token, activities):
    if not os.path.exists('strava_activities'):
        os.makedirs('strava_activities')
    
    if not os.path.exists('strava_gpx'):
        os.makedirs('strava_gpx')
    
    total_activities = len(activities)
    processed_activities = 0
    saved_activities = 0
    saved_gpx = 0

    for activity in activities:
        processed_activities += 1
        safe_name = sanitize_filename(activity['name'])
        
        json_filename = f"strava_activities/activity_{activity['id']}_{safe_name}.json"
        if not os.path.exists(json_filename):
            try:
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(activity, f, indent=2, ensure_ascii=False)
                saved_activities += 1
                print(f"Saved activity {activity['id']} to {json_filename}")
            except Exception as e:
                print(f"Error saving activity {activity['id']}: {str(e)}")
        else:
            print(f"Activity {activity['id']} already exists, skipping")

        gpx_filename = f"strava_gpx/activity_{activity['id']}_{safe_name}.gpx"
        if not os.path.exists(gpx_filename):
            streams = get_activity_streams(access_token, activity['id'])
            if streams:
                try:
                    gpx_content = create_gpx(activity, streams)
                    with open(gpx_filename, 'w', encoding='utf-8') as f:
                        f.write(gpx_content)
                    saved_gpx += 1
                    print(f"Saved GPX for activity {activity['id']} to {gpx_filename}")
                except Exception as e:
                    print(f"Error saving GPX for activity {activity['id']}: {str(e)}")
            else:
                print(f"No GPX data available for activity {activity['id']}")
        else:
            print(f"GPX for activity {activity['id']} already exists, skipping")

        print(f"Progress: {processed_activities}/{total_activities} activities processed")
        print(f"Saved: {saved_activities} JSON files, {saved_gpx} GPX files")
        time.sleep(1)  # API 요청 제한 고려

def main():
    try:
        access_token = get_authorization()
        print("Authorization successful!")

        print("Retrieving all activities...")
        activities = get_all_activities(access_token)
        print(f"Retrieved {len(activities)} activities.")

        print("Saving activities and GPX files...")
        save_activities_and_gpx(access_token, activities)

        print("All activities and available GPX files have been processed!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()